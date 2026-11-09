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


def _seed_doc_a(repos):
    repos["doc_repo"].save(
        Document(
            id="doc_a",
            name="AI_ML_Guide.pdf",
            file_type="pdf",
            status="INDEXED",
            pages=20,
        )
    )
    repos["summary_repo"].save(
        LearningSummary(
            document_id="doc_a",
            title="ملخص AI و ML",
        )
    )
    repos["concept_repo"].save_many(
        [
            KeyConcept(
                document_id="doc_a",
                term="التعلم الآلي",
                definition="فرع من الذكاء الاصطناعي",
                topic="ML",
            ),
            KeyConcept(
                document_id="doc_a",
                term="الشبكات العصبية",
                definition="نمذجة الدماغ",
                topic="DL",
            ),
        ]
    )
    repos["question_repo"].save_many(
        [
            Question(
                document_id="doc_a",
                question="ما هو التعلم الآلي؟",
                answer="تعلم من البيانات",
                topic="ML",
            ),
            Question(
                document_id="doc_a",
                question="ما هي الشبكات العصبية؟",
                answer="نمذجة الدماغ",
                topic="DL",
            ),
        ]
    )
    quiz_a = repos["quiz_repo"].save_quiz(
        Quiz(document_id="doc_a", title="اختبار AI")
    )
    qa1 = repos["quiz_repo"].save_question(
        QuizQuestion(
            quiz_id=quiz_a.id,
            question="Q_A1?",
            correct_answer="A1",
            topic="ML",
        )
    )
    qa2 = repos["quiz_repo"].save_question(
        QuizQuestion(
            quiz_id=quiz_a.id,
            question="Q_A2?",
            correct_answer="A2",
            topic="DL",
        )
    )
    sa = repos["quiz_repo"].save_session(
        QuizSession(
            quiz_id=quiz_a.id,
            status="completed",
            score=2,
            percentage=100.0,
        )
    )
    repos["quiz_repo"].save_answers(
        [
            QuizAnswer(
                session_id=sa.id,
                quiz_question_id=qa1.id,
                user_answer="A1",
                is_correct=True,
            ),
            QuizAnswer(
                session_id=sa.id,
                quiz_question_id=qa2.id,
                user_answer="A2",
                is_correct=True,
            ),
        ]
    )
    fc_a1 = repos["flashcard_repo"].save(
        Flashcard(
            document_id="doc_a",
            front="ما هو ML؟",
            back="تعلم من البيانات",
            topic="ML",
        )
    )
    fc_a2 = repos["flashcard_repo"].save(
        Flashcard(
            document_id="doc_a",
            front="ما هو DL؟",
            back="شبكات عصبية",
            topic="DL",
        )
    )
    repos["flashcard_repo"].save_review(
        FlashcardReview(
            flashcard_id=fc_a1.id,
            rating="EASY",
        )
    )
    repos["flashcard_repo"].save_review(
        FlashcardReview(
            flashcard_id=fc_a2.id,
            rating="GOOD",
        )
    )


def _seed_doc_b(repos):
    repos["doc_repo"].save(
        Document(
            id="doc_b",
            name="Web_Dev_Handbook.pdf",
            file_type="pdf",
            status="INDEXED",
            pages=15,
        )
    )
    repos["summary_repo"].save(
        LearningSummary(
            document_id="doc_b",
            title="ملخص تطوير الويب",
        )
    )
    repos["concept_repo"].save_many(
        [
            KeyConcept(
                document_id="doc_b",
                term="HTML",
                definition="لغة تشييد الصفحات",
                topic="Frontend",
            ),
            KeyConcept(
                document_id="doc_b",
                term="CSS",
                definition="تنسيق الصفحات",
                topic="Frontend",
            ),
        ]
    )
    repos["question_repo"].save_many(
        [
            Question(
                document_id="doc_b",
                question="ما هو HTML؟",
                answer="لغة تشييد الصفحات",
                topic="Frontend",
            ),
            Question(
                document_id="doc_b",
                question="ما هو CSS؟",
                answer="تنسيق الصفحات",
                topic="Frontend",
            ),
        ]
    )
    quiz_b = repos["quiz_repo"].save_quiz(
        Quiz(document_id="doc_b", title="اختبار Web")
    )
    qb1 = repos["quiz_repo"].save_question(
        QuizQuestion(
            quiz_id=quiz_b.id,
            question="Q_B1?",
            correct_answer="B1",
            topic="Frontend",
        )
    )
    qb2 = repos["quiz_repo"].save_question(
        QuizQuestion(
            quiz_id=quiz_b.id,
            question="Q_B2?",
            correct_answer="B2",
            topic="Backend",
        )
    )
    sb = repos["quiz_repo"].save_session(
        QuizSession(
            quiz_id=quiz_b.id,
            status="completed",
            score=1,
            percentage=50.0,
        )
    )
    repos["quiz_repo"].save_answers(
        [
            QuizAnswer(
                session_id=sb.id,
                quiz_question_id=qb1.id,
                user_answer="B1",
                is_correct=True,
            ),
            QuizAnswer(
                session_id=sb.id,
                quiz_question_id=qb2.id,
                user_answer="wrong",
                is_correct=False,
            ),
        ]
    )
    fc_b1 = repos["flashcard_repo"].save(
        Flashcard(
            document_id="doc_b",
            front="ما هو HTML؟",
            back="لغة تشييد الصفحات",
            topic="Frontend",
        )
    )
    repos["flashcard_repo"].save_review(
        FlashcardReview(
            flashcard_id=fc_b1.id,
            rating="HARD",
        )
    )


class TestDocumentIsolation:

    def test_doc_a_stats_excludes_doc_b_data(
        self, repos, service
    ):
        _seed_doc_a(repos)
        _seed_doc_b(repos)

        stats_a = service.get_document_stats("doc_a")
        assert stats_a["document"].name == "AI_ML_Guide.pdf"
        assert stats_a["has_summary"] is True
        assert stats_a["concept_count"] == 2
        assert stats_a["question_count"] == 2
        assert stats_a["quiz_count"] == 1
        assert stats_a["flashcard_count"] == 2
        assert stats_a["answers_total"] == 2
        assert stats_a["answers_correct"] == 2
        assert stats_a["flashcards_known"] == 2
        assert stats_a["flashcards_reviewed"] == 2

    def test_doc_b_stats_excludes_doc_a_data(
        self, repos, service
    ):
        _seed_doc_a(repos)
        _seed_doc_b(repos)

        stats_b = service.get_document_stats("doc_b")
        assert stats_b["document"].name == "Web_Dev_Handbook.pdf"
        assert stats_b["has_summary"] is True
        assert stats_b["concept_count"] == 2
        assert stats_b["question_count"] == 2
        assert stats_b["quiz_count"] == 1
        assert stats_b["flashcard_count"] == 1
        assert stats_b["answers_total"] == 2
        assert stats_b["answers_correct"] == 1
        assert stats_b["flashcards_known"] == 0
        assert stats_b["flashcards_reviewed"] == 1

    def test_doc_a_topics_exclude_doc_b_topics(
        self, repos, service
    ):
        _seed_doc_a(repos)
        _seed_doc_b(repos)

        topics_a = service.get_document_topics("doc_a")
        topic_names_a = set(topics_a.keys())
        assert "ML" in topic_names_a
        assert "DL" in topic_names_a
        assert "Frontend" not in topic_names_a
        assert "Backend" not in topic_names_a

    def test_doc_b_topics_exclude_doc_a_topics(
        self, repos, service
    ):
        _seed_doc_a(repos)
        _seed_doc_b(repos)

        topics_b = service.get_document_topics("doc_b")
        topic_names_b = set(topics_b.keys())
        assert "Frontend" in topic_names_b
        assert "ML" not in topic_names_b
        assert "DL" not in topic_names_b

    def test_delete_doc_a_does_not_affect_doc_b(
        self, repos, service
    ):
        _seed_doc_a(repos)
        _seed_doc_b(repos)

        repos["summary_repo"].delete_by_document_id("doc_a")
        repos["concept_repo"].delete_by_document_id("doc_a")
        repos["question_repo"].delete_by_document_id("doc_a")
        repos["quiz_repo"].delete_quizzes_by_document_id(
            "doc_a"
        )
        repos["flashcard_repo"].delete_by_document_id(
            "doc_a"
        )
        repos["doc_repo"].delete("doc_a")

        stats_b = service.get_document_stats("doc_b")
        assert stats_b["document"].name == "Web_Dev_Handbook.pdf"
        assert stats_b["has_summary"] is True
        assert stats_b["concept_count"] == 2
        assert stats_b["question_count"] == 2
        assert stats_b["quiz_count"] == 1
        assert stats_b["flashcard_count"] == 1
        assert stats_b["answers_total"] == 2

    def test_delete_doc_b_does_not_affect_doc_a(
        self, repos, service
    ):
        _seed_doc_a(repos)
        _seed_doc_b(repos)

        repos["summary_repo"].delete_by_document_id("doc_b")
        repos["concept_repo"].delete_by_document_id("doc_b")
        repos["question_repo"].delete_by_document_id("doc_b")
        repos["quiz_repo"].delete_quizzes_by_document_id(
            "doc_b"
        )
        repos["flashcard_repo"].delete_by_document_id(
            "doc_b"
        )
        repos["doc_repo"].delete("doc_b")

        stats_a = service.get_document_stats("doc_a")
        assert stats_a["document"].name == "AI_ML_Guide.pdf"
        assert stats_a["has_summary"] is True
        assert stats_a["concept_count"] == 2
        assert stats_a["question_count"] == 2
        assert stats_a["quiz_count"] == 1
        assert stats_a["flashcard_count"] == 2
        assert stats_a["answers_total"] == 2

    def test_global_stats_combine_both_documents(
        self, repos, service
    ):
        _seed_doc_a(repos)
        _seed_doc_b(repos)

        stats = service.get_stats()
        assert stats.total_documents == 2
        assert stats.indexed_documents == 2
        assert stats.total_summaries == 2
        assert stats.total_concepts == 4
        assert stats.total_questions == 4
        assert stats.total_quizzes == 2
        assert stats.total_answers == 4
        assert stats.correct_answers == 3
        assert stats.accuracy == 75.0
        assert stats.total_flashcards == 3
        assert stats.total_flashcard_reviews == 3
        assert stats.flashcards_known == 2

    def test_quiz_scoring_isolation(
        self, repos, service
    ):
        _seed_doc_a(repos)
        _seed_doc_b(repos)

        stats_a = service.get_document_stats("doc_a")
        assert stats_a["answers_correct"] == 2
        assert stats_a["answers_total"] == 2

        stats_b = service.get_document_stats("doc_b")
        assert stats_b["answers_correct"] == 1
        assert stats_b["answers_total"] == 2

    def test_flashcard_review_isolation(
        self, repos, service
    ):
        _seed_doc_a(repos)
        _seed_doc_b(repos)

        stats_a = service.get_document_stats("doc_a")
        assert stats_a["flashcards_known"] == 2
        assert stats_a["flashcards_reviewed"] == 2

        stats_b = service.get_document_stats("doc_b")
        assert stats_b["flashcards_known"] == 0
        assert stats_b["flashcards_reviewed"] == 1

    def test_nonexistent_document_returns_empty(
        self, service
    ):
        assert service.get_document_stats("nonexistent") == {}
        assert service.get_document_topics("nonexistent") == {}
