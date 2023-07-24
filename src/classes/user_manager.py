import jwt
from fastapi import HTTPException
from psycopg2 import IntegrityError
from sqlmodel import Session, select

from src.database import engine
from src.models import User, Patient, UserRoles, Doctor, Admin
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
    def create_user(cls, email, password=None, name=None, last_name=None) -> User:
        """
        Create a new user

        Parameters
        ----------
        email   :   User email address
        password: User password
        name : Username
        last_name: User last name

        """
        try:
            hashed_password = None
            if password:
                hashed_password = User.hash_password(password)
            user = User(
                email=email,
                hashed_password=hashed_password,
                name=name,
                last_name=last_name,
                disabled=True,
            )
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
            if user and user.disabled and not existing_patient:
                user.disabled = False
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
        if role == UserRoles.admin:
            admin = Admin(id_user=user.email)
            with Session(engine) as session:
                is_admin = session.exec(
                    select(Admin).where(Admin.id_user == user.email)
                ).first()
                if not is_admin:
                    session.add(admin)
                    session.commit()
                else:
                    raise HTTPException(
                        status_code=400, detail="Error setting user role"
                    )
        elif role == UserRoles.doctor:
            doctor = Doctor(id_user=user.email)
            with Session(engine) as session:
                is_doctor = session.exec(
                    select(Doctor).where(Doctor.id_user == user.email)
                ).first()
                if not is_doctor:
                    session.add(doctor)
                    session.commit()
                else:
                    raise HTTPException(
                        status_code=400, detail="Error setting user role"
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
