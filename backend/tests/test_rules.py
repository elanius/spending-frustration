from fastapi.testclient import TestClient
from pymongo.collection import Collection


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_rules_crud(
    app_client: TestClient,
    auth_token: str,
    rules_col: Collection,
    users_col: Collection,
) -> None:
    # Create
    rule_payload = {
        "conditions": [
            {"field": "merchant", "operator": "contains", "value": "coffee"}
        ],
        "logical_operator": "AND",
        "priority": 5,
        "action": {"category": "food_drink", "tags": ["coffee"]},
    }
    create_resp = app_client.post(
        "/rules", json=rule_payload, headers=auth_header(auth_token)
    )
    assert create_resp.status_code == 201, create_resp.text
    created_body = create_resp.json()
    rule_id = created_body["_id"]
    # DB assertion: rule exists with correct fields
    db_rule = rules_col.find_one({"_id": __import__("bson").ObjectId(rule_id)})
    assert db_rule is not None
    assert db_rule["priority"] == 5
    assert db_rule["conditions"][0]["field"] == "merchant"

    # List
    list_resp = app_client.get("/rules", headers=auth_header(auth_token))
    assert list_resp.status_code == 200
    assert any(rule["_id"] == rule_id for rule in list_resp.json())

    # Get single
    get_resp = app_client.get(f"/rules/{rule_id}", headers=auth_header(auth_token))
    assert get_resp.status_code == 200

    # Update
    update_resp = app_client.put(
        f"/rules/{rule_id}",
        json={"priority": 10},
        headers=auth_header(auth_token),
    )
    assert update_resp.status_code == 200
    # Verify update persisted
    updated_rule = rules_col.find_one({"_id": db_rule["_id"]})
    assert updated_rule["priority"] == 10

    # Delete
    del_resp = app_client.delete(f"/rules/{rule_id}", headers=auth_header(auth_token))
    assert del_resp.status_code == 200

    # Ensure deleted (API + DB)
    missing = app_client.get(f"/rules/{rule_id}", headers=auth_header(auth_token))
    assert missing.status_code == 404
    assert rules_col.find_one({"_id": db_rule["_id"]}) is None
