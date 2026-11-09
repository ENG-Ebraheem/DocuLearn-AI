from unittest.mock import MagicMock
import pytest

from app.application.services.rag.hybrid_retriever import HybridRetriever
from app.application.services.rag.retriever import RetrievedChunk, Retriever


class TestHybridRetriever:

    def test_weighted_fusion(self):
        mock_dense = MagicMock()
        mock_lexical = MagicMock()

        chunk1 = RetrievedChunk(
            chunk_id="c1",
            document_id="d1",
            document_name="A.pdf",
            chunk_index=0,
            content="AI content",
            score=0.9,
        )
        chunk2 = RetrievedChunk(
            chunk_id="c2",
            document_id="d1",
            document_name="A.pdf",
            chunk_index=1,
            content="ML content",
            score=0.8,
        )

        mock_dense.retrieve.return_value = [chunk1]
        mock_dense.top_k = 5
        mock_lexical.retrieve.return_value = [chunk1, chunk2]

        hybrid = HybridRetriever(
            dense_retriever=mock_dense,
            lexical_retriever=mock_lexical,
            fusion_method="weighted",
        )
        results = hybrid.retrieve(query="AI", document_id="d1")

        assert len(results) == 2
        assert results[0].chunk_id == "c1"

    def test_rrf_fusion(self):
        mock_dense = MagicMock()
        mock_lexical = MagicMock()

        chunk1 = RetrievedChunk(
            chunk_id="c1",
            document_id="d1",
            document_name="A.pdf",
            chunk_index=0,
            content="RRF candidate 1",
            score=0.95,
        )
        mock_dense.retrieve.return_value = [chunk1]
        mock_dense.top_k = 5
        mock_lexical.retrieve.return_value = [chunk1]

        hybrid = HybridRetriever(
            dense_retriever=mock_dense,
            lexical_retriever=mock_lexical,
            fusion_method="rrf",
        )
        results = hybrid.retrieve(query="candidate", document_id="d1")

        assert len(results) == 1
        assert results[0].chunk_id == "c1"
