from typing import List

from sqlmodel import Session, select

from src.models import Doctor, Patient, Assignment


class DoctorManager:
    @staticmethod
    def list_patients(*, doctor: Doctor, session: Session) -> List[Patient]:
        """
        Get patients of a doctor

        Parameters
        ----------
        doctor : Doctor
            Doctor
        session : Session
            SQLAlchemy session

        Returns
        -------
        List[Patient]
            List of patients

        """
        # Search every patient that has the doctor as their doctor in an assignment

        assignments = session.exec(
            select(Assignment).where(Assignment.id_doctor == doctor.id_user)
        ).all()
        patients = []
        for assignment in assignments:
            patients.append(assignment.patient)
        return patients

    @staticmethod
    def get_doctor(id_doctor: str, session: Session) -> Doctor:
        """
        Get doctor by id

        Parameters
        ----------
        id_doctor : str
            Doctor id
        session : Session
            SQLAlchemy session

        Returns
        -------
        Doctor
            Doctor object if found, None otherwise

        """
        return session.exec(select(Doctor).where(Doctor.id_user == id_doctor)).first()
