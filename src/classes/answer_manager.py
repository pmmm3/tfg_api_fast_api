from sqlmodel import Session, select, SQLModel

from src.classes.assignment_manager import AssignmentManager
from src.models import Answer, Assignment


class AnswerInput(SQLModel):
    id_assignment: int
    id_question_question_id: int
    id_question_module_id: int
    id_option: int = None
    open_answer: str = None


class AnswerManager:
    @classmethod
    def get_answer(
        cls, id_assignment: int, id_module: int, id_question: int, session: Session
    ) -> Answer:
        answer: Answer = session.exec(
            select(Answer)
            .where(Answer.id_assignment == id_assignment)
            .where(Answer.id_question_question_id == id_question)
            .where(Answer.id_question_module_id == id_module)
        ).first()
        return answer

    @classmethod
    def save_answer(cls, answer: AnswerInput, session: Session):
        assignment: Assignment = AssignmentManager.get_assignment(
            answer.id_assignment, session=session
        )
        if not assignment:
            raise Exception("Assignment not found")
        if assignment.status == "completed":
            raise Exception("Assignment already completed")
        if assignment.status != "draft":
            AssignmentManager.update_status(assignment, "draft", session=session)
        answer = Answer(**answer.dict())
        session.add(answer)
        session.commit()
        session.refresh(answer)
        return answer

    @classmethod
    def get_punctuation_per_module(
        cls, id_assignment: int, id_module: int, session: Session
    ):
        answers = session.exec(
            select(Answer)
            .where(Answer.id_assignment == id_assignment)
            .where(Answer.id_question_module_id == id_module)
        ).all()
        punctuation = 0
        for answer in answers:
            if answer.id_option:
                punctuation += answer.option.score
        return punctuation
