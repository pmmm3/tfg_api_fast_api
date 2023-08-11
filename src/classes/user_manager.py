from functools import partial
from typing import Any

import jwt
from fastapi import HTTPException
from psycopg2 import IntegrityError
from sqlalchemy import desc, asc
from sqlmodel import Session, select

from src.database import engine
from src.models import User, Patient, UserRoles, Doctor, Admin, StatusUser, ListParams
from src.settings import Settings


def _set_role(user, role_model, role_name, *, session):
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


class UserManager:
    @classmethod
    def delete_user(cls, user: User, *, session):
        session.delete(user)
        session.commit()

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
    def activate_pending_user(cls, email: str, *, session):
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
        *,
        session,
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
            session.add(user)
            session.commit()
            return user
        except IntegrityError:
            raise HTTPException(status_code=409, detail="Email already exists")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creating user: {e}")

    @classmethod
    def activate_user_to_patient(cls, data, *, session):
        email = jwt.decode(data.token, Settings().token_secret, algorithms=["HS256"])[
            "email"
        ]
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
    def set_user_role(cls, user: User, role: UserRoles, *, session):
        set_role = partial(_set_role, session=session, user=user)
        if role == UserRoles.admin:
            set_role(role_model=Admin, role_name="admin")
        elif role == UserRoles.doctor:
            set_role(role_model=Doctor, role_name="doctor")
        else:
            raise HTTPException(status_code=400, detail="Invalid user role")

    @classmethod
    def update_user(cls, user: User, *, session) -> User:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @classmethod
    def get_role_user(cls, user: User, *, session) -> UserRoles:
        role_checks = [
            (cls.is_doctor, UserRoles.doctor),
            (cls.is_admin, UserRoles.admin),
            (cls.is_patient, UserRoles.patient),
        ]

        for check, role in role_checks:
            if check(user, session=session):
                return role
        return UserRoles.user

    @classmethod
    def list_users(cls, params: ListParams, *, session) -> tuple[Any, int]:
        statement_count = statement = select(User)
        if params:
            if params.filters:
                for filter_item in params.filters:
                    if hasattr(User, filter_item.field):
                        statement = statement.where(
                            getattr(User, filter_item.field) == filter_item.value
                        )
            statement_count = statement

            if params.page >= 0 and params.per_page > 0:
                statement = statement.offset(params.page * params.per_page).limit(
                    params.per_page
                )
            if params.sort:
                descending = params.sort[0] == "-"
                if descending:
                    params.sort = params.sort[1:]
                if hasattr(User, params.sort):
                    statement = statement.order_by(
                        desc(getattr(User, params.sort))
                        if descending
                        else asc(getattr(User, params.sort))
                    )

        return (
            session.exec(statement).all(),
            len(session.exec(statement_count).all()),
        )

    @classmethod
    def is_admin(cls, user: User, *, session):
        return (
            session.exec(select(Admin).where(Admin.id_user == user.email)).first()
            is not None
        )

    @classmethod
    def is_doctor(cls, user: User, *, session):
        return (
            session.exec(select(Doctor).where(Doctor.id_user == user.email)).first()
            is not None
        )

    @classmethod
    def is_patient(cls, user: User, *, session):
        return (
            session.exec(select(Patient).where(Patient.id_user == user.email)).first()
            is not None
        )
