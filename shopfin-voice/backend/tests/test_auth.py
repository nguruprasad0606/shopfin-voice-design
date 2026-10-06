from tests.conftest import make_user


def test_register_login_me(client):
    make_user(client)
    r = client.post("/api/auth/login", json={"email": "OWNER@example.com", "password": "secret123"})
    assert r.status_code == 200
    me = client.get("/api/auth/me", headers={"Authorization": "Bearer " + r.json()["access_token"]})
    assert me.json()["shop"] == "Test Shop"


def test_duplicate_email_and_bad_password(client):
    make_user(client)
    assert client.post("/api/auth/register", json={
        "name": "X Y", "email": "owner@example.com", "password": "secret123",
        "shop": "S2", "type": "Retail"}).status_code == 409
    assert client.post("/api/auth/login", json={"email": "owner@example.com", "password": "nope"}).status_code == 401


def test_swagger_form_login(client):
    make_user(client)
    r = client.post("/api/auth/token", data={"username": "owner@example.com", "password": "secret123"})
    assert r.status_code == 200


def test_requires_token(client):
    assert client.get("/api/transactions/").status_code == 401
