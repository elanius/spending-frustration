import os
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
