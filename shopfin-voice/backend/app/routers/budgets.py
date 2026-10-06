from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_business
from app.database.database import get_db
from app.models.budget import BudgetCategory
from app.models.business import Business
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate
from app.services.analytics_service import budget_overview
from app.services.budget_service import list_budgets

router = APIRouter()


def _one(db: Session, business: Business, budget_id: int) -> dict:
    return next(b for b in list_budgets(db, business.id) if b["id"] == budget_id)


def _owned(db: Session, business: Business, budget_id: int) -> BudgetCategory:
    item = db.query(BudgetCategory).filter(
        BudgetCategory.id == budget_id, BudgetCategory.business_id == business.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Budget category not found")
    return item


@router.get("/", response_model=list[BudgetResponse])
def get_budgets(business: Business = Depends(get_current_business), db: Session = Depends(get_db)):
    return list_budgets(db, business.id)


@router.get("/overview")
def get_budget_overview(business: Business = Depends(get_current_business), db: Session = Depends(get_db)):
    return budget_overview(db, business.id)


@router.post("/", response_model=BudgetResponse, status_code=201)
def create_budget(
    data: BudgetCreate,
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    item = BudgetCategory(business_id=business.id, name=data.name.strip(), limit=data.limit)
    db.add(item)
    db.commit()
    db.refresh(item)
    return _one(db, business, item.id)


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    data: BudgetUpdate,
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    item = _owned(db, business, budget_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(item, key, value)
    db.commit()
    return _one(db, business, budget_id)


@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    db.delete(_owned(db, business, budget_id))
    db.commit()
    return {"success": True}
