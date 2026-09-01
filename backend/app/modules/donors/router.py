from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.shared.responses import PaginatedResponse
from .schemas import CreateDonorRequest, UpdateDonorRequest, DonorResponse
from . import service

router = APIRouter(prefix="/donors", tags=["Donors"])


@router.get("", response_model=PaginatedResponse[DonorResponse])
async def list_donors(page: int = 1, size: int = 10, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.list_donors(page, size, db)


@router.get("/{donor_id}", response_model=DonorResponse)
async def get_donor(donor_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.get_donor(donor_id, db)


@router.post("", response_model=DonorResponse, status_code=201)
async def create_donor(data: CreateDonorRequest, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.create_donor(data, db)


@router.patch("/{donor_id}", response_model=DonorResponse)
async def update_donor(donor_id: str, data: UpdateDonorRequest, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.update_donor(donor_id, data, db)


@router.delete("/{donor_id}", status_code=204)
async def delete_donor(donor_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    await service.delete_donor(donor_id, db)
