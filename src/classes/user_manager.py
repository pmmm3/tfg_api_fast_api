from sqlmodel import Session

from src.database import engine
from src.models import User, Role


class UserManager:
    @classmethod
    def create_user(cls, email, password, name=None, last_name=None, role=Role.patient):
        """
        Create a new user
        :param email: user email
        :param password: user password
        :param name: username
        :param last_name: user last name
        :param role: user role
        :return: None

        """
        hashed_password = User.hash_password(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            name=name,
            last_name=last_name,
            role=role,
        )
        with Session(engine) as session:
            session.add(user)
            session.commit()
