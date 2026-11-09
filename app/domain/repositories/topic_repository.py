from abc import ABC, abstractmethod

from app.domain.entities.learning import Topic


class TopicRepository(ABC):

    @abstractmethod
    def save(
        self, topic: Topic
    ) -> Topic:
        pass

    @abstractmethod
    def save_many(
        self, topics: list[Topic]
    ) -> list[Topic]:
        pass

    @abstractmethod
    def find_by_document_id(
        self, document_id: str
    ) -> list[Topic]:
        pass

    @abstractmethod
    def delete_by_document_id(
        self, document_id: str
    ) -> bool:
        pass
