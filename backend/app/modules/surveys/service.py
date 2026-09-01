import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.modules.auth.models import User
from app.shared.exceptions import NotFoundException, ForbiddenException, BadRequestException, ValidationException
from .models import Project, Response
from .schemas import (
    CreateProjectRequest,
    UpdateProjectRequest,
    ProjectResponse,
    SubmitResponseRequest,
    Answer,
    ResponseOut,
)


async def _get_project_or_404(project_id: str, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundException("Project not found")
    return project


async def _count_responses(project_id: str, db: AsyncSession) -> int:
    result = await db.execute(
        select(func.count(Response.id)).where(Response.project_id == project_id)
    )
    return result.scalar_one()


def _to_project_response(project: Project, response_count: int) -> ProjectResponse:
    data = ProjectResponse.model_validate(project)
    data.response_count = response_count
    return data


async def create_project(data: CreateProjectRequest, admin: User, db: AsyncSession) -> ProjectResponse:
    project = Project(
        name=data.name,
        description=data.description,
        questions=[q.model_dump() for q in data.questions],
        created_by=admin.id,
    )
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return _to_project_response(project, 0)


async def list_projects(user: User, db: AsyncSession) -> list[ProjectResponse]:
    query = select(Project, func.count(Response.id)).outerjoin(
        Response, Response.project_id == Project.id
    )
    if user.role != "ADMIN":
        query = query.where(Project.status == "PUBLISHED")
    query = query.group_by(Project.id).order_by(Project.created_at.desc())
    result = await db.execute(query)
    return [_to_project_response(project, count) for project, count in result.all()]


async def get_project(project_id: str, user: User, db: AsyncSession) -> ProjectResponse:
    project = await _get_project_or_404(project_id, db)
    if user.role != "ADMIN" and project.status != "PUBLISHED":
        raise NotFoundException("Project not found")
    count = await _count_responses(project_id, db)
    return _to_project_response(project, count)


async def update_project(project_id: str, data: UpdateProjectRequest, db: AsyncSession) -> ProjectResponse:
    project = await _get_project_or_404(project_id, db)
    project.name = data.name
    project.description = data.description
    project.questions = [q.model_dump() for q in data.questions]
    await db.flush()
    await db.refresh(project)
    count = await _count_responses(project_id, db)
    return _to_project_response(project, count)


async def delete_project(project_id: str, db: AsyncSession) -> None:
    project = await _get_project_or_404(project_id, db)
    await db.delete(project)
    await db.flush()


async def publish_project(project_id: str, db: AsyncSession) -> ProjectResponse:
    project = await _get_project_or_404(project_id, db)
    if not project.questions:
        raise BadRequestException("Cannot publish a project with no questions", error_code="EMPTY_FORM")
    project.status = "PUBLISHED"
    await db.flush()
    await db.refresh(project)
    count = await _count_responses(project_id, db)
    return _to_project_response(project, count)


async def archive_project(project_id: str, db: AsyncSession) -> ProjectResponse:
    project = await _get_project_or_404(project_id, db)
    project.status = "ARCHIVED"
    await db.flush()
    await db.refresh(project)
    count = await _count_responses(project_id, db)
    return _to_project_response(project, count)


def _validate_answer_type(question: dict, answer) -> None:
    qtype = question["type"]
    qid = question["id"]
    option_ids = {opt["id"] for opt in question.get("options") or []}

    if qtype in ("text", "textarea"):
        if not isinstance(answer, str):
            raise ValidationException(f"question '{qid}' expects a text answer")
    elif qtype == "number":
        if isinstance(answer, bool) or not isinstance(answer, (int, float)):
            raise ValidationException(f"question '{qid}' expects a numeric answer")
    elif qtype == "boolean":
        if not isinstance(answer, bool):
            raise ValidationException(f"question '{qid}' expects a boolean answer")
    elif qtype == "rating":
        if isinstance(answer, bool) or not isinstance(answer, int) or not (1 <= answer <= 5):
            raise ValidationException(f"question '{qid}' expects a rating from 1 to 5")
    elif qtype == "date":
        if not isinstance(answer, str):
            raise ValidationException(f"question '{qid}' expects a date string")
        try:
            datetime.date.fromisoformat(answer)
        except ValueError:
            raise ValidationException(f"question '{qid}' expects an ISO-8601 date string")
    elif qtype == "single_choice":
        if not isinstance(answer, str) or answer not in option_ids:
            raise ValidationException(f"question '{qid}' answer must be one of the defined option ids")
    elif qtype == "multiple_choice":
        if not isinstance(answer, list) or not answer or not all(isinstance(a, str) for a in answer):
            raise ValidationException(f"question '{qid}' expects a non-empty list of option ids")
        if not set(answer).issubset(option_ids):
            raise ValidationException(f"question '{qid}' answer contains an option id that does not exist")


async def submit_response(
    project_id: str, data: SubmitResponseRequest, user: User, db: AsyncSession
) -> ResponseOut:
    project = await _get_project_or_404(project_id, db)
    if project.status != "PUBLISHED":
        raise BadRequestException(
            "Project is not open for submissions", error_code="PROJECT_NOT_PUBLISHED"
        )

    questions_by_id = {q["id"]: q for q in project.questions}
    submitted_ids = set()

    for item in data.answers:
        if item.question_id not in questions_by_id:
            raise BadRequestException(
                f"Unknown question id '{item.question_id}'", error_code="UNKNOWN_QUESTION"
            )
        submitted_ids.add(item.question_id)
        _validate_answer_type(questions_by_id[item.question_id], item.answer)

    required_ids = {q["id"] for q in project.questions if q.get("required")}
    missing = required_ids - submitted_ids
    if missing:
        raise BadRequestException(
            f"Missing required questions: {', '.join(sorted(missing))}",
            error_code="MISSING_REQUIRED_ANSWER",
        )

    response = Response(
        project_id=project.id,
        user_id=user.id,
        answers=[a.model_dump() for a in data.answers],
    )
    db.add(response)
    await db.flush()
    await db.refresh(response)
    return ResponseOut.model_validate(response)


async def list_responses(project_id: str, db: AsyncSession) -> list[ResponseOut]:
    await _get_project_or_404(project_id, db)
    result = await db.execute(
        select(Response).where(Response.project_id == project_id).order_by(Response.submitted_at.desc())
    )
    return [ResponseOut.model_validate(r) for r in result.scalars().all()]


async def get_response(response_id: str, user: User, db: AsyncSession) -> ResponseOut:
    result = await db.execute(select(Response).where(Response.id == response_id))
    response = result.scalar_one_or_none()
    if not response:
        raise NotFoundException("Response not found")
    if user.role != "ADMIN" and response.user_id != user.id:
        raise ForbiddenException("You may only view your own responses")
    return ResponseOut.model_validate(response)
