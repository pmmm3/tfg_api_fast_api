from pydantic import EmailStr
from sqlmodel import Session, SQLModel
from src.models import Assignment, Questionnaire, Patient, Doctor, TypeCondition


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

    @classmethod
    def get_assignment_analytics(cls, assignment, session):
        resume = []
        for module in assignment.questionnaire.modules:
            from src.classes.answer_manager import AnswerManager

            diagnostic = []
            observations = []
            punctuation = AnswerManager.get_punctuation_per_module(
                assignment.id, module.id, session=session
            )
            # Get diagnostic
            if module.outputs:
                module_outputs = []
                for output in module.outputs:
                    if get_operation(
                        output.condition_type,
                        output.condition_value,
                        punctuation,
                    ):
                        module_outputs.append(output.text)
                diagnostic.append(module_outputs)
            total_diagnostic = {"punctuation": punctuation, "diagnostic": diagnostic}
            # Get observations
            for question in module.questions:
                if question.outputs:
                    answer = AnswerManager.get_answer(
                        assignment.id, module.id, question.id, session=session
                    )
                    if answer:
                        for output in question.outputs:
                            if get_operation(
                                output.condition_type,
                                output.condition_value,
                                answer.option.score,
                            ):
                                observations.append(output.text)

            resume.append(
                {
                    "module": module.title,
                    "diagnostic": total_diagnostic,
                    "observations": observations,
                }
            )
        return resume


def get_operation(type: TypeCondition, expected_value: int, actual_value: int) -> bool:
    if type == TypeCondition.GREATER:
        return actual_value > expected_value
    elif type == TypeCondition.GREATER_EQUAL:
        return actual_value >= expected_value
    elif type == TypeCondition.LESS:
        return actual_value < expected_value
    elif type == TypeCondition.LESS_EQUAL:
        return actual_value <= expected_value
    elif type == TypeCondition.EQUAL:
        return actual_value == expected_value
    elif type == TypeCondition.NOT_EQUAL:
        return actual_value != expected_value
    else:
        raise Exception("Invalid type")
