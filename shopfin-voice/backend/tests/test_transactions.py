from datetime import date

from tests.conftest import make_user


def tx(**kw):
    base = {"type": "Sale", "category": "Sales", "method": "Cash", "amount": 100, "date": date.today().isoformat()}
    return {**base, **kw}


def test_crud(client, auth):
    r = client.post("/api/transactions/", headers=auth, json=tx(amount=250))
    assert r.status_code == 201 and r.json()["type"] == "Sale" and r.json()["amount"] == 250
    tid = r.json()["id"]
    assert len(client.get("/api/transactions/", headers=auth).json()) == 1
    assert client.put(f"/api/transactions/{tid}", headers=auth, json={"amount": 300}).json()["amount"] == 300
    assert client.delete(f"/api/transactions/{tid}", headers=auth).status_code == 200
    assert client.get("/api/transactions/", headers=auth).json() == []


def test_validation(client, auth):
    assert client.post("/api/transactions/", headers=auth, json=tx(type="Banana")).status_code == 422
    assert client.post("/api/transactions/", headers=auth, json=tx(amount=-5)).status_code == 422
    assert client.post("/api/transactions/", headers=auth, json=tx(method="Barter")).status_code == 422


def test_users_cannot_see_each_others_data(client, auth):
    tid = client.post("/api/transactions/", headers=auth, json=tx()).json()["id"]
    other = make_user(client, "other@example.com", "Other Shop")
    assert client.get("/api/transactions/", headers=other).json() == []
    assert client.delete(f"/api/transactions/{tid}", headers=other).status_code == 404
