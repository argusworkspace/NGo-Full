from pydantic import BaseModel, EmailStr
from typing import Optional, Literal


class CreateVolunteerRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None


class UpdateVolunteerRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[Literal["active", "inactive"]] = None


class VolunteerResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    status: str

    model_config = {"from_attributes": True}
