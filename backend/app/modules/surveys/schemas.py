import datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from pydantic.alias_generators import to_camel

CamelModel = ConfigDict(alias_generator=to_camel, populate_by_name=True)

QuestionType = Literal[
    "text", "number", "date", "single_choice", "multiple_choice", "boolean", "textarea", "rating"
]

CHOICE_TYPES = {"single_choice", "multiple_choice"}


class Option(BaseModel):
    id: str
    label: str


class Question(BaseModel):
    id: str
    question: str
    type: QuestionType
    required: bool = False
    options: list[Option] | None = None

    @model_validator(mode="after")
    def validate_options(self):
        if self.type in CHOICE_TYPES:
            if not self.options:
                raise ValueError(f"question '{self.id}' of type '{self.type}' requires options")
        elif self.options:
            raise ValueError(f"question '{self.id}' of type '{self.type}' must not define options")
        return self


class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    questions: list[Question] = []

    @field_validator("questions")
    @classmethod
    def unique_question_ids(cls, questions: list[Question]) -> list[Question]:
        ids = [q.id for q in questions]
        if len(ids) != len(set(ids)):
            raise ValueError("question ids must be unique within a project")
        return questions


class CreateProjectRequest(ProjectBase):
    pass


class UpdateProjectRequest(ProjectBase):
    pass


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    questions: list[Question]
    status: Literal["DRAFT", "PUBLISHED", "ARCHIVED"]
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    response_count: int = 0

    model_config = {**CamelModel, "from_attributes": True}


class Answer(BaseModel):
    question_id: str
    answer: Any

    model_config = CamelModel


class SubmitResponseRequest(BaseModel):
    answers: list[Answer]


class ResponseOut(BaseModel):
    id: str
    project_id: str
    user_id: str
    answers: list[Answer]
    submitted_at: datetime.datetime
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {**CamelModel, "from_attributes": True}


class QuestionStat(BaseModel):
    question_id: str
    question: str
    type: QuestionType
    response_count: int

    # number / rating
    average: float | None = None
    min: float | None = None
    max: float | None = None

    # boolean
    true_count: int | None = None
    false_count: int | None = None

    # single_choice / multiple_choice — option id -> count
    option_counts: dict[str, int] | None = None

    # text / textarea
    summary: str | None = None
    summary_source: Literal["ai", "heuristic"] | None = None
    sample_answers: list[str] | None = None

    model_config = CamelModel


class DashboardResponse(BaseModel):
    project_id: str
    project_name: str
    description: str | None
    status: Literal["DRAFT", "PUBLISHED", "ARCHIVED"]
    total_responses: int
    questions: list[QuestionStat]
    generated_at: datetime.datetime

    model_config = CamelModel
