from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.models import Role
from src.routers.auth import router as auth_router
from src.routers.user_service import router as user_router
from src.utils.authorization import has_role

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

app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")


@app.get("/protected")
async def protected_route(authorized_role: bool = Depends(has_role([Role.admin]))):
    if authorized_role:
        return {"message": "This is a protected route"}
