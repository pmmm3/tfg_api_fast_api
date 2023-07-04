from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.classes.auth import IncorrectPassword, UserNotFound, Auth, UserDisabled
from src.models import Token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        return Auth.login(form_data.username, form_data.password)
    except (UserNotFound, IncorrectPassword, UserDisabled) as e:
        raise HTTPException(status_code=401, detail=str(e))
