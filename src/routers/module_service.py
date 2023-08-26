from fastapi import APIRouter, Depends

from src.classes.modules_manager import ModuleNotFound, ModuleManager
from src.utils.reuse import get_session

router = APIRouter(prefix="/module", tags=["Modulos"])


@router.get("/{id_module}")
async def get_module(id_module: str, session=Depends(get_session)):
    """
    Get a module by id

    Parameters
    ----------
    id_module
        Module id

    Returns
    -------
    Module
        Module object

    Raises
    ------
    ModuleNotFound
        If module does not exist
    """
    module = ModuleManager.get_module(id_module, session=session)
    if module:
        return module
    raise ModuleNotFound()


# Get all modules endpoint
@router.get("/")
async def get_modules(session=Depends(get_session)):
    """
    Get all-modules
    Returns
    -------
    list[Module]
        List of all modules
    """
    return ModuleManager.get_modules(session=session)


@router.get("/{id_module}/questions")
async def get_module_with_questions(id_module: str, session=Depends(get_session)):
    return ModuleManager.get_module_with_questions(id_module, session=session)
