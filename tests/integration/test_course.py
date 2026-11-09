import pytest
from app.infrastructure.database.database import (
    Base,
    engine,
    SessionLocal,
)
from app.infrastructure.database.repositories.document_repository_impl import (
    DocumentRepositoryImpl,
)
from app.infrastructure.database.repositories.course_repository_impl import (
    CourseRepositoryImpl,
)
from app.infrastructure.database.repositories.chunk_repository_impl import (
    ChunkRepositoryImpl,
)
from app.infrastructure.database.repositories.learning_summary_repository_impl import (
    LearningSummaryRepositoryImpl,
)
from app.infrastructure.database.repositories.key_concept_repository_impl import (
    KeyConceptRepositoryImpl,
)
from app.infrastructure.database.repositories.question_repository_impl import (
    QuestionRepositoryImpl,
)
from app.infrastructure.database.repositories.quiz_repository_impl import (
    QuizRepositoryImpl,
)
from app.infrastructure.database.repositories.flashcard_repository_impl import (
    FlashcardRepositoryImpl,
)
from app.infrastructure.database.repositories.topic_repository_impl import (
    TopicRepositoryImpl,
)
from app.application.services.learning.learning_progress import (
    LearningProgressService,
)
from app.domain.entities.course import Course
from app.domain.entities.document import Document
from app.domain.entities.learning import (
    LearningSummary,
    KeyConcept,
    Question,
    Quiz,
    QuizQuestion,
    QuizSession,
    QuizAnswer,
    Flashcard,
    FlashcardReview,
)


@pytest.fixture(autouse=True)
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def repos(db):
    return {
        "course_repo": CourseRepositoryImpl(db),
        "doc_repo": DocumentRepositoryImpl(db),
        "chunk_repo": ChunkRepositoryImpl(db),
        "summary_repo": LearningSummaryRepositoryImpl(db),
        "concept_repo": KeyConceptRepositoryImpl(db),
        "question_repo": QuestionRepositoryImpl(db),
        "quiz_repo": QuizRepositoryImpl(db),
        "flashcard_repo": FlashcardRepositoryImpl(db),
        "topic_repo": TopicRepositoryImpl(db),
    }


@pytest.fixture
def service(repos):
    return LearningProgressService(
        doc_repo=repos["doc_repo"],
        chunk_repo=repos["chunk_repo"],
        summary_repo=repos["summary_repo"],
        concept_repo=repos["concept_repo"],
        question_repo=repos["question_repo"],
        quiz_repo=repos["quiz_repo"],
        flashcard_repo=repos["flashcard_repo"],
        topic_repo=repos["topic_repo"],
    )


def _seed_course_a(repos):
    course = repos["course_repo"].save(
        Course(id="course_a", name="Math 101")
    )
    repos["doc_repo"].save(
        Document(
            id="doc_a1",
            name="Algebra.pdf",
            file_type="pdf",
            status="INDEXED",
            course_id="course_a",
        )
    )
    repos["doc_repo"].save(
        Document(
            id="doc_a2",
            name="Calculus.pdf",
            file_type="pdf",
            status="INDEXED",
            course_id="course_a",
        )
    )
    repos["summary_repo"].save(
        LearningSummary(
            document_id="doc_a1", title="Algebra Summary"
        )
    )
    repos["summary_repo"].save(
        LearningSummary(
            document_id="doc_a2", title="Calculus Summary"
        )
    )
    repos["concept_repo"].save_many(
        [
            KeyConcept(
                document_id="doc_a1",
                term="Polynomial",
                definition="Expression with variables",
                topic="Algebra",
            ),
            KeyConcept(
                document_id="doc_a2",
                term="Derivative",
                definition="Rate of change",
                topic="Calculus",
            ),
        ]
    )
    repos["question_repo"].save_many(
        [
            Question(
                document_id="doc_a1",
                question="What is x+1?",
                answer="x+1",
                topic="Algebra",
            ),
            Question(
                document_id="doc_a2",
                question="What is d/dx?",
                answer="Derivative",
                topic="Calculus",
            ),
        ]
    )
    quiz = repos["quiz_repo"].save_quiz(
        Quiz(document_id="doc_a1", title="Algebra Quiz")
    )
    q1 = repos["quiz_repo"].save_question(
        QuizQuestion(
            quiz_id=quiz.id,
            question="2+2?",
            correct_answer="4",
            topic="Algebra",
        )
    )
    sess = repos["quiz_repo"].save_session(
        QuizSession(
            quiz_id=quiz.id,
            status="completed",
            score=1,
            percentage=100.0,
        )
    )
    repos["quiz_repo"].save_answers(
        [
            QuizAnswer(
                session_id=sess.id,
                quiz_question_id=q1.id,
                user_answer="4",
                is_correct=True,
            )
        ]
    )
    fc = repos["flashcard_repo"].save(
        Flashcard(
            document_id="doc_a1",
            front="Poly?",
            back="Polynomial",
            topic="Algebra",
        )
    )
    repos["flashcard_repo"].save_review(
        FlashcardReview(flashcard_id=fc.id, rating="GOOD")
    )


def _seed_course_b(repos):
    repos["course_repo"].save(
        Course(id="course_b", name="CS 201")
    )
    repos["doc_repo"].save(
        Document(
            id="doc_b1",
            name="Algorithms.pdf",
            file_type="pdf",
            status="INDEXED",
            course_id="course_b",
        )
    )
    repos["summary_repo"].save(
        LearningSummary(
            document_id="doc_b1",
            title="Algorithms Summary",
        )
    )
    repos["concept_repo"].save_many(
        [
            KeyConcept(
                document_id="doc_b1",
                term="Sorting",
                definition="Ordering elements",
                topic="Algorithms",
            ),
        ]
    )
    quiz_b = repos["quiz_repo"].save_quiz(
        Quiz(
            document_id="doc_b1", title="Algorithms Quiz"
        )
    )
    qb1 = repos["quiz_repo"].save_question(
        QuizQuestion(
            quiz_id=quiz_b.id,
            question="Quick sort?",
            correct_answer="O(n log n)",
            topic="Algorithms",
        )
    )
    sb = repos["quiz_repo"].save_session(
        QuizSession(
            quiz_id=quiz_b.id,
            status="completed",
            score=0,
            percentage=0.0,
        )
    )
    repos["quiz_repo"].save_answers(
        [
            QuizAnswer(
                session_id=sb.id,
                quiz_question_id=qb1.id,
                user_answer="wrong",
                is_correct=False,
            )
        ]
    )
    fc_b = repos["flashcard_repo"].save(
        Flashcard(
            document_id="doc_b1",
            front="Sort?",
            back="Ordering",
            topic="Algorithms",
        )
    )
    repos["flashcard_repo"].save_review(
        FlashcardReview(
            flashcard_id=fc_b.id, rating="HARD"
        )
    )


class TestCourseIsolation:

    def test_course_a_stats_exclude_course_b(
        self, repos, service
    ):
        _seed_course_a(repos)
        _seed_course_b(repos)

        stats = service.get_course_stats("course_a")
        assert stats["document_count"] == 2
        assert stats["total_summaries"] == 2
        assert stats["total_concepts"] == 2
        assert stats["total_questions"] == 2
        assert stats["quiz_count"] == 1
        assert stats["answers_total"] == 1
        assert stats["answers_correct"] == 1
        assert stats["total_flashcards"] == 1
        assert stats["flashcards_reviewed"] == 1
        assert stats["flashcards_known"] == 1

    def test_course_b_stats_exclude_course_a(
        self, repos, service
    ):
        _seed_course_a(repos)
        _seed_course_b(repos)

        stats = service.get_course_stats("course_b")
        assert stats["document_count"] == 1
        assert stats["total_summaries"] == 1
        assert stats["total_concepts"] == 1
        assert stats["total_questions"] == 0
        assert stats["quiz_count"] == 1
        assert stats["answers_total"] == 1
        assert stats["answers_correct"] == 0
        assert stats["total_flashcards"] == 1
        assert stats["flashcards_reviewed"] == 1
        assert stats["flashcards_known"] == 0

    def test_course_accuracy_isolated(
        self, repos, service
    ):
        _seed_course_a(repos)
        _seed_course_b(repos)

        stats_a = service.get_course_stats("course_a")
        assert stats_a["accuracy"] == 100.0

        stats_b = service.get_course_stats("course_b")
        assert stats_b["accuracy"] == 0.0

    def test_nonexistent_course_returns_empty(
        self, service
    ):
        assert service.get_course_stats("none") == {}

    def test_course_with_no_learning_data(
        self, repos, service
    ):
        repos["course_repo"].save(
            Course(id="empty_course", name="Empty")
        )
        repos["doc_repo"].save(
            Document(
                id="empty_doc",
                name="Blank.pdf",
                file_type="pdf",
                status="UPLOADED",
                course_id="empty_course",
            )
        )
        stats = service.get_course_stats("empty_course")
        assert stats["document_count"] == 1
        assert stats["indexed_count"] == 0
        assert stats["total_summaries"] == 0
        assert stats["total_concepts"] == 0
        assert stats["overall_progress"] == 0.0

    def test_delete_course_documents_independent(
        self, repos, service
    ):
        _seed_course_a(repos)
        _seed_course_b(repos)

        repos["summary_repo"].delete_by_document_id(
            "doc_a1"
        )
        repos["concept_repo"].delete_by_document_id(
            "doc_a1"
        )
        repos["question_repo"].delete_by_document_id(
            "doc_a1"
        )
        repos["quiz_repo"].delete_quizzes_by_document_id(
            "doc_a1"
        )
        repos["flashcard_repo"].delete_by_document_id(
            "doc_a1"
        )
        repos["doc_repo"].delete("doc_a1")

        stats_b = service.get_course_stats("course_b")
        assert stats_b["document_count"] == 1
        assert stats_b["total_concepts"] == 1
        assert stats_b["answers_total"] == 1


class TestCourseDocumentMove:

    def test_move_document_to_course(self, db):
        doc_repo = DocumentRepositoryImpl(db)
        course_repo = CourseRepositoryImpl(db)

        course_repo.save(
            Course(id="target", name="Target")
        )
        doc = doc_repo.save(
            Document(
                id="mover",
                name="mover.pdf",
                file_type="pdf",
                course_id=None,
            )
        )
        assert doc.course_id is None

        doc.course_id = "target"
        updated = doc_repo.update(doc)

        docs_in_course = doc_repo.find_by_course_id(
            "target"
        )
        assert len(docs_in_course) == 1
        assert docs_in_course[0].id == "mover"

    def test_move_document_between_courses(self, db):
        doc_repo = DocumentRepositoryImpl(db)
        course_repo = CourseRepositoryImpl(db)

        course_repo.save(Course(id="c1", name="C1"))
        course_repo.save(Course(id="c2", name="C2"))

        doc = doc_repo.save(
            Document(
                id="d1",
                name="d.pdf",
                file_type="pdf",
                course_id="c1",
            )
        )
        assert len(doc_repo.find_by_course_id("c1")) == 1
        assert len(doc_repo.find_by_course_id("c2")) == 0

        doc.course_id = "c2"
        doc_repo.update(doc)

        assert len(doc_repo.find_by_course_id("c1")) == 0
        assert len(doc_repo.find_by_course_id("c2")) == 1

    def test_unassign_document_from_course(self, db):
        doc_repo = DocumentRepositoryImpl(db)
        course_repo = CourseRepositoryImpl(db)

        course_repo.save(Course(id="c1", name="C1"))
        doc = doc_repo.save(
            Document(
                id="d1",
                name="d.pdf",
                file_type="pdf",
                course_id="c1",
            )
        )

        doc.course_id = None
        doc_repo.update(doc)

        assert len(doc_repo.find_by_course_id("c1")) == 0
        found = doc_repo.find_by_id("d1")
        assert found.course_id is None


class TestCourseProgress:

    def test_progress_computed_from_course_documents(
        self, repos, service
    ):
        _seed_course_a(repos)
        _seed_course_b(repos)

        stats_a = service.get_course_stats("course_a")
        assert stats_a["overall_progress"] > 0

        stats_b = service.get_course_stats("course_b")
        assert stats_b["overall_progress"] > 0

    def test_course_progress_ignores_unindexed(
        self, repos, service
    ):
        repos["course_repo"].save(
            Course(id="c1", name="C1")
        )
        repos["doc_repo"].save(
            Document(
                id="d1",
                name="a.pdf",
                file_type="pdf",
                status="UPLOADED",
                course_id="c1",
            )
        )
        repos["doc_repo"].save(
            Document(
                id="d2",
                name="b.pdf",
                file_type="pdf",
                status="INDEXED",
                course_id="c1",
            )
        )
        repos["summary_repo"].save(
            LearningSummary(document_id="d2", title="S")
        )

        stats = service.get_course_stats("c1")
        assert stats["document_count"] == 2
        assert stats["indexed_count"] == 1
        assert stats["total_summaries"] == 1

    def test_no_course_documents_returns_empty(
        self, service
    ):
        assert service.get_course_stats("empty") == {}
