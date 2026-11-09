from abc import ABC, abstractmethod

from app.domain.entities.course import Course


class CourseRepository(ABC):

    @abstractmethod
    def save(self, course: Course) -> Course:
        pass

    @abstractmethod
    def find_by_id(self, course_id: str) -> Course | None:
        pass

    @abstractmethod
    def find_all(self) -> list[Course]:
        pass

    @abstractmethod
    def delete(self, course_id: str) -> bool:
        pass

    @abstractmethod
    def update(self, course: Course) -> Course:
        pass
