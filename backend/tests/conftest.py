import os
import sys
import time
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

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


class _TestCollections:
    """Test-only access to raw collections.

    This breaks encapsulation intentionally for cleanup/setup until
    higher-level test helpers are introduced.
    """

    def __init__(self):
        from app.db import db as _db

        # Reach into private attributes.
        self.users = _db._users_collection  # type: ignore[attr-defined]
        self.rules = _db._rules_collection  # type: ignore[attr-defined]
        self.transactions = _db._transactions_collection  # type: ignore[attr-defined]


@pytest.fixture()
def test_collections(app_client) -> _TestCollections:
    return _TestCollections()


@pytest.fixture(autouse=True)
def clean_db(app_client, test_collections):  # app_client first
    test_collections.users.delete_many({})
    test_collections.rules.delete_many({})
    test_collections.transactions.delete_many({})
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
