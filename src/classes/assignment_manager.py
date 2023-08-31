from pydantic import EmailStr
from sqlmodel import Session, SQLModel

from src.models import (
    Assignment,
    Questionnaire,
    Patient,
    Doctor,
    Answer,
    Module,
    OptionAnswer,
)


class AssignmentInput(SQLModel):
    questionnaire_id: int
    patient_id: EmailStr
    doctor_id: EmailStr


class AssignmentManager:
    @classmethod
    def create_assignment(
        cls,
        questionnaire: Questionnaire,
        patient: Patient,
        doctor: Doctor,
        session: Session,
    ) -> Assignment:
        assignment = Assignment(
            questionnaire=questionnaire, patient=patient, doctor=doctor
        )
        session.add(assignment)
        session.commit()
        session.refresh(assignment)
        return assignment

    @classmethod
    def get_status(cls, assignment: Assignment) -> str:
        return assignment.status

    @classmethod
    def get_assignment(cls, id_assignment: int, session: Session) -> Assignment:
        return session.get(Assignment, id_assignment)

    @classmethod
    def update_status(
        cls, assignment: Assignment, status: str, session: Session
    ) -> Assignment:
        assignment.status = status
        session.add(assignment)
        session.commit()
        session.refresh(assignment)
        return assignment

    @classmethod
    def save_answers(
        cls,
        assignment: Assignment,
        answers: Answer,
        module: Module,
        option: OptionAnswer,
        open_text: str,
        session: Session,
    ):
        pass
        # TODO: save answers
        # if option:
        #     answer = AnswerManager(assignment=assignment, module=module, option=option)
        # else:
        #     answer = AnswerManager(
        #         assignment=assignment, module=module, open_text=open_text
        #     )
