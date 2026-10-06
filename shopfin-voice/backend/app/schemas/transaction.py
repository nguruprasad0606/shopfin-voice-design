import datetime as dt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import ALL_TYPES, PAYMENT_METHODS, STATUSES  # noqa: F401

TxType = Literal["Sale", "Customer Payment", "Other Income", "Expense", "Purchase", "Supplier Payment"]
PayMethod = Literal["Cash", "UPI", "Card", "Bank Transfer"]
TxStatus = Literal["Completed", "Pending"]


class TransactionCreate(BaseModel):
    type: TxType
    category: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=255)
    method: PayMethod = "Cash"
    amount: float = Field(gt=0, le=1_000_000_000)
    date: dt.date
    status: TxStatus = "Completed"
    notes: str | None = Field(default=None, max_length=500)


class TransactionUpdate(BaseModel):
    type: TxType | None = None
    category: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    method: PayMethod | None = None
    amount: float | None = Field(default=None, gt=0, le=1_000_000_000)
    date: dt.date | None = None
    status: TxStatus | None = None
    notes: str | None = Field(default=None, max_length=500)


class TransactionResponse(BaseModel):
    # The API speaks type/method/date; the database columns are
    # transaction_type/payment_method/transaction_date.
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    date: dt.date = Field(validation_alias="transaction_date")
    type: str = Field(validation_alias="transaction_type")
    category: str
    description: str
    method: str = Field(validation_alias="payment_method")
    amount: float
    status: str
    notes: str | None = None
