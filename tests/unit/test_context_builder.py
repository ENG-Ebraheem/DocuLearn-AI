import pytest
from app.application.services.rag.context_builder import (
    ContextBuilder,
)
from app.application.services.rag.retriever import (
    RetrievedChunk,
)


@pytest.fixture
def builder():
    return ContextBuilder(max_chunks=3)


class TestContextBuilder:

    def _make_chunks(self):
        return [
            RetrievedChunk(
                chunk_id="c1",
                document_id="d1",
                document_name="test.pdf",
                chunk_index=0,
                content="First chunk content.",
                score=0.9,
                metadata={},
            ),
            RetrievedChunk(
                chunk_id="c2",
                document_id="d1",
                document_name="test.pdf",
                chunk_index=1,
                content="Second chunk content.",
                score=0.8,
                metadata={},
            ),
        ]

    def test_build_context(self, builder):
        chunks = self._make_chunks()
        result = builder.build("test query", chunks)

        assert len(result.chunks) == 2
        assert "First chunk" in result.context_text
        assert "Second chunk" in result.context_text
        assert result.query == "test query"

    def test_deduplication(self, builder):
        chunks = [
            RetrievedChunk(
                chunk_id="c1",
                document_id="d1",
                document_name="test.pdf",
                chunk_index=0,
                content="Content.",
                score=0.9,
                metadata={},
            ),
            RetrievedChunk(
                chunk_id="c1",
                document_id="d1",
                document_name="test.pdf",
                chunk_index=0,
                content="Content.",
                score=0.8,
                metadata={},
            ),
        ]
        result = builder.build("query", chunks)
        assert len(result.chunks) == 1

    def test_max_chunks_limit(self, builder):
        chunks = [
            RetrievedChunk(
                chunk_id=f"c{i}",
                document_id="d1",
                document_name="test.pdf",
                chunk_index=i,
                content=f"Chunk {i}.",
                score=0.9 - i * 0.1,
                metadata={},
            )
            for i in range(5)
        ]
        result = builder.build("query", chunks)
        assert len(result.chunks) == 3

    def test_sources_built(self, builder):
        chunks = self._make_chunks()
        result = builder.build("query", chunks)
        assert len(result.sources) == 2
        assert (
            result.sources[0]["document_name"]
            == "test.pdf"
        )

    def test_empty_chunks(self, builder):
        result = builder.build("query", [])
        assert result.chunks == []
        assert result.context_text == ""
