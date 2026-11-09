from abc import ABC, abstractmethod

from app.domain.entities.learning import Question


class QuestionRepository(ABC):

    @abstractmethod
    def save(
        self, question: Question
    ) -> Question:
        pass

    @abstractmethod
    def save_many(
        self, questions: list[Question]
    ) -> list[Question]:
        pass

    @abstractmethod
    def find_by_document_id(
        self, document_id: str
    ) -> list[Question]:
        pass

    @abstractmethod
    def delete_by_document_id(
        self, document_id: str
    ) -> bool:
        pass

    @abstractmethod
    def find_all(
        self,
    ) -> list[Question]:
        pass
