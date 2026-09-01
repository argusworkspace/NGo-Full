from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.shared.responses import PaginatedResponse
from .schemas import CreateVolunteerRequest, UpdateVolunteerRequest, VolunteerResponse
from . import service

router = APIRouter(prefix="/volunteers", tags=["Volunteers"])


@router.get("", response_model=PaginatedResponse[VolunteerResponse])
async def list_volunteers(page: int = 1, size: int = 10, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.list_volunteers(page, size, db)


@router.get("/{volunteer_id}", response_model=VolunteerResponse)
async def get_volunteer(volunteer_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.get_volunteer(volunteer_id, db)


@router.post("", response_model=VolunteerResponse, status_code=201)
async def create_volunteer(data: CreateVolunteerRequest, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.create_volunteer(data, db)


@router.patch("/{volunteer_id}", response_model=VolunteerResponse)
async def update_volunteer(volunteer_id: str, data: UpdateVolunteerRequest, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.update_volunteer(volunteer_id, data, db)


@router.delete("/{volunteer_id}", status_code=204)
async def delete_volunteer(volunteer_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    await service.delete_volunteer(volunteer_id, db)
