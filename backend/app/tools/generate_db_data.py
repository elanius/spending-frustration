"""Utility script to seed the database with one demo user and synthetic transactions.

Usage (run from project root or backend/):

    python -m app.tools.generate_db_data \
        --email demo@example.com \
        --password Secret123! \
        --count 250 \
        --seed 42 \
        --wipe

Options:
  --email / --password : credentials for the (single) user to create or reuse.
  --count               : number of transactions to generate (default: 100).
  --seed                : RNG seed for reproducibility.
  --wipe                : if provided, existing transactions for the user are deleted.

The script uses the Pydantic models defined in `app.models` for validation before
inserting documents. It talks directly to Mongo via `app.db`.

Environment variables honored:
  MONGO_URI (default: mongodb://localhost:27017/ )
  MONGO_DB  (default: spending-frustration)
"""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta, timezone
from typing import List

from bson import ObjectId

from app.auth import get_password_hash
from app.db import users_collection, transactions_collection
from app.models import DBUser, DBTransaction


MERCHANTS = [
    ("Coffee Roasters", "food_drink", ["coffee", "morning"]),
    ("Sandwich Shop", "food_drink", ["lunch"]),
    ("Grocery Market", "groceries", ["weekly", "food"]),
    ("Online Books", "shopping", ["books"]),
    ("Streaming Service", "entertainment", ["subscription", "streaming"]),
    ("Gas Station", "transport", ["fuel", "car"]),
    ("Ride Share", "transport", ["uber"]),
    ("Pharmacy", "health", ["meds"]),
    ("Gym Membership", "fitness", ["health", "subscription"]),
    ("Movie Theater", "entertainment", ["movies"]),
]


def ensure_user(email: str, password: str) -> DBUser:
    """Create the user if absent. Returns a DBUser (without reliable _id attribute).

    Note: Pydantic v2 treats underscore-prefixed names as protected by default, so
    DBUser._id may be None. Always fetch the ObjectId separately from the collection
    when you need it.
    """
    existing = users_collection.find_one({"email": email})
    if existing:
        return DBUser.model_validate(existing)
    hashed_password = get_password_hash(password)
    user_doc = {"email": email, "hashed_password": hashed_password}
    result = users_collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return DBUser.model_validate(user_doc)


def generate_transactions(
    user_id: ObjectId, count: int, now: datetime
) -> List[DBTransaction]:
    txs: List[DBTransaction] = []
    for _ in range(count):
        merchant, category, base_tags = random.choice(MERCHANTS)
        day_offset = int(random.random() ** 2 * 90)
        date = now - timedelta(
            days=day_offset, hours=random.randint(0, 23), minutes=random.randint(0, 59)
        )
        amount_mean_lookup = {
            "Coffee Roasters": 5.5,
            "Sandwich Shop": 14.0,
            "Grocery Market": 85.0,
            "Online Books": 28.0,
            "Streaming Service": 12.99,
            "Gas Station": 45.0,
            "Ride Share": 18.0,
            "Pharmacy": 22.0,
            "Gym Membership": 45.0,
            "Movie Theater": 32.0,
        }
        amount_mean = amount_mean_lookup[merchant]
        jitter = random.uniform(-0.4, 0.4)
        amount = round(amount_mean * (1 + jitter), 2)
        tags = base_tags[:]
        if random.random() < 0.25:
            tags.append("sale")
        if random.random() < 0.1:
            tags.append("promo")
        tags = sorted(set(tags))
        notes = None
        if random.random() < 0.15:
            notes = f"Auto-generated {merchant.lower()} expense"
        tx = DBTransaction(
            user_id=user_id,
            date=date,
            amount=amount,
            merchant=merchant,
            category=category,
            tags=tags,
            notes=notes,
        )
        txs.append(tx)
    return txs


def main():  # pragma: no cover - utility script
    parser = argparse.ArgumentParser(description="Seed database with synthetic data")
    parser.add_argument("--email", required=True, help="User email to create/use")
    parser.add_argument(
        "--password", required=True, help="Password for the user if created"
    )
    parser.add_argument(
        "--count", type=int, default=100, help="Number of transactions to generate"
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--wipe",
        action="store_true",
        help="Delete existing transactions for this user first",
    )
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    ensure_user(args.email, args.password)
    # Always fetch real Mongo document to get ObjectId
    user_doc = users_collection.find_one({"email": args.email})
    assert user_doc is not None, "User document unexpectedly missing after creation"
    user_id: ObjectId = user_doc["_id"]

    if args.wipe:
        deleted = transactions_collection.delete_many(
            {"user_id": user_id}
        ).deleted_count
        print(f"Wiped {deleted} existing transactions for {args.email}")

    now = datetime.now(timezone.utc)
    tx_models = generate_transactions(user_id, args.count, now)
    documents = [tx.model_dump() for tx in tx_models]
    if documents:
        result = transactions_collection.insert_many(documents)
        print(f"Inserted {len(result.inserted_ids)} transactions for {args.email}")
    else:
        print("No transactions generated")

    sample = (
        transactions_collection.find({"user_id": user_id}).sort("date", -1).limit(3)
    )
    print("Sample (latest 3):")
    for doc in sample:
        print(
            f"  {doc['date'].date()} | {doc['merchant']:<18} | ${doc['amount']:>6} | {doc.get('category', '')} | tags={', '.join(doc.get('tags', []))}"
        )


if __name__ == "__main__":
    main()
