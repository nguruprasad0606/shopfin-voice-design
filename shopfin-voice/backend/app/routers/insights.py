from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_business
from app.database.database import get_db
from app.models.business import Business
from app.services.insight_service import generate_insights

router = APIRouter()


@router.get("/")
def get_insights(
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    return generate_insights(db, business.id)
