from abc import ABC, abstractmethod

from app.domain.entities.chat_message import ChatMessage


class ChatMessageRepository(ABC):

    @abstractmethod
    def save(self, message: ChatMessage) -> ChatMessage:
        pass

    @abstractmethod
    def find_by_conversation_id(
        self, conversation_id: str
    ) -> list[ChatMessage]:
        pass

    @abstractmethod
    def delete_by_conversation_id(
        self, conversation_id: str
    ) -> bool:
        pass
