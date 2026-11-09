import pytest
import tempfile
from pathlib import Path

from app.infrastructure.vector_store.faiss_vector_store import (
    FAISSVectorStore,
)
from app.domain.entities.chunk import Chunk


@pytest.fixture
def store_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def vector_store(store_path):
    return FAISSVectorStore(
        dimension=4, store_path=str(store_path)
    )


class TestFAISSVectorStore:

    def test_add_and_count(self, vector_store):
        chunks = [
            Chunk(
                id="c1",
                document_id="d1",
                content="Hello",
                chunk_index=0,
                metadata={"document_name": "test.pdf"},
            )
        ]
        embeddings = [[0.1, 0.2, 0.3, 0.4]]

        ids = vector_store.add(chunks, embeddings)
        assert len(ids) == 1
        assert vector_store.count() == 1

    def test_search(self, vector_store):
        chunks = [
            Chunk(
                id="c1",
                document_id="d1",
                content="Hello world",
                chunk_index=0,
                metadata={"document_name": "test.pdf"},
            ),
            Chunk(
                id="c2",
                document_id="d1",
                content="Goodbye world",
                chunk_index=1,
                metadata={"document_name": "test.pdf"},
            ),
        ]
        embeddings = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
        ]

        vector_store.add(chunks, embeddings)

        results = vector_store.search(
            query_embedding=[1.0, 0.0, 0.0, 0.0],
            top_k=1,
        )

        assert len(results) == 1
        assert results[0][0].id == "c1"
        assert results[0][1] > 0.9

    def test_delete_by_document_id(self, vector_store):
        chunks = [
            Chunk(
                id="c1",
                document_id="d1",
                content="A",
                chunk_index=0,
                metadata={},
            ),
            Chunk(
                id="c2",
                document_id="d2",
                content="B",
                chunk_index=0,
                metadata={},
            ),
        ]
        embeddings = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
        ]

        vector_store.add(chunks, embeddings)
        assert vector_store.count() == 2

        deleted = vector_store.delete_by_document_id(
            "d1"
        )
        assert deleted is True
        assert vector_store.count() == 1

    def test_persistence(self, store_path):
        chunks = [
            Chunk(
                id="c1",
                document_id="d1",
                content="Hello",
                chunk_index=0,
                metadata={},
            )
        ]
        embeddings = [[1.0, 0.0, 0.0, 0.0]]

        store1 = FAISSVectorStore(
            dimension=4, store_path=str(store_path)
        )
        store1.add(chunks, embeddings)
        store1.save()

        store2 = FAISSVectorStore(
            dimension=4, store_path=str(store_path)
        )
        assert store2.count() == 1

        results = store2.search(
            query_embedding=[1.0, 0.0, 0.0, 0.0],
            top_k=1,
        )
        assert len(results) == 1
        assert results[0][0].id == "c1"

    def test_mismatched_chunks_embeddings_raises(
        self, vector_store
    ):
        from app.core.exceptions import VectorStoreError

        chunks = [
            Chunk(
                id="c1",
                document_id="d1",
                content="A",
                chunk_index=0,
                metadata={},
            )
        ]
        embeddings = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
        ]

        with pytest.raises(VectorStoreError):
            vector_store.add(chunks, embeddings)
