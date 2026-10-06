import os
import tempfile

# Must be set before the app is imported so tests never touch the real database.
_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_db.name}"

import pytest
from fastapi.testclient import TestClient

from app.database.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestClient(app)


def make_user(client, email="owner@example.com", shop="Test Shop"):
    r = client.post("/api/auth/register", json={
        "name": "Owner", "email": email, "password": "secret123", "shop": shop, "type": "Retail Shop"})
    assert r.status_code == 201, r.text
    return {"Authorization": "Bearer " + r.json()["access_token"]}


@pytest.fixture()
def auth(client):
    return make_user(client)
