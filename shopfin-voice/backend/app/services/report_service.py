from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import EXPENSE_TYPES, INCOME_TYPES, today_ist
from app.models.savings import SavingsGoal
from app.models.transaction import Transaction
from app.services.budget_service import list_budgets


def build_report(db: Session, business_id: int, period: str) -> dict:
    today = today_ist()
    if period == "daily":
        start = today
    elif period == "weekly":
        start = today - timedelta(days=6)
    else:
        start = today.replace(day=1)

    def total(types):
        return float(
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.business_id == business_id,
                Transaction.transaction_type.in_(types),
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= today,
            )
            .scalar()
            or 0
        )

    top = (
        db.query(Transaction.category)
        .filter(
            Transaction.business_id == business_id,
            Transaction.transaction_type.in_(EXPENSE_TYPES),
            Transaction.transaction_date >= start,
            Transaction.transaction_date <= today,
        )
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
        .first()
    )
    budgets = list_budgets(db, business_id)
    limit = sum(b["limit"] for b in budgets)
    spent = sum(b["spent"] for b in budgets)
    savings = db.query(func.coalesce(func.sum(SavingsGoal.current_amount), 0)).filter(
        SavingsGoal.business_id == business_id
    ).scalar()
    sales, expenses = total(INCOME_TYPES), total(EXPENSE_TYPES)
    return {
        "period": period,
        "start": start.isoformat(),
        "end": today.isoformat(),
        "total_sales": sales,
        "total_expenses": expenses,
        "estimated_surplus": sales - expenses,
        "top_expense_category": top[0] if top else None,
        "budget_used": round(spent / limit * 100, 2) if limit else 0,
        "savings_total": float(savings or 0),
    }
