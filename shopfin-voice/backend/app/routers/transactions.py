from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_business
from app.database.database import get_db
from app.models.business import Business
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate

router = APIRouter()

_FIELD_TO_COLUMN = {"type": "transaction_type", "method": "payment_method", "date": "transaction_date"}


def _get_owned(db: Session, business: Business, transaction_id: int) -> Transaction:
    item = db.query(Transaction).filter(
        Transaction.id == transaction_id, Transaction.business_id == business.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return item


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    start: date | None = None,
    end: date | None = None,
    type: str | None = None,
    limit: int = Query(200, ge=1, le=1000),
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    q = db.query(Transaction).filter(Transaction.business_id == business.id)
    if start:
        q = q.filter(Transaction.transaction_date >= start)
    if end:
        q = q.filter(Transaction.transaction_date <= end)
    if type:
        q = q.filter(Transaction.transaction_type == type)
    return q.order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).limit(limit).all()


@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(
    data: TransactionCreate,
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    transaction = Transaction(
        business_id=business.id,
        transaction_type=data.type,
        category=data.category.strip(),
        description=data.description,
        payment_method=data.method,
        amount=data.amount,
        transaction_date=data.date,
        status=data.status,
        notes=data.notes,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    item = _get_owned(db, business, transaction_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        if value is None and key in ("type", "method", "date", "amount", "category", "status"):
            continue
        setattr(item, _FIELD_TO_COLUMN.get(key, key), value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    business: Business = Depends(get_current_business),
    db: Session = Depends(get_db),
):
    db.delete(_get_owned(db, business, transaction_id))
    db.commit()
    return {"success": True, "message": "Transaction deleted successfully"}
