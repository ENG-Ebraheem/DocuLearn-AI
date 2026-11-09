from abc import ABC, abstractmethod

from app.domain.entities.conversation import Conversation


class ConversationRepository(ABC):

    @abstractmethod
    def save(self, conversation: Conversation) -> Conversation:
        pass

    @abstractmethod
    def find_by_id(self, conversation_id: str) -> Conversation | None:
        pass

    @abstractmethod
    def find_by_document_id(self, document_id: str) -> list[Conversation]:
        pass

    @abstractmethod
    def find_all(self) -> list[Conversation]:
        pass

    @abstractmethod
    def delete(self, conversation_id: str) -> bool:
        pass
