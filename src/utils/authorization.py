import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer
from jwt import InvalidSignatureError, InvalidTokenError
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select

from src.database import engine
from src.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        email = payload["email"]
        with Session(engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            return user
    except InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Define the has_role dependency function
def has_role(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def check_role(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
        try:
            # Get the user's email from the token payload
            payload = jwt.decode(credentials, "secret", algorithms=["HS256"])
            email = payload["email"]

            # Query the database for the user
            with Session(engine) as db:
                user = db.query(User).filter_by(email=email).first()

                # Check if the user has the required role
                if user.role not in allowed_roles:
                    raise HTTPException(status_code=403, detail="Not authorized")
            return True
        except (InvalidSignatureError, InvalidTokenError, SQLAlchemyError):
            raise HTTPException(status_code=403, detail="Not authorized")

    return check_role
