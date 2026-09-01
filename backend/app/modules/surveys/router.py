from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_admin
from app.modules.auth.models import User
from .schemas import (
    CreateProjectRequest,
    UpdateProjectRequest,
    ProjectResponse,
    SubmitResponseRequest,
    ResponseOut,
)
from . import service

project_router = APIRouter(prefix="/projects", tags=["Projects"])
response_router = APIRouter(prefix="/responses", tags=["Responses"])


@project_router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: CreateProjectRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await service.create_project(data, admin, db)


@project_router.get("", response_model=list[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.list_projects(user, db)


@project_router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    return await service.get_project(project_id, user, db)


@project_router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: UpdateProjectRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await service.update_project(project_id, data, db)


@project_router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)
):
    await service.delete_project(project_id, db)


@project_router.patch("/{project_id}/publish", response_model=ProjectResponse)
async def publish_project(
    project_id: str, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)
):
    return await service.publish_project(project_id, db)


@project_router.patch("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    project_id: str, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)
):
    return await service.archive_project(project_id, db)


@project_router.post("/{project_id}/responses", response_model=ResponseOut, status_code=201)
async def submit_response(
    project_id: str,
    data: SubmitResponseRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await service.submit_response(project_id, data, user, db)


@project_router.get("/{project_id}/responses", response_model=list[ResponseOut])
async def list_responses(
    project_id: str, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)
):
    return await service.list_responses(project_id, db)


@response_router.get("/{response_id}", response_model=ResponseOut)
async def get_response(
    response_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    return await service.get_response(response_id, user, db)
