import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv
from gridfs import GridFS

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in environment variables")

if not DB_NAME:
    raise ValueError("DB_NAME not found in environment variables")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

fs = GridFS(db)

restaurants_collection = db["restaurants"]
users_collection = db["users"]
reviews_collection = db["reviews"]
orders_historic_collection = db["orders_historic"]