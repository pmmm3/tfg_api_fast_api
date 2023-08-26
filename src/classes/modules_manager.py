from functools import partial
from typing import Optional, List

from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import select
from src.models import Module, Question

ModuleNotFound = partial(HTTPException, status_code=404, detail="Module not found")


class ModuleOutput(BaseModel):
    id: Optional[int]
    title: Optional[str]
    description: Optional[str]
    questions_list: List[Question]  # This assumes you have a `Question` class defined


class ModuleManager:
    @classmethod
    def get_module(cls, id_module: str, *, session) -> Module:
        """
        Get module by id
        Parameters
        ----------
        id_module

        Returns
        -------
        Module
            Object if module exists, None otherwise
        """
        return session.exec(select(Module).where(Module.id == id_module)).first()

    @classmethod
    def get_modules(cls, *, session) -> list[Module]:
        """
        Get all-modules
        Returns
        -------
        list[Module]
            List of all modules
        """
        return session.exec(select(Module)).all()

    @classmethod
    def get_module_with_questions(cls, id_module, *, session) -> ModuleOutput:
        """
        Get module with questions

        Parameters
        ----------
        id_module
            Module id

        Returns
        -------
        ModuleOutput
            Module object with questions

        Raises
        ------
        ModuleNotFound
            If module does not exist
        """
        module = cls.get_module(id_module, session=session)

        if module:
            # Fetch the associated questions for the module
            questions = session.exec(
                select(Question).where(Question.id_module == id_module)
            ).all()

            # Create a ModuleOutput instance with the retrieved module attributes and questions
            module_output = ModuleOutput(
                id=module.id,
                title=module.title,
                description=module.description,
                questions_list=questions,
            )

            return module_output

        raise ModuleNotFound()
