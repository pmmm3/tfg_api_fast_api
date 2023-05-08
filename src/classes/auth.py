import jwt
from sqlmodel import Session, select

from src.database import engine
from src.models import User


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


class UserDisabled(Exception):
    def __init__(self):
        self.message = "User disabled."
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
            if user.disabled:
                raise UserDisabled()
            # Crear el token de autenticación
            payload = {"email": user.email}
            token = jwt.encode(payload, "secret", algorithm="HS256")
            return {"access_token": token}
