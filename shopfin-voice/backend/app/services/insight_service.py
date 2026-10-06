from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import EXPENSE_TYPES, today_ist
from app.models.transaction import Transaction
from app.services.budget_service import list_budgets
from app.services.savings_service import list_goals


def category_totals(db: Session, business_id: int) -> list[dict]:
    rows = (
        db.query(Transaction.category, func.sum(Transaction.amount))
        .filter(Transaction.business_id == business_id, Transaction.transaction_type.in_(EXPENSE_TYPES))
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )
    return [{"category": name, "amount": float(total)} for name, total in rows]


def _month_expense(db: Session, business_id: int, category: str, start, end) -> float:
    return float(
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.business_id == business_id,
            Transaction.transaction_type.in_(EXPENSE_TYPES),
            func.lower(Transaction.category) == category.lower(),
            Transaction.transaction_date >= start,
            Transaction.transaction_date <= end,
        )
        .scalar()
        or 0
    )


def generate_insights(db: Session, business_id: int) -> list[dict]:
    """Plain-language observations computed from the shop's own numbers."""
    out: list[dict] = []
    today = today_ist()
    inr = lambda n: "₹{:,.0f}".format(n)  # noqa: E731

    budgets = list_budgets(db, business_id)
    for b in budgets:
        if b["status"] == "Exceeded":
            out.append({"id": f"over-{b['id']}", "tone": "warn",
                        "text": f"{b['name']} is over budget: {inr(b['spent'])} spent of {inr(b['limit'])}."})
        elif b["status"] == "Warning":
            out.append({"id": f"near-{b['id']}", "tone": "warn",
                        "text": f"{b['name']} has used {b['percentage']:.0f}% of its monthly budget."})
    if budgets:
        left = sum(b["limit"] for b in budgets) - sum(b["spent"] for b in budgets)
        if left > 0:
            out.append({"id": "budget-left", "tone": "good",
                        "text": f"You have {inr(left)} remaining in this month's planned budget."})

    # Month-over-month change for the biggest expense category this month.
    this_start = today.replace(day=1)
    prev_end = this_start - timedelta(days=1)
    prev_start = prev_end.replace(day=1)
    cats = [c for c in category_totals(db, business_id)]
    for c in cats[:1]:
        now = _month_expense(db, business_id, c["category"], this_start, today)
        before = _month_expense(db, business_id, c["category"], prev_start, prev_end)
        if before > 0 and now > 0:
            change = (now - before) / before * 100
            if abs(change) >= 5:
                word = "higher" if change > 0 else "lower"
                out.append({"id": "mom", "tone": "warn" if change > 0 else "good",
                            "text": f"{c['category']} spending is {abs(change):.0f}% {word} than last month."})

    goals = list_goals(db, business_id)
    if goals:
        g = max(goals, key=lambda x: float(x.current_amount) / float(x.target_amount or 1))
        pct = float(g.current_amount) / float(g.target_amount or 1) * 100
        out.append({"id": f"goal-{g.id}", "tone": "info",
                    "text": f"Your {g.name} is {min(pct, 100):.0f}% complete."})
    else:
        out.append({"id": "no-goal", "tone": "info",
                    "text": 'Start saving: type "today I saved 500" in the command bar.'})
    return out[:5]
