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
