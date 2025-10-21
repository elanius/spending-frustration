import bson
from datetime import datetime
from fastapi.testclient import TestClient
from pymongo.collection import Collection


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_transactions_flow(app_client: TestClient, auth_token: str, transactions_col: Collection) -> None:
    # Start with empty list
    list_empty = app_client.get("/transactions", headers=auth_header(auth_token))
    assert list_empty.status_code == 200
    assert list_empty.json() == []

    # Simulate creating transactions directly in DB (upload endpoint disabled in app)
    # Prepare two documents
    inserted_ids = []
    for row in [
        {
            "date": datetime(2025, 9, 1),
            "amount": 42.15,
            "merchant": "Coffee Roasters",
            "category": "food_drink",
            "tags": ["coffee", "morning"],
            "notes": "Team sync latte",
        },
        {
            "date": datetime(2025, 9, 2),
            "amount": 15.00,
            "merchant": "Sandwich Shop",
            "category": "food_drink",
            "tags": ["lunch"],
            "notes": None,
        },
    ]:
        result = transactions_col.insert_one(
            {
                **row,
                "user_id": transactions_col.database["users"].find_one()["_id"],
            }
        )
        inserted_ids.append(result.inserted_id)

    # List after insert
    list_resp = app_client.get("/transactions", headers=auth_header(auth_token))
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 2
    first_id = items[0]["_id"] if "_id" in items[0] else items[0]["id"]
    # DB assertion: two docs present
    db_docs = list(transactions_col.find({}))
    assert len(db_docs) == 2
    merchants = {doc["merchant"] for doc in db_docs}
    assert merchants == {"Coffee Roasters", "Sandwich Shop"}

    # Filter by merchant substring
    filter_resp = app_client.get(
        "/transactions/filter",
        params={"merchant_contains": "coffee"},
        headers=auth_header(auth_token),
    )
    assert filter_resp.status_code == 200
    assert any("Coffee" in tx["merchant"] for tx in filter_resp.json())

    # Patch one transaction
    patch_resp = app_client.patch(
        f"/transactions/{first_id}",
        json={"notes": "Updated note"},
        headers=auth_header(auth_token),
    )
    assert patch_resp.status_code == 200

    # Get single to verify patch
    get_one = app_client.get(f"/transactions/{first_id}", headers=auth_header(auth_token))
    assert get_one.status_code == 200
    assert get_one.json()["notes"] == "Updated note"
    # DB assertion for patch
    patched_doc = transactions_col.find_one({"_id": bson.ObjectId(first_id)})
    assert patched_doc is not None and patched_doc["notes"] == "Updated note"
