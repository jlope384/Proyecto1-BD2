from http.client import InvalidURL

from fastapi import APIRouter, HTTPException, Depends, Response
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