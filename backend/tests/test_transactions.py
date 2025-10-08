import io
import csv
import bson
from fastapi.testclient import TestClient
from pymongo.collection import Collection


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_transactions_flow(
    app_client: TestClient, auth_token: str, transactions_col: Collection
) -> None:
    # Start with empty list
    list_empty = app_client.get("/transactions", headers=auth_header(auth_token))
    assert list_empty.status_code == 200
    assert list_empty.json() == []

    # Upload CSV to create transactions
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["date", "amount", "merchant", "category", "tags", "notes"])
    writer.writerow(
        [
            "2025-09-01",
            "42.15",
            "Coffee Roasters",
            "food_drink",
            "coffee,morning",
            "Team sync latte",
        ]
    )
    writer.writerow(
        ["2025-09-02", "15.00", "Sandwich Shop", "food_drink", "lunch", ""]
    )  # second row
    csv_buffer.seek(0)
    files = {"file": ("transactions.csv", csv_buffer.read(), "text/csv")}
    upload_resp = app_client.post(
        "/upload-statement", headers=auth_header(auth_token), files=files
    )
    assert upload_resp.status_code == 200, upload_resp.text
    body = upload_resp.json()
    assert body["inserted"] == 2

    # List again
    list_resp = app_client.get("/transactions", headers=auth_header(auth_token))
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 2
    first_id = items[0]["_id"]
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
    get_one = app_client.get(
        f"/transactions/{first_id}", headers=auth_header(auth_token)
    )
    assert get_one.status_code == 200
    assert get_one.json()["notes"] == "Updated note"
    # DB assertion for patch
    patched_doc = transactions_col.find_one({"_id": bson.ObjectId(first_id)})
    assert patched_doc is not None and patched_doc["notes"] == "Updated note"
