from unittest.mock import MagicMock
import pytest

from app.config.settings import settings
from app.application.services.platform_service import PlatformService


class TestPhase7ProductionHardening:

    def test_settings_startup_validation(self):
        assert settings.validate_startup() is True
        assert settings.max_upload_size_bytes == settings.max_upload_size_mb * 1024 * 1024

    def test_upload_oversized_file_rejected(self):
        service = PlatformService(
            session=MagicMock(),
            doc_repo=MagicMock(),
            chunk_repo=MagicMock(),
            course_repo=MagicMock(),
            summary_repo=MagicMock(),
            concept_repo=MagicMock(),
            question_repo=MagicMock(),
            quiz_repo=MagicMock(),
            flashcard_repo=MagicMock(),
            topic_repo=MagicMock(),
            conv_repo=MagicMock(),
            msg_repo=MagicMock(),
            vector_store=MagicMock(),
            embedding_provider=MagicMock(),
            llm_provider=MagicMock(),
        )
        huge_content = b"a" * (settings.max_upload_size_bytes + 10)
        with pytest.raises(ValueError, match="حجم الملف يتجاوز الحد المسموح به"):
            service.ingest_uploaded_document("big.pdf", huge_content)

    def test_upload_unsupported_extension_rejected(self):
        service = PlatformService(
            session=MagicMock(),
            doc_repo=MagicMock(),
            chunk_repo=MagicMock(),
            course_repo=MagicMock(),
            summary_repo=MagicMock(),
            concept_repo=MagicMock(),
            question_repo=MagicMock(),
            quiz_repo=MagicMock(),
            flashcard_repo=MagicMock(),
            topic_repo=MagicMock(),
            conv_repo=MagicMock(),
            msg_repo=MagicMock(),
            vector_store=MagicMock(),
            embedding_provider=MagicMock(),
            llm_provider=MagicMock(),
        )
        with pytest.raises(ValueError, match="نوع الملف غير مدعوم"):
            service.ingest_uploaded_document("test.exe", b"binary content")

    def test_health_check_returns_valid_structure(self):
        mock_doc_repo = MagicMock()
        mock_doc_repo.find_all.return_value = []
        service = PlatformService(
            session=MagicMock(),
            doc_repo=mock_doc_repo,
            chunk_repo=MagicMock(),
            course_repo=MagicMock(),
            summary_repo=MagicMock(),
            concept_repo=MagicMock(),
            question_repo=MagicMock(),
            quiz_repo=MagicMock(),
            flashcard_repo=MagicMock(),
            topic_repo=MagicMock(),
            conv_repo=MagicMock(),
            msg_repo=MagicMock(),
            vector_store=MagicMock(),
            embedding_provider=MagicMock(),
            llm_provider=MagicMock(),
        )
        health = service.health_check()
        assert health["status"] == "healthy"
        assert health["database"] is True
        assert health["vector_store"] is True
        assert health["embedding_provider"] is True
