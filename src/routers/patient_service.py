from fastapi import APIRouter, HTTPException

from src.classes.user_manager import UserManager
from src.models import Token

router = APIRouter(prefix="/patient", tags=["patient"])


@router.post("/activate")
async def activate(token: Token):
    """
    Activate a user account with a token sent to email address when user was created

    Parameters
    ----------
    token
        Token object with token field

    Returns
    -------
    User
        User object if user was activated successfully

    """
    user = UserManager.activate_user_to_patient(token.access_token)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Invalid token")
