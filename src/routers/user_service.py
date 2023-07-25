from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlmodel import Session

from src.classes.mail import email_manager
from src.classes.user_manager import UserManager
from src.database import engine
from src.models import UserBase, UserInput, UserRoles
from src.utils.authorization import is_doctor_or_admin, is_admin

router = APIRouter(prefix="/user", tags=["user"])


def get_session():
    with Session(engine) as session:
        yield session


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


# @router.post(
#     "/list", response_model=List[UserBase], dependencies=[Depends(is_doctor_or_admin)]
# )
# async def list_users(
#     params: ListParams,
# ) -> any:
#     """
#     List users
#
#     Parameters
#     ----------
#     params
#         ListParams object with limit, offset and sort fields
#
#     Returns
#     -------
#     list[User]
#         List of users
#     """
#     try:
#         result = UserManager.list_users(params)
#         users = []
#         for user in result:
#             users.append(UserBase.from_orm(user))
#         return users
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error listing users: {e}")
