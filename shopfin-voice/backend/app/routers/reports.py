from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_business
from app.database.database import get_db
from app.models.business import Business
from app.services.report_service import build_report

router = APIRouter()

@router.get("/{period}")
def get_report(
    period: str,
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    if period not in {"daily", "weekly", "monthly"}:
        raise HTTPException(status_code=400, detail="Period must be daily, weekly, or monthly")
    return build_report(db, business.id, period)
