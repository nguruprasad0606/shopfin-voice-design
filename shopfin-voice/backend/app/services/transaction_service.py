from sqlalchemy.orm import Session
from app.models.transaction import Transaction

def list_transactions(db: Session, business_id: int):
    return db.query(Transaction).filter(Transaction.business_id == business_id).all()
