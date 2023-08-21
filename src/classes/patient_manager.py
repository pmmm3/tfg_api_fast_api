from pydantic import EmailStr
from sqlmodel import Session, select

from src.models import Patient


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
            if name != patient.name:
                patient.name = name
            if last_name != patient.last_name:
                patient.last_name = last_name
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
