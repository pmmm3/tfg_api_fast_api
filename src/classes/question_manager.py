from sqlmodel import Session, select

from src.models import Question


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
