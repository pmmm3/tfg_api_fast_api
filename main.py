from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

from src.routers.auth import router

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(router, prefix="/api")


@app.get("/protected")
async def protected(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"message": "Errr    "}
