from enum import Enum
from typing import Optional

import jwt
from pydantic import EmailStr
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

from passlib.hash import pbkdf2_sha256


class Token(SQLModel):
    access_token: str


class Role(str, Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"


class StatusQuestionnaire(str, Enum):
    active = "active"
    inactive = "inactive"
    draft = "draft"
    published = "published"
    archived = "archived"


class UserAnswerQuestionnaireLink(SQLModel, table=True):
    __tablename__ = "user_answer_questionnaire_link"
    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", primary_key=True
    )
    questionnaire_id: Optional[int] = Field(
        default=None, foreign_key="questionnaire.id", primary_key=True
    )


class UserBase(SQLModel):
    email: EmailStr = Field(
        index=True, nullable=False, sa_column_kwargs={"unique": True}
    )
    name: str = Field(default=None)
    last_name: str = Field(default=None)
    disabled: bool = False
    role: Role = Field(default=Role.patient, index=True)


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    questionnaires_created: list["Questionnaire"] = Relationship(
        back_populates="doctor"
    )
    questionnaires_answered: list["Questionnaire"] = Relationship(
        back_populates="patients", link_model=UserAnswerQuestionnaireLink
    )
    token: Optional[str] = Field(default=None)

    @staticmethod
    def hash_password(password: str):
        return pbkdf2_sha256.hash(password)

    def verify_password(self, password: str):
        return pbkdf2_sha256.verify(password, self.hashed_password)

    def create_activation_token(self):
        """
        Create a new activation token to send on email
        """
        self.token = jwt.encode({"email": self.email}, "secret", algorithm="HS256")


class UserInput(UserBase):
    password: str


class UserOutput(UserBase):
    created_at: datetime
    updated_at: datetime


class QueryFilterSchema(SQLModel):
    field: str = Field(description="Field name", nullable=False)
    value: bool | str = Field(description="Value", nullable=False)


class ListParams(SQLModel):
    sort: str = Field(
        description="Sort by field String with a list of sort fields separated by `|`."
        "Prepend a `+` or `-` symbol to indicate the sorting method. "
        "Example:  `+address|-name|-year`",
        default=None,
    )
    page: int = Field(default=0, description="Page number to retrieve. First page is 0")
    per_page: int = Field(description="Number of items per page. Default is not limit")
    filters: list[QueryFilterSchema] = Field(
        description="List of boolean filters to apply to the query", default=None
    )


class QuestionnaireModuleLink(SQLModel, table=True):
    questionnaire_id: Optional[int] = Field(
        default=None, foreign_key="questionnaire.id", primary_key=True
    )
    module_id: Optional[int] = Field(
        default=None, foreign_key="module.id", primary_key=True
    )


class Questionnaire(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    title: str = Field(default=None)
    description: str = Field(default=None)
    status: StatusQuestionnaire = Field(default=StatusQuestionnaire.draft)
    # Relation with a User model
    created_by: int = Field(foreign_key=User.id)
    doctor: User = Relationship(back_populates="questionnaires_created")
    patients: list["User"] = Relationship(
        back_populates="questionnaires_answered", link_model=UserAnswerQuestionnaireLink
    )
    modules: list["Module"] = Relationship(
        back_populates="questionnaires", link_model=QuestionnaireModuleLink
    )


class Module(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    description: str = Field(default=None)
    questionnaires: list["Questionnaire"] = Relationship(
        back_populates="modules", link_model=QuestionnaireModuleLink
    )
    questions: list["Question"] = Relationship(back_populates="module")
    diagnostics: list["Diagnostic"] = Relationship(back_populates="module")


class Question(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    question_text: str = Field(default=None)
    description: str = Field(default=None)
    module_id: int = Field(foreign_key="module.id")
    module: "Module" = Relationship(back_populates="questions")


class Diagnostic(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    questions_ids: list[int] = Field(default=None)
    quantity: int = Field(default=None)
    value_question: list[str] = Field(default=None)
    diagnostic_result: str = Field(default=None)
    module_id: int = Field(foreign_key=Module.id)
    module: Module = Relationship(back_populates="diagnostics")


class ActivateUserData(SQLModel):
    token: str = Field(default=None)
    password: str = Field(default=None)
    name: str = Field(default=None)
    last_name: str = Field(default=None)
