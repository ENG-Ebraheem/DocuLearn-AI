import pytest
from app.config.settings import Settings


class TestSettings:

    def test_default_values(self):
        s = Settings(
            _env_file=None,
        )
        assert s.app_name == "DocuLearn AI"
        assert s.environment == "development"
        assert s.embedding_model == "all-MiniLM-L6-v2"
        assert s.llm_provider == "gemini"
        assert s.llm_model == "gemini-3.5-flash"
        assert s.chunk_size == 1000
        assert s.chunk_overlap == 150
        assert isinstance(s.is_api_key_configured, bool)

    def test_chunk_overlap_validation_in_chunker(self):
        from app.services.text_processing.chunker import TextChunker

        with pytest.raises(ValueError):
            TextChunker(chunk_size=100, overlap=100)
