from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, HTTPException

from src.classes.mail import email_manager
from src.classes.user_manager import UserManager
from src.models import (
    Role,
    ActivateUserData,
    User,
    UserInput,
    ListParams,
    UserOutput,
    UserBase,
)
from src.utils.authorization import has_role, get_current_user

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/send-activate_account")
async def send_activate_account(
    email: Annotated[str, Body(embed=True)],
    authorized_role: bool = Depends(has_role([Role.admin, Role.doctor])),
):
    """
    Send email with token to activate user account

    Parameters
    ----------
    email
        User email address
    authorized_role
        User role

    Returns
    -------
    Nothing
    """

    user = UserManager.create_user(email=email, password="temp")
    if user:
        return await email_manager.send_activate_account(to=email, token=user.token)
    raise HTTPException(status_code=400, detail="Email already exists")


@router.post("/register", response_model=UserOutput)
async def register(data: UserInput) -> UserOutput:
    """
    Create a new admin or doctor account

    Parameters
    ----------
    data
        UserInput object with email, password, name, last_name and role fields

    Returns
    -------
    User
        User object if user was created successfully

    """
    try:
        return UserManager.create_user(**data.dict())
    except Exception:
        raise HTTPException(status_code=400, detail="Error while creating user")


@router.post("/activate")
async def activate(data: ActivateUserData) -> UserOutput:
    """
    Activate a user account with a token sent to email address when user was created

    Parameters
    ----------
    data
        ActivateUserData object with token, name, last_name and password fields

    Returns
    -------
    User
        User object if user was activated successfully

    """
    user = UserManager.activate_user(data)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Invalid token")


@router.patch("/update")
async def update_user(
    user: User, current_user: User = Depends(get_current_user)
) -> UserOutput:
    """
    Update user data.

    Parameters
    ----------

    current_user
        User object with current user data.
    user
        UpdateUser object with updated data.

    """
    if user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        UserManager.update_user(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {e}")


@router.patch("/update/{user_id}")
async def update_user_by_id(
    user_id: int, user: User, authorized_role: bool = Depends(has_role([Role.admin]))
) -> User:
    """
    Update user data.

    Parameters
    ----------
    user_id
        User id.

    user
        UpdateUser object with updated data.

    authorized_role
        User role

    Returns
    -------
    User
        User object if user was updated successfully

    """
    if user.role == Role.admin and authorized_role != Role.admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        return UserManager.update_user(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {e}")


@router.post("/list", response_model=List[UserBase])
async def list_users(
    params: ListParams, authorized_role: bool = Depends(has_role([Role.admin]))
) -> any:
    """
    List users

    Parameters
    ----------
    params
        ListParams object with limit, offset and sort fields

    authorized_role
        User role

    Returns
    -------
    list[User]
        List of users
    """
    try:
        result = UserManager.list_users(params)
        users = []
        for user in result:
            users.append(UserBase.from_orm(user))
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing users: {e}")
