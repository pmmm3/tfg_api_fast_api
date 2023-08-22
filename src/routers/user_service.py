from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlmodel import Session

from src.classes.doctor_manager import DoctorManager
from src.classes.mail import email_manager
from src.classes.user_manager import UserManager
from src.models import (
    UserBase,
    UserInput,
    UserRoles,
    User,
    ListParams,
    UserBaseWithRole,
    DocOrAdminInput,
)
from src.utils.authorization import (
    is_doctor_or_admin,
    is_admin,
    get_current_user,
    get_current_doctor,
)
from src.utils.reuse import get_session

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/send-activate-account")
async def send_activate_account(
    email: Annotated[str, Body(embed=True)],
    _=Depends(is_doctor_or_admin),
    *,
    session: Session = Depends(get_session),
):
    """
    Send email with token to activate user account

    Parameters
    ----------
    email
        User email address

    Returns
    -------
    Nothing
    """

    user = UserManager.create_user(email=email, password="temp", session=session)
    if user:
        return await email_manager.send_activate_account(to=email, token=user.token)
    raise HTTPException(status_code=400, detail="Email already exists")


@router.post("/activate")
async def activate(data: UserInput, *, session: Session = Depends(get_session)):
    """
    Activate a user account with a token sent to email address when user was created

    Parameters
    ----------
    data
        UserInput object with token field and optional email, password, name, last_name fields

    Returns
    -------
    User
        User object if user was activated successfully

    Raises
    ------
    HTTPException
        If token is invalid

    """
    user = UserManager.activate_user_to_patient(data, session=session)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Invalid token")


@router.post("/register", response_model=UserBase)
async def register(
    email: Annotated[str, Body(embed=True)],
    role: UserRoles,
    _=Depends(is_admin),
    *,
    session: Session = Depends(get_session),
):
    """
    Admin creates a new admin or doctor account

    Parameters
    ----------
    email
        User email address
    role
        User role (admin or doctor)

    Returns
    -------
    User
        User object if user was created successfully

    """
    try:
        user = UserManager.create_user(email=email, password="temp", session=session)
        if user:
            UserManager.set_user_role(user, role)
            await email_manager.send_activate_account(to=user.email, token=user.token)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error while creating user in register{e}"
        )


@router.post("/request-register", status_code=status.HTTP_201_CREATED)
async def request_register(
    email: Annotated[str, Body(embed=True)],
    role: UserRoles,
    session: Session = Depends(get_session),
):
    """
    Request admin to create a new admin or doctor account
    It creates a new user with the status "pending"

    Parameters
    ----------
    email
    role

    Returns
    -------
        HTTP status code 201 if user was created successfully

    """
    try:
        user = UserManager.create_user(
            email=email, password="temp", status="pending", session=session
        )
        if user:
            try:
                UserManager.set_user_role(user, role, session=session)
                return {"message": "User created successfully"}
            except Exception as e:
                UserManager.delete_user(user, session=session)
                raise e

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error while creating user {e}")


@router.post("/forgot-password")
async def restore_password(
    email: Annotated[str, Body(embed=True)], *, session: Session = Depends(get_session)
):
    """
    Send email with token to restore user password
    Parameters
    ----------
    email

    Returns
    -------
    HTTP status code 200 if email was sent successfully

    """
    user = UserManager.get_user(email, session=session)
    if user:
        user.create_activation_token()
        session.add(user)
        session.commit()
        return await email_manager.send_restore_password(to=email, token=user.token)
    raise HTTPException(status_code=400, detail="Email not found")


@router.post("/change-password")
async def change_password(data: UserInput, *, session: Session = Depends(get_session)):
    """
    Change password for a user
    """
    user = UserManager.get_user_by_token(data.token, session=session)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    user.hashed_password = user.hash_password(data.password)
    user.token = None
    session.add(user)
    session.commit()
    return {"message": "Password changed successfully"}


@router.post("/activate-pending-user", response_model=UserBase)
async def activate_pending_user(
    email: str, _=Depends(is_admin), *, session: Session = Depends(get_session)
):
    """
    Activate a pending user account
    Parameters
    ----------
    email
    _

    Returns
    -------
    User
        User object if user was activated successfully

    """
    user = UserManager.activate_pending_user(email, session=session)
    if user:
        return user
    raise HTTPException(
        status_code=400, detail="Something went wrong while activating user"
    )


@router.get("/is-admin", response_model=bool)
async def is_user_admin(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    """
    Check if the current user is admin
    Returns
    -------
    bool
        True if user is admin

    """
    return UserManager.is_admin(user, session=session)


@router.get("/is-doctor", response_model=bool)
async def is_user_doctor(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    """
    Check if the current user is doctor
    Returns
    -------
    bool
        True if user is doctor

    """
    return UserManager.is_doctor(user, session=session)


@router.get("/is-patient", response_model=bool)
async def is_user_patient(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    """
    Check if the current user is patient
    Returns
    -------
    bool
        True if user is patient

    """
    return UserManager.is_patient(user, session=session)


@router.post("/list")
async def list_users(
    params: ListParams = None,
    *,
    session: Session = Depends(get_session),
    _=Depends(is_admin),
) -> dict:
    """
    List users

    Parameters
    ----------
    params
        ListParams object with limit, offset and sort fields

    Returns
    -------
    list[User]
        List of users
    total
        number of users with the given filters
    """
    try:
        result, total = UserManager.list_users(params, session=session)
        users = []
        for user in result:
            rol = UserManager.get_role_user(user, session=session)
            users.append(UserBaseWithRole.from_orm(user, {"rol": rol}))
        return {"users": users, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing users: {e}")


@router.delete("/{user_id}")
async def delete_user(
    user_id, *, session: Session = Depends(get_session), _=Depends(is_doctor_or_admin)
):
    """
    Delete user
    Parameters
    ----------
    user_id
        User email address

    Returns
    -------
    Nothing
    """
    try:
        user = UserManager.get_user(user_id, session=session)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        UserManager.delete_user(user, session=session)
        return {"message": "User deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {e}")


@router.get("/list-patients")
async def list_patients(
    doc=Depends(get_current_doctor), *, session: Session = Depends(get_session)
):
    """
    List patients

    Parameters
    ----------

    Returns
    -------
    list[User]
        List of users
    """
    try:
        result = DoctorManager.list_patients(doctor=doc, session=session)
        return {"patients": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing patients: {e}")


# TODO: Implementar bien el request delete
@router.put("/request-delete")
async def request_delete(
    email: str,
    *,
    session: Session = Depends(get_session),
    _=Depends(is_doctor_or_admin),
):
    """
    Request admin to delete a user account
    It changes the user status to "pending-delete"

    Parameters
    ----------
    email

    Returns
    -------
    HTTP status code 201 if user was created successfully

    """
    try:
        user = UserManager.get_user(email=email, session=session)
        if user:
            user.status = "pending-delete"
            session.commit()
            return {"message": "User deleted successfully"}
        raise HTTPException(status_code=400, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {e}")


@router.post("/request-activate", status_code=201)
async def request_activate(
    data: DocOrAdminInput, *, session: Session = Depends(get_session)
):
    """
    Request admin to activate a doctor account
    It creates a new user with the status "pending-activate"

    Parameters
    ----------
    data
        DocOrAdminInput object with email and role fields

    Returns
    -------
    HTTP status code 201 if user was created successfully

    """
    UserManager.request_activate(data, session=session)
    # Return 201
    return {"message": "Record saved"}
