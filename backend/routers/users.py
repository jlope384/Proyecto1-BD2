from fastapi import APIRouter, HTTPException, Depends, Response
from bson import ObjectId
from database import users_collection
from datetime import datetime
from utils.utils import serialize_doc, allow_all_cors

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(allow_all_cors)],
)

@router.options("/{full_path:path}")
def users_cors(full_path: str, response: Response):
    allow_all_cors(response)
    return {"status": "ok"}

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

@router.post("/login")
def login(data: dict):

    username = data.get("username")
    password = data.get("password")

    user = users_collection.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if password != user["hashed_password_with_user_sided_salt"]:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "message": "Login successful",
        "user_id": str(user["_id"])
    }