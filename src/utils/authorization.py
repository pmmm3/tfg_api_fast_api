import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidSignatureError, InvalidTokenError
from sqlmodel import Session, select

from src.database import engine
from src.models import User, Patient, Doctor, Admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        email = payload["email"]
        with Session(engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            return user
    except (InvalidSignatureError, InvalidTokenError):
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_patient(user: User = Depends(get_current_user)) -> Patient:
    try:
        with Session(engine) as session:
            return session.exec(
                select(Patient).where(Patient.id_user == user.email)
            ).first()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid patient")


async def get_current_doctor(user: User = Depends(get_current_user)) -> Doctor:
    try:
        with Session(engine) as session:
            return session.exec(
                select(Doctor).where(Doctor.id_user == user.email)
            ).first()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid patient")


async def is_doctor(user: User = Depends(get_current_user)):
    try:
        with Session(engine) as session:
            return (
                session.exec(select(Doctor).where(Doctor.id_user == user.email)).first()
                is not None
            )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid patient")


async def is_patient(user: User = Depends(get_current_user)):
    try:
        with Session(engine) as session:
            return (
                session.exec(
                    select(Patient).where(Patient.id_user == user.email)
                ).first()
                is not None
            )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid patient")


async def is_admin(user: User = Depends(get_current_user)):
    try:
        with Session(engine) as session:
            return (
                session.exec(select(Admin).where(User.email == user.email)).first()
                is not None
            )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid admin")
