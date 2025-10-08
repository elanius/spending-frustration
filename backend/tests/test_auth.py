from fastapi.testclient import TestClient
from pymongo.collection import Collection


def test_register_and_login_flow(app_client: TestClient, users_col: Collection) -> None:
    email = "user1@example.com"
    password = "Secret123!"
    # Register
    resp = app_client.post(
        "/auth/register", json={"email": email, "password": password}
    )
    assert resp.status_code == 201, resp.text
    # DB state after create
    user_docs = list(users_col.find({}))
    assert len(user_docs) == 1
    assert user_docs[0]["email"] == email
    assert "hashed_password" in user_docs[0]
    assert "password" not in user_docs[0]
    # Duplicate register should fail
    dup = app_client.post("/auth/register", json={"email": email, "password": password})
    assert dup.status_code == 400
    # Login
    login = app_client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200, login.text
    data = login.json()
    assert "access_token" in data and data["token_type"] == "bearer"
