from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.entities.learning import (
    Quiz,
    QuizQuestion,
    QuizSession,
    QuizAnswer,
)
from app.domain.repositories.quiz_repository import (
    QuizRepository,
)
from app.infrastructure.database.models.learning_models import (
    QuizModel,
    QuizQuestionModel,
    QuizSessionModel,
    QuizAnswerModel,
)


class QuizRepositoryImpl(QuizRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def save_quiz(self, quiz: Quiz) -> Quiz:
        model = QuizModel(
            id=quiz.id,
            document_id=quiz.document_id,
            title=quiz.title,
            description=quiz.description,
            created_at=quiz.created_at,
        )
        model.extra_metadata = {
            "difficulty": quiz.difficulty,
            "question_types": quiz.question_types,
            "number_of_questions": quiz.number_of_questions,
        }
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._quiz_to_entity(model)

    def find_quiz_by_id(
        self, quiz_id: str
    ) -> Quiz | None:
        model = self.session.get(QuizModel, quiz_id)
        if model is None:
            return None
        return self._quiz_to_entity(model)

    def find_quizzes_by_document_id(
        self, document_id: str
    ) -> list[Quiz]:
        models = (
            self.session.query(QuizModel)
            .filter(QuizModel.document_id == document_id)
            .order_by(QuizModel.created_at.desc())
            .all()
        )
        return [self._quiz_to_entity(m) for m in models]

    def delete_quizzes_by_document_id(
        self, document_id: str
    ) -> bool:
        quizzes = (
            self.session.query(QuizModel)
            .filter(QuizModel.document_id == document_id)
            .all()
        )
        quiz_ids = [q.id for q in quizzes]

        for qid in quiz_ids:
            session_ids = [
                s.id
                for s in self.session.query(
                    QuizSessionModel.id
                )
                .filter(QuizSessionModel.quiz_id == qid)
                .all()
            ]

            if session_ids:
                self.session.query(
                    QuizAnswerModel
                ).filter(
                    QuizAnswerModel.session_id.in_(
                        session_ids
                    )
                ).delete(synchronize_session="fetch")

            self.session.query(QuizSessionModel).filter(
                QuizSessionModel.quiz_id == qid
            ).delete()

            self.session.query(
                QuizQuestionModel
            ).filter(
                QuizQuestionModel.quiz_id == qid
            ).delete()

        count = self.session.query(QuizModel).filter(
            QuizModel.document_id == document_id
        ).delete()

        self.session.commit()
        return count > 0

    def save_question(
        self, question: QuizQuestion
    ) -> QuizQuestion:
        model = QuizQuestionModel(
            id=question.id,
            quiz_id=question.quiz_id,
            question_text=question.question,
            question_type=question.question_type,
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            order_index=question.order_index,
        )
        model.extra_metadata = {
            "options": question.options,
            "difficulty": question.difficulty,
            "topic": question.topic,
            "sources": question.sources,
        }
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._question_to_entity(model)

    def save_questions(
        self, questions: list[QuizQuestion]
    ) -> list[QuizQuestion]:
        models = []
        for q in questions:
            model = QuizQuestionModel(
                id=q.id,
                quiz_id=q.quiz_id,
                question_text=q.question,
                question_type=q.question_type,
                correct_answer=q.correct_answer,
                explanation=q.explanation,
                order_index=q.order_index,
            )
            model.extra_metadata = {
                "options": q.options,
                "difficulty": q.difficulty,
                "topic": q.topic,
                "sources": q.sources,
            }
            self.session.add(model)
            models.append(model)

        self.session.commit()
        for m in models:
            self.session.refresh(m)

        return [
            self._question_to_entity(m)
            for m in models
        ]

    def find_questions_by_quiz_id(
        self, quiz_id: str
    ) -> list[QuizQuestion]:
        models = (
            self.session.query(QuizQuestionModel)
            .filter(QuizQuestionModel.quiz_id == quiz_id)
            .order_by(QuizQuestionModel.order_index)
            .all()
        )
        return [
            self._question_to_entity(m) for m in models
        ]

    def save_session(
        self, session_obj: QuizSession
    ) -> QuizSession:
        existing = self.session.get(
            QuizSessionModel, session_obj.id
        )

        if existing:
            existing.quiz_id = session_obj.quiz_id
            existing.started_at = session_obj.started_at
            existing.completed_at = session_obj.completed_at
            existing.status = session_obj.status
            existing.score = session_obj.score
            existing.percentage = session_obj.percentage
            self.session.commit()
            self.session.refresh(existing)
            return self._session_to_entity(existing)

        model = QuizSessionModel(
            id=session_obj.id,
            quiz_id=session_obj.quiz_id,
            started_at=session_obj.started_at,
            completed_at=session_obj.completed_at,
            status=session_obj.status,
            score=session_obj.score,
            percentage=session_obj.percentage,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._session_to_entity(model)

    def find_session_by_id(
        self, session_id: str
    ) -> QuizSession | None:
        model = self.session.get(
            QuizSessionModel, session_id
        )
        if model is None:
            return None
        return self._session_to_entity(model)

    def save_answer(
        self, answer: QuizAnswer
    ) -> QuizAnswer:
        model = QuizAnswerModel(
            id=answer.id,
            session_id=answer.session_id,
            quiz_question_id=answer.quiz_question_id,
            user_answer=answer.user_answer,
            is_correct=answer.is_correct,
            answered_at=answer.answered_at,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._answer_to_entity(model)

    def save_answers(
        self, answers: list[QuizAnswer]
    ) -> list[QuizAnswer]:
        models = []
        for a in answers:
            model = QuizAnswerModel(
                id=a.id,
                session_id=a.session_id,
                quiz_question_id=a.quiz_question_id,
                user_answer=a.user_answer,
                is_correct=a.is_correct,
                answered_at=a.answered_at,
            )
            self.session.add(model)
            models.append(model)

        self.session.commit()
        for m in models:
            self.session.refresh(m)

        return [
            self._answer_to_entity(m) for m in models
        ]

    def find_answers_by_session_id(
        self, session_id: str
    ) -> list[QuizAnswer]:
        models = (
            self.session.query(QuizAnswerModel)
            .filter(
                QuizAnswerModel.session_id == session_id
            )
            .all()
        )
        return [
            self._answer_to_entity(m) for m in models
        ]

    def delete_sessions_by_quiz_id(
        self, quiz_id: str
    ) -> bool:
        session_ids = [
            s.id
            for s in self.session.query(
                QuizSessionModel.id
            )
            .filter(QuizSessionModel.quiz_id == quiz_id)
            .all()
        ]

        if session_ids:
            self.session.query(QuizAnswerModel).filter(
                QuizAnswerModel.session_id.in_(
                    session_ids
                )
            ).delete(synchronize_session="fetch")

        count = self.session.query(
            QuizSessionModel
        ).filter(
            QuizSessionModel.quiz_id == quiz_id
        ).delete()

        self.session.commit()
        return count > 0

    def _quiz_to_entity(
        self, model: QuizModel
    ) -> Quiz:
        meta = model.extra_metadata
        return Quiz(
            id=model.id,
            document_id=model.document_id,
            title=model.title,
            description=model.description,
            difficulty=meta.get("difficulty", "MEDIUM"),
            question_types=meta.get(
                "question_types", []
            ),
            number_of_questions=meta.get(
                "number_of_questions", 5
            ),
            created_at=model.created_at,
        )

    def _question_to_entity(
        self, model: QuizQuestionModel
    ) -> QuizQuestion:
        meta = model.extra_metadata
        return QuizQuestion(
            id=model.id,
            quiz_id=model.quiz_id,
            question=model.question_text,
            question_type=model.question_type,
            options=meta.get("options", []),
            correct_answer=model.correct_answer,
            explanation=model.explanation,
            difficulty=meta.get("difficulty", "MEDIUM"),
            topic=meta.get("topic", ""),
            sources=meta.get("sources", []),
            order_index=model.order_index,
        )

    def _session_to_entity(
        self, model: QuizSessionModel
    ) -> QuizSession:
        return QuizSession(
            id=model.id,
            quiz_id=model.quiz_id,
            started_at=model.started_at,
            completed_at=model.completed_at,
            status=model.status,
            score=model.score,
            percentage=model.percentage,
        )

    def _answer_to_entity(
        self, model: QuizAnswerModel
    ) -> QuizAnswer:
        return QuizAnswer(
            id=model.id,
            session_id=model.session_id,
            quiz_question_id=model.quiz_question_id,
            user_answer=model.user_answer,
            is_correct=model.is_correct,
            answered_at=model.answered_at,
        )

    def find_all_sessions(self) -> list[QuizSession]:
        models = (
            self.session.query(QuizSessionModel).all()
        )
        return [
            self._session_to_entity(m) for m in models
        ]

    def find_completed_sessions(
        self,
    ) -> list[QuizSession]:
        models = (
            self.session.query(QuizSessionModel)
            .filter(
                QuizSessionModel.status == "completed"
            )
            .all()
        )
        return [
            self._session_to_entity(m) for m in models
        ]

    def find_all_answers(self) -> list[QuizAnswer]:
        models = (
            self.session.query(QuizAnswerModel).all()
        )
        return [
            self._answer_to_entity(m) for m in models
        ]
