import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.database import Base
from app.infrastructure.database.repositories.course_repository_impl import (
    CourseRepositoryImpl,
)
from app.infrastructure.database.repositories.document_repository_impl import (
    DocumentRepositoryImpl,
)
from app.domain.entities.course import Course
from app.domain.entities.document import Document


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestCourseEntity:

    def test_create_course_defaults(self):
        c = Course(name="AI 101")
        assert c.name == "AI 101"
        assert len(c.id) == 32
        assert c.created_at is not None
        assert c.updated_at is not None

    def test_course_id_unique(self):
        c1 = Course(name="A")
        c2 = Course(name="B")
        assert c1.id != c2.id


class TestCourseRepositoryImpl:

    def test_save_and_find(self, db_session):
        repo = CourseRepositoryImpl(db_session)
        c = Course(name="Machine Learning")
        saved = repo.save(c)
        assert saved.name == "Machine Learning"

        found = repo.find_by_id(c.id)
        assert found is not None
        assert found.name == "Machine Learning"

    def test_find_nonexistent(self, db_session):
        repo = CourseRepositoryImpl(db_session)
        assert repo.find_by_id("nope") is None

    def test_find_all(self, db_session):
        repo = CourseRepositoryImpl(db_session)
        repo.save(Course(name="A"))
        repo.save(Course(name="B"))
        all_courses = repo.find_all()
        assert len(all_courses) == 2

    def test_find_all_ordered_desc(self, db_session):
        import time
        repo = CourseRepositoryImpl(db_session)
        repo.save(Course(name="First"))
        time.sleep(0.01)
        repo.save(Course(name="Second"))
        all_courses = repo.find_all()
        assert all_courses[0].name == "Second"
        assert all_courses[1].name == "First"

    def test_update(self, db_session):
        repo = CourseRepositoryImpl(db_session)
        c = repo.save(Course(name="Old Name"))
        c.name = "New Name"
        updated = repo.update(c)
        assert updated.name == "New Name"

        found = repo.find_by_id(c.id)
        assert found.name == "New Name"

    def test_update_nonexistent_raises(self, db_session):
        repo = CourseRepositoryImpl(db_session)
        with pytest.raises(ValueError, match="not found"):
            repo.update(Course(id="bad", name="X"))

    def test_delete(self, db_session):
        repo = CourseRepositoryImpl(db_session)
        c = repo.save(Course(name="To Delete"))
        assert repo.delete(c.id) is True
        assert repo.find_by_id(c.id) is None

    def test_delete_nonexistent(self, db_session):
        repo = CourseRepositoryImpl(db_session)
        assert repo.delete("nope") is False


class TestDocumentCourseId:

    def test_save_document_with_course_id(self, db_session):
        doc_repo = DocumentRepositoryImpl(db_session)
        doc = Document(
            name="lecture1.pdf",
            file_type="pdf",
            course_id="course_1",
        )
        saved = doc_repo.save(doc)
        assert saved.course_id == "course_1"

    def test_find_by_course_id(self, db_session):
        doc_repo = DocumentRepositoryImpl(db_session)
        doc_repo.save(
            Document(
                name="a.pdf",
                file_type="pdf",
                course_id="c1",
            )
        )
        doc_repo.save(
            Document(
                name="b.pdf",
                file_type="pdf",
                course_id="c1",
            )
        )
        doc_repo.save(
            Document(
                name="c.pdf",
                file_type="pdf",
                course_id="c2",
            )
        )

        c1_docs = doc_repo.find_by_course_id("c1")
        assert len(c1_docs) == 2
        assert all(d.course_id == "c1" for d in c1_docs)

        c2_docs = doc_repo.find_by_course_id("c2")
        assert len(c2_docs) == 1

    def test_find_by_course_id_empty(self, db_session):
        doc_repo = DocumentRepositoryImpl(db_session)
        assert doc_repo.find_by_course_id("none") == []

    def test_update_document_course_id(self, db_session):
        doc_repo = DocumentRepositoryImpl(db_session)
        doc = doc_repo.save(
            Document(
                name="move.pdf",
                file_type="pdf",
                course_id=None,
            )
        )
        assert doc.course_id is None

        doc.course_id = "target_course"
        updated = doc_repo.update(doc)
        assert updated.course_id == "target_course"

    def test_document_default_no_course(self, db_session):
        doc_repo = DocumentRepositoryImpl(db_session)
        doc = doc_repo.save(
            Document(name="solo.pdf", file_type="pdf")
        )
        assert doc.course_id is None
