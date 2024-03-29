from enum import Enum

import jwt
from typing import Optional, List
from pydantic import EmailStr, conint
from sqlalchemy import ForeignKeyConstraint
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

from passlib.hash import pbkdf2_sha256

from src.settings import Settings


class Token(SQLModel):
    access_token: str


class StatusQuestionnaire(str, Enum):
    active = "active"
    inactive = "inactive"
    draft = "draft"
    published = "published"
    archived = "archived"
    finished = "finished"


class StatusUser(str, Enum):
    disabled = "disabled"
    pending_activate = "pending_activate"
    active = "active"


class UserBase(SQLModel):
    email: Optional[EmailStr] = Field(default=None)
    name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    status: StatusUser = Field(default=StatusUser.disabled)


class UserRoles(str, Enum):
    patient = "Paciente"
    doctor = "Doctor"
    admin = "Administrador"
    user = "Usuario"


class UserBaseWithRole(UserBase):
    rol: Optional[UserRoles] = Field(default=UserRoles.user)


class DocOrAdminInput(SQLModel):
    email: EmailStr = Field(description="User email", nullable=False)
    name: Optional[str] = Field(description="User name", nullable=True)
    last_name: Optional[str] = Field(description="User last name", nullable=True)
    password: str = Field(description="User password", nullable=False)


class UserInput(SQLModel):
    token: str = Field(description="Token to activate user account", nullable=False)
    password: str = Field(description="User password", nullable=False)
    name: Optional[str] = Field(description="User name", nullable=True)
    last_name: Optional[str] = Field(description="User last name", nullable=True)


class User(UserBase, table=True):
    email: Optional[EmailStr] = Field(default=None, primary_key=True)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    token: Optional[str] = Field(default=None)

    doctors: Optional[List["Doctor"]] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    patients: Optional[List["Patient"]] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    admins: Optional[List["Admin"]] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    @staticmethod
    def hash_password(password: str):
        return pbkdf2_sha256.hash(password)

    def verify_password(self, password: str):
        return pbkdf2_sha256.verify(password, self.hashed_password)

    def create_activation_token(self):
        """
        Create a new activation token to send on email
        """
        self.token = jwt.encode(
            {"email": self.email}, Settings().token_secret, algorithm="HS256"
        )


class Doctor(SQLModel, table=True):
    id_user: Optional[EmailStr] = Field(
        default=None, primary_key=True, foreign_key="user.email"
    )
    user: User = Relationship(
        back_populates="doctors",
        sa_relationship_kwargs={"cascade": "all"},
    )
    assignments: Optional[List["Assignment"]] = Relationship(back_populates="doctor")


class Admin(SQLModel, table=True):
    id_user: Optional[EmailStr] = Field(
        default=None, primary_key=True, foreign_key="user.email"
    )
    user: User = Relationship(
        sa_relationship_kwargs={"cascade": "all"},
        back_populates="admins",
    )


class Patient(SQLModel, table=True):
    id_user: Optional[EmailStr] = Field(
        default=None, primary_key=True, foreign_key="user.email"
    )
    consent: Optional[bool] = Field(default=False)
    telephone_number: Optional[conint(ge=100000000, le=999999999999)] = Field(
        default=None
    )
    gender: Optional[int] = Field(default=None)
    civil_status: Optional[str] = Field(default=None)
    employment_status: Optional[str] = Field(default=None)
    education_level: Optional[int] = Field(default=None)
    region: Optional[int] = Field(default=None)
    zone: Optional[int] = Field(default=None)
    native_language: Optional[str] = Field(default=None)
    nationality: Optional[str] = Field(default=None)
    birth_date: Optional[datetime] = Field(default=None)
    dni: Optional[str] = Field(default=None)

    ci_barona: Optional[float] = Field(default=None)
    has_ci_barona: Optional[bool] = Field(default=False)

    # If the consent is false, the patient can't be assigned to a questionnaire
    # If the consent is true, the patient can be assigned to a questionnaire and need to have DNI

    user: User = Relationship(
        sa_relationship_kwargs={"cascade": "all"},
        back_populates="patients",
    )
    assignments: Optional[List["Assignment"]] = Relationship(back_populates="patient")


class PatientOutput(Patient):
    email: EmailStr = Field(description="User email", nullable=False)
    name: Optional[str] = Field(description="User name", nullable=True)
    last_name: Optional[str] = Field(description="User last name", nullable=True)


class ConsentField(SQLModel):
    name: str
    dni: str
    last_name: str


class QuestionnaireModuleLink(SQLModel, table=True):
    __tablename__ = "questionnaire_module_link"
    id_questionnaire: Optional[int] = Field(
        default=None, foreign_key="questionnaire.id", primary_key=True
    )
    id_module: Optional[int] = Field(
        default=None, foreign_key="module.id", primary_key=True
    )


class Questionnaire(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[EmailStr] = Field(default=None, foreign_key="user.email")

    modules: List["Module"] = Relationship(
        back_populates="questionnaires", link_model=QuestionnaireModuleLink
    )
    assignments: Optional[List["Assignment"]] = Relationship(
        back_populates="questionnaire"
    )


class ModuleOutputLink(SQLModel, table=True):
    __tablename__ = "module_output_link"
    id: Optional[int] = Field(default=None, primary_key=True)
    id_module: Optional[int] = Field(default=None, foreign_key="module.id")
    id_output: Optional[int] = Field(default=None, foreign_key="output.id")


class QuestionOutputLink(SQLModel, table=True):
    __tablename__ = "question_output_link"
    __table_args__ = (
        ForeignKeyConstraint(
            ["id_question_question_id", "id_question_module_id"],
            ["question.id", "question.id_module"],
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    id_question_question_id: Optional[int] = Field(default=None)
    id_question_module_id: Optional[int] = Field(default=None)
    id_output: Optional[int] = Field(default=None, foreign_key="output.id")


class Module(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)

    questionnaires: List[Questionnaire] = Relationship(
        back_populates="modules", link_model=QuestionnaireModuleLink
    )

    questions: List["Question"] = Relationship(
        back_populates="module",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    outputs: Optional[List["Output"]] = Relationship(
        back_populates="modules", link_model=ModuleOutputLink
    )


class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_module: Optional[int] = Field(
        default=None, foreign_key="module.id", primary_key=True
    )
    content: str = Field(default=None)

    parent_question_id_question: Optional[int] = Field(default=None, nullable=True)
    parent_question_id_module: Optional[int] = Field(default=None, nullable=True)

    module: Module = Relationship(back_populates="questions")
    options: List["OptionAnswer"] = Relationship(back_populates="question")
    answers: Optional[List["Answer"]] = Relationship(back_populates="question")
    outputs: Optional[List["Output"]] = Relationship(
        back_populates="questions", link_model=QuestionOutputLink
    )


class Assignment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    id_doctor: Optional[EmailStr] = Field(default=None, foreign_key="doctor.id_user")
    id_patient: Optional[EmailStr] = Field(default=None, foreign_key="patient.id_user")
    id_questionnaire: Optional[int] = Field(
        default=None, foreign_key="questionnaire.id"
    )
    date: datetime = Field(default_factory=datetime.utcnow)
    status: Optional[StatusQuestionnaire] = Field(default=None)

    doctor: Doctor = Relationship(back_populates="assignments")
    patient: Patient = Relationship(back_populates="assignments")
    questionnaire: Questionnaire = Relationship(back_populates="assignments")
    answers: Optional[List["Answer"]] = Relationship(back_populates="assignment")


class QueryFilterSchema(SQLModel):
    field: str = Field(description="Field name", nullable=False)
    value: bool | str = Field(description="Value", nullable=False)


class OptionAnswer(SQLModel, table=True):
    __tablename__ = "option_answer"
    __table_args__ = (
        ForeignKeyConstraint(
            ["id_question_question_id", "id_question_module_id"],
            ["question.id", "question.id_module"],
        ),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    id_question_question_id: Optional[int] = Field(default=None)
    id_question_module_id: Optional[int] = Field(default=None)
    content: str = Field(default=None)
    score: Optional[int] = Field(default=None)

    question: Question = Relationship(back_populates="options")
    answers: Optional[List["Answer"]] = Relationship(back_populates="option")


class Answer(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(
            ["id_question_question_id", "id_question_module_id"],
            ["question.id", "question.id_module"],
        ),
    )
    id_assignment: Optional[int] = Field(
        default=None, foreign_key="assignment.id", primary_key=True
    )
    id_question_question_id: Optional[int] = Field(default=None, primary_key=True)
    id_question_module_id: Optional[int] = Field(default=None, primary_key=True)
    id_option: Optional[int] = Field(default=None, foreign_key="option_answer.id")
    open_answer: Optional[str] = Field(default=None)
    date: datetime = Field(default_factory=datetime.utcnow)

    assignment: Assignment = Relationship(back_populates="answers")
    question: Question = Relationship(back_populates="answers")
    option: OptionAnswer = Relationship(back_populates="answers")


class TypeCondition(str, Enum):
    GREATER = "GREATER"
    LESS = "LESS"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS_EQUAL = "LESS_EQUAL"
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"


class Output(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str = Field(default=None)
    condition_type: TypeCondition = Field(default=None)
    condition_value: int = Field(default=None)

    modules: Optional[List[Module]] = Relationship(
        back_populates="outputs", link_model=ModuleOutputLink
    )
    questions: Optional[List[Question]] = Relationship(
        back_populates="outputs", link_model=QuestionOutputLink
    )


class ListParams(SQLModel):
    sort: str = Field(
        description="Sort by field String with a list of sort fields separated by `|`."
        "Prepend a `+` or `-` symbol to indicate the sorting method. "
        "Example:  `+address|-name|-year`",
        default=None,
    )
    page: int = Field(default=0, description="Page number to retrieve. First page is 0")
    per_page: int = Field(
        default=0, description="Number of items per page. Default is not limit"
    )
    filters: list[QueryFilterSchema] = Field(
        description="List of boolean filters to apply to the query", default=None
    )


class QuestionnaireStatus(SQLModel):
    questionnaire: Questionnaire
    status: StatusQuestionnaire = Field(default=None)


class BaronaInput(SQLModel):
    gender: int
    age: datetime
    education_level: int
    region: int
    zone: int
