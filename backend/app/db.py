import os
import logging
from bson import ObjectId
from pymongo import MongoClient

from app.models import RuleDB, Transaction, User

logger = logging.getLogger(__name__)

# Central Mongo client/DB setup. For tests we optionally allow an in-memory
# mongomock fallback (triggered by MONGO_URI starting with "mongomock://").
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

if MONGO_URI.startswith("mongomock://"):
    # Lazy import so production deployments do not require mongomock.
    import mongomock  # type: ignore

    mongo_client = mongomock.MongoClient()
    logger.info("Using mongomock MongoDB client for testing")
else:
    mongo_client = MongoClient(MONGO_URI)
    logger.info("Connected to MongoDB at %s", MONGO_URI)


def to_oid(id_str: str) -> ObjectId:
    if not ObjectId.is_valid(id_str):
        raise ValueError(f"Invalid ObjectId: {id_str}")
    return ObjectId(id_str)


class DB:
    def __init__(self):
        self._db = mongo_client[os.getenv("MONGO_DB", "spending-frustration")]
        # Private collections
        self._users_collection = self._db["users"]
        self._transactions_collection = self._db["transactions"]
        self._rules_collection = self._db["rules"]
        logger.info("Database initialized: %s", self._db.name)

    def get_user(self, username: str) -> User:
        user_doc = self._users_collection.find_one({"username": username})
        if not user_doc:
            raise ValueError(f"User '{username}' not found")
        return User.model_validate(user_doc)

    def create_user(self, user: User) -> str:
        res = self._users_collection.insert_one(user.model_dump(exclude_none=True))
        return str(res.inserted_id)

    def get_rules(self, user_id: str) -> list[RuleDB]:
        # Return all rule documents for a user
        docs = self._rules_collection.find({"user_id": to_oid(user_id)})
        rules = [RuleDB.model_validate(doc) for doc in docs]
        return rules

    def add_rule(self, user_id: str, rule, priority: int = 0):
        if hasattr(rule, "model_dump"):
            doc = rule.model_dump(exclude_none=True)
        elif isinstance(rule, dict):
            doc = dict(rule)
        else:
            raise ValueError("rule must be RuleDB or dict")

        # ensure user_id stored as ObjectId
        doc["user_id"] = to_oid(user_id)
        res = self._rules_collection.insert_one(doc)
        return str(res.inserted_id)

    def get_rule(self, rule_id: str) -> RuleDB | None:
        doc = self._rules_collection.find_one({"_id": to_oid(rule_id)})
        if not doc:
            return None
        return RuleDB.model_validate(doc)

    def update_rule(self, rule_id: str, update_data: dict) -> bool:
        # Convert user-provided id fields if present
        if "user_id" in update_data:
            update_data["user_id"] = to_oid(update_data["user_id"])
        res = self._rules_collection.update_one({"_id": to_oid(rule_id)}, {"$set": update_data})
        return res.modified_count > 0

    def delete_rule(self, rule_id: str) -> bool:
        res = self._rules_collection.delete_one({"_id": to_oid(rule_id)})
        return res.deleted_count > 0

    def get_transaction(self, tx_id: str) -> Transaction | None:
        doc = self._transactions_collection.find_one({"_id": to_oid(tx_id)})
        if not doc:
            return None
        return Transaction.model_validate(doc)

    def insert_transactions(self, transactions: list[Transaction]) -> list[str]:
        docs = []
        for tx in transactions:
            doc = tx.model_dump(exclude_none=True)
            doc["user_id"] = to_oid(tx.user_id)
            docs.append(doc)

        if not docs:
            return []
        logger.info("Inserting %d transactions", len(docs))
        res = self._transactions_collection.insert_many(docs)
        inserted = [str(_id) for _id in res.inserted_ids]
        logger.info("Inserted %d transactions", len(inserted))
        return inserted

    def update_transaction(self, tx_id: str, transaction: Transaction) -> bool:
        logger.debug(f"Updating transaction {tx_id} with data: {transaction}")
        tx_doc = transaction.model_dump(exclude_none=True)
        tx_doc["user_id"] = to_oid(transaction.user_id)

        res = self._transactions_collection.update_one({"_id": to_oid(tx_id)}, {"$set": tx_doc})
        if res.modified_count:
            logger.info("Updated transaction %s", tx_id)
        return res.modified_count > 0

    def get_transactions(self, user: str) -> list[Transaction]:
        docs = self._transactions_collection.find({"user_id": to_oid(user)})
        return [Transaction.model_validate(doc) for doc in docs]


db = DB()
