from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.classes.auth import IncorrectPassword, UserNotFound, Auth
from src.models import Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        return Auth.login(form_data.username, form_data.password)
    except UserNotFound as e:
        return {"message": e.message}, e.code
    except IncorrectPassword as e:
        return {"message": e.message}, e.code
