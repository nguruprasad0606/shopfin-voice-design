"""Numbers behind the Sales, Expenses, Cash Flow and Budget dashboards.

Everything is calculated from the transactions, budgets and savings already stored in
the database, so a dashboard is always in step with what was just recorded.
"""
import calendar
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import EXPENSE_TYPES, INCOME_TYPES, PAYMENT_METHODS, today_ist
from app.models.business import Business
from app.models.savings import SavingsGoal
from app.models.transaction import Transaction
from app.services.budget_service import list_budgets

MAX_DAYS = 365


# ---------- small helpers ----------

def _conds(business_id: int, types, start: date | None = None, end: date | None = None):
    conds = [Transaction.business_id == business_id, Transaction.transaction_type.in_(types)]
    if start:
        conds.append(Transaction.transaction_date >= start)
    if end:
        conds.append(Transaction.transaction_date <= end)
    return conds


def total(db: Session, business_id: int, types, start=None, end=None) -> float:
    q = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(*_conds(business_id, types, start, end))
    return float(q.scalar() or 0)


def count(db: Session, business_id: int, types, start=None, end=None) -> int:
    q = db.query(func.count(Transaction.id)).filter(*_conds(business_id, types, start, end))
    return int(q.scalar() or 0)


def pct_change(now: float, before: float) -> float | None:
    return round((now - before) / before * 100, 1) if before else None


def window(days: int) -> tuple[date, date, int]:
    days = max(1, min(int(days), MAX_DAYS))
    end = today_ist()
    return end - timedelta(days=days - 1), end, days


def _label(d: date, days: int) -> str:
    return d.strftime("%a") if days <= 7 else f"{d.day} {d.strftime('%b')}"


def daily_totals(db: Session, business_id: int, types, start: date, end: date) -> dict[date, float]:
    rows = (
        db.query(Transaction.transaction_date, func.sum(Transaction.amount))
        .filter(*_conds(business_id, types, start, end))
        .group_by(Transaction.transaction_date)
        .all()
    )
    return {d: float(t) for d, t in rows}


def grouped(db: Session, business_id: int, types, start: date, end: date, column) -> list[dict]:
    """Totals per category / payment method, biggest first, with each one's share."""
    rows = (
        db.query(column, func.sum(Transaction.amount))
        .filter(*_conds(business_id, types, start, end))
        .group_by(column)
        .all()
    )
    merged: dict[str, dict] = {}
    for name, amount in rows:
        key = (name or "Other").strip().lower()
        item = merged.setdefault(key, {"name": (name or "Other").strip(), "amount": 0.0})
        item["amount"] += float(amount)
    items = sorted(merged.values(), key=lambda i: i["amount"], reverse=True)
    grand = sum(i["amount"] for i in items)
    for i in items:
        i["share"] = round(i["amount"] / grand * 100, 1) if grand else 0.0
    return items


def recent(db: Session, business_id: int, types, limit: int = 8) -> list[dict]:
    rows = (
        db.query(Transaction)
        .filter(*_conds(business_id, types))
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        .limit(limit)
        .all()
    )
    return [
        {"id": t.id, "date": t.transaction_date, "type": t.transaction_type, "category": t.category,
         "description": t.description, "method": t.payment_method, "amount": float(t.amount)}
        for t in rows
    ]


def _series(start: date, end: date, values: dict[date, float], days: int) -> list[dict]:
    out, d = [], start
    while d <= end:
        out.append({"date": d.isoformat(), "label": _label(d, days), "amount": values.get(d, 0.0)})
        d += timedelta(days=1)
    return out


def _previous_month_to_date(today: date) -> tuple[date, date]:
    """Same stretch of last month (1st to today's day number) for a fair comparison."""
    prev_end = today.replace(day=1) - timedelta(days=1)
    prev_start = prev_end.replace(day=1)
    return prev_start, prev_start.replace(day=min(today.day, prev_end.day))


def _period_summary(db: Session, business_id: int, types, today: date) -> dict:
    yesterday = today - timedelta(days=1)
    week_start, prev_week_start = today - timedelta(days=6), today - timedelta(days=13)
    month_start = today.replace(day=1)
    prev_start, prev_end = _previous_month_to_date(today)

    t, y = total(db, business_id, types, today, today), total(db, business_id, types, yesterday, yesterday)
    w = total(db, business_id, types, week_start, today)
    pw = total(db, business_id, types, prev_week_start, week_start - timedelta(days=1))
    m, pm = total(db, business_id, types, month_start, today), total(db, business_id, types, prev_start, prev_end)
    return {
        "today": t, "yesterday": y, "today_change": pct_change(t, y),
        "week": w, "prev_week": pw, "week_change": pct_change(w, pw),
        "month": m, "prev_month": pm, "month_change": pct_change(m, pm),
    }


# ---------- dashboards ----------

def _flow_dashboard(db: Session, business_id: int, types, days: int) -> dict:
    start, end, days = window(days)
    daily = _series(start, end, daily_totals(db, business_id, types, start, end), days)
    range_total = sum(p["amount"] for p in daily)
    busiest = max(daily, key=lambda p: p["amount"]) if range_total else None
    n_today = count(db, business_id, types, end, end)
    today_total = total(db, business_id, types, end, end)
    return {
        "days": days, "start": start.isoformat(), "end": end.isoformat(),
        **_period_summary(db, business_id, types, end),
        "today_count": n_today,
        "today_average": round(today_total / n_today, 2) if n_today else 0.0,
        "range_total": range_total,
        "daily_average": round(range_total / days, 2),
        "best_day": busiest,
        "daily": daily,
        "by_method": grouped(db, business_id, types, start, end, Transaction.payment_method),
        "by_category": grouped(db, business_id, types, start, end, Transaction.category),
        "recent": recent(db, business_id, types),
    }


def sales_dashboard(db: Session, business_id: int, days: int = 30) -> dict:
    return _flow_dashboard(db, business_id, INCOME_TYPES, days)


def expenses_dashboard(db: Session, business_id: int, days: int = 30) -> dict:
    data = _flow_dashboard(db, business_id, EXPENSE_TYPES, days)
    budgets = list_budgets(db, business_id)
    limit = sum(b["limit"] for b in budgets)
    spent = sum(b["spent"] for b in budgets)
    data["budget_total"] = limit
    data["budget_used_percent"] = round(spent / limit * 100, 1) if limit else 0.0
    return data


def get_opening_cash(db: Session, business_id: int) -> float:
    biz = db.get(Business, business_id)
    return float(biz.opening_cash or 0) if biz else 0.0


def set_opening_cash(db: Session, business_id: int, amount: float) -> float:
    biz = db.get(Business, business_id)
    biz.opening_cash = amount
    db.commit()
    return float(biz.opening_cash)


def savings_total(db: Session, business_id: int) -> float:
    return float(
        db.query(func.coalesce(func.sum(SavingsGoal.current_amount), 0))
        .filter(SavingsGoal.business_id == business_id)
        .scalar() or 0
    )


def available_cash(db: Session, business_id: int) -> float:
    """Opening cash + everything that came in - everything that went out."""
    return get_opening_cash(db, business_id) + total(db, business_id, INCOME_TYPES) - total(db, business_id, EXPENSE_TYPES)


def cash_dashboard(db: Session, business_id: int, days: int = 30) -> dict:
    start, end, days = window(days)
    opening = get_opening_cash(db, business_id)
    total_in, total_out = total(db, business_id, INCOME_TYPES), total(db, business_id, EXPENSE_TYPES)
    available = opening + total_in - total_out
    saved = savings_total(db, business_id)

    # Balance per payment method. Opening cash is treated as notes-and-coins in the till.
    methods: dict[str, dict] = {m: {"name": m, "money_in": 0.0, "money_out": 0.0} for m in PAYMENT_METHODS}
    for types, field in ((INCOME_TYPES, "money_in"), (EXPENSE_TYPES, "money_out")):
        rows = (
            db.query(Transaction.payment_method, func.sum(Transaction.amount))
            .filter(*_conds(business_id, types))
            .group_by(Transaction.payment_method)
            .all()
        )
        for name, amount in rows:
            methods.setdefault(name, {"name": name, "money_in": 0.0, "money_out": 0.0})[field] += float(amount)
    by_method = []
    for m in methods.values():
        m["balance"] = m["money_in"] - m["money_out"] + (opening if m["name"] == "Cash" else 0.0)
        by_method.append(m)
    cash_in_hand = next((m["balance"] for m in by_method if m["name"] == "Cash"), 0.0)

    # Day-by-day money in / out and the running balance.
    ins = daily_totals(db, business_id, INCOME_TYPES, start, end)
    outs = daily_totals(db, business_id, EXPENSE_TYPES, start, end)
    before = start - timedelta(days=1)
    running = opening + total(db, business_id, INCOME_TYPES, end=before) - total(db, business_id, EXPENSE_TYPES, end=before)
    flow, d = [], start
    while d <= end:
        money_in, money_out = ins.get(d, 0.0), outs.get(d, 0.0)
        running += money_in - money_out
        flow.append({"date": d.isoformat(), "label": _label(d, days), "money_in": money_in,
                     "money_out": money_out, "net": money_in - money_out, "balance": running})
        d += timedelta(days=1)

    month_start = end.replace(day=1)
    month_in, month_out = total(db, business_id, INCOME_TYPES, month_start, end), total(db, business_id, EXPENSE_TYPES, month_start, end)
    avg_out = total(db, business_id, EXPENSE_TYPES, end - timedelta(days=29), end) / 30
    return {
        "days": days, "start": start.isoformat(), "end": end.isoformat(),
        "opening_cash": opening, "total_in": total_in, "total_out": total_out,
        "available_cash": available, "savings_total": saved, "cash_after_savings": available - saved,
        "cash_in_hand": cash_in_hand, "digital_balance": available - cash_in_hand,
        "month_in": month_in, "month_out": month_out, "month_net": month_in - month_out,
        "avg_daily_spend": round(avg_out, 2),
        "runway_days": int(available // avg_out) if avg_out > 0 and available > 0 else None,
        "by_method": by_method, "flow": flow,
    }


def budget_overview(db: Session, business_id: int) -> dict:
    """Budget usage for the month so far, plus where spending is heading by month end."""
    today = today_ist()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    elapsed = today.day
    days_left = days_in_month - elapsed

    items = []
    for b in list_budgets(db, business_id):
        projected = b["spent"] / elapsed * days_in_month
        items.append({
            **b,
            "remaining": b["limit"] - b["spent"],
            "projected": round(projected, 2),
            "projected_percentage": round(projected / b["limit"] * 100, 1) if b["limit"] else 0.0,
        })
    limit = sum(i["limit"] for i in items)
    spent = sum(i["spent"] for i in items)
    remaining = limit - spent
    projected = spent / elapsed * days_in_month

    budgeted = {i["name"].strip().lower() for i in items}
    unbudgeted = [
        {"category": c["name"], "spent": c["amount"]}
        for c in grouped(db, business_id, EXPENSE_TYPES, today.replace(day=1), today, Transaction.category)
        if c["name"].strip().lower() not in budgeted
    ]
    return {
        "month": today.strftime("%B %Y"),
        "day_of_month": elapsed, "days_in_month": days_in_month, "days_left": days_left,
        "total_limit": limit, "total_spent": spent, "remaining": remaining,
        "percentage": round(spent / limit * 100, 1) if limit else 0.0,
        "daily_burn": round(spent / elapsed, 2),
        "projected_spend": round(projected, 2),
        "projected_percentage": round(projected / limit * 100, 1) if limit else 0.0,
        "safe_daily_spend": round(remaining / max(days_left, 1), 2) if remaining > 0 else 0.0,
        "counts": {s: sum(1 for i in items if i["status"] == s) for s in ("Healthy", "Warning", "Exceeded")},
        "items": items,
        "unbudgeted": unbudgeted,
    }
