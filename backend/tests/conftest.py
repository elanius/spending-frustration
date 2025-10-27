import os
import sys
import time
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from mongomock import Collection
from app.db import DB

# Ensure backend root (directory containing 'app') is on sys.path even if pytest is launched oddly
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


@pytest.fixture(scope="session")
def mongo_uri() -> str:
    """Provide Mongo URI; default to mongomock unless MONGO_URI provided externally.

    If a developer wants to point at a real Mongo instance they can export MONGO_URI
    before running pytest, e.g. MONGO_URI='mongodb://localhost:27017/'.
    """
    return os.getenv("MONGO_URI", "mongomock://localhost")


@pytest.fixture(scope="session")
def test_db_name() -> str:
    return f"test_db_{int(time.time())}"


@pytest.fixture(scope="session")
def app_client(mongo_uri: str, test_db_name: str) -> TestClient:
    # Configure environment before importing app
    os.environ["MONGO_URI"] = mongo_uri
    os.environ["MONGO_DB"] = test_db_name
    # Import inside fixture to ensure it uses test env
    from app.main import app  # noqa

    return TestClient(app)


@pytest.fixture()
def users_collection() -> Collection:
    return DB.get_instance()._users_collection


@pytest.fixture()
def rules_collection() -> Collection:
    return DB.get_instance()._rules_collection


@pytest.fixture()
def transactions_collection() -> Collection:
    return DB.get_instance()._transactions_collection


@pytest.fixture(autouse=True)
def init_db(
    app_client, users_collection: Collection, rules_collection: Collection, transactions_collection: Collection
):
    users_collection.delete_many({})
    rules_collection.delete_many({})
    transactions_collection.delete_many({})
    yield


@pytest.fixture()
def auth_token(app_client) -> str:
    email = "tester@example.com"
    password = "Secret123!"
    # Register (use username as primary identifier; keep email optional)
    r = app_client.post("/auth/register", json={"username": email, "email": email, "password": password})
    assert r.status_code == 201, r.text
    # Login
    r2 = app_client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r2.status_code == 200, r2.text
    token = r2.json()["access_token"]
    return token
