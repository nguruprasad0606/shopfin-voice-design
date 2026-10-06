from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import EXPENSE_TYPES, INCOME_TYPES, today_ist
from app.models.budget import BudgetCategory
from app.models.savings import SavingsGoal
from app.models.transaction import Transaction
from app.services.analytics_service import count, get_opening_cash, grouped
from app.services.budget_service import list_budgets


def _sum(db: Session, business_id: int, types, start=None, end=None) -> float:
    q = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.business_id == business_id,
        Transaction.transaction_type.in_(types),
    )
    if start:
        q = q.filter(Transaction.transaction_date >= start)
    if end:
        q = q.filter(Transaction.transaction_date <= end)
    return float(q.scalar() or 0)


def _change(today: float, before: float) -> float | None:
    if not before:
        return None
    return round((today - before) / before * 100, 1)


def dashboard_summary(db: Session, business_id: int) -> dict:
    today = today_ist()
    yesterday = today - timedelta(days=1)

    sales = _sum(db, business_id, INCOME_TYPES, today, today)
    expenses = _sum(db, business_id, EXPENSE_TYPES, today, today)
    sales_y = _sum(db, business_id, INCOME_TYPES, yesterday, yesterday)
    expenses_y = _sum(db, business_id, EXPENSE_TYPES, yesterday, yesterday)
    total_in = _sum(db, business_id, INCOME_TYPES)
    total_out = _sum(db, business_id, EXPENSE_TYPES)
    opening = get_opening_cash(db, business_id)
    sales_count = count(db, business_id, INCOME_TYPES, today, today)

    budgets = list_budgets(db, business_id)
    savings = db.query(func.coalesce(func.sum(SavingsGoal.current_amount), 0)).filter(
        SavingsGoal.business_id == business_id
    ).scalar()

    # Last 7 days, oldest first, for the chart.
    start = today - timedelta(days=6)
    rows = (
        db.query(Transaction.transaction_date, Transaction.transaction_type, Transaction.amount)
        .filter(Transaction.business_id == business_id, Transaction.transaction_date >= start)
        .all()
    )
    days = {start + timedelta(days=i): {"sales": 0.0, "exp": 0.0} for i in range(7)}
    for d, t, a in rows:
        if d in days:
            days[d]["sales" if t in INCOME_TYPES else "exp"] += float(a)
    weekly = [{"d": d.strftime("%a"), "date": d.isoformat(), **v} for d, v in days.items()]

    return {
        "today_sales": sales,
        "today_expenses": expenses,
        "sales_change": _change(sales, sales_y),
        "expenses_change": _change(expenses, expenses_y),
        "available_cash": opening + total_in - total_out,
        "opening_cash": opening,
        "cash_after_savings": opening + total_in - total_out - float(savings or 0),
        "today_sales_count": sales_count,
        "today_average_sale": round(sales / sales_count, 2) if sales_count else 0.0,
        "today_by_method": grouped(db, business_id, INCOME_TYPES, today, today, Transaction.payment_method),
        "estimated_surplus": sales - expenses,
        "total_sales": total_in,
        "total_expenses": total_out,
        "budget_total": sum(b["limit"] for b in budgets),
        "budget_used": sum(b["spent"] for b in budgets),
        "savings_total": float(savings or 0),
        "weekly": weekly,
    }
