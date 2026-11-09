import pytest

from app.infrastructure.database.database import (
    Base,
    engine,
    SessionLocal,
)
from app.infrastructure.database.repositories.document_repository_impl import (
    DocumentRepositoryImpl,
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
    TopicPerformance,
)
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
    Topic,
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
    return LearningProgressService(**repos)


class TestNewRepoMethods:

    def test_question_repo_find_all(self, db, repos):
        repos["question_repo"].save_many(
            [
                Question(
                    document_id="d1",
                    question="Q1",
                    answer="A1",
                ),
                Question(
                    document_id="d2",
                    question="Q2",
                    answer="A2",
                ),
            ]
        )
        all_q = repos["question_repo"].find_all()
        assert len(all_q) == 2

    def test_concept_repo_find_all(self, db, repos):
        repos["concept_repo"].save_many(
            [
                KeyConcept(
                    document_id="d1",
                    term="T1",
                    definition="D1",
                ),
            ]
        )
        all_c = repos["concept_repo"].find_all()
        assert len(all_c) == 1
        assert all_c[0].term == "T1"

    def test_summary_repo_find_all(self, db, repos):
        repos["summary_repo"].save(
            LearningSummary(
                document_id="d1",
                title="S1",
            )
        )
        all_s = repos["summary_repo"].find_all()
        assert len(all_s) == 1

    def test_quiz_repo_find_all_sessions(
        self, db, repos
    ):
        quiz = repos["quiz_repo"].save_quiz(
            Quiz(document_id="d1")
        )
        repos["quiz_repo"].save_session(
            QuizSession(quiz_id=quiz.id)
        )
        all_s = repos["quiz_repo"].find_all_sessions()
        assert len(all_s) == 1

    def test_quiz_repo_find_completed_sessions(
        self, db, repos
    ):
        quiz = repos["quiz_repo"].save_quiz(
            Quiz(document_id="d1")
        )
        s1 = repos["quiz_repo"].save_session(
            QuizSession(
                quiz_id=quiz.id,
                status="completed",
                score=3,
                percentage=75.0,
            )
        )
        repos["quiz_repo"].save_session(
            QuizSession(quiz_id=quiz.id)
        )
        completed = (
            repos["quiz_repo"].find_completed_sessions()
        )
        assert len(completed) == 1
        assert completed[0].status == "completed"

    def test_quiz_repo_find_all_answers(
        self, db, repos
    ):
        quiz = repos["quiz_repo"].save_quiz(
            Quiz(document_id="d1")
        )
        q = repos["quiz_repo"].save_question(
            QuizQuestion(
                quiz_id=quiz.id,
                question="Q?",
                correct_answer="A",
            )
        )
        s = repos["quiz_repo"].save_session(
            QuizSession(quiz_id=quiz.id)
        )
        repos["quiz_repo"].save_answers(
            [
                QuizAnswer(
                    session_id=s.id,
                    quiz_question_id=q.id,
                    user_answer="A",
                    is_correct=True,
                )
            ]
        )
        all_a = repos["quiz_repo"].find_all_answers()
        assert len(all_a) == 1
        assert all_a[0].is_correct

    def test_flashcard_repo_find_all(self, db, repos):
        repos["flashcard_repo"].save_many(
            [
                Flashcard(
                    document_id="d1",
                    front="F",
                    back="B",
                )
            ]
        )
        all_f = repos["flashcard_repo"].find_all()
        assert len(all_f) == 1

    def test_flashcard_repo_count_by_document_id(
        self, db, repos
    ):
        repos["flashcard_repo"].save_many(
            [
                Flashcard(
                    document_id="d1",
                    front="F1",
                    back="B1",
                ),
                Flashcard(
                    document_id="d1",
                    front="F2",
                    back="B2",
                ),
                Flashcard(
                    document_id="d2",
                    front="F3",
                    back="B3",
                ),
            ]
        )
        assert (
            repos["flashcard_repo"].count_by_document_id(
                "d1"
            )
            == 2
        )
        assert (
            repos["flashcard_repo"].count_by_document_id(
                "d2"
            )
            == 1
        )
        assert (
            repos["flashcard_repo"].count_by_document_id(
                "d3"
            )
            == 0
        )

    def test_flashcard_repo_find_all_reviews(
        self, db, repos
    ):
        fc = repos["flashcard_repo"].save(
            Flashcard(
                document_id="d1",
                front="F",
                back="B",
            )
        )
        repos["flashcard_repo"].save_review(
            FlashcardReview(
                flashcard_id=fc.id,
                rating="GOOD",
            )
        )
        all_r = repos["flashcard_repo"].find_all_reviews()
        assert len(all_r) == 1
        assert all_r[0].rating == "GOOD"

    def test_flashcard_repo_find_reviews_by_ids(
        self, db, repos
    ):
        fc1 = repos["flashcard_repo"].save(
            Flashcard(
                document_id="d1",
                front="F1",
                back="B1",
            )
        )
        fc2 = repos["flashcard_repo"].save(
            Flashcard(
                document_id="d1",
                front="F2",
                back="B2",
            )
        )
        repos["flashcard_repo"].save_review(
            FlashcardReview(
                flashcard_id=fc1.id,
                rating="GOOD",
            )
        )
        repos["flashcard_repo"].save_review(
            FlashcardReview(
                flashcard_id=fc2.id,
                rating="HARD",
            )
        )
        reviews = repos[
            "flashcard_repo"
        ].find_reviews_by_flashcard_ids(
            [fc1.id]
        )
        assert len(reviews) == 1
        assert reviews[0].rating == "GOOD"

    def test_flashcard_repo_find_reviews_empty(
        self, db, repos
    ):
        reviews = repos[
            "flashcard_repo"
        ].find_reviews_by_flashcard_ids([])
        assert reviews == []


class TestLearningProgressService:

    def test_empty_stats(self, service):
        stats = service.get_stats()
        assert stats.total_documents == 0
        assert stats.indexed_documents == 0
        assert stats.total_questions == 0
        assert stats.total_quizzes == 0
        assert stats.total_answers == 0
        assert stats.accuracy == 0.0
        assert stats.overall_progress == 0.0
        assert len(stats.strong_topics) == 0
        assert len(stats.weak_topics) == 0
        assert len(stats.recent_activity) == 0

    def test_stats_with_data(self, repos, service):
        repos["doc_repo"].save(
            Document(
                id="d1",
                name="test.pdf",
                file_type="pdf",
                status="INDEXED",
            )
        )
        repos["summary_repo"].save(
            LearningSummary(
                document_id="d1",
                title="Summary",
            )
        )
        repos["concept_repo"].save_many(
            [
                KeyConcept(
                    document_id="d1",
                    term="T1",
                    definition="D1",
                )
            ]
        )
        repos["question_repo"].save_many(
            [
                Question(
                    document_id="d1",
                    question="Q1?",
                    answer="A1",
                )
            ]
        )
        repos["flashcard_repo"].save_many(
            [
                Flashcard(
                    document_id="d1",
                    front="F1",
                    back="B1",
                )
            ]
        )

        quiz = repos["quiz_repo"].save_quiz(
            Quiz(document_id="d1", title="Quiz")
        )
        q = repos["quiz_repo"].save_question(
            QuizQuestion(
                quiz_id=quiz.id,
                question="QQ?",
                correct_answer="A",
                topic="AI",
            )
        )
        s = repos["quiz_repo"].save_session(
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
                    session_id=s.id,
                    quiz_question_id=q.id,
                    user_answer="A",
                    is_correct=True,
                )
            ]
        )

        fc = repos["flashcard_repo"].find_all()[0]
        repos["flashcard_repo"].save_review(
            FlashcardReview(
                flashcard_id=fc.id,
                rating="GOOD",
            )
        )

        stats = service.get_stats()
        assert stats.total_documents == 1
        assert stats.indexed_documents == 1
        assert stats.total_questions == 1
        assert stats.total_quizzes == 1
        assert stats.total_answers == 1
        assert stats.correct_answers == 1
        assert stats.accuracy == 100.0
        assert stats.total_flashcards == 1
        assert stats.total_flashcard_reviews == 1
        assert stats.flashcards_known == 1
        assert stats.overall_progress > 0

    def test_progress_zero_when_no_docs(self, service):
        assert service.get_stats().overall_progress == 0.0

    def test_progress_not_zero_with_data(
        self, repos, service
    ):
        repos["doc_repo"].save(
            Document(
                id="d1",
                name="t.pdf",
                file_type="pdf",
                status="INDEXED",
            )
        )
        repos["summary_repo"].save(
            LearningSummary(
                document_id="d1",
                title="S",
            )
        )
        stats = service.get_stats()
        assert stats.overall_progress > 0

    def test_strong_topics(self, repos, service):
        repos["doc_repo"].save(
            Document(
                id="d1",
                name="t.pdf",
                file_type="pdf",
                status="INDEXED",
            )
        )
        quiz = repos["quiz_repo"].save_quiz(
            Quiz(document_id="d1")
        )
        q = repos["quiz_repo"].save_question(
            QuizQuestion(
                quiz_id=quiz.id,
                question="Q?",
                correct_answer="A",
                topic="Machine Learning",
            )
        )
        s = repos["quiz_repo"].save_session(
            QuizSession(
                quiz_id=quiz.id,
                status="completed",
                score=2,
                percentage=100.0,
            )
        )
        repos["quiz_repo"].save_answers(
            [
                QuizAnswer(
                    session_id=s.id,
                    quiz_question_id=q.id,
                    user_answer="A",
                    is_correct=True,
                ),
                QuizAnswer(
                    session_id=s.id,
                    quiz_question_id=q.id,
                    user_answer="A",
                    is_correct=True,
                ),
            ]
        )

        stats = service.get_stats()
        assert len(stats.strong_topics) == 1
        assert (
            stats.strong_topics[0].topic
            == "Machine Learning"
        )
        assert stats.strong_topics[0].accuracy == 100.0

    def test_weak_topics(self, repos, service):
        repos["doc_repo"].save(
            Document(
                id="d1",
                name="t.pdf",
                file_type="pdf",
                status="INDEXED",
            )
        )
        quiz = repos["quiz_repo"].save_quiz(
            Quiz(document_id="d1")
        )
        q = repos["quiz_repo"].save_question(
            QuizQuestion(
                quiz_id=quiz.id,
                question="Q?",
                correct_answer="A",
                topic="Deep Learning",
            )
        )
        s = repos["quiz_repo"].save_session(
            QuizSession(
                quiz_id=quiz.id,
                status="completed",
                score=0,
                percentage=0.0,
            )
        )
        repos["quiz_repo"].save_answers(
            [
                QuizAnswer(
                    session_id=s.id,
                    quiz_question_id=q.id,
                    user_answer="B",
                    is_correct=False,
                )
            ]
        )

        stats = service.get_stats()
        assert len(stats.weak_topics) == 1
        assert (
            stats.weak_topics[0].topic
            == "Deep Learning"
        )
        assert stats.weak_topics[0].accuracy == 0.0

    def test_document_stats(self, repos, service):
        repos["doc_repo"].save(
            Document(
                id="d1",
                name="test.pdf",
                file_type="pdf",
                status="INDEXED",
            )
        )
        repos["summary_repo"].save(
            LearningSummary(
                document_id="d1",
                title="S",
            )
        )
        repos["concept_repo"].save_many(
            [
                KeyConcept(
                    document_id="d1",
                    term="T",
                    definition="D",
                )
            ]
        )

        doc_stats = service.get_document_stats("d1")
        assert doc_stats["has_summary"]
        assert doc_stats["concept_count"] == 1

    def test_document_stats_nonexistent(self, service):
        doc_stats = service.get_document_stats("nope")
        assert doc_stats == {}

    def test_recent_activity_populated(
        self, repos, service
    ):
        repos["doc_repo"].save(
            Document(
                id="d1",
                name="doc.pdf",
                file_type="pdf",
                status="INDEXED",
            )
        )
        repos["summary_repo"].save(
            LearningSummary(
                document_id="d1",
                title="Summary",
            )
        )
        stats = service.get_stats()
        assert len(stats.recent_activity) > 0

    def test_accuracy_zero_when_no_answers(self, service):
        stats = service.get_stats()
        assert stats.accuracy == 0.0

    def test_accuracy_calculated_correctly(
        self, repos, service
    ):
        repos["doc_repo"].save(
            Document(
                id="d1",
                name="t.pdf",
                file_type="pdf",
                status="INDEXED",
            )
        )
        quiz = repos["quiz_repo"].save_quiz(
            Quiz(document_id="d1")
        )
        q = repos["quiz_repo"].save_question(
            QuizQuestion(
                quiz_id=quiz.id,
                question="Q?",
                correct_answer="A",
            )
        )
        s = repos["quiz_repo"].save_session(
            QuizSession(
                quiz_id=quiz.id,
                status="completed",
            )
        )
        repos["quiz_repo"].save_answers(
            [
                QuizAnswer(
                    session_id=s.id,
                    quiz_question_id=q.id,
                    user_answer="A",
                    is_correct=True,
                ),
                QuizAnswer(
                    session_id=s.id,
                    quiz_question_id=q.id,
                    user_answer="B",
                    is_correct=False,
                ),
                QuizAnswer(
                    session_id=s.id,
                    quiz_question_id=q.id,
                    user_answer="A",
                    is_correct=True,
                ),
            ]
        )

        stats = service.get_stats()
        assert stats.total_answers == 3
        assert stats.correct_answers == 2
        assert stats.accuracy == pytest.approx(
            66.7, abs=0.1
        )

    def test_flashcards_known_count(
        self, repos, service
    ):
        fc = repos["flashcard_repo"].save(
            Flashcard(
                document_id="d1",
                front="F",
                back="B",
            )
        )
        repos["flashcard_repo"].save_review(
            FlashcardReview(
                flashcard_id=fc.id,
                rating="EASY",
            )
        )
        repos["flashcard_repo"].save_review(
            FlashcardReview(
                flashcard_id=fc.id,
                rating="UNKNOWN",
            )
        )

        stats = service.get_stats()
        assert stats.total_flashcard_reviews == 2
        assert stats.flashcards_known == 1
