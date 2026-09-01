import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.shared.exceptions import NotFoundException
from app.shared.responses import PaginatedResponse
from .models import Program
from .schemas import CreateProgramRequest, UpdateProgramRequest, ProgramResponse


async def list_programs(page: int, size: int, db: AsyncSession) -> PaginatedResponse[ProgramResponse]:
    total = (await db.execute(select(func.count()).select_from(Program))).scalar_one()
    result = await db.execute(select(Program).offset((page - 1) * size).limit(size))
    items = [ProgramResponse.model_validate(p) for p in result.scalars()]
    return PaginatedResponse(items=items, total=total, page=page, size=size, pages=math.ceil(total / size))


async def get_program(program_id: str, db: AsyncSession) -> ProgramResponse:
    program = (await db.execute(select(Program).where(Program.id == program_id))).scalar_one_or_none()
    if not program:
        raise NotFoundException("Program not found")
    return ProgramResponse.model_validate(program)


async def create_program(data: CreateProgramRequest, db: AsyncSession) -> ProgramResponse:
    program = Program(**data.model_dump())
    db.add(program)
    await db.flush()
    return ProgramResponse.model_validate(program)


async def update_program(program_id: str, data: UpdateProgramRequest, db: AsyncSession) -> ProgramResponse:
    program = (await db.execute(select(Program).where(Program.id == program_id))).scalar_one_or_none()
    if not program:
        raise NotFoundException("Program not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(program, field, value)
    await db.flush()
    return ProgramResponse.model_validate(program)


async def delete_program(program_id: str, db: AsyncSession) -> None:
    program = (await db.execute(select(Program).where(Program.id == program_id))).scalar_one_or_none()
    if not program:
        raise NotFoundException("Program not found")
    await db.delete(program)
