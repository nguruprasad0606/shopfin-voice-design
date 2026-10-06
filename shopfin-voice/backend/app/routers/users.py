from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.business import BusinessUpdate, BusinessResponse

router = APIRouter()

@router.get("/business", response_model=BusinessResponse)
def get_business(current_user: User = Depends(get_current_user)):
    return current_user.business

@router.put("/business", response_model=BusinessResponse)
def update_business(
    data: BusinessUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    business = current_user.business
    business.name = data.name
    business.owner_name = data.owner_name
    business.business_type = data.business_type
    business.currency = data.currency
    current_user.name = data.owner_name
    db.commit()
    db.refresh(business)
    return business
