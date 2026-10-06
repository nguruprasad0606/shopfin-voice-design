from datetime import date


def test_spent_is_computed_from_transactions(client, auth):
    client.post("/api/budgets/", headers=auth, json={"name": "Inventory", "limit": 10000})
    client.post("/api/transactions/", headers=auth, json={
        "type": "Expense", "category": "inventory", "method": "UPI", "amount": 8500,
        "date": date.today().isoformat()})
    b = client.get("/api/budgets/", headers=auth).json()[0]
    assert b["spent"] == 8500 and b["status"] == "Warning"
    client.post("/api/transactions/", headers=auth, json={
        "type": "Expense", "category": "Inventory", "method": "UPI", "amount": 2000,
        "date": date.today().isoformat()})
    assert client.get("/api/budgets/", headers=auth).json()[0]["status"] == "Exceeded"
