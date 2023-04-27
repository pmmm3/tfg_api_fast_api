from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from datetime import datetime

from passlib.hash import pbkdf2_sha256


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: EmailStr = Field(index=True)
    name: str
    last_name: str = Field(default=None)
    hashed_password: str
    disabled: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @staticmethod
    def hash_password(password: str):
        return pbkdf2_sha256.hash(password)

    def verify_password(self, password: str):
        return pbkdf2_sha256.verify(password, self.hashed_password)


class LoginParams(SQLModel):
    email: EmailStr
    password: str
