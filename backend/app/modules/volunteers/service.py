import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.shared.exceptions import NotFoundException, ConflictException
from app.shared.responses import PaginatedResponse
from .models import Volunteer
from .schemas import CreateVolunteerRequest, UpdateVolunteerRequest, VolunteerResponse


async def list_volunteers(page: int, size: int, db: AsyncSession) -> PaginatedResponse[VolunteerResponse]:
    total = (await db.execute(select(func.count()).select_from(Volunteer))).scalar_one()
    result = await db.execute(select(Volunteer).offset((page - 1) * size).limit(size))
    items = [VolunteerResponse.model_validate(v) for v in result.scalars()]
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=math.ceil(total / size))


async def get_volunteer(volunteer_id: str, db: AsyncSession) -> VolunteerResponse:
    v = (await db.execute(select(Volunteer).where(Volunteer.id == volunteer_id))).scalar_one_or_none()
    if not v:
        raise NotFoundException("Volunteer not found")
    return VolunteerResponse.model_validate(v)


async def create_volunteer(data: CreateVolunteerRequest, db: AsyncSession) -> VolunteerResponse:
    existing = (await db.execute(select(Volunteer).where(Volunteer.email == data.email))).scalar_one_or_none()
    if existing:
        raise ConflictException("Volunteer with this email already exists")
    v = Volunteer(**data.model_dump())
    db.add(v)
    await db.flush()
    return VolunteerResponse.model_validate(v)


async def update_volunteer(volunteer_id: str, data: UpdateVolunteerRequest, db: AsyncSession) -> VolunteerResponse:
    v = (await db.execute(select(Volunteer).where(Volunteer.id == volunteer_id))).scalar_one_or_none()
    if not v:
        raise NotFoundException("Volunteer not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(v, field, value)
    await db.flush()
    return VolunteerResponse.model_validate(v)


async def delete_volunteer(volunteer_id: str, db: AsyncSession) -> None:
    v = (await db.execute(select(Volunteer).where(Volunteer.id == volunteer_id))).scalar_one_or_none()
    if not v:
        raise NotFoundException("Volunteer not found")
    await db.delete(v)
