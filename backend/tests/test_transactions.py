from bson import json_util
from fastapi.testclient import TestClient
from mongomock import Collection

from app.models import Transaction


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_transactions_flow(
    app_client: TestClient, auth_token: str, users_collection: Collection, transactions_collection: Collection
) -> None:
    user = users_collection.find_one()
    assert user is not None
    user_id = user["_id"]

    list_empty = app_client.get("/transactions", headers=auth_header(auth_token))
    assert list_empty.status_code == 200
    assert list_empty.json() == []

    with open("backend/tests/data/transactions.json", "r", encoding="utf-8") as f:
        transactions_arr = json_util.loads(f.read())
        for tx in transactions_arr:
            tx["user_id"] = user_id

        transactions_collection.insert_many(transactions_arr)

    # List after insert
    list_resp = app_client.get("/transactions", headers=auth_header(auth_token))
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 4

    transactions = [Transaction.model_validate(tx) for tx in items]

    first_id = transactions[0].id

    # # Filter by merchant substring
    # filter_resp = app_client.get(
    #     "/transactions/filter",
    #     params={"merchant_contains": "coffee"},
    #     headers=auth_header(auth_token),
    # )
    # assert filter_resp.status_code == 200
    # assert any("Coffee" in tx["merchant"] for tx in filter_resp.json())

    # # Patch one transaction
    # patch_resp = app_client.patch(
    #     f"/transactions/{first_id}",
    #     json={"notes": "Updated note"},
    #     headers=auth_header(auth_token),
    # )
    # assert patch_resp.status_code == 200

    # Get single to verify patch
    get_one = app_client.get(f"/transactions/{first_id}", headers=auth_header(auth_token))
    assert get_one.status_code == 200
    first_transaction = Transaction.model_validate(get_one.json())
    assert first_transaction == transactions[0]
