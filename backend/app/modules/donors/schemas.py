from pydantic import BaseModel, EmailStr
from typing import Optional


class CreateDonorRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None


class UpdateDonorRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class DonorResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    total_donated: float

    model_config = {"from_attributes": True}
