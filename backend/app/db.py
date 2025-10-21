import os
from bson import ObjectId
from pymongo import MongoClient

# Central Mongo client/DB setup. For tests we optionally allow an in-memory
# mongomock fallback (triggered by MONGO_URI starting with "mongomock://").
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

if MONGO_URI.startswith("mongomock://"):
    # Lazy import so production deployments do not require mongomock.
    import mongomock  # type: ignore

    client = mongomock.MongoClient()
else:
    client = MongoClient(MONGO_URI)

db = client[os.getenv("MONGO_DB", "spending-frustration")]
users_collection = db["users"]
transactions_collection = db["transactions"]
rules_collection = db["rules"]
user_rules_collection = db["user_rules"]


def get_user_id(user: str) -> ObjectId:
    """Helper to get a user's ObjectId by email."""
    user_doc = users_collection.find_one({"email": user})
    if not user_doc:
        raise ValueError(f"User '{user}' not found")
    return user_doc["_id"]
