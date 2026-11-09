import pytest
import tempfile

from app.infrastructure.embeddings.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from app.infrastructure.vector_store.faiss_vector_store import (
    FAISSVectorStore,
)
from app.domain.entities.chunk import Chunk


class TestFAISSDocumentFilter:

    @pytest.fixture
    def store(self):
        provider = SentenceTransformerEmbeddingProvider()
        with tempfile.TemporaryDirectory() as tmpdir:
            store = FAISSVectorStore(
                dimension=provider.dimension,
                store_path=tmpdir,
            )
            yield store, provider

    def test_search_with_document_id_filter(
        self, store
    ):
        store_obj, provider = store

        chunks = [
            Chunk(
                id="c1",
                document_id="d1",
                content="Object oriented programming",
                chunk_index=0,
                metadata={
                    "document_name": "a.pdf",
                    "document_id": "d1",
                },
            ),
            Chunk(
                id="c2",
                document_id="d2",
                content="SQL databases",
                chunk_index=0,
                metadata={
                    "document_name": "b.pdf",
                    "document_id": "d2",
                },
            ),
        ]
        embeddings = provider.embed_documents(
            [c.content for c in chunks]
        )
        store_obj.add(chunks, embeddings)

        query = provider.embed_text(
            "programming"
        )
        results = store_obj.search(
            query, top_k=10, document_id="d1"
        )

        assert len(results) == 1
        assert results[0][0].document_id == "d1"

    def test_search_no_filter_returns_all(
        self, store
    ):
        store_obj, provider = store

        chunks = [
            Chunk(
                id="c1",
                document_id="d1",
                content="A",
                chunk_index=0,
                metadata={
                    "document_name": "a.pdf",
                    "document_id": "d1",
                },
            ),
            Chunk(
                id="c2",
                document_id="d2",
                content="B",
                chunk_index=0,
                metadata={
                    "document_name": "b.pdf",
                    "document_id": "d2",
                },
            ),
        ]
        embeddings = provider.embed_documents(
            [c.content for c in chunks]
        )
        store_obj.add(chunks, embeddings)

        results = store_obj.search(
            provider.embed_text("test"),
            top_k=10,
        )
        assert len(results) == 2

    def test_search_filter_nonexistent_doc(
        self, store
    ):
        store_obj, provider = store

        chunks = [
            Chunk(
                id="c1",
                document_id="d1",
                content="A",
                chunk_index=0,
                metadata={
                    "document_name": "a.pdf",
                    "document_id": "d1",
                },
            ),
        ]
        embeddings = provider.embed_documents(
            [c.content for c in chunks]
        )
        store_obj.add(chunks, embeddings)

        results = store_obj.search(
            provider.embed_text("test"),
            top_k=10,
            document_id="nonexistent",
        )
        assert len(results) == 0
