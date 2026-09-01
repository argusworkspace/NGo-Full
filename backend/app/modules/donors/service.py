import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.shared.exceptions import NotFoundException, ConflictException
from app.shared.responses import PaginatedResponse
from .models import Donor
from .schemas import CreateDonorRequest, UpdateDonorRequest, DonorResponse


async def list_donors(page: int, size: int, db: AsyncSession) -> PaginatedResponse[DonorResponse]:
    total = (await db.execute(select(func.count()).select_from(Donor))).scalar_one()
    result = await db.execute(select(Donor).offset((page - 1) * size).limit(size))
    items = [DonorResponse.model_validate(d) for d in result.scalars()]
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=math.ceil(total / size))


async def get_donor(donor_id: str, db: AsyncSession) -> DonorResponse:
    donor = (await db.execute(select(Donor).where(Donor.id == donor_id))).scalar_one_or_none()
    if not donor:
        raise NotFoundException("Donor not found")
    return DonorResponse.model_validate(donor)


async def create_donor(data: CreateDonorRequest, db: AsyncSession) -> DonorResponse:
    existing = (await db.execute(select(Donor).where(Donor.email == data.email))).scalar_one_or_none()
    if existing:
        raise ConflictException("Donor with this email already exists")
    donor = Donor(**data.model_dump())
    db.add(donor)
    await db.flush()
    return DonorResponse.model_validate(donor)


async def update_donor(donor_id: str, data: UpdateDonorRequest, db: AsyncSession) -> DonorResponse:
    donor = (await db.execute(select(Donor).where(Donor.id == donor_id))).scalar_one_or_none()
    if not donor:
        raise NotFoundException("Donor not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(donor, field, value)
    await db.flush()
    return DonorResponse.model_validate(donor)


async def delete_donor(donor_id: str, db: AsyncSession) -> None:
    donor = (await db.execute(select(Donor).where(Donor.id == donor_id))).scalar_one_or_none()
    if not donor:
        raise NotFoundException("Donor not found")
    await db.delete(donor)
