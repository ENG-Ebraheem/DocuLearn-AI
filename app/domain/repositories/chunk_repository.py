from abc import ABC, abstractmethod

from app.domain.entities.chunk import Chunk


class ChunkRepository(ABC):

    @abstractmethod
    def save(self, chunk: Chunk) -> Chunk:
        pass

    @abstractmethod
    def save_many(self, chunks: list[Chunk]) -> list[Chunk]:
        pass

    @abstractmethod
    def find_by_id(self, chunk_id: str) -> Chunk | None:
        pass

    @abstractmethod
    def find_by_document_id(self, document_id: str) -> list[Chunk]:
        pass

    @abstractmethod
    def delete_by_document_id(self, document_id: str) -> bool:
        pass
