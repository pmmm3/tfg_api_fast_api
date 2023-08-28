from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session

from src.classes.patient_manager import PatientManager
from src.models import (
    PatientOutput,
    Doctor,
)
from src.utils.authorization import (
    get_current_doctor,
)
from src.utils.reuse import get_session

router = APIRouter(prefix="/doctor", tags=["doctor"])


@router.get("/{id_doctor}/patients", response_model=list[PatientOutput])
async def get_patients(
    id_doctor: str,
    current_doctor: Doctor = Depends(get_current_doctor),
    session: Session = Depends(get_session),
):
    """
    Get all patients of a doctor
    """
    if current_doctor.id_user != id_doctor:
        raise HTTPException(status_code=401, detail="Unauthorized")
    patients = list(
        dict.fromkeys(
            [assignment.patient.id_user for assignment in current_doctor.assignments]
        )
    )
    return [
        PatientManager.get_patient_output(id_patient, session=session)
        for id_patient in patients
    ]
