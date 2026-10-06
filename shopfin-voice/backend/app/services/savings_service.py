from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_SAVINGS_GOAL, today_ist
from app.models.savings import SavingsDeposit, SavingsGoal


def serialize_goal(item: SavingsGoal) -> dict:
    target = float(item.target_amount)
    current = float(item.current_amount)
    return {
        "id": item.id,
        "name": item.name,
        "target_amount": target,
        "current_amount": current,
        "target_date": item.target_date,
        "monthly_contribution": float(item.monthly_contribution),
        "progress": round(min(current / target * 100, 100), 2) if target else 0,
    }


def list_goals(db: Session, business_id: int) -> list[SavingsGoal]:
    return (
        db.query(SavingsGoal)
        .filter(SavingsGoal.business_id == business_id)
        .order_by(SavingsGoal.id)
        .all()
    )


def find_goal_by_name(db: Session, business_id: int, name: str) -> SavingsGoal | None:
    key = name.strip().lower()
    return next((g for g in list_goals(db, business_id) if g.name.strip().lower() == key), None)


def get_or_create_default_goal(db: Session, business_id: int) -> SavingsGoal:
    goal = find_goal_by_name(db, business_id, DEFAULT_SAVINGS_GOAL)
    if goal:
        return goal
    # No target yet: use a placeholder the owner can edit on the Savings page.
    goal = SavingsGoal(
        business_id=business_id,
        name=DEFAULT_SAVINGS_GOAL,
        target_amount=100000,
        current_amount=0,
        monthly_contribution=0,
    )
    db.add(goal)
    db.flush()
    return goal


def add_deposit(
    db: Session,
    goal: SavingsGoal,
    amount: float,
    when: date | None = None,
    note: str = "",
) -> SavingsDeposit:
    """Record the deposit AND bump the goal balance in one transaction."""
    deposit = SavingsDeposit(
        business_id=goal.business_id,
        goal_id=goal.id,
        amount=amount,
        deposit_date=when or today_ist(),
        note=note[:255],
    )
    goal.current_amount = Decimal(goal.current_amount or 0) + Decimal(str(amount))
    db.add(deposit)
    db.flush()
    return deposit
