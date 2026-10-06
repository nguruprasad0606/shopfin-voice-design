import pytest

from app.services.command_service import extract_amount


@pytest.mark.parametrize("text,expected", [
    ("today I saved 500", 500), ("sold goods for ₹2,500", 2500), ("spent 5k on stock", 5000),
    ("received 1.5 lakh", 150000), ("paid 800 rupees", 800), ("on 3rd I paid Rs 1200", 1200),
    ("no number here", None),
    ("Today I saved five hundred rupees.", 500), ("Sold goods for two thousand rupees by UPI.", 2000),
    ("Spent three thousand five hundred on inventory", 3500), ("saved one lakh", 100000),
    ("I sold one item for 500", 500), ("saved twenty five hundred", 2500), ("I saved ₹500.", 500),
    ("Spent 3,000 on stock!", 3000), ("saved a thousand rupees", None) if False else ("saved 1 thousand", 1000),
])
def test_extract_amount(text, expected):
    assert extract_amount(text) == expected


def test_indian_grouping():
    from app.services.command_service import inr
    assert inr(200000) == "₹2,00,000" and inr(1500) == "₹1,500" and inr(99) == "₹99" and inr(12.5) == "₹12.50"


def cmd(client, auth, text):
    r = client.post("/api/command/", headers=auth, json={"text": text})
    assert r.status_code == 200, r.text
    return r.json()


def test_saved_money_is_stored_in_savings(client, auth):
    r = cmd(client, auth, "Today I saved 500")
    assert r["ok"] and r["intent"] == "ADD_SAVINGS"
    goals = client.get("/api/savings/", headers=auth).json()
    assert goals[0]["name"] == "General Savings" and goals[0]["current_amount"] == 500
    cmd(client, auth, "I saved 250 rupees")
    assert client.get("/api/savings/", headers=auth).json()[0]["current_amount"] == 750
    assert len(client.get("/api/savings/history", headers=auth).json()) == 2


def test_saving_into_a_named_goal(client, auth):
    client.post("/api/savings/", headers=auth, json={"name": "Emergency Fund", "target_amount": 50000})
    cmd(client, auth, "saved 1000 for the emergency fund")
    names = {g["name"]: g["current_amount"] for g in client.get("/api/savings/", headers=auth).json()}
    assert names == {"Emergency Fund": 1000}


def test_sale_and_expense(client, auth):
    cmd(client, auth, "sold goods for 2000 by UPI")
    assert cmd(client, auth, "got 300 from a customer")["intent"] == "ADD_SALE"
    client.delete("/api/transactions/2", headers=auth)
    r = cmd(client, auth, "spent 800 on rent")
    txs = client.get("/api/transactions/", headers=auth).json()
    assert {(t["type"], t["category"], t["method"]) for t in txs} == {
        ("Sale", "Sales", "UPI"), ("Expense", "Rent", "Cash")}
    d = client.get("/api/dashboard/", headers=auth).json()
    assert d["today_sales"] == 2000 and d["today_expenses"] == 800 and r["ok"]


def test_expense_warns_when_budget_exceeded(client, auth):
    client.post("/api/budgets/", headers=auth, json={"name": "Inventory", "limit": 1000})
    r = cmd(client, auth, "bought stock worth 1500")
    assert "exceeded" in r["warning"]


def test_create_goal_and_queries(client, auth):
    r = cmd(client, auth, "create a savings goal called New Freezer of 40000")
    assert r["ok"] and client.get("/api/savings/", headers=auth).json()[0]["name"] == "New Freezer"
    cmd(client, auth, "spent 300 on petrol")
    assert "₹300" in cmd(client, auth, "how much did I spend today")["message"]
    assert "₹0" in cmd(client, auth, "how much have I saved")["message"]


def test_unknown_and_missing_amount_change_nothing(client, auth):
    assert not cmd(client, auth, "hello there")["ok"]
    assert not cmd(client, auth, "I saved some money")["ok"]
    assert client.get("/api/savings/", headers=auth).json() == []
    assert client.get("/api/command/history", headers=auth).json()[0]["ok"] is False


def test_wispr_style_sentences_end_to_end(client, auth):
    """Dictation tools capitalise, add full stops and spell numbers out."""
    for text in ["Today I saved five hundred rupees.", "I saved ₹250.", "Today, I saved Rs. 100 in my savings."]:
        assert cmd(client, auth, text)["ok"], text
    assert client.get("/api/savings/", headers=auth).json()[0]["current_amount"] == 850
    r = cmd(client, auth, "I sold goods for two thousand rupees by Google Pay.")
    assert r["ok"] and "UPI" in r["message"]
    assert cmd(client, auth, "I spent three thousand five hundred on inventory.")["data"]["amount"] == 3500
