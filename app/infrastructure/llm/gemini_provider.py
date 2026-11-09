import logging

from app.config.settings import settings
from app.core.exceptions import LLMError
from app.domain.repositories.llm_provider import (
    LLMProvider,
)


logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
    ) -> None:
        self._api_key = api_key
        self._model_name = model_name or settings.llm_model
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client

        api_key = (
            self._api_key
            if self._api_key is not None
            else settings.api_key
        )
        if not api_key:
            raise LLMError(
                "Gemini API key not configured. "
                "Set GEMINI_API_KEY in .env"
            )

        try:
            from google import genai

            self._client = genai.Client(api_key=api_key)
            return self._client

        except ImportError:
            raise LLMError(
                "google-genai not installed. "
                "Run: pip install google-genai"
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize Gemini client: {e}"
            )
            raise LLMError(
                "Failed to initialize Gemini service"
            ) from e

    def generate(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.3,
    ) -> str:
        client = self._get_client()

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=temperature,
            )
            if system_instruction:
                config.system_instruction = system_instruction

            response = client.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config=config,
            )

            if not response or not response.text:
                raise LLMError("Received empty response from Gemini API")

            return response.text

        except LLMError:
            raise
        except Exception as e:
            err_msg = str(e)
            logger.error(f"Gemini generation failed: {err_msg}")

            if (
                "401" in err_msg
                or "UNAUTHENTICATED" in err_msg
                or "API key not valid" in err_msg
            ):
                raise LLMError(
                    "Gemini authentication error: Invalid API Key"
                ) from e
            elif "404" in err_msg or "NOT_FOUND" in err_msg:
                raise LLMError(
                    f"Gemini model '{self._model_name}' not found or unsupported"
                ) from e
            elif "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                raise LLMError(
                    "Gemini API quota exceeded or rate limit reached"
                ) from e

            raise LLMError(
                "Gemini service is currently unavailable. Please try again later."
            ) from e

    def is_available(self) -> bool:
        key = (
            self._api_key
            if self._api_key is not None
            else settings.api_key
        )
        return bool(key)

    @property
    def model_name(self) -> str:
        return self._model_name


class FallbackLLMProvider(LLMProvider):

    def __init__(self) -> None:
        self._provider = None
        self._init_provider()

    def _init_provider(self) -> None:
        provider_name = settings.llm_provider.lower()

        if provider_name == "gemini":
            try:
                self._provider = GeminiProvider()
            except Exception as e:
                logger.warning(f"Gemini init failed: {e}")
                self._provider = None
        else:
            logger.warning(
                f"Unknown LLM provider: {provider_name}"
            )

    def generate(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.3,
    ) -> str:
        if self._provider is None or not self._provider.is_available():
            raise LLMError(
                "No LLM provider available. "
                "Configure GEMINI_API_KEY in .env"
            )

        return self._provider.generate(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
        )

    def is_available(self) -> bool:
        return (
            self._provider is not None
            and self._provider.is_available()
        )

    @property
    def model_name(self) -> str:
        if self._provider is None:
            return "none"
        return self._provider.model_name
