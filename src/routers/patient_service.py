from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import EmailStr
from sqlmodel import Session

from src.classes.patient_manager import PatientManager
from src.classes.user_manager import UserManager
from src.models import (
    Patient,
    Token,
    ConsentField,
    User,
    PatientOutput,
    Assignment,
    BaronaInput,
)
from src.utils.authorization import (
    get_current_patient,
    get_current_user,
)
from src.utils.reuse import get_session

router = APIRouter(prefix="/patient", tags=["patient"])


@router.get("/consent")
async def get_accepted(current_patient: Patient = Depends(get_current_patient)):
    """
    Check if a patient has accepted consent

    Returns
    -------
    bool
        True if patient has accepted consent

    """
    return current_patient.consent if current_patient.consent else False


@router.get("/{id_patient}/has-ci-barona")
async def has_ci_barona(
    id_patient: EmailStr,
    current_patient: Patient = Depends(get_current_patient),
    session: Session = Depends(get_session),
):
    """
    Check if a patient has accepted consent

    Returns
    -------
    bool
        True if patient has accepted consent


    """
    if current_patient.id_user != id_patient:
        is_user_doc = UserManager.is_doctor(current_patient.user, session=session)
        if not is_user_doc:
            raise HTTPException(status_code=401, detail="Unauthorized")
    patient = PatientManager.get_patient(id_patient, session=session)
    return patient.has_ci_barona if patient.has_ci_barona else False


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


@router.post("/{id_patient}/barona")
async def calculate_barona(
    id_patient,
    data: BaronaInput,
    current_patient=Depends(get_current_patient),
    session: Session = Depends(get_session),
):
    """
    Calculate barona score of a patient

    Parameters
    ----------
    id_patient
        Patient id

    data
        BaronaInput object with gender, age, education_level, region and zone fields

    """
    #     Check user is admin or patient
    if current_patient.id_user != id_patient:
        raise HTTPException(status_code=401, detail="Unauthorized")

    patient = PatientManager.get_patient(id_patient, session=session)
    patient.gender = data.gender
    patient.birth_date = data.age
    patient.education_level = data.education_level
    patient.region = data.region
    patient.zone = data.zone
    session.add(patient)
    session.commit()

    return PatientManager.get_ci_barona(id_patient, session=session)


@router.get("/{id_patient}/assignments", response_model=list[Assignment])
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
    return PatientManager.get_assignments(id_patient, session=session)


@router.get("/has-assignment/{id_assignment}", response_model=bool)
async def has_assignment(
    *, id_assignment: int, get_current_patient: Patient = Depends(get_current_patient)
):
    """
    Check if a current patient has an assignment

    Parameters
    ----------
    id_assignment
        Assignment id

    Returns
    -------
    bool
        True if patient has an assignment

    """
    ids_assignments = [assignment.id for assignment in get_current_patient.assignments]
    return id_assignment in ids_assignments
