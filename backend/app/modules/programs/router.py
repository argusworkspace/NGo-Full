from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.shared.responses import PaginatedResponse
from .schemas import CreateProgramRequest, UpdateProgramRequest, ProgramResponse
from . import service

router = APIRouter(prefix="/programs", tags=["Programs"])


@router.get("", response_model=PaginatedResponse[ProgramResponse])
async def list_programs(page: int = 1, size: int = 10, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.list_programs(page, size, db)


@router.get("/{program_id}", response_model=ProgramResponse)
async def get_program(program_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.get_program(program_id, db)


@router.post("", response_model=ProgramResponse, status_code=201)
async def create_program(data: CreateProgramRequest, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.create_program(data, db)


@router.patch("/{program_id}", response_model=ProgramResponse)
async def update_program(program_id: str, data: UpdateProgramRequest, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    return await service.update_program(program_id, data, db)


@router.delete("/{program_id}", status_code=204)
async def delete_program(program_id: str, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    await service.delete_program(program_id, db)
