from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Session, select

from src.models import (
    Patient,
    PatientOutput,
    User,
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
    def get_assignments(cls, id_patient, session):
        return cls.get_patient(id_patient, session=session).assignments

    @classmethod
    def get_ci_barona(cls, id_patient, session):
        patient = cls.get_patient(id_patient, session=session)
        if patient:
            if patient.has_ci_barona:
                return patient.ci_barona
            else:
                # Check we have all fields needed
                if not patient.gender:
                    return "Not gender"
                if not patient.education_level:
                    return "Not education level"
                if not patient.region:
                    return "Not region"
                if not patient.zone:
                    return "Not zone"
                if not patient.birth_date:
                    return "Not birth date"

                age = datetime.now().year - patient.birth_date.year
                # Range of age
                age_level = _get_age_group(age)

                if age <= 65:
                    ci = (
                        75.927
                        + (15.519 * patient.education_level)
                        + (4.260 * age_level)
                        - (2.050 * patient.region)
                        - (3.3793 * patient.gender)
                        - (1.838 * patient.zone)
                    )
                else:
                    ci = (
                        63.488
                        + (13.015 * patient.education_level)
                        + (28.568 * age_level)
                        - (1.647 * age)
                        - (6.642 * patient.gender)
                    )
                patient.has_ci_barona = True
                patient.ci_barona = ci
                session.add(patient)
        return None


def _get_age_group(age):
    if age < 19:
        return 1
    elif 19 <= age <= 24:
        return 2
    elif 25 <= age <= 34:
        return 3
    elif 35 <= age <= 54:
        return 4
    elif 55 <= age <= 69:
        return 5
    else:
        return 6
