import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidSignatureError, InvalidTokenError
from sqlmodel import Session, select

from src.classes.user_manager import UserManager
from src.database import engine
from src.models import User, Patient, Doctor
from src.settings import Settings
from src.utils.reuse import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, Settings().token_secret, algorithms=["HS256"])
        email = payload["email"]
        with Session(engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
    except (InvalidSignatureError, InvalidTokenError):
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_patient(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> Patient:
    patient = session.exec(select(Patient).where(Patient.id_user == user.email)).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


async def get_current_doctor(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> Doctor:
    doctor = session.exec(select(Doctor).where(Doctor.id_user == user.email)).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


async def is_doctor(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    if not UserManager().is_doctor(user, session=session):
        raise HTTPException(status_code=401, detail="User is not a doctor")
    return True


async def is_patient(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    if not UserManager().is_patient(user, session=session):
        raise HTTPException(status_code=401, detail="User is not a patient")
    return True


async def is_admin(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    if not UserManager().is_admin(user, session=session):
        raise HTTPException(status_code=401, detail="User is not an admin")
    return True


async def is_doctor_or_admin(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    return UserManager().is_admin(user, session=session) or UserManager().is_doctor(
        user, session=session
    )
