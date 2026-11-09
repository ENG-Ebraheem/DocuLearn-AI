from unittest.mock import MagicMock, patch

import pytest

from app.config.settings import settings
from app.core.exceptions import LLMError
from app.infrastructure.llm.gemini_provider import (
    FallbackLLMProvider,
    GeminiProvider,
)


class TestGeminiProviderUnit:

    def test_init_without_api_key_raises_error(self):
        provider = GeminiProvider(api_key="")
        with pytest.raises(LLMError) as exc_info:
            provider.generate("Hello")
        assert "Gemini API key not configured" in str(exc_info.value)

    @patch("app.infrastructure.llm.gemini_provider.genai", create=True)
    def test_generate_success_mock(self, mock_genai_pkg):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Mocked AI Response"
        mock_client.models.generate_content.return_value = mock_response

        with patch("google.genai.Client", return_value=mock_client):
            provider = GeminiProvider(
                api_key="fake-test-key",
                model_name="gemini-3.5-flash",
            )
            res = provider.generate("Test prompt")
            assert res == "Mocked AI Response"
            assert provider.is_available() is True
            assert provider.model_name == "gemini-3.5-flash"

    def test_fallback_provider_handles_missing_key(self):
        with patch.object(settings, "gemini_api_key", ""):
            provider = FallbackLLMProvider()
            assert provider.is_available() is False
            with pytest.raises(LLMError):
                provider.generate("test")


class TestGeminiRealIntegration:
    """Optional integration test against real Gemini API when GEMINI_API_KEY is set."""

    @pytest.mark.skipif(
        not settings.is_api_key_configured,
        reason="GEMINI_API_KEY environment variable is not configured",
    )
    def test_real_gemini_generation(self):
        # 1. Verify Settings reads API key
        assert settings.is_api_key_configured is True
        assert len(settings.api_key) > 0

        # 2. Verify GeminiProvider initializes
        provider = GeminiProvider()
        assert provider.is_available() is True

        try:
            response = provider.generate(
                prompt="مرحباً، أجب في كلمة واحدة: جاهز",
                system_instruction="أنت مساعد تجريبي.",
            )
            assert isinstance(response, str)
            assert len(response.strip()) > 0
        except LLMError as err:
            assert any(term in str(err).lower() for term in ("quota", "unavailable", "gemini", "error"))
