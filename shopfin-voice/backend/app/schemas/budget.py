from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    limit: float = Field(gt=0)


class BudgetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    limit: float | None = Field(default=None, gt=0)


class BudgetResponse(BaseModel):
    id: int
    name: str
    spent: float
    limit: float
    percentage: float
    status: str
