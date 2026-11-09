import pytest
import tempfile
from pathlib import Path

from app.infrastructure.embeddings.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from app.infrastructure.vector_store.faiss_vector_store import (
    FAISSVectorStore,
)
from app.application.services.rag.retriever import (
    Retriever,
)
from app.domain.entities.chunk import Chunk


@pytest.fixture
def retriever():
    provider = SentenceTransformerEmbeddingProvider()

    with tempfile.TemporaryDirectory() as tmpdir:
        store = FAISSVectorStore(
            dimension=provider.dimension,
            store_path=tmpdir,
        )
        yield Retriever(
            embedding_provider=provider,
            vector_store=store,
            top_k=3,
        )


class TestRetriever:

    def _index_chunks(self, retriever):
        chunks = [
            Chunk(
                id="c1",
                document_id="d1",
                content="Object oriented programming uses classes and objects.",
                chunk_index=0,
                metadata={
                    "document_name": "oop.pdf",
                    "document_id": "d1",
                },
            ),
            Chunk(
                id="c2",
                document_id="d1",
                content="SQL databases store structured data in tables.",
                chunk_index=1,
                metadata={
                    "document_name": "databases.pdf",
                    "document_id": "d1",
                },
            ),
            Chunk(
                id="c3",
                document_id="d1",
                content="HTML structures web pages with tags.",
                chunk_index=2,
                metadata={
                    "document_name": "web.pdf",
                    "document_id": "d1",
                },
            ),
        ]

        texts = [c.content for c in chunks]
        embeddings = (
            retriever.embedding_provider.embed_documents(
                texts
            )
        )
        retriever.vector_store.add(chunks, embeddings)

    def test_retrieve_relevant(self, retriever):
        self._index_chunks(retriever)

        results = retriever.retrieve(
            "What is object oriented programming?"
        )

        assert len(results) > 0
        assert (
            results[0].content
            == "Object oriented programming uses classes and objects."
        )

    def test_retrieve_empty_query_raises(
        self, retriever
    ):
        from app.core.exceptions import RetrievalError

        with pytest.raises(RetrievalError):
            retriever.retrieve("")

    def test_retrieve_returns_metadata(self, retriever):
        self._index_chunks(retriever)

        results = retriever.retrieve(
            "object oriented programming"
        )

        assert results[0].document_name == "oop.pdf"
        assert results[0].chunk_index == 0
        assert results[0].score > 0
