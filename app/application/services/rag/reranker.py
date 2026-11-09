from abc import ABC, abstractmethod

from app.application.services.rag.retriever import (
    RetrievedChunk,
)


class Reranker(ABC):

    @abstractmethod
    def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        pass


class PassThroughReranker(Reranker):

    def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        return candidates
