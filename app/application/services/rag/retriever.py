from dataclasses import dataclass, field

from app.config.settings import settings
from app.domain.repositories.embedding_provider import (
    EmbeddingProvider,
)
from app.domain.repositories.vector_store_repository import (
    VectorStoreRepository,
)
from app.core.exceptions import RetrievalError


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    document_name: str
    chunk_index: int
    content: str
    score: float
    metadata: dict = field(default_factory=dict)


class Retriever:

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStoreRepository,
        top_k: int | None = None,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.top_k = top_k or settings.top_k

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        document_id: str | None = None,
    ) -> list[RetrievedChunk]:
        if not query.strip():
            raise RetrievalError(
                "Query cannot be empty"
            )

        k = top_k or self.top_k

        try:
            query_embedding = (
                self.embedding_provider.embed_text(query)
            )
        except Exception as e:
            raise RetrievalError(
                f"Failed to embed query: {e}"
            ) from e

        try:
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=k,
                document_id=document_id,
            )
        except Exception as e:
            raise RetrievalError(
                f"Vector search failed: {e}"
            ) from e

        retrieved = []

        for chunk, score in results:
            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    document_name=chunk.metadata.get(
                        "document_name", ""
                    ),
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    score=score,
                    metadata=chunk.metadata,
                )
            )

        return retrieved
