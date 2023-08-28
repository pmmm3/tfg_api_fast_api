from fastapi import APIRouter, Depends

from src.classes.questionnaire_manager import QuestionnaireManager, QuestionnaireInput
from src.utils.authorization import is_doctor_or_admin, get_current_user
from src.utils.reuse import get_session

router = APIRouter(prefix="/questionnaire", tags=["Questionnaire"])


@router.get("/")
async def get_questionnaires(
    is_admin_or_doctor=Depends(is_doctor_or_admin), session=Depends(get_session)
):
    return QuestionnaireManager.get_questionnaires(session=session)


@router.get("/{id_questionnaire}/modules")
async def get_modules_from_questionnaire(
    id_questionnaire: int, session=Depends(get_session)
):
    return QuestionnaireManager.get_modules_from_questionnaire(
        id_questionnaire, session=session
    )


@router.post("/")
async def create_questionnaire(
    data: QuestionnaireInput,
    session=Depends(get_session),
    is_admin_or_doctor=Depends(is_doctor_or_admin),
    current_user=Depends(get_current_user),
):
    """
    Create a questionnaire with a list of modules if provided

    Parameters
    ----------
    data
        QuestionnaireInput object with title, description and modules fields

    Returns
    -------
    Questionnaire
        Questionnaire object created
    """
    return QuestionnaireManager.create_questionnaire(
        title=data.title,
        description=data.description,
        modules=data.modules,
        author=current_user.email,
        session=session,
    )
