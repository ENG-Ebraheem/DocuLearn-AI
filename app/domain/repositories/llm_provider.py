from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.3,
    ) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass
