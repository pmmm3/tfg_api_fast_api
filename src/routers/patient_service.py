from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import Session

from src.classes.patient_manager import PatientManager
from src.classes.user_manager import UserManager
from src.models import (
    Patient,
    Token,
    ConsentField,
    User,
    PatientOutput,
    QuestionnaireStatus,
)
from src.utils.authorization import (
    get_current_patient,
    get_current_user,
)
from src.utils.reuse import get_session

router = APIRouter(prefix="/patient", tags=["patient"])


@router.get("/{id_patient}", response_model=PatientOutput)
async def get_patient(
    id_patient: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get a patient by id

    Parameters
    ----------
    id_patient
        Patient id

    Returns
    -------
    Patient
        Patient object if patient was found

    """
    #     Check user is admin or patient
    if current_user.email != id_patient:
        is_user_admin = UserManager.is_admin(current_user, session=session)
        if not is_user_admin:
            raise HTTPException(status_code=401, detail="Unauthorized")
    return PatientManager.get_patient_output(id_patient, session=session)


@router.post("/activate")
async def activate(token: Token, *, session: Session = Depends(get_session)):
    """
    Activate a user account with a token sent to email address when user was created

    Parameters
    ----------
    token
        Token object with token field

    Returns
    -------
    User
        User object if user was activated successfully

    """
    user = UserManager.activate_user_to_patient(token.access_token, session=session)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Invalid token")


# Todo: Broken for no reason
# @router.get("/is-consent-accepted")
# async def get_accepted(*, current_patient: Patient = Depends(get_current_patient)):
#     """
#     Check if a patient has accepted consent
#
#     Returns
#     -------
#     bool
#         True if patient has accepted consent
#
#     """
#     return current_patient.consent
#


@router.post("/{id_patient}/accept-consent")
async def accept_consent(
    *,
    id_patient,
    consentField: Annotated[ConsentField, Body()],
    get_current_patient: Patient = Depends(get_current_patient),
    session: Session = Depends(get_session)
):
    """
    Accept consent of a patient

    Parameters
    ----------
    consentField
        ConsentField object with patient_id field

    Returns
    -------
    User
        User object if user was activated successfully

    """
    if get_current_patient.id_user != id_patient:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = PatientManager.accept_consent(
        id=id_patient,
        consent=True,
        dni=consentField.dni,
        name=consentField.name,
        last_name=consentField.last_name,
        session=session,
    )
    if user:
        return user
    raise HTTPException(status_code=400, detail="Invalid token")


# TODO: Questionnaire with assignment status
@router.get("/{id_patient}/questionnaires", response_model=list[QuestionnaireStatus])
async def get_questionnaires(
    *,
    id_patient,
    get_current_patient: Patient = Depends(get_current_patient),
    session: Session = Depends(get_session)
):
    """
    Get questionnaires of a patient

    Parameters
    ----------
    id_patient
        Patient id

    Returns
    -------
    list[Questionnaire]

    """
    #     Check user is admin or patient
    if get_current_patient.id_user != id_patient:
        is_user_admin_or_doctor = UserManager.is_admin(
            get_current_patient.user, session=session
        ) or UserManager.is_doctor(get_current_patient.user, session=session)
        if not is_user_admin_or_doctor:
            raise HTTPException(status_code=401, detail="Unauthorized")
    return PatientManager.get_assignemts_questionnaire(id_patient, session=session)
