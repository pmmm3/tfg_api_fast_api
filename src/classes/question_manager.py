from enum import Enum

from sqlmodel import Session, select, SQLModel

from src.models import Question


class QuestionType(str, Enum):
    YN = "YesNo"
    MULTIPLE = "multiple"
    TEXT = "text"


class QuestionOption(SQLModel):
    type_opt: QuestionType
    options: list[str] or None


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
    def get_question_options(
        cls, id_question: int, id_module: int, session: Session
    ) -> QuestionOption or None:
        question = cls.get_question(id_question, id_module, session=session)
        if question:
            options = question.options
            if options:
                options = [option.content for option in options]
            type_opt = QuestionType.TEXT
            if len(options) == 2:
                type_opt = QuestionType.YN
            elif len(options) > 2:
                type_opt = QuestionType.MULTIPLE
            return QuestionOption(type_opt=type_opt, options=options)
        else:
            return None
