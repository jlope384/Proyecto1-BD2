from fastapi import APIRouter, HTTPException
from bson import ObjectId
from database import reviews_collection
from datetime import datetime
from utils.utils import serialize_doc

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/")
def create_review(data: dict):
    data["from_user"] = ObjectId(data["from_user"])
    data["for_restaurant"] = ObjectId(data["for_restaurant"])
    data["created_at"] = datetime.utcnow()

    result = reviews_collection.insert_one(data)
    return {"id": str(result.inserted_id)}

@router.get("/")
def get_reviews():
    reviews = list(reviews_collection.find())
    return [serialize_doc(r) for r in reviews]

@router.get("/restaurant/{restaurant_id}")
def get_reviews_by_restaurant(restaurant_id: str):
    reviews = list(
        reviews_collection.find({"for_restaurant": ObjectId(restaurant_id)})
    )
    return [serialize_doc(r) for r in reviews]

@router.delete("/{review_id}")
def delete_review(review_id: str):
    reviews_collection.delete_one({"_id": ObjectId(review_id)})
    return {"message": "Review deleted"}