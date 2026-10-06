from app.core.constants import today_ist


def _tx(client, auth, type_, category, amount, method="Cash"):
    r = client.post("/api/transactions/", headers=auth, json={
        "type": type_, "category": category, "method": method, "amount": amount,
        "date": today_ist().isoformat()})
    assert r.status_code == 201, r.text


def test_sales_dashboard_today_and_breakdowns(client, auth):
    _tx(client, auth, "Sale", "Sales", 3000, "UPI")
    _tx(client, auth, "Sale", "Sales", 1000, "Cash")
    _tx(client, auth, "Expense", "Rent", 500)
    d = client.get("/api/analytics/sales?days=7", headers=auth).json()
    assert d["today"] == 4000 and d["today_count"] == 2 and d["today_average"] == 2000
    assert len(d["daily"]) == 7 and d["daily"][-1]["amount"] == 4000
    assert {m["name"]: m["amount"] for m in d["by_method"]} == {"UPI": 3000, "Cash": 1000}


def test_expenses_dashboard_ignores_sales(client, auth):
    _tx(client, auth, "Sale", "Sales", 9000)
    _tx(client, auth, "Expense", "Inventory", 700)
    d = client.get("/api/analytics/expenses", headers=auth).json()
    assert d["today"] == 700 and d["by_category"][0]["name"] == "Inventory"


def test_cash_dashboard_uses_opening_cash(client, auth):
    assert client.put("/api/analytics/cash/opening", headers=auth, json={"amount": 5000}).status_code == 200
    _tx(client, auth, "Sale", "Sales", 3000, "UPI")
    _tx(client, auth, "Expense", "Rent", 1000, "Cash")
    d = client.get("/api/analytics/cash?days=7", headers=auth).json()
    assert d["available_cash"] == 7000
    assert d["cash_in_hand"] == 4000 and d["digital_balance"] == 3000
    assert d["flow"][-1]["balance"] == 7000
    assert client.get("/api/dashboard/", headers=auth).json()["available_cash"] == 7000


def test_negative_opening_cash_rejected(client, auth):
    assert client.put("/api/analytics/cash/opening", headers=auth, json={"amount": -1}).status_code == 422


def test_budget_overview_projection_and_unbudgeted(client, auth):
    client.post("/api/budgets/", headers=auth, json={"name": "Inventory", "limit": 10000})
    _tx(client, auth, "Expense", "Inventory", 2000)
    _tx(client, auth, "Expense", "Gifts", 300)
    d = client.get("/api/budgets/overview", headers=auth).json()
    assert d["total_limit"] == 10000 and d["total_spent"] == 2000 and d["remaining"] == 8000
    assert d["items"][0]["projected"] >= 2000
    assert d["unbudgeted"] == [{"category": "Gifts", "spent": 300}]
    assert d["counts"]["Healthy"] == 1


def test_dashboards_are_private_per_business(client, auth):
    from tests.conftest import make_user
    _tx(client, auth, "Sale", "Sales", 999)
    other = make_user(client, email="other@example.com", shop="Other")
    assert client.get("/api/analytics/sales", headers=other).json()["today"] == 0
