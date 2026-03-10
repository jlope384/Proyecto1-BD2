from http.client import InvalidURL

from fastapi import APIRouter, HTTPException
from bson import ObjectId
from utils.utils import serialize_doc
from database import restaurants_collection
from datetime import datetime

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

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