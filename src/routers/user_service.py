from fastapi import APIRouter

from src.classes.mail import email_manager

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/send-activate_account")
async def send_activate_account(to: str):
    return await email_manager.send_activate_account(to)
