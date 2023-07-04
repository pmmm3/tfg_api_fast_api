from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, HTTPException

from src.classes.mail import email_manager
from src.classes.user_manager import UserManager
from src.models import ListParams, UserBase
from src.utils.authorization import is_doctor, is_admin

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "/send-activate-account", dependencies=[Depends(is_doctor), Depends(is_admin)]
)
async def send_activate_account(email: Annotated[str, Body(embed=True)]):
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

    user = UserManager.create_user(email=email, password="temp")
    if user:
        return await email_manager.send_activate_account(to=email, token=user.token)
    raise HTTPException(status_code=400, detail="Email already exists")


@router.post("/register", response_model=UserBase)
async def register(data):
    """
    Create a new admin or doctor account

    Parameters
    ----------
    data
        UserInput object with email, password, name, last_name fields

    Returns
    -------
    User
        User object if user was created successfully

    """
    try:
        return UserManager.create_user(**data.dict())
    except Exception:
        raise HTTPException(status_code=400, detail="Error while creating user")


@router.post("/list", response_model=List[UserBase], dependencies=[Depends(is_admin)])
async def list_users(
    params: ListParams,
) -> any:
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
    """
    try:
        result = UserManager.list_users(params)
        users = []
        for user in result:
            users.append(UserBase.from_orm(user))
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing users: {e}")
