from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException

from src.classes.mail import email_manager
from src.classes.user_manager import UserManager
from src.models import Role, ActivateUserData
from src.utils.authorization import has_role

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/send-activate_account")
async def send_activate_account(
    email: Annotated[str, Body(embed=True)],
    authorized_role: bool = Depends(has_role([Role.admin, Role.doctor])),
):
    user = UserManager.create_user(email=email, password="temp")
    if user:
        return await email_manager.send_activate_account(to=email, token=user.token)
    raise HTTPException(status_code=400, detail="Email already exists")


@router.post("/activate")
async def activate(data: ActivateUserData):
    user = UserManager.activate_user(data)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Invalid token")
