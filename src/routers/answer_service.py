from fastapi import APIRouter, Depends
from src.classes.answer_manager import AnswerInput, AnswerManager
from src.utils.reuse import get_session

router = APIRouter(prefix="/answer", tags=["Answer"])


@router.get("/{id_assignment}/{id_module}/{id_question}")
async def get_answer(
    id_assignment: int, id_module: int, id_question: int, session=Depends(get_session)
):
    # Check the assignment exists
    # Check the current user is patient or doctor related to the assignment

    # Check the module exists
    # Check the question exists
    return AnswerManager.get_answer(
        id_assignment, id_module, id_question, session=session
    )


@router.post("/")
async def create_answer(answer: AnswerInput, session=Depends(get_session)):
    # Check the assignment exists

    # Check the patient is related to the assignment

    # Check the module exists
    # Check the question exists
    # Check the question if is option set the option exists
    # Check the question if is open_text set the option is None

    old_answer = AnswerManager.get_answer(
        answer.id_assignment,
        answer.id_question_module_id,
        answer.id_question_question_id,
        session=session,
    )
    if old_answer:
        old_answer.id_option = (
            answer.id_option if answer.id_option else answer.id_option
        )
        old_answer.open_answer = (
            answer.open_answer if answer.open_answer else answer.open_answer
        )
        session.add(old_answer)
        session.commit()
        session.refresh(old_answer)
        return old_answer

    return AnswerManager.save_answer(answer, session=session)
