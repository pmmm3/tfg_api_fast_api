from typing import Optional, List

from pydantic import Field
from sqlmodel import Session, select, SQLModel

from src.classes.modules_manager import ModuleManager
from src.models import Questionnaire, QuestionnaireModuleLink, Module


class QuestionnaireInput(SQLModel):
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    modules: List[Module] = Field(default=None)


class QuestionnaireManager:
    @staticmethod
    def get_questionnaires(session: Session) -> list[Questionnaire]:
        return session.exec(select(Questionnaire)).all()

    @staticmethod
    def create_questionnaire(
        title: str,
        description: str,
        author: str,
        modules: list[Module] = None,
        *,
        session: Session,
    ) -> Questionnaire:
        questionnaire = Questionnaire(
            title=title, description=description, created_by=author
        )
        session.add(questionnaire)
        if modules:
            for module in modules:
                module = ModuleManager.get_module(module.id, session=session)
                if module:
                    session.add(
                        QuestionnaireModuleLink(
                            id_questionnaire=questionnaire.id, id_module=module.id
                        )
                    )

        session.commit()
        session.refresh(questionnaire)
        return questionnaire

    @staticmethod
    def get_modules_from_questionnaire(
        id_questionnaire: int, session: Session
    ) -> list[Module]:
        return [
            ModuleManager.get_module(link.id_module, session=session)
            for link in session.exec(
                select(QuestionnaireModuleLink).where(
                    QuestionnaireModuleLink.id_questionnaire == id_questionnaire
                )
            ).all()
        ]

    @staticmethod
    def get_questionnaire(id_questionnaire: int, session: Session) -> Questionnaire:
        return session.exec(
            select(Questionnaire).where(Questionnaire.id == id_questionnaire)
        ).first()
