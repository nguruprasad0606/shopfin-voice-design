def test_goal_and_manual_deposit(client, auth):
    g = client.post("/api/savings/", headers=auth, json={"name": "Bike", "target_amount": 1000}).json()
    r = client.post(f"/api/savings/{g['id']}/deposit", headers=auth, json={"amount": 250})
    assert r.json()["current_amount"] == 250 and r.json()["progress"] == 25
    assert client.get("/api/savings/history", headers=auth).json()[0]["amount"] == 250
