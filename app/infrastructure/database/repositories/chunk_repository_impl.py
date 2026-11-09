from sqlalchemy.orm import Session

from app.domain.entities.chunk import Chunk
from app.domain.repositories.chunk_repository import (
    ChunkRepository,
)
from app.infrastructure.database.models.chunk_model import (
    ChunkModel,
)


class ChunkRepositoryImpl(ChunkRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, chunk: Chunk) -> Chunk:
        model = ChunkModel(
            id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            created_at=chunk.created_at,
        )
        model.extra_metadata = chunk.metadata
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def save_many(
        self, chunks: list[Chunk]
    ) -> list[Chunk]:
        models = []
        for chunk in chunks:
            model = ChunkModel(
                id=chunk.id,
                document_id=chunk.document_id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                created_at=chunk.created_at,
            )
            model.extra_metadata = chunk.metadata
            self.session.add(model)
            models.append(model)

        self.session.commit()

        for model in models:
            self.session.refresh(model)

        return [self._to_entity(m) for m in models]

    def find_by_id(
        self, chunk_id: str
    ) -> Chunk | None:
        model = self.session.get(ChunkModel, chunk_id)
        if model is None:
            return None
        return self._to_entity(model)

    def find_by_document_id(
        self, document_id: str
    ) -> list[Chunk]:
        models = (
            self.session.query(ChunkModel)
            .filter(
                ChunkModel.document_id == document_id
            )
            .order_by(ChunkModel.chunk_index)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def delete_by_document_id(
        self, document_id: str
    ) -> bool:
        count = (
            self.session.query(ChunkModel)
            .filter(
                ChunkModel.document_id == document_id
            )
            .delete()
        )
        self.session.commit()
        return count > 0

    def _to_entity(self, model: ChunkModel) -> Chunk:
        return Chunk(
            id=model.id,
            document_id=model.document_id,
            content=model.content,
            chunk_index=model.chunk_index,
            metadata=model.extra_metadata,
            created_at=model.created_at,
        )
