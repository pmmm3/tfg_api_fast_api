from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware

from src.routers.auth import router as auth_router
from src.routers.user_service import router as user_router

app = FastAPI()

# Allow CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")


@app.get("/protected")
async def protected(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"message": "Errr    "}
