from abc import ABC, abstractmethod

from app.domain.entities.learning import KeyConcept


class KeyConceptRepository(ABC):

    @abstractmethod
    def save(
        self, concept: KeyConcept
    ) -> KeyConcept:
        pass

    @abstractmethod
    def save_many(
        self, concepts: list[KeyConcept]
    ) -> list[KeyConcept]:
        pass

    @abstractmethod
    def find_by_document_id(
        self, document_id: str
    ) -> list[KeyConcept]:
        pass

    @abstractmethod
    def delete_by_document_id(
        self, document_id: str
    ) -> bool:
        pass

    @abstractmethod
    def find_all(
        self,
    ) -> list[KeyConcept]:
        pass
