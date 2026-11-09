from sqlalchemy.orm import Session

from app.domain.entities.learning import (
    LearningSummary,
)
from app.domain.repositories.learning_summary_repository import (
    LearningSummaryRepository,
)
from app.infrastructure.database.models.learning_models import (
    LearningSummaryModel,
)


class LearningSummaryRepositoryImpl(
    LearningSummaryRepository
):

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(
        self, summary: LearningSummary
    ) -> LearningSummary:
        model = LearningSummaryModel(
            id=summary.id,
            document_id=summary.document_id,
            title=summary.title,
            overview=summary.overview,
            created_at=summary.created_at,
            updated_at=summary.updated_at,
        )
        model.extra_metadata = {
            "sections": summary.sections,
            "key_takeaways": summary.key_takeaways,
            "sources": summary.sources,
            "summary_length": summary.summary_length,
        }
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_document_id(
        self, document_id: str
    ) -> LearningSummary | None:
        model = (
            self.session.query(LearningSummaryModel)
            .filter(
                LearningSummaryModel.document_id
                == document_id
            )
            .first()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def delete_by_document_id(
        self, document_id: str
    ) -> bool:
        count = (
            self.session.query(LearningSummaryModel)
            .filter(
                LearningSummaryModel.document_id
                == document_id
            )
            .delete()
        )
        self.session.commit()
        return count > 0

    def _to_entity(
        self, model: LearningSummaryModel
    ) -> LearningSummary:
        meta = model.extra_metadata
        return LearningSummary(
            id=model.id,
            document_id=model.document_id,
            title=model.title,
            overview=model.overview,
            sections=meta.get("sections", []),
            key_takeaways=meta.get(
                "key_takeaways", []
            ),
            sources=meta.get("sources", []),
            summary_length=meta.get(
                "summary_length", "medium"
            ),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def find_all(self) -> list[LearningSummary]:
        models = (
            self.session.query(
                LearningSummaryModel
            ).all()
        )
        return [self._to_entity(m) for m in models]
