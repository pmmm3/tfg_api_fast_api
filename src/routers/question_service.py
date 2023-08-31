from fastapi import APIRouter, Depends

from src.classes.question_manager import QuestionManager
from src.utils.reuse import get_session

router = APIRouter(prefix="/question", tags=["Question"])


@router.get("/{id_question}/{id_module}/type")
async def get_question_type(
    id_question: int, id_module: int, session=Depends(get_session)
):
    return QuestionManager.get_question_options(id_question, id_module, session=session)
