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
