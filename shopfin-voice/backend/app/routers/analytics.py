from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_business
from app.database.database import get_db
from app.models.business import Business
from app.services import analytics_service as svc

router = APIRouter()


class OpeningCash(BaseModel):
    amount: float = Field(ge=0, le=1_000_000_000)


@router.get("/sales")
def sales(
    days: int = Query(30, ge=1, le=365),
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return svc.sales_dashboard(db, business.id, days)


@router.get("/expenses")
def expenses(
    days: int = Query(30, ge=1, le=365),
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return svc.expenses_dashboard(db, business.id, days)


@router.get("/cash")
def cash(
    days: int = Query(30, ge=1, le=365),
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return svc.cash_dashboard(db, business.id, days)


@router.put("/cash/opening")
def set_opening(
    data: OpeningCash,
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return {"opening_cash": svc.set_opening_cash(db, business.id, data.amount)}
