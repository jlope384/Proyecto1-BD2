from fastapi import APIRouter, HTTPException
from bson import ObjectId
from database import client
from datetime import datetime
from utils.utils import serialize_doc

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/")
def create_order(user_id: str, restaurant_id: str, order_data: dict):

    with client.start_session() as session:
        with session.start_transaction():

            db = session.client.restaurant_system
            users_collection = db.users
            restaurants_collection = db.restaurants

            order_data["created_at"] = datetime.utcnow()
            order_data["for_restaurant"] = ObjectId(restaurant_id)

            user_result = users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"orders": order_data}},
                session=session
            )

            restaurant_result = restaurants_collection.update_one(
                {"_id": ObjectId(restaurant_id)},
                {"$inc": {"total_orders": 1}},
                session=session
            )

            if user_result.matched_count == 0 or restaurant_result.matched_count == 0:
                raise HTTPException(status_code=404, detail="User or Restaurant not found")

    return {"message": "Order created successfully"}

@router.get("/user/{user_id}")
def get_user_orders(user_id: str):
    user = client.restaurant_system.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(404, "User not found")

    return serialize_doc({"orders": user.get("orders", [])})