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

from database import users_collection

@router.get("/")
def get_reviews():
    users = users_collection.find()
    reviews = []

    for user in users:
        for order in user.get("orders", []):
            for item in order.get("menu_items", []):
                if item.get("menu_note"):
                    reviews.append({
                        "user_id": str(user["_id"]),
                        "restaurant_id": str(order["for_restaurant"]),
                        "note": item["menu_note"]
                    })

    return reviews

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