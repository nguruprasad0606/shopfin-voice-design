from pydantic import BaseModel, EmailStr

class UserProfile(BaseModel):
    id: int
    name: str
    email: EmailStr
    business_name: str
    business_type: str
    currency: str

    model_config = {"from_attributes": True}
