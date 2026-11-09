from unittest.mock import MagicMock
import pytest

from app.application.services.rag.answer_response import AnswerResponse, Source
from app.application.services.rag.qa_service import QAService
from app.presentation.navigation.router import get_back_label


class TestPhase8QualityEngineering:

    def test_document_chat_vs_general_ai_isolation(self):
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = []
        mock_llm = MagicMock()
        mock_llm.is_available.return_value = True
        mock_llm.model_name = "gemini-3.5-flash"
        mock_llm.generate.return_value = "الإجابة العامة المعرفة"

        qa_service = QAService(
            retriever=mock_retriever,
            llm_provider=mock_llm,
            min_context_score=0.5,
        )

        # 1. Document question with low context returns refusal
        doc_response = qa_service.ask(query="سؤال غير معروف", document_id="doc1")
        assert doc_response.has_sufficient_context is False
        assert doc_response.confidence == 0.0
        assert "لا توجد معلومات كافية" in doc_response.answer

        # 2. General AI chat returns ungrounded general answer
        gen_response = qa_service.general_chat(query="ما هي عاصمة فرنسا؟")
        assert gen_response.has_sufficient_context is False
        assert gen_response.answer == "الإجابة العامة المعرفة"
        assert gen_response.sources == []

    def test_source_attribution_preserves_metadata(self):
        chunk_mock = MagicMock()
        chunk_mock.chunk_id = "c1"
        chunk_mock.document_id = "doc123"
        chunk_mock.document_name = "AI_Basics.pdf"
        chunk_mock.metadata = {"page": 12}
        chunk_mock.score = 0.85
        chunk_mock.content = "محتوى الذكاء الاصطناعي في الصفحة 12."

        sources = QAService._build_sources(None, [chunk_mock])
        assert len(sources) == 1
        assert sources[0].document_id == "doc123"
        assert sources[0].document_name == "AI_Basics.pdf"
        assert sources[0].page == 12
        assert sources[0].score == 0.85

    def test_navigation_context_labels(self):
        label_default = get_back_label()
        assert "العودة إلى" in label_default
