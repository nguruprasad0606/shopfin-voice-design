from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.constants import today_ist
from app.core.dependencies import get_current_business
from app.database.database import get_db
from app.models.business import Business
from app.models.savings import SavingsDeposit, SavingsGoal
from app.schemas.savings import (
    DepositCreate, DepositResponse, SavingsCreate, SavingsResponse, SavingsUpdate,
)
from app.services.savings_service import add_deposit, list_goals, serialize_goal

router = APIRouter()


def _owned(db: Session, business: Business, goal_id: int) -> SavingsGoal:
    item = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id, SavingsGoal.business_id == business.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    return item


@router.get("/", response_model=list[SavingsResponse])
def get_savings(business: Business = Depends(get_current_business), db: Session = Depends(get_db)):
    return [serialize_goal(g) for g in list_goals(db, business.id)]


@router.get("/history", response_model=list[DepositResponse])
def savings_history(business: Business = Depends(get_current_business), db: Session = Depends(get_db)):
    rows = (
        db.query(SavingsDeposit, SavingsGoal.name)
        .join(SavingsGoal, SavingsGoal.id == SavingsDeposit.goal_id)
        .filter(SavingsDeposit.business_id == business.id)
        .order_by(SavingsDeposit.deposit_date.desc(), SavingsDeposit.id.desc())
        .limit(50)
        .all()
    )
    return [
        DepositResponse(id=d.id, goal_id=d.goal_id, goal_name=name, amount=float(d.amount),
                        date=d.deposit_date, note=d.note)
        for d, name in rows
    ]


@router.post("/", response_model=SavingsResponse, status_code=201)
def create_savings(
    data: SavingsCreate,
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    item = SavingsGoal(
        business_id=business.id,
        name=data.name.strip(),
        target_amount=data.target_amount,
        current_amount=data.current_amount,
        target_date=data.target_date,
        monthly_contribution=data.monthly_contribution,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize_goal(item)


@router.post("/{goal_id}/deposit", response_model=SavingsResponse)
def deposit(
    goal_id: int,
    data: DepositCreate,
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    goal = _owned(db, business, goal_id)
    add_deposit(db, goal, data.amount, data.date or today_ist(), data.note)
    db.commit()
    db.refresh(goal)
    return serialize_goal(goal)


@router.put("/{goal_id}", response_model=SavingsResponse)
def update_savings(
    goal_id: int,
    data: SavingsUpdate,
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    item = _owned(db, business, goal_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        if value is None and key != "target_date":
            continue
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return serialize_goal(item)


@router.delete("/{goal_id}")
def delete_savings(
    goal_id: int,
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    db.delete(_owned(db, business, goal_id))
    db.commit()
    return {"success": True}
