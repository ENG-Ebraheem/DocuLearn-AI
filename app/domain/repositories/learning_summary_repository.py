from abc import ABC, abstractmethod

from app.domain.entities.learning import (
    LearningSummary,
)


class LearningSummaryRepository(ABC):

    @abstractmethod
    def save(
        self, summary: LearningSummary
    ) -> LearningSummary:
        pass

    @abstractmethod
    def find_by_document_id(
        self, document_id: str
    ) -> LearningSummary | None:
        pass

    @abstractmethod
    def delete_by_document_id(
        self, document_id: str
    ) -> bool:
        pass

    @abstractmethod
    def find_all(
        self,
    ) -> list[LearningSummary]:
        pass
