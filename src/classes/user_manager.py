import jwt
from fastapi import HTTPException
from psycopg2 import IntegrityError
from sqlmodel import Session, select

from src.database import engine
from src.models import User, Patient, UserRoles, Doctor, Admin, StatusUser
from src.settings import Settings


class UserManager:
    @classmethod
    def get_user(cls, email: str) -> User:
        """
        Get user by email
        Parameters
        ----------
        email

        Returns
        -------
        User
            User object if user exists, None otherwise
        """
        with Session(engine) as session:
            return session.exec(select(User).where(User.email == email)).first()

    @classmethod
    def activate_pending_user(cls, email: str):
        """
        Activate a pending user

        Parameters
        ----------
        email
            User email address

        Returns
        -------
        User
            User object if user was activated successfully

        Raises
        ------
        HTTPException
            If user is not pending
        """
        with Session(engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if user and user.status == StatusUser.pending:
                user.status = StatusUser.active
                session.add(user)
                session.commit()
                return user
            raise HTTPException(status_code=400, detail="User is not pending")

    @classmethod
    def create_user(
        cls,
        email,
        password="temp",
        name=None,
        last_name=None,
        status=StatusUser.disabled,
    ) -> User:
        """
        Create a new user with email and password and set status to disabled

        Parameters
        ----------
        email   :   User email address
        password: User password
        name : Username
        last_name: User last name
        status: User status

        """
        try:
            hashed_password = User.hash_password(password)
            user = User(
                email=email,
                hashed_password=hashed_password,
                name=name,
                last_name=last_name,
                status=status,
            )
            if status == StatusUser.disabled:
                user.create_activation_token()
            with Session(engine) as session:
                session.add(user)
                session.commit()
            return user
        except IntegrityError:
            raise HTTPException(status_code=409, detail="Email already exists")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creating user: {e}")

    @classmethod
    def activate_user_to_patient(cls, data):
        email = jwt.decode(data.token, Settings().token_secret, algorithms=["HS256"])[
            "email"
        ]
        with Session(engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            existing_patient = session.exec(
                select(Patient).where(Patient.id_user == user.email)
            ).first()
            if user.token != data.token:
                raise HTTPException(status_code=400, detail="Invalid token")
            if user and user.status == StatusUser.disabled and not existing_patient:
                user.status = StatusUser.active
                user.name = data.name if data.name else None
                user.last_name = data.last_name if data.last_name else None
                user.hashed_password = User.hash_password(data.password)
                user.token = None
                session.add(user)
                # Check if is an admin or doctor
                is_doctor = session.exec(
                    select(Doctor).where(Doctor.id_user == user.email)
                ).first()
                is_admin = session.exec(
                    select(Admin).where(Admin.id_user == user.email)
                ).first()
                if not is_doctor and not is_admin:
                    patient = Patient(id_user=user.email)
                    session.add(patient)
                    session.commit()

                return user
            raise HTTPException(status_code=400, detail="Error activating user")

    @classmethod
    def set_user_role(cls, user: User, role: UserRoles):
        with Session(engine) as session:
            if role == UserRoles.admin:
                cls._set_role(session, user, Admin, "admin")
            elif role == UserRoles.doctor:
                cls._set_role(session, user, Doctor, "doctor")
            else:
                raise HTTPException(status_code=400, detail="Invalid user role")

    @staticmethod
    def _set_role(session, user, role_model, role_name):
        user_role = role_model(id_user=user.email)
        existing_role = session.exec(
            select(role_model).where(role_model.id_user == user.email)
        ).first()
        if not existing_role:
            session.add(user_role)
            session.commit()
        else:
            raise HTTPException(
                status_code=400, detail=f"Error setting user role as {role_name}"
            )

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
