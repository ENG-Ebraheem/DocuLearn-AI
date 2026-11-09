from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.domain.entities.course import Course
from app.domain.repositories.course_repository import (
    CourseRepository,
)
from app.infrastructure.database.models.course_model import (
    CourseModel,
)


class CourseRepositoryImpl(CourseRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, course: Course) -> Course:
        model = CourseModel(
            id=course.id,
            name=course.name,
            created_at=course.created_at,
            updated_at=course.updated_at,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(
        self, course_id: str
    ) -> Course | None:
        model = self.session.get(CourseModel, course_id)
        if model is None:
            return None
        return self._to_entity(model)

    def find_all(self) -> list[Course]:
        models = (
            self.session.query(CourseModel)
            .order_by(CourseModel.created_at.desc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    def update(self, course: Course) -> Course:
        model = self.session.get(CourseModel, course.id)
        if model is None:
            raise ValueError(
                f"Course {course.id} not found"
            )
        model.name = course.name
        model.updated_at = datetime.now(timezone.utc)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def delete(self, course_id: str) -> bool:
        model = self.session.get(CourseModel, course_id)
        if model is None:
            return False
        self.session.delete(model)
        self.session.commit()
        return True

    def _to_entity(
        self, model: CourseModel
    ) -> Course:
        return Course(
            id=model.id,
            name=model.name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
