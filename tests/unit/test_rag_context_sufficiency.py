from unittest.mock import MagicMock

from app.application.services.rag.qa_service import QAService
from app.application.services.rag.retriever import RetrievedChunk
from app.infrastructure.llm.fake_llm_provider import FakeLLMProvider


def test_weak_document_context_uses_fallback_without_calling_llm():
    """Weak semantic matches must not produce an invented document-grounded answer."""
    retriever = MagicMock()
    retriever.retrieve.return_value = [
        RetrievedChunk(
            chunk_id="weak-chunk",
            document_id="document-a",
            document_name="A.pdf",
            chunk_index=0,
            content="Unrelated content",
            score=0.05,
            metadata={"page": 1},
        )
    ]
    provider = FakeLLMProvider(response="This must not be returned")
    service = QAService(
        retriever=retriever,
        llm_provider=provider,
        min_context_score=0.50,
    )

    response = service.ask("A question outside the document", document_id="document-a")

    assert response.has_sufficient_context is False
    assert response.sources == []
    assert "لا توجد معلومات كافية" in response.answer
    assert provider.call_count == 0
    retriever.retrieve.assert_called_once_with(
        query="A question outside the document", document_id="document-a"
    )


def test_relevant_document_context_calls_llm_and_keeps_document_source():
    retriever = MagicMock()
    retriever.retrieve.return_value = [
        RetrievedChunk(
            chunk_id="relevant-chunk",
            document_id="document-a",
            document_name="A.pdf",
            chunk_index=0,
            content="Relevant content about the requested concept",
            score=0.89,
            metadata={"page": 4},
        )
    ]
    provider = FakeLLMProvider(response="Grounded answer")
    service = QAService(
        retriever=retriever,
        llm_provider=provider,
        min_context_score=0.50,
    )

    response = service.ask("Explain the concept", document_id="document-a")

    assert response.has_sufficient_context is True
    assert response.answer == "Grounded answer"
    assert response.sources[0].document_id == "document-a"
    assert response.sources[0].page == 4
    assert provider.call_count == 1
