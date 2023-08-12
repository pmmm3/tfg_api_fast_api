import jwt
from sqlmodel import Session, select

from src.database import engine
from src.models import User, StatusUser
from src.settings import Settings


class UserNotFound(Exception):
    def __init__(self, email):
        self.message = f"User with email {email} not found."
        self.code = 404
        super().__init__(self.message)


class IncorrectPassword(Exception):
    def __init__(self):
        self.message = "Incorrect password."
        self.code = 401
        super().__init__(self.message)


class UserNotStatusValid(Exception):
    def __init__(self):
        self.message = "User status is not valid."
        self.code = 401
        super().__init__(self.message)


class Auth:
    @classmethod
    def login(cls, email, password):
        with Session(engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if not user:
                raise UserNotFound(email)
            if not user.verify_password(password):
                raise IncorrectPassword()
            if user.status == StatusUser.disabled:
                raise UserNotStatusValid()
            payload = {"email": user.email}
            token = jwt.encode(payload, Settings().token_secret, algorithm="HS256")
            return {"access_token": token}
