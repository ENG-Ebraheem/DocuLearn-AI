from abc import ABC, abstractmethod

from app.domain.entities.document import Document


class DocumentRepository(ABC):

    @abstractmethod
    def save(self, document: Document) -> Document:
        pass

    @abstractmethod
    def find_by_id(self, document_id: str) -> Document | None:
        pass

    @abstractmethod
    def find_all(self) -> list[Document]:
        pass

    @abstractmethod
    def find_by_course_id(
        self, course_id: str
    ) -> list[Document]:
        pass

    @abstractmethod
    def delete(self, document_id: str) -> bool:
        pass

    @abstractmethod
    def update(self, document: Document) -> Document:
        pass
