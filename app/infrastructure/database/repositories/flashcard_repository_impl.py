from sqlalchemy.orm import Session

from app.domain.entities.learning import (
    Flashcard,
    FlashcardReview,
)
from app.domain.repositories.flashcard_repository import (
    FlashcardRepository,
)
from app.infrastructure.database.models.learning_models import (
    FlashcardModel,
    FlashcardReviewModel,
)


class FlashcardRepositoryImpl(FlashcardRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(
        self, flashcard: Flashcard
    ) -> Flashcard:
        model = FlashcardModel(
            id=flashcard.id,
            document_id=flashcard.document_id,
            front=flashcard.front,
            back=flashcard.back,
            created_at=flashcard.created_at,
        )
        model.extra_metadata = {
            "topic": flashcard.topic,
            "sources": flashcard.sources,
        }
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def save_many(
        self, flashcards: list
    ) -> list:
        models = []
        for fc in flashcards:
            model = FlashcardModel(
                id=fc.id,
                document_id=fc.document_id,
                front=fc.front,
                back=fc.back,
                created_at=fc.created_at,
            )
            model.extra_metadata = {
                "topic": fc.topic,
                "sources": fc.sources,
            }
            self.session.add(model)
            models.append(model)

        self.session.commit()
        for m in models:
            self.session.refresh(m)

        return [self._to_entity(m) for m in models]

    def find_by_document_id(
        self, document_id: str
    ) -> list:
        models = (
            self.session.query(FlashcardModel)
            .filter(
                FlashcardModel.document_id
                == document_id
            )
            .all()
        )
        return [self._to_entity(m) for m in models]

    def delete_by_document_id(
        self, document_id: str
    ) -> bool:
        cards = (
            self.session.query(FlashcardModel)
            .filter(
                FlashcardModel.document_id
                == document_id
            )
            .all()
        )
        card_ids = [c.id for c in cards]

        if card_ids:
            self.session.query(
                FlashcardReviewModel
            ).filter(
                FlashcardReviewModel.flashcard_id.in_(
                    card_ids
                )
            ).delete(synchronize_session="fetch")

        count = self.session.query(
            FlashcardModel
        ).filter(
            FlashcardModel.document_id == document_id
        ).delete()

        self.session.commit()
        return count > 0

    def save_review(
        self, review: FlashcardReview
    ) -> FlashcardReview:
        model = FlashcardReviewModel(
            id=review.id,
            flashcard_id=review.flashcard_id,
            rating=review.rating,
            reviewed_at=review.reviewed_at,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return FlashcardReview(
            id=model.id,
            flashcard_id=model.flashcard_id,
            rating=model.rating,
            reviewed_at=model.reviewed_at,
        )

    def find_reviews_by_flashcard_id(
        self, flashcard_id: str
    ) -> list:
        models = (
            self.session.query(FlashcardReviewModel)
            .filter(
                FlashcardReviewModel.flashcard_id
                == flashcard_id
            )
            .all()
        )
        return [
            FlashcardReview(
                id=m.id,
                flashcard_id=m.flashcard_id,
                rating=m.rating,
                reviewed_at=m.reviewed_at,
            )
            for m in models
        ]

    def _to_entity(self, model) -> Flashcard:
        meta = model.extra_metadata
        return Flashcard(
            id=model.id,
            document_id=model.document_id,
            front=model.front,
            back=model.back,
            topic=meta.get("topic", ""),
            sources=meta.get("sources", []),
            created_at=model.created_at,
        )

    def find_all(self) -> list[Flashcard]:
        models = (
            self.session.query(FlashcardModel).all()
        )
        return [self._to_entity(m) for m in models]

    def count_by_document_id(
        self, document_id: str
    ) -> int:
        return (
            self.session.query(FlashcardModel)
            .filter(
                FlashcardModel.document_id
                == document_id
            )
            .count()
        )

    def find_all_reviews(
        self,
    ) -> list[FlashcardReview]:
        models = (
            self.session.query(
                FlashcardReviewModel
            ).all()
        )
        return [
            FlashcardReview(
                id=m.id,
                flashcard_id=m.flashcard_id,
                rating=m.rating,
                reviewed_at=m.reviewed_at,
            )
            for m in models
        ]

    def find_reviews_by_flashcard_ids(
        self, flashcard_ids: list[str]
    ) -> list[FlashcardReview]:
        if not flashcard_ids:
            return []
        models = (
            self.session.query(FlashcardReviewModel)
            .filter(
                FlashcardReviewModel.flashcard_id.in_(
                    flashcard_ids
                )
            )
            .all()
        )
        return [
            FlashcardReview(
                id=m.id,
                flashcard_id=m.flashcard_id,
                rating=m.rating,
                reviewed_at=m.reviewed_at,
            )
            for m in models
        ]