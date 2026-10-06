from pydantic import BaseModel, Field

class BusinessUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    owner_name: str = Field(min_length=2, max_length=100)
    business_type: str = Field(min_length=2, max_length=100)
    currency: str = "INR"

class BusinessResponse(BusinessUpdate):
    id: int

    model_config = {"from_attributes": True}
