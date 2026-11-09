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
from app.infrastructure.database.repositories.conversation_repository_impl import (
    ConversationRepositoryImpl,
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
from app.domain.entities.document import Document
from app.domain.entities.chunk import Chunk
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
        "conv_repo": ConversationRepositoryImpl(db),
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


class TestPhase5FullFlow:

    def test_document_with_all_content_stats(
        self, repos, service
    ):
        repos["doc_repo"].save(
            Document(
                id="d1",
                name="ai_intro.pdf",
                file_type="pdf",
                status="INDEXED",
                pages=10,
            )
        )

        repos["chunk_repo"].save_many(
            [
                Chunk(
                    id="c1",
                    document_id="d1",
                    content="text",
                    chunk_index=0,
                ),
                Chunk(
                    id="c2",
                    document_id="d1",
                    content="text2",
                    chunk_index=1,
                ),
            ]
        )

        repos["summary_repo"].save(
            LearningSummary(
                document_id="d1",
                title="ملخص AI",
            )
        )

        repos["concept_repo"].save_many(
            [
                KeyConcept(
                    document_id="d1",
                    term="التعلم الآلي",
                    definition="فرع من AI",
                    topic="ML",
                ),
                KeyConcept(
                    document_id="d1",
                    term="الشبكات العصبية",
                    definition="مبنى مستوحى من الدماغ",
                    topic="DL",
                ),
            ]
        )

        repos["question_repo"].save_many(
            [
                Question(
                    document_id="d1",
                    question="ما هو ML؟",
                    answer="تعلم من البيانات",
                    topic="ML",
                ),
                Question(
                    document_id="d1",
                    question="ما هو DL؟",
                    answer="شبكات عصبية",
                    topic="DL",
                ),
                Question(
                    document_id="d1",
                    question="سؤال ثالث",
                    answer="إجابة ثالثة",
                    topic="ML",
                ),
            ]
        )

        quiz = repos["quiz_repo"].save_quiz(
            Quiz(document_id="d1", title="اختبار AI")
        )

        q1 = repos["quiz_repo"].save_question(
            QuizQuestion(
                quiz_id=quiz.id,
                question="Q1?",
                correct_answer="A",
                topic="ML",
            )
        )
        q2 = repos["quiz_repo"].save_question(
            QuizQuestion(
                quiz_id=quiz.id,
                question="Q2?",
                correct_answer="B",
                topic="DL",
            )
        )

        s1 = repos["quiz_repo"].save_session(
            QuizSession(
                quiz_id=quiz.id,
                status="completed",
                score=1,
                percentage=50.0,
            )
        )
        repos["quiz_repo"].save_answers(
            [
                QuizAnswer(
                    session_id=s1.id,
                    quiz_question_id=q1.id,
                    user_answer="A",
                    is_correct=True,
                ),
                QuizAnswer(
                    session_id=s1.id,
                    quiz_question_id=q2.id,
                    user_answer="A",
                    is_correct=False,
                ),
            ]
        )

        s2 = repos["quiz_repo"].save_session(
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
                    session_id=s2.id,
                    quiz_question_id=q1.id,
                    user_answer="A",
                    is_correct=True,
                ),
                QuizAnswer(
                    session_id=s2.id,
                    quiz_question_id=q2.id,
                    user_answer="B",
                    is_correct=True,
                ),
            ]
        )

        fc1 = repos["flashcard_repo"].save(
            Flashcard(
                document_id="d1",
                front="ما هو ML؟",
                back="تعلم من البيانات",
                topic="ML",
            )
        )
        fc2 = repos["flashcard_repo"].save(
            Flashcard(
                document_id="d1",
                front="ما هو DL؟",
                back="شبكات عصبية",
                topic="DL",
            )
        )

        repos["flashcard_repo"].save_review(
            FlashcardReview(
                flashcard_id=fc1.id,
                rating="EASY",
            )
        )
        repos["flashcard_repo"].save_review(
            FlashcardReview(
                flashcard_id=fc2.id,
                rating="UNKNOWN",
            )
        )

        stats = service.get_stats()
        assert stats.total_documents == 1
        assert stats.indexed_documents == 1
        assert stats.total_summaries == 1
        assert stats.total_concepts == 2
        assert stats.total_questions == 3
        assert stats.total_quizzes == 2
        assert stats.total_answers == 4
        assert stats.correct_answers == 3
        assert stats.accuracy == 75.0
        assert stats.total_flashcards == 2
        assert stats.total_flashcard_reviews == 2
        assert stats.flashcards_known == 1
        assert stats.overall_progress > 0

        strong = [
            t
            for t in stats.strong_topics
            if t.topic == "ML"
        ]
        assert len(strong) == 1
        assert strong[0].accuracy == 100.0

        weak = [
            t
            for t in stats.weak_topics
            if t.topic == "DL"
        ]
        assert len(weak) == 1
        assert weak[0].accuracy == 50.0

    def test_document_overview_full(self, repos, service):
        repos["doc_repo"].save(
            Document(
                id="d1",
                name="test.pdf",
                file_type="pdf",
                status="INDEXED",
                pages=5,
            )
        )
        repos["chunk_repo"].save_many(
            [
                Chunk(
                    id="c1",
                    document_id="d1",
                    content="text",
                    chunk_index=0,
                )
            ]
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
        repos["question_repo"].save_many(
            [
                Question(
                    document_id="d1",
                    question="Q?",
                    answer="A",
                )
            ]
        )
        repos["flashcard_repo"].save_many(
            [
                Flashcard(
                    document_id="d1",
                    front="F",
                    back="B",
                )
            ]
        )

        ds = service.get_document_stats("d1")
        assert ds["document"].name == "test.pdf"
        assert ds["chunks"] == 1
        assert ds["has_summary"]
        assert ds["concept_count"] == 1
        assert ds["question_count"] == 1
        assert ds["flashcard_count"] == 1

    def test_delete_cleans_dashboard_stats(
        self, repos, service
    ):
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

        stats_before = service.get_stats()
        assert stats_before.total_documents == 1
        assert stats_before.total_summaries == 1

        repos["summary_repo"].delete_by_document_id("d1")
        repos["concept_repo"].delete_by_document_id("d1")
        repos["doc_repo"].delete("d1")

        stats_after = service.get_stats()
        assert stats_after.total_documents == 0
        assert stats_after.total_summaries == 0
        assert stats_after.total_concepts == 0

    def test_multiple_documents_progress(
        self, repos, service
    ):
        for i in range(3):
            repos["doc_repo"].save(
                Document(
                    id=f"d{i}",
                    name=f"doc{i}.pdf",
                    file_type="pdf",
                    status="INDEXED",
                )
            )

        repos["summary_repo"].save(
            LearningSummary(
                document_id="d0",
                title="S0",
            )
        )

        stats = service.get_stats()
        assert stats.total_documents == 3
        assert stats.indexed_documents == 3
        assert stats.total_summaries == 1
        assert stats.overall_progress > 0

    def test_no_data_dashboard(self, service):
        stats = service.get_stats()
        assert stats.total_documents == 0
        assert stats.overall_progress == 0.0
        assert len(stats.recent_activity) == 0
        assert len(stats.strong_topics) == 0
        assert len(stats.weak_topics) == 0

    def test_progress_increases_with_content(
        self, repos, service
    ):
        repos["doc_repo"].save(
            Document(
                id="d1",
                name="test.pdf",
                file_type="pdf",
                status="INDEXED",
            )
        )

        stats_empty = service.get_stats()
        progress_empty = stats_empty.overall_progress

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
        repos["question_repo"].save_many(
            [
                Question(
                    document_id="d1",
                    question="Q?",
                    answer="A",
                )
            ]
        )
        repos["flashcard_repo"].save_many(
            [
                Flashcard(
                    document_id="d1",
                    front="F",
                    back="B",
                )
            ]
        )

        stats_with = service.get_stats()
        assert stats_with.overall_progress > progress_empty

    def test_recent_activity_sorted_by_date(
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
        assert len(stats.recent_activity) >= 1

        dates = [
            a["date"]
            for a in stats.recent_activity
            if a["date"]
        ]
        assert dates == sorted(dates, reverse=True)

    def test_flashcards_known_only_good_easy(
        self, repos, service
    ):
        fc = repos["flashcard_repo"].save(
            Flashcard(
                document_id="d1",
                front="F",
                back="B",
            )
        )
        for rating in [
            "UNKNOWN",
            "HARD",
            "GOOD",
            "EASY",
            "GOOD",
        ]:
            repos["flashcard_repo"].save_review(
                FlashcardReview(
                    flashcard_id=fc.id,
                    rating=rating,
                )
            )

        stats = service.get_stats()
        assert stats.total_flashcard_reviews == 5
        assert stats.flashcards_known == 3

    def test_document_stats_nonexistent(
        self, service
    ):
        assert service.get_document_stats("none") == {}

    def test_full_delete_cascade(
        self, repos, service
    ):
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
        repos["question_repo"].save_many(
            [
                Question(
                    document_id="d1",
                    question="Q?",
                    answer="A",
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

        stats_before = service.get_stats()
        assert stats_before.total_documents == 1
        assert stats_before.total_answers == 1

        repos["summary_repo"].delete_by_document_id("d1")
        repos["concept_repo"].delete_by_document_id("d1")
        repos["question_repo"].delete_by_document_id("d1")
        repos["quiz_repo"].delete_quizzes_by_document_id(
            "d1"
        )
        repos["flashcard_repo"].delete_by_document_id(
            "d1"
        )
        repos["doc_repo"].delete("d1")

        stats_after = service.get_stats()
        assert stats_after.total_documents == 0
        assert stats_after.total_answers == 0
        assert stats_after.total_quizzes == 0
        assert stats_after.total_flashcards == 0
        assert stats_after.total_summaries == 0
        assert stats_after.total_concepts == 0
        assert stats_after.overall_progress == 0.0
        assert len(stats_after.strong_topics) == 0
        assert len(stats_after.weak_topics) == 0
