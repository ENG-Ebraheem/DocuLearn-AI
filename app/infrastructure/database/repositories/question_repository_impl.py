from sqlalchemy.orm import Session

from app.domain.entities.learning import Question
from app.domain.repositories.question_repository import (
    QuestionRepository,
)
from app.infrastructure.database.models.learning_models import (
    QuestionModel,
)


class QuestionRepositoryImpl(QuestionRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(
        self, question: Question
    ) -> Question:
        model = QuestionModel(
            id=question.id,
            document_id=question.document_id,
            question_text=question.question,
            answer=question.answer,
            difficulty=question.difficulty,
            question_type=question.question_type,
            created_at=question.created_at,
        )
        model.extra_metadata = {
            "topic": question.topic,
            "sources": question.sources,
        }
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def save_many(
        self, questions: list[Question]
    ) -> list[Question]:
        models = []
        for q in questions:
            model = QuestionModel(
                id=q.id,
                document_id=q.document_id,
                question_text=q.question,
                answer=q.answer,
                difficulty=q.difficulty,
                question_type=q.question_type,
                created_at=q.created_at,
            )
            model.extra_metadata = {
                "topic": q.topic,
                "sources": q.sources,
            }
            self.session.add(model)
            models.append(model)

        self.session.commit()
        for m in models:
            self.session.refresh(m)

        return [self._to_entity(m) for m in models]

    def find_by_document_id(
        self, document_id: str
    ) -> list[Question]:
        models = (
            self.session.query(QuestionModel)
            .filter(
                QuestionModel.document_id
                == document_id
            )
            .all()
        )
        return [self._to_entity(m) for m in models]

    def delete_by_document_id(
        self, document_id: str
    ) -> bool:
        count = (
            self.session.query(QuestionModel)
            .filter(
                QuestionModel.document_id
                == document_id
            )
            .delete()
        )
        self.session.commit()
        return count > 0

    def _to_entity(
        self, model: QuestionModel
    ) -> Question:
        meta = model.extra_metadata
        return Question(
            id=model.id,
            document_id=model.document_id,
            question=model.question_text,
            answer=model.answer,
            difficulty=model.difficulty,
            question_type=model.question_type,
            topic=meta.get("topic", ""),
            sources=meta.get("sources", []),
            created_at=model.created_at,
        )

    def find_all(self) -> list[Question]:
        models = (
            self.session.query(QuestionModel).all()
        )
        return [self._to_entity(m) for m in models]
