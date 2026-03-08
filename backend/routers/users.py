from fastapi import APIRouter, HTTPException
from bson import ObjectId
from database import users_collection
from datetime import datetime
from utils.utils import serialize_doc

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/")
def create_user(data: dict):
    data["created_at"] = datetime.utcnow()
    data["orders"] = []
    result = users_collection.insert_one(data)
    return {"id": str(result.inserted_id)}

@router.get("/")
def get_users():
    users = list(users_collection.find())
    return [serialize_doc(u) for u in users]

@router.get("/{user_id}")
def get_user(user_id: str):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(404, "User not found")
    return serialize_doc(user)

@router.delete("/{user_id}")
def delete_user(user_id: str):
    users_collection.delete_one({"_id": ObjectId(user_id)})
    return {"message": "User deleted"}