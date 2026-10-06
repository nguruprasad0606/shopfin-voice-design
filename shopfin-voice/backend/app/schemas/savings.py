import datetime as dt
from pydantic import BaseModel, Field


class SavingsCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    target_date: dt.date | None = None
    monthly_contribution: float = Field(default=0, ge=0)


class SavingsUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    target_amount: float | None = Field(default=None, gt=0)
    current_amount: float | None = Field(default=None, ge=0)
    target_date: dt.date | None = None
    monthly_contribution: float | None = Field(default=None, ge=0)


class SavingsResponse(BaseModel):
    id: int
    name: str
    target_amount: float
    current_amount: float
    target_date: dt.date | None
    monthly_contribution: float
    progress: float


class DepositCreate(BaseModel):
    amount: float = Field(gt=0, le=1_000_000_000)
    date: dt.date | None = None
    note: str = Field(default="", max_length=255)


class DepositResponse(BaseModel):
    id: int
    goal_id: int
    goal_name: str
    amount: float
    date: dt.date
    note: str
