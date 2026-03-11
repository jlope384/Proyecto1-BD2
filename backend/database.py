import os
import logging
from pathlib import Path
from pymongo import MongoClient, monitoring
from dotenv import load_dotenv
from gridfs import GridFS

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
LOG_MONGO_COMMANDS = (os.getenv("LOG_MONGO_COMMANDS", "true").lower() == "true")

if not MONGO_URI:
    raise ValueError("MONGO_URI not found in environment variables")

if not DB_NAME:
    raise ValueError("DB_NAME not found in environment variables")

query_logger = logging.getLogger("restaurant_system.mongo")

class MongoCommandLogger(monitoring.CommandListener):
    def started(self, event):
        collection = event.command.get(event.command_name)
        safe_command = {k: v for k, v in event.command.items() if k not in {"$readPreference", "$db", "lsid", "$clusterTime", "$readConcern"}}
        query_logger.info(
            "[%s] %s.%s -> %s",
            event.command_name.upper(),
            event.database_name,
            collection,
            safe_command,
        )

    def failed(self, event):
        query_logger.error(
            "[%s] FAILED %s.%s (%s)",
            event.command_name.upper(),
            event.database_name,
            event.command.get(event.command_name),
            event.failure,
        )

if LOG_MONGO_COMMANDS and not query_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[MongoDB] %(message)s"))
    query_logger.addHandler(handler)
    query_logger.setLevel(logging.INFO)
    monitoring.register(MongoCommandLogger())

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

fs = GridFS(db)

restaurants_collection = db["restaurants"]
users_collection = db["users"]
reviews_collection = db["reviews"]
orders_historic_collection = db["orders_historic"]