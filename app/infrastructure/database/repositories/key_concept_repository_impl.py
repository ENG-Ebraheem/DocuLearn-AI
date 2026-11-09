from sqlalchemy.orm import Session

from app.domain.entities.learning import KeyConcept
from app.domain.repositories.key_concept_repository import (
    KeyConceptRepository,
)
from app.infrastructure.database.models.learning_models import (
    KeyConceptModel,
)


class KeyConceptRepositoryImpl(KeyConceptRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(
        self, concept: KeyConcept
    ) -> KeyConcept:
        model = KeyConceptModel(
            id=concept.id,
            document_id=concept.document_id,
            term=concept.term,
            definition=concept.definition,
            created_at=concept.created_at,
        )
        model.extra_metadata = {
            "explanation": concept.explanation,
            "importance": concept.importance,
            "topic": concept.topic,
            "sources": concept.sources,
        }
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def save_many(
        self, concepts: list[KeyConcept]
    ) -> list[KeyConcept]:
        models = []
        for concept in concepts:
            model = KeyConceptModel(
                id=concept.id,
                document_id=concept.document_id,
                term=concept.term,
                definition=concept.definition,
                created_at=concept.created_at,
            )
            model.extra_metadata = {
                "explanation": concept.explanation,
                "importance": concept.importance,
                "topic": concept.topic,
                "sources": concept.sources,
            }
            self.session.add(model)
            models.append(model)

        self.session.commit()
        for m in models:
            self.session.refresh(m)

        return [self._to_entity(m) for m in models]

    def find_by_document_id(
        self, document_id: str
    ) -> list[KeyConcept]:
        models = (
            self.session.query(KeyConceptModel)
            .filter(
                KeyConceptModel.document_id
                == document_id
            )
            .all()
        )
        return [self._to_entity(m) for m in models]

    def delete_by_document_id(
        self, document_id: str
    ) -> bool:
        count = (
            self.session.query(KeyConceptModel)
            .filter(
                KeyConceptModel.document_id
                == document_id
            )
            .delete()
        )
        self.session.commit()
        return count > 0

    def _to_entity(
        self, model: KeyConceptModel
    ) -> KeyConcept:
        meta = model.extra_metadata
        return KeyConcept(
            id=model.id,
            document_id=model.document_id,
            term=model.term,
            definition=model.definition,
            explanation=meta.get("explanation", ""),
            importance=meta.get("importance", ""),
            topic=meta.get("topic", ""),
            sources=meta.get("sources", []),
            created_at=model.created_at,
        )

    def find_all(self) -> list[KeyConcept]:
        models = (
            self.session.query(KeyConceptModel).all()
        )
        return [self._to_entity(m) for m in models]
