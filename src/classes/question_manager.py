from enum import Enum

from sqlmodel import Session, select

from src.models import Question


class QuestionType(str, Enum):
    YN = "YesNo"
    MULTIPLE = "multiple"
    TEXT = "text"


class QuestionManager:
    @classmethod
    def get_question(
        cls, id_question: int, id_module: int, session: Session
    ) -> Question:
        return session.exec(
            select(Question).where(
                Question.id == id_question and Question.id_module == id_module
            )
        ).first()

    @classmethod
    def get_questions(cls, id_module: int, session: Session) -> list[Question]:
        return session.exec(
            select(Question).where(Question.id_module == id_module)
        ).all()

    @classmethod
    def get_question_type(
        cls, id_question: int, id_module: int, session: Session
    ) -> QuestionType or None:
        question = cls.get_question(id_question, id_module, session=session)
        if question:
            options = question.options
            if len(options) == 2:
                return QuestionType.YN
            elif len(options) > 2:
                return QuestionType.MULTIPLE
            return QuestionType.TEXT
        else:
            return None
