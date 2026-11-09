from abc import ABC, abstractmethod

from app.domain.entities.learning import (
    Flashcard,
    FlashcardReview,
)


class FlashcardRepository(ABC):

    @abstractmethod
    def save(
        self, flashcard: Flashcard
    ) -> Flashcard:
        pass

    @abstractmethod
    def save_many(
        self, flashcards: list[Flashcard]
    ) -> list[Flashcard]:
        pass

    @abstractmethod
    def find_by_document_id(
        self, document_id: str
    ) -> list[Flashcard]:
        pass

    @abstractmethod
    def delete_by_document_id(
        self, document_id: str
    ) -> bool:
        pass

    @abstractmethod
    def save_review(
        self, review: FlashcardReview
    ) -> FlashcardReview:
        pass

    @abstractmethod
    def find_reviews_by_flashcard_id(
        self, flashcard_id: str
    ) -> list[FlashcardReview]:
        pass

    @abstractmethod
    def find_all(
        self,
    ) -> list[Flashcard]:
        pass

    @abstractmethod
    def count_by_document_id(
        self, document_id: str
    ) -> int:
        pass

    @abstractmethod
    def find_all_reviews(
        self,
    ) -> list[FlashcardReview]:
        pass

    @abstractmethod
    def find_reviews_by_flashcard_ids(
        self, flashcard_ids: list[str]
    ) -> list[FlashcardReview]:
        pass
