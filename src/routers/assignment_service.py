from fastapi import APIRouter, Depends

from src.classes.assignment_manager import AssignmentInput, AssignmentManager
from src.classes.doctor_manager import DoctorManager
from src.classes.patient_manager import PatientManager
from src.classes.questionnaire_manager import QuestionnaireManager
from src.classes.user_manager import UserManager
from src.models import User
from src.utils.authorization import (
    is_doctor_or_admin,
    get_current_user,
)
from src.utils.reuse import get_session

router = APIRouter(prefix="/assignment", tags=["Assignment"])


@router.post("/")
async def create_assignment(
    data: AssignmentInput,
    *,
    _=Depends(is_doctor_or_admin),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session)
):
    """
    Create an assignment

    Parameters
    ----------
    data
        AssignmentInput object with id_patient, id_module, id_doctor, date fields

    Returns
    -------
    Assignment
        Assignment object
    """
    patient = PatientManager.get_patient(data.patient_id, session=session)
    if not patient:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Patient not found")
    is_admin = UserManager.is_admin(current_user, session=session)
    if not is_admin:
        if current_user.email != data.doctor_id:
            from fastapi import HTTPException

            raise HTTPException(status_code=401, detail="Unauthorized")
    doctor = DoctorManager.get_doctor(data.doctor_id, session=session)

    questionnaire = QuestionnaireManager.get_questionnaire(
        data.questionnaire_id, session=session
    )

    return AssignmentManager.create_assignment(
        patient=patient, doctor=doctor, questionnaire=questionnaire, session=session
    )


@router.get("/{id_assignment}")
async def get_assignment(
    id_assignment: int,
    session=Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get an assignment by id
    """
    #     Check user is admin
    have_access = UserManager.is_admin(current_user, session=session)
    if not have_access:
        # Check is related to the assignment
        assignment = AssignmentManager.get_assignment(id_assignment, session=session)
        if (
            current_user.email != assignment.doctor.id_user
            and current_user.email != assignment.patient.id_user
        ):
            from fastapi import HTTPException

            raise HTTPException(status_code=401, detail="Unauthorized")
    return AssignmentManager.get_assignment(id_assignment, session=session)
