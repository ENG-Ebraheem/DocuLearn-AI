import pytest
import tempfile

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
def setup():
    provider = SentenceTransformerEmbeddingProvider()
    with tempfile.TemporaryDirectory() as tmpdir:
        store = FAISSVectorStore(
            dimension=provider.dimension,
            store_path=tmpdir,
        )

        chunks = [
            Chunk(
                id="c1",
                document_id="d1",
                content="Object oriented programming uses classes and objects.",
                chunk_index=0,
                metadata={
                    "document_name": "oop.pdf",
                    "document_id": "d1",
                    "page": 3,
                },
            ),
            Chunk(
                id="c2",
                document_id="d2",
                content="SQL databases store structured data.",
                chunk_index=0,
                metadata={
                    "document_name": "db.pdf",
                    "document_id": "d2",
                    "page": 1,
                },
            ),
        ]
        embeddings = provider.embed_documents(
            [c.content for c in chunks]
        )
        store.add(chunks, embeddings)

        retriever = Retriever(
            embedding_provider=provider,
            vector_store=store,
            top_k=5,
        )

        yield retriever


class TestRetrieverDocumentFilter:

    def test_retrieve_without_filter(
        self, setup
    ):
        results = setup.retrieve("programming")
        assert len(results) == 2

    def test_retrieve_with_document_filter(
        self, setup
    ):
        results = setup.retrieve(
            "programming", document_id="d1"
        )
        assert len(results) == 1
        assert results[0].document_id == "d1"

    def test_retrieve_filter_wrong_doc(
        self, setup
    ):
        results = setup.retrieve(
            "programming", document_id="d2"
        )
        assert len(results) == 1
        assert results[0].document_id == "d2"

    def test_retrieve_metadata_has_page(
        self, setup
    ):
        results = setup.retrieve(
            "programming", document_id="d1"
        )
        assert results[0].metadata.get("page") == 3
