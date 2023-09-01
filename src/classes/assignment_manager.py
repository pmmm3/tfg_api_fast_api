from pydantic import EmailStr
from sqlmodel import Session, SQLModel


from src.models import Assignment, Questionnaire, Patient, Doctor


class AssignmentInput(SQLModel):
    questionnaire_id: int
    patient_id: EmailStr
    doctor_id: EmailStr


class AssignmentManager:
    @classmethod
    def create_assignment(
        cls,
        questionnaire: Questionnaire,
        patient: Patient,
        doctor: Doctor,
        session: Session,
    ) -> Assignment:
        assignment = Assignment(
            questionnaire=questionnaire, patient=patient, doctor=doctor
        )
        session.add(assignment)
        session.commit()
        session.refresh(assignment)
        return assignment

    @classmethod
    def get_status(cls, assignment: Assignment) -> str:
        return assignment.status

    @classmethod
    def get_assignment(cls, id_assignment: int, session: Session) -> Assignment:
        return session.get(Assignment, id_assignment)

    @classmethod
    def update_status(
        cls, assignment: Assignment, status: str, session: Session
    ) -> Assignment:
        assignment.status = status
        session.add(assignment)
        session.commit()
        session.refresh(assignment)
        return assignment

    @classmethod
    def finish_assignment(cls, assignment: Assignment, session: Session) -> Assignment:
        # Check if all modules are finished
        from src.classes.answer_manager import AnswerManager

        questions_answered = []
        for answer in assignment.answers:
            answer_bd = AnswerManager.get_answer(
                answer.id_assignment,
                answer.id_question_module_id,
                answer.id_question_question_id,
                session=session,
            )
            if answer_bd:
                questions_answered.append(answer_bd.id_question_question_id)

        for module in assignment.questionnaire.modules:
            all_questions_per_module = [questions.id for questions in module.questions]

            if not all(
                questions in questions_answered
                for questions in all_questions_per_module
            ):
                raise Exception("Not all questions are answered")

        assignment.status = "finished"
        session.add(assignment)
        session.commit()
        session.refresh(assignment)
        return assignment
