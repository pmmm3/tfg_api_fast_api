from fastapi import APIRouter

from src.classes.mail import email_manager

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/send-email")
async def send_email(
    to: str, subject: str, body: str, link: str = None, attachment_path: str = None
):
    return await email_manager.send_email(to, subject, body, link, attachment_path)
