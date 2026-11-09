from abc import ABC, abstractmethod

from app.domain.entities.chunk import Chunk


class VectorStoreRepository(ABC):

    @abstractmethod
    def add(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> list[str]:
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        document_id: str | None = None,
    ) -> list[tuple[Chunk, float]]:
        pass

    @abstractmethod
    def delete_by_document_id(self, document_id: str) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass
