from unittest.mock import MagicMock
import pytest

from app.application.services.rag.lexical_retriever import LexicalRetriever
from app.domain.entities.chunk import Chunk


class TestLexicalRetriever:

    def test_lexical_retrieval_ranks_matching_chunk(self):
        mock_repo = MagicMock()
        chunk1 = Chunk(
            id="c1",
            document_id="doc1",
            chunk_index=0,
            content="الذكاء الاصطناعي هو مجال في علم الحاسوب.",
            metadata={"document_name": "AI.pdf"},
        )
        chunk2 = Chunk(
            id="c2",
            document_id="doc1",
            chunk_index=1,
            content="الفيزياء هي علم دراسة المادة والطاقة.",
            metadata={"document_name": "AI.pdf"},
        )
        mock_repo.find_by_document_id.return_value = [chunk1, chunk2]

        retriever = LexicalRetriever(chunk_repo=mock_repo)
        results = retriever.retrieve(query="الذكاء الاصطناعي", document_id="doc1")

        assert len(results) >= 1
        assert results[0].chunk_id == "c1"

    def test_document_isolation(self):
        mock_repo = MagicMock()
        chunk_a = Chunk(
            id="ca",
            document_id="doc_a",
            chunk_index=0,
            content="محتوى كيمياء غير عضوي",
            metadata={"document_name": "Chem.pdf"},
        )
        mock_repo.find_by_document_id.side_effect = lambda doc_id: [chunk_a] if doc_id == "doc_a" else []

        retriever = LexicalRetriever(chunk_repo=mock_repo)
        results = retriever.retrieve(query="كيمياء", document_id="doc_b")

        assert results == []
