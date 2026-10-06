from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import EXPENSE_TYPES, today_ist
from app.models.budget import BudgetCategory
from app.models.transaction import Transaction


def month_start(d: date) -> date:
    return d.replace(day=1)


def spent_by_category(db: Session, business_id: int, today: date | None = None) -> dict[str, float]:
    """This month's expenses per category (lower-cased), straight from transactions."""
    today = today or today_ist()
    rows = (
        db.query(Transaction.category, func.sum(Transaction.amount))
        .filter(
            Transaction.business_id == business_id,
            Transaction.transaction_type.in_(EXPENSE_TYPES),
            Transaction.transaction_date >= month_start(today),
            Transaction.transaction_date <= today,
        )
        .group_by(Transaction.category)
        .all()
    )
    totals: dict[str, float] = {}
    for name, total in rows:
        key = name.strip().lower()
        totals[key] = totals.get(key, 0) + float(total)
    return totals


def budget_status(percentage: float) -> str:
    return "Exceeded" if percentage > 100 else "Warning" if percentage >= 80 else "Healthy"


def list_budgets(db: Session, business_id: int) -> list[dict]:
    spent = spent_by_category(db, business_id)
    items = (
        db.query(BudgetCategory)
        .filter(BudgetCategory.business_id == business_id)
        .order_by(BudgetCategory.id)
        .all()
    )
    return [serialize_budget(i, spent.get(i.name.strip().lower(), 0.0)) for i in items]


def serialize_budget(item: BudgetCategory, spent: float) -> dict:
    limit = float(item.limit)
    pct = round(spent / limit * 100, 2) if limit else 0
    return {
        "id": item.id,
        "name": item.name,
        "spent": spent,
        "limit": limit,
        "percentage": pct,
        "status": budget_status(pct),
    }


def budget_for_category(db: Session, business_id: int, category: str) -> dict | None:
    key = category.strip().lower()
    return next((b for b in list_budgets(db, business_id) if b["name"].strip().lower() == key), None)
