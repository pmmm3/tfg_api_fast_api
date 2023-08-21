from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session

from src.classes.patient_manager import PatientManager
from src.classes.user_manager import UserManager
from src.models import Token, ConsentField, Patient
from src.utils.reuse import get_session
from src.utils.authorization import (
    get_current_patient,
)

router = APIRouter(prefix="/patient", tags=["patient"])


@router.post("/activate")
async def activate(token: Token):
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
    user = UserManager.activate_user_to_patient(token.access_token)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Invalid token")


@router.post("/accept-consent")
async def accept_consent(
    consentField: ConsentField,
    *,
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
    user = PatientManager.accept_consent(
        id=consentField.id_patient,
        consent=True,
        dni=consentField.dni,
        name=consentField.name,
        last_name=consentField.last_name,
        session=session,
    )
    if user:
        return user
    raise HTTPException(status_code=400, detail="Invalid token")
