from fastapi.testclient import TestClient


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_rules_crud(
    app_client: TestClient,
    auth_token: str,
    test_collections,
) -> None:
    # Create text rule
    rule_payload = {
        "rule": "amount > 100 -> #big",
        "active": True,
    }
    create_resp = app_client.post("/rules", json=rule_payload, headers=auth_header(auth_token))
    assert create_resp.status_code == 201, create_resp.text
    created_body = create_resp.json()
    rule_id = created_body["id"]
    # DB assertion
    db_rule = test_collections.rules.find_one({"_id": __import__("bson").ObjectId(rule_id)})
    assert db_rule is not None
    assert db_rule["rule"] == "amount > 100 -> #big"
    assert db_rule.get("active") is True

    # List
    list_resp = app_client.get("/rules", headers=auth_header(auth_token))
    assert list_resp.status_code == 200
    assert any(rule["id"] == rule_id for rule in list_resp.json())

    # Get single
    get_resp = app_client.get(f"/rules/{rule_id}", headers=auth_header(auth_token))
    assert get_resp.status_code == 200

    # Update
    update_resp = app_client.put(f"/rules/{rule_id}", json={"active": False}, headers=auth_header(auth_token))
    assert update_resp.status_code == 200
    # Verify update persisted
    updated_rule = test_collections.rules.find_one({"_id": db_rule["_id"]})
    assert updated_rule["active"] is False

    # Delete
    del_resp = app_client.delete(f"/rules/{rule_id}", headers=auth_header(auth_token))
    assert del_resp.status_code == 200

    # Ensure deleted (API + DB)
    missing = app_client.get(f"/rules/{rule_id}", headers=auth_header(auth_token))
    assert missing.status_code == 404
    assert test_collections.rules.find_one({"_id": db_rule["_id"]}) is None
