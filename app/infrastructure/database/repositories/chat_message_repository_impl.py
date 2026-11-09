from sqlalchemy.orm import Session

from app.domain.entities.chat_message import ChatMessage
from app.domain.repositories.chat_message_repository import (
    ChatMessageRepository,
)
from app.infrastructure.database.models.chat_message_model import (
    ChatMessageModel,
)


class ChatMessageRepositoryImpl(ChatMessageRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(
        self, message: ChatMessage
    ) -> ChatMessage:
        model = ChatMessageModel(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )
        model.sources = message.sources
        model.extra_metadata = message.metadata
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_conversation_id(
        self, conversation_id: str
    ) -> list[ChatMessage]:
        models = (
            self.session.query(ChatMessageModel)
            .filter(
                ChatMessageModel.conversation_id
                == conversation_id
            )
            .order_by(ChatMessageModel.created_at)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def delete_by_conversation_id(
        self, conversation_id: str
    ) -> bool:
        count = (
            self.session.query(ChatMessageModel)
            .filter(
                ChatMessageModel.conversation_id
                == conversation_id
            )
            .delete()
        )
        self.session.commit()
        return count > 0

    def _to_entity(
        self, model: ChatMessageModel
    ) -> ChatMessage:
        return ChatMessage(
            id=model.id,
            conversation_id=model.conversation_id,
            role=model.role,
            content=model.content,
            sources=model.sources,
            metadata=model.extra_metadata,
            created_at=model.created_at,
        )
