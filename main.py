from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.auth import router as auth_router
from src.routers.user_service import router as user_router
from src.routers.patient_service import router as patient_router
from src.routers.doctor_service import router as doctor_router
from src.routers.module_service import router as module_router
from src.routers.questionnaire_service import router as questionnaire_router
from src.routers.assignment_service import router as assignments_router
from src.routers.question_service import router as question_router

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(patient_router)
app.include_router(doctor_router)
app.include_router(module_router)
app.include_router(questionnaire_router)
app.include_router(assignments_router)
app.include_router(question_router)
