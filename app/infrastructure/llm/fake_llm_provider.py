from app.domain.repositories.llm_provider import LLMProvider


class FakeLLMProvider(LLMProvider):

    def __init__(
        self, response: str = "Fake response"
    ) -> None:
        self._response = response
        self._call_count = 0

    def generate(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.3,
    ) -> str:
        self._call_count += 1
        return self._response

    def is_available(self) -> bool:
        return True

    @property
    def model_name(self) -> str:
        return "fake-llm"

    @property
    def call_count(self) -> int:
        return self._call_count
