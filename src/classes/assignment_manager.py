from pydantic import EmailStr
from sqlmodel import Session, SQLModel

from src.models import Assignment, Questionnaire, Patient, Doctor


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
