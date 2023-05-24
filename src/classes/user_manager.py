import jwt
from fastapi import HTTPException
from psycopg2 import IntegrityError
from sqlmodel import Session, select

from src.database import engine
from src.models import User, Role


class UserManager:
    @classmethod
    def create_user(
        cls, email, password=None, name=None, last_name=None, role=Role.patient
    ) -> User:
        """
        Create a new user

        Parameters
        ----------
        email   :   User email address
        password: User password
        name : Username
        last_name: User last name
        role: User role

        """
        try:
            hashed_password = User.hash_password(password)
            user = User(
                email=email,
                hashed_password=hashed_password,
                name=name,
                last_name=last_name,
                role=role,
                disabled=True,
            )
            user.create_activation_token()
            with Session(engine) as session:
                session.add(user)
                session.commit()
            return user
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Email already exists")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating user: {e}")

    @classmethod
    def activate_user(cls, data):
        if not data.token:
            raise HTTPException(status_code=400, detail="Token is required")
        email = jwt.decode(data.token, "secret", algorithms=["HS256"])["email"]
        with Session(engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if user.token != data.token:
                raise HTTPException(status_code=400, detail="Invalid token")
            if user and user.disabled:
                user.disabled = False
                user.name = data.name if data.name else None
                user.last_name = data.last_name if data.last_name else None
                user.hashed_password = User.hash_password(data.password)
                user.token = None
                session.add(user)
                session.commit()
                return user
            raise HTTPException(status_code=400, detail="Error activating user")

    @classmethod
    def update_user(cls, user: User) -> User:
        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    @classmethod
    def list_users(cls, params):
        statement = select(User)

        if params.filters:
            for filter_item in params.filters:
                if hasattr(User, filter_item.field):
                    statement = statement.where(
                        getattr(User, filter_item.field) == filter_item.value
                    )

        if params.page >= 0 and params.per_page > 0:
            statement = statement.offset(params.page * params.per_page).limit(
                params.per_page
            )

        with Session(engine) as session:
            return session.exec(statement).all()
