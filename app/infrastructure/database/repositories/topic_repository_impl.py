from sqlalchemy.orm import Session

from app.domain.entities.learning import Topic
from app.domain.repositories.topic_repository import (
    TopicRepository,
)
from app.infrastructure.database.models.learning_models import (
    TopicModel,
)


class TopicRepositoryImpl(TopicRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, topic: Topic) -> Topic:
        model = TopicModel(
            id=topic.id,
            document_id=topic.document_id,
            name=topic.name,
            description=topic.description,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return Topic(
            id=model.id,
            document_id=model.document_id,
            name=model.name,
            description=model.description,
        )

    def save_many(
        self, topics: list
    ) -> list:
        models = []
        for t in topics:
            model = TopicModel(
                id=t.id,
                document_id=t.document_id,
                name=t.name,
                description=t.description,
            )
            self.session.add(model)
            models.append(model)

        self.session.commit()
        for m in models:
            self.session.refresh(m)

        return [
            Topic(
                id=m.id,
                document_id=m.document_id,
                name=m.name,
                description=m.description,
            )
            for m in models
        ]

    def find_by_document_id(
        self, document_id: str
    ) -> list:
        models = (
            self.session.query(TopicModel)
            .filter(
                TopicModel.document_id == document_id
            )
            .all()
        )
        return [
            Topic(
                id=m.id,
                document_id=m.document_id,
                name=m.name,
                description=m.description,
            )
            for m in models
        ]

    def delete_by_document_id(
        self, document_id: str
    ) -> bool:
        count = self.session.query(TopicModel).filter(
            TopicModel.document_id == document_id
        ).delete()
        self.session.commit()
        return count > 0
