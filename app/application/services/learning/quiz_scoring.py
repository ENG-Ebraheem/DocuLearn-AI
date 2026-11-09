from datetime import datetime, timezone

from app.domain.entities.learning import (
    QuizSession,
    QuizAnswer,
    QuizQuestion,
)
from app.domain.repositories.quiz_repository import (
    QuizRepository,
)


class QuizScoringService:

    def __init__(
        self, quiz_repo: QuizRepository
    ) -> None:
        self.quiz_repo = quiz_repo

    def submit_session(
        self,
        session_id: str,
        answers: list[dict],
    ) -> QuizSession:
        session = self.quiz_repo.find_session_by_id(
            session_id
        )
        if session is None:
            raise ValueError(
                f"Session {session_id} not found"
            )

        questions = (
            self.quiz_repo.find_questions_by_quiz_id(
                session.quiz_id
            )
        )

        q_map = {
            q.id: q for q in questions
        }

        saved_answers = []
        correct_count = 0

        for ans_data in answers:
            qid = ans_data.get(
                "quiz_question_id", ""
            )
            user_answer = ans_data.get(
                "user_answer", ""
            )

            question = q_map.get(qid)
            is_correct = False

            if question:
                is_correct = (
                    user_answer.strip().lower()
                    == question.correct_answer.strip().lower()
                )

            if is_correct:
                correct_count += 1

            saved_answers.append(
                QuizAnswer(
                    session_id=session_id,
                    quiz_question_id=qid,
                    user_answer=user_answer,
                    is_correct=is_correct,
                )
            )

        if saved_answers:
            self.quiz_repo.save_answers(saved_answers)

        total = len(questions)
        percentage = (
            (correct_count / total * 100)
            if total > 0
            else 0.0
        )

        session.score = correct_count
        session.percentage = percentage
        session.status = "completed"
        session.completed_at = datetime.now(
            timezone.utc
        )

        return self.quiz_repo.save_session(session)

    def get_results(
        self, session_id: str
    ) -> dict:
        session = self.quiz_repo.find_session_by_id(
            session_id
        )
        if session is None:
            return {}

        answers = (
            self.quiz_repo.find_answers_by_session_id(
                session_id
            )
        )

        questions = (
            self.quiz_repo.find_questions_by_quiz_id(
                session.quiz_id
            )
        )

        q_map = {q.id: q for q in questions}

        detailed = []
        for ans in answers:
            q = q_map.get(
                ans.quiz_question_id
            )
            detailed.append(
                {
                    "question": q.question
                    if q
                    else "",
                    "user_answer": ans.user_answer,
                    "correct_answer": q.correct_answer
                    if q
                    else "",
                    "is_correct": ans.is_correct,
                    "explanation": q.explanation
                    if q
                    else "",
                    "options": q.options if q else [],
                    "sources": q.sources if q else [],
                }
            )

        return {
            "session_id": session.id,
            "score": session.score,
            "total": len(questions),
            "percentage": session.percentage,
            "status": session.status,
            "answers": detailed,
        }
