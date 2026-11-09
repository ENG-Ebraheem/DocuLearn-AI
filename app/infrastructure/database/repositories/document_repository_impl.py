from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.entities.document import Document
from app.domain.repositories.document_repository import (
    DocumentRepository,
)
from app.infrastructure.database.models.document_model import (
    DocumentModel,
)


class DocumentRepositoryImpl(DocumentRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, document: Document) -> Document:
        model = DocumentModel(
            id=document.id,
            name=document.name,
            file_type=document.file_type,
            file_path=document.file_path,
            pages=document.pages,
            size=document.size,
            status=document.status,
            course_id=document.course_id,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
        model.extra_metadata = document.metadata
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(
        self, document_id: str
    ) -> Document | None:
        model = self.session.get(
            DocumentModel, document_id
        )
        if model is None:
            return None
        return self._to_entity(model)

    def find_all(self) -> list[Document]:
        models = (
            self.session.query(DocumentModel)
            .order_by(DocumentModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_course_id(
        self, course_id: str
    ) -> list[Document]:
        models = (
            self.session.query(DocumentModel)
            .filter(DocumentModel.course_id == course_id)
            .order_by(DocumentModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def update(self, document: Document) -> Document:
        model = self.session.get(
            DocumentModel, document.id
        )
        if model is None:
            raise ValueError(
                f"Document {document.id} not found"
            )

        model.name = document.name
        model.file_type = document.file_type
        model.file_path = document.file_path
        model.pages = document.pages
        model.size = document.size
        model.status = document.status
        model.course_id = document.course_id
        model.extra_metadata = document.metadata
        model.updated_at = datetime.now(timezone.utc)

        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def delete(self, document_id: str) -> bool:
        model = self.session.get(
            DocumentModel, document_id
        )
        if model is None:
            return False

        self.session.delete(model)
        self.session.commit()
        return True

    def _to_entity(
        self, model: DocumentModel
    ) -> Document:
        return Document(
            id=model.id,
            name=model.name,
            file_type=model.file_type,
            file_path=model.file_path,
            pages=model.pages,
            size=model.size,
            status=model.status,
            course_id=model.course_id,
            metadata=model.extra_metadata,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
