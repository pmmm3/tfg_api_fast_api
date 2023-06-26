import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidSignatureError, InvalidTokenError
from sqlmodel import Session, select

from src.database import engine
from src.models import User, Patient

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


async def get_current_patient(token: str = Depends(oauth2_scheme)) -> Patient:
    try:
        user = await get_current_user(token)
        with Session(engine) as session:
            patient = session.exec(
                select(Patient).where(Patient.id_user == user.email)
            ).first()
            return patient
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
