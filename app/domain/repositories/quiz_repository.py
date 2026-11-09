from abc import ABC, abstractmethod

from app.domain.entities.learning import (
    Quiz,
    QuizQuestion,
    QuizSession,
    QuizAnswer,
)


class QuizRepository(ABC):

    @abstractmethod
    def save_quiz(
        self, quiz: Quiz
    ) -> Quiz:
        pass

    @abstractmethod
    def find_quiz_by_id(
        self, quiz_id: str
    ) -> Quiz | None:
        pass

    @abstractmethod
    def find_quizzes_by_document_id(
        self, document_id: str
    ) -> list[Quiz]:
        pass

    @abstractmethod
    def delete_quizzes_by_document_id(
        self, document_id: str
    ) -> bool:
        pass

    @abstractmethod
    def save_question(
        self, question: QuizQuestion
    ) -> QuizQuestion:
        pass

    @abstractmethod
    def save_questions(
        self, questions: list[QuizQuestion]
    ) -> list[QuizQuestion]:
        pass

    @abstractmethod
    def find_questions_by_quiz_id(
        self, quiz_id: str
    ) -> list[QuizQuestion]:
        pass

    @abstractmethod
    def save_session(
        self, session: QuizSession
    ) -> QuizSession:
        pass

    @abstractmethod
    def find_session_by_id(
        self, session_id: str
    ) -> QuizSession | None:
        pass

    @abstractmethod
    def save_answer(
        self, answer: QuizAnswer
    ) -> QuizAnswer:
        pass

    @abstractmethod
    def save_answers(
        self, answers: list[QuizAnswer]
    ) -> list[QuizAnswer]:
        pass

    @abstractmethod
    def find_answers_by_session_id(
        self, session_id: str
    ) -> list[QuizAnswer]:
        pass

    @abstractmethod
    def delete_sessions_by_quiz_id(
        self, quiz_id: str
    ) -> bool:
        pass

    @abstractmethod
    def find_all_sessions(
        self,
    ) -> list[QuizSession]:
        pass

    @abstractmethod
    def find_completed_sessions(
        self,
    ) -> list[QuizSession]:
        pass

    @abstractmethod
    def find_all_answers(
        self,
    ) -> list[QuizAnswer]:
        pass
