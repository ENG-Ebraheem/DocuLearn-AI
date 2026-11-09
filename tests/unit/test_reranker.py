from app.application.services.rag.reranker import (
    PassThroughReranker,
)
from app.application.services.rag.retriever import (
    RetrievedChunk,
)


class TestPassThroughReranker:

    def test_rerank_preserves_order(self):
        reranker = PassThroughReranker()
        chunks = [
            RetrievedChunk(
                chunk_id="c1",
                document_id="d1",
                document_name="test.pdf",
                chunk_index=0,
                content="First",
                score=0.9,
                metadata={},
            ),
            RetrievedChunk(
                chunk_id="c2",
                document_id="d1",
                document_name="test.pdf",
                chunk_index=1,
                content="Second",
                score=0.8,
                metadata={},
            ),
        ]

        result = reranker.rerank("query", chunks)
        assert len(result) == 2
        assert result[0].chunk_id == "c1"
        assert result[1].chunk_id == "c2"

    def test_rerank_empty(self):
        reranker = PassThroughReranker()
        result = reranker.rerank("query", [])
        assert result == []
