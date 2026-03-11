from http.client import InvalidURL
import re

from fastapi import APIRouter, HTTPException, Depends, Response, Query
from bson import ObjectId
from pymongo import DESCENDING
from utils.utils import serialize_doc, allow_all_cors
from database import restaurants_collection
from datetime import datetime

router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"],
    dependencies=[Depends(allow_all_cors)],
)

@router.options("/{full_path:path}")
def restaurants_cors(full_path: str, response: Response):
    allow_all_cors(response)
    return {"status": "ok"}

@router.post("/")
def create_restaurant(data: dict):
    data["created_at"] = datetime.utcnow()
    data["total_orders"] = 0
    result = restaurants_collection.insert_one(data)
    return {"id": str(result.inserted_id)}

@router.get("/")
def get_restaurants():
    restaurants = list(restaurants_collection.find())
    return [serialize_doc(r) for r in restaurants]

@router.get("/top")
def get_top_restaurants(limit: int = 4):
    if limit < 1 or limit > 50:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 50")

    restaurants = list(
        restaurants_collection.find().sort("total_orders", DESCENDING).limit(limit)
    )
    return [serialize_doc(r) for r in restaurants]

@router.get("/search")
def search_restaurants(
    term: str | None = Query(default=None, alias="term"),
    min_orders: int = Query(default=0, ge=0, alias="min_orders"),
    min_rating: float = Query(default=0.0, ge=0.0, le=5.0, alias="min_rating"),
    limit: int = Query(default=10, ge=1, le=50),
):
    pipeline = []
    match_conditions = []

    if term:
        safe_term = term.strip()
        if safe_term:
            regex = re.compile(re.escape(safe_term), re.IGNORECASE)
            match_conditions.append(
                {
                    "$or": [
                        {"name": regex},
                        {"cuisine": regex},
                        {"city": regex},
                        {"menu_items.name": regex},
                    ]
                }
            )

    if min_orders:
        match_conditions.append({"total_orders": {"$gte": min_orders}})

    if match_conditions:
        pipeline.append({"$match": {"$and": match_conditions}})

    pipeline.extend(
        [
            {
                "$lookup": {
                    "from": "reviews",
                    "localField": "_id",
                    "foreignField": "for_restaurant",
                    "as": "reviews_docs",
                }
            },
            {
                "$addFields": {
                    "ratings_only": {
                        "$filter": {
                            "input": {
                                "$map": {
                                    "input": "$reviews_docs",
                                    "as": "review",
                                    "in": "$$review.rating",
                                }
                            },
                            "as": "rating",
                            "cond": {
                                "$and": [
                                    {"$ne": ["$$rating", None]},
                                    {"$isNumber": "$$rating"},
                                ]
                            },
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "avg_rating": {
                        "$cond": [
                            {"$gt": [{"$size": "$ratings_only"}, 0]},
                            {"$round": [{"$avg": "$ratings_only"}, 2]},
                            None,
                        ]
                    },
                    "rating_count": {"$size": "$ratings_only"},
                }
            },
            {
                "$project": {
                    "ratings_only": 0,
                    "reviews_docs": 0,
                }
            },
        ]
    )

    if min_rating:
        pipeline.append({"$match": {"avg_rating": {"$gte": min_rating}}})

    pipeline.append({"$sort": {"total_orders": DESCENDING, "avg_rating": DESCENDING}})
    pipeline.append({"$limit": limit})

    restaurants = list(restaurants_collection.aggregate(pipeline))
    return [serialize_doc(r) for r in restaurants]

@router.get("/{restaurant_id}")
def get_restaurant(restaurant_id: str):
    try:
        obj_id = ObjectId(restaurant_id)
    except InvalidURL:
        raise HTTPException(status_code=400, detail="Invalid restaurant ID")

    restaurant = restaurants_collection.find_one({"_id": obj_id})

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return serialize_doc(restaurant)

@router.delete("/{restaurant_id}")
def delete_restaurant(restaurant_id: str):
    restaurants_collection.delete_one({"_id": ObjectId(restaurant_id)})
    return {"message": "Deleted"}