from sqlalchemy.orm import Session

from app.domain.entities.conversation import Conversation
from app.domain.repositories.conversation_repository import (
    ConversationRepository,
)
from app.infrastructure.database.models.conversation_model import (
    ConversationModel,
)


class ConversationRepositoryImpl(ConversationRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(
        self, conversation: Conversation
    ) -> Conversation:
        model = ConversationModel(
            id=conversation.id,
            document_id=conversation.document_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )
        model.extra_metadata = conversation.metadata
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(
        self, conversation_id: str
    ) -> Conversation | None:
        model = self.session.get(
            ConversationModel, conversation_id
        )
        if model is None:
            return None
        return self._to_entity(model)

    def find_by_document_id(
        self, document_id: str
    ) -> list[Conversation]:
        models = (
            self.session.query(ConversationModel)
            .filter(
                ConversationModel.document_id
                == document_id
            )
            .order_by(ConversationModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_all(self) -> list[Conversation]:
        models = (
            self.session.query(ConversationModel)
            .order_by(ConversationModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def delete(self, conversation_id: str) -> bool:
        model = self.session.get(
            ConversationModel, conversation_id
        )
        if model is None:
            return False

        self.session.delete(model)
        self.session.commit()
        return True

    def _to_entity(
        self, model: ConversationModel
    ) -> Conversation:
        return Conversation(
            id=model.id,
            document_id=model.document_id,
            title=model.title,
            metadata=model.extra_metadata,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
