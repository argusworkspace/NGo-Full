from pydantic import BaseModel
from typing import Optional, Literal
import datetime


class CreateProgramRequest(BaseModel):
    title: str
    description: str
    start_date: datetime.date
    end_date: Optional[datetime.date] = None
    budget: float


class UpdateProgramRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Literal["active", "completed", "draft"]] = None
    end_date: Optional[datetime.date] = None
    budget: Optional[float] = None


class ProgramResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    start_date: datetime.date
    end_date: Optional[datetime.date]
    budget: float

    model_config = {"from_attributes": True}
