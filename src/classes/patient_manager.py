from pydantic import EmailStr
from sqlmodel import Session, select

from src.models import (
    Patient,
    PatientOutput,
    User,
    QuestionnaireStatus,
)


class PatientManager:
    @staticmethod
    def accept_consent(
        id: EmailStr,
        name: str,
        last_name: str,
        dni: str,
        consent: bool,
        session: Session,
    ) -> Patient:
        patient = session.exec(select(Patient).where(Patient.id_user == id)).first()
        if patient:
            if name != patient.user.name:
                patient.user.name = name
            if last_name != patient.user.last_name:
                patient.user.last_name = last_name
            patient.dni = dni
            patient.consent = consent
            session.add(patient)
            session.commit()
            session.refresh(patient)
            return patient

    @staticmethod
    def remove_consent(id: EmailStr, session: Session) -> Patient:
        patient = session.exec(select(Patient).where(Patient.id_user == id)).first()
        if patient:
            patient.consent = False
            session.add(patient)
            session.commit()
            session.refresh(patient)
            return patient

    @classmethod
    def get_patient(cls, id_patient, session: Session) -> Patient:
        return session.exec(
            select(Patient).where(
                Patient.id_user == id_patient and User.email == id_patient
            )
        ).first()

    @classmethod
    def get_patient_output(cls, id_patient, session: Session) -> PatientOutput:
        patient = cls.get_patient(id_patient, session=session)
        if patient:
            # Serialize as PatientOutput with the date from user inside the patient
            data = PatientOutput(**patient.__dict__)
            data.email = patient.user.email
            data.name = patient.user.name
            data.last_name = patient.user.last_name
            return data

    @classmethod
    def get_assignemts_questionnaire(
        cls, id_patient, session
    ) -> list[QuestionnaireStatus]:
        patient = session.exec(
            select(Patient).where(Patient.id_user == id_patient)
        ).first()
        if patient:
            return [
                QuestionnaireStatus(
                    questionnaire=assignment.questionnaire, status=assignment.status
                )
                for assignment in patient.assignments
            ]
        return []
