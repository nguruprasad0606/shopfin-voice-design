from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_business
from app.database.database import get_db
from app.models.business import Business
from app.services.dashboard_service import dashboard_summary

router = APIRouter()

@router.get("/")
def get_dashboard(
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return dashboard_summary(db, business.id)
