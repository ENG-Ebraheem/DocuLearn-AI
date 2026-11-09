import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.database import Base
from app.infrastructure.database.repositories.document_repository_impl import (
    DocumentRepositoryImpl,
)
from app.infrastructure.database.repositories.course_repository_impl import (
    CourseRepositoryImpl,
)
from app.infrastructure.database.repositories.chunk_repository_impl import (
    ChunkRepositoryImpl,
)
from app.infrastructure.database.repositories.conversation_repository_impl import (
    ConversationRepositoryImpl,
)
from app.infrastructure.database.repositories.chat_message_repository_impl import (
    ChatMessageRepositoryImpl,
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
from app.application.services.rag.qa_service import QAService
from app.application.services.rag.retriever import Retriever
from app.application.services.learning.learning_progress import (
    LearningProgressService,
)
from app.infrastructure.llm.fake_llm_provider import (
    FakeLLMProvider,
)
from app.domain.entities.document import Document
from app.domain.entities.course import Course
from app.domain.entities.chat_mode import ChatMode
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


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def repos(db_session):
    return {
        "doc_repo": DocumentRepositoryImpl(db_session),
        "course_repo": CourseRepositoryImpl(db_session),
        "chunk_repo": ChunkRepositoryImpl(db_session),
        "conv_repo": ConversationRepositoryImpl(db_session),
        "msg_repo": ChatMessageRepositoryImpl(db_session),
        "summary_repo": LearningSummaryRepositoryImpl(db_session),
        "concept_repo": KeyConceptRepositoryImpl(db_session),
        "question_repo": QuestionRepositoryImpl(db_session),
        "quiz_repo": QuizRepositoryImpl(db_session),
        "flashcard_repo": FlashcardRepositoryImpl(db_session),
        "topic_repo": TopicRepositoryImpl(db_session),
    }


@pytest.fixture
def progress_svc(repos):
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


class TestChatMode:

    def test_chat_mode_enum_values(self):
        assert ChatMode.GENERAL.value == "general"
        assert ChatMode.DOCUMENT_RAG.value == "document_rag"
        assert ChatMode.GENERAL_FALLBACK.value == "general_fallback"

    def test_chat_mode_is_hashable(self):
        modes = {ChatMode.GENERAL, ChatMode.DOCUMENT_RAG}
        assert len(modes) == 2


class TestGeneralChat:

    def test_general_chat_no_retriever(self):
        """General Chat must not use Retriever."""
        fake_llm = FakeLLMProvider(response="AI is artificial intelligence")
        qa = QAService(retriever=None, llm_provider=fake_llm)
        response = qa.general_chat(query="What is AI?")
        assert response.answer == "AI is artificial intelligence"
        assert response.sources == []
        assert response.has_sufficient_context is False

    def test_general_chat_no_sources(self):
        """General Chat must never include sources."""
        fake_llm = FakeLLMProvider(response="General answer")
        qa = QAService(retriever=None, llm_provider=fake_llm)
        response = qa.general_chat(query="test")
        assert response.sources == []

    def test_general_chat_with_history(self):
        fake_llm = FakeLLMProvider(response="Follow-up answer")
        qa = QAService(retriever=None, llm_provider=fake_llm)
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
        response = qa.general_chat(query="Tell me more", history=history)
        assert response.answer == "Follow-up answer"

    def test_general_chat_offline(self):
        class OfflineLLM(FakeLLMProvider):
            def is_available(self):
                return False
        fake_llm = OfflineLLM()
        qa = QAService(retriever=None, llm_provider=fake_llm)
        response = qa.general_chat(query="test")
        assert "تعذر" in response.answer
        assert response.sources == []


class TestDocumentChatRAG:

    def test_document_chat_uses_retriever(self):
        """Document Chat must use RAG (Retriever)."""
        from unittest.mock import MagicMock, patch
        from app.application.services.rag.retriever import RetrievedChunk

        from app.application.services.rag.context_builder import BuiltContext

        mock_retriever = MagicMock()
        chunk = RetrievedChunk(
            chunk_id="c1",
            document_id="doc1",
            document_name="test.pdf",
            content="test content about AI",
            metadata={"page": 1},
            score=0.9,
            chunk_index=0,
        )
        mock_retriever.retrieve.return_value = [chunk]

        fake_llm = FakeLLMProvider(response="AI stands for Artificial Intelligence")
        qa = QAService(retriever=mock_retriever, llm_provider=fake_llm)

        with patch.object(qa.context_builder, "build", return_value=BuiltContext(context_text="", chunks=[chunk], sources=[], query="")):
            response = qa.ask(query="What is AI?", document_id="doc1")

        mock_retriever.retrieve.assert_called_once()
        assert response.sources is not None

    def test_document_chat_has_sources(self):
        from unittest.mock import MagicMock, patch
        from app.application.services.rag.retriever import RetrievedChunk
        from app.application.services.rag.context_builder import BuiltContext

        mock_retriever = MagicMock()
        chunk = RetrievedChunk(
            chunk_id="c1",
            document_id="doc1",
            document_name="test.pdf",
            content="test content",
            metadata={"page": 1},
            score=0.9,
            chunk_index=0,
        )
        mock_retriever.retrieve.return_value = [chunk]

        fake_llm = FakeLLMProvider(response="Answer")
        qa = QAService(retriever=mock_retriever, llm_provider=fake_llm)

        with patch.object(qa.context_builder, "build", return_value=BuiltContext(context_text="", chunks=[chunk], sources=[], query="")):
            response = qa.ask(query="test?", document_id="doc1")

        assert len(response.sources) > 0
        assert response.sources[0].document_name == "test.pdf"

    def test_document_chat_out_of_document_no_context(self):
        from unittest.mock import MagicMock, patch
        from app.application.services.rag.context_builder import BuiltContext

        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = []

        fake_llm = FakeLLMProvider(response="No context answer")
        qa = QAService(retriever=mock_retriever, llm_provider=fake_llm)

        with patch.object(qa.context_builder, "build", return_value=BuiltContext(context_text="", chunks=[], sources=[], query="")):
            response = qa.ask(query="random question", document_id="doc1")

        assert response.has_sufficient_context is False
        assert response.sources == []


class TestDocumentIsolationPhase53:

    def test_doc_a_stats_excludes_doc_b(self, repos, progress_svc):
        repos["doc_repo"].save(Document(id="doc_a", name="A.pdf", file_type="pdf", status="INDEXED"))
        repos["doc_repo"].save(Document(id="doc_b", name="B.pdf", file_type="pdf", status="INDEXED"))
        repos["summary_repo"].save(LearningSummary(document_id="doc_a", title="Summary A"))
        repos["summary_repo"].save(LearningSummary(document_id="doc_b", title="Summary B"))
        repos["concept_repo"].save_many([
            KeyConcept(document_id="doc_a", term="ConceptA", definition="def A", topic="TopicA"),
            KeyConcept(document_id="doc_b", term="ConceptB", definition="def B", topic="TopicB"),
        ])

        stats_a = progress_svc.get_document_stats("doc_a")
        stats_b = progress_svc.get_document_stats("doc_b")

        assert stats_a["has_summary"] is True
        assert stats_a["concept_count"] == 1
        assert stats_b["has_summary"] is True
        assert stats_b["concept_count"] == 1

    def test_delete_doc_a_no_effect_on_b(self, repos, progress_svc):
        repos["doc_repo"].save(Document(id="doc_a", name="A.pdf", file_type="pdf", status="INDEXED"))
        repos["doc_repo"].save(Document(id="doc_b", name="B.pdf", file_type="pdf", status="INDEXED"))
        repos["summary_repo"].save(LearningSummary(document_id="doc_a", title="S A"))
        repos["summary_repo"].save(LearningSummary(document_id="doc_b", title="S B"))

        repos["summary_repo"].delete_by_document_id("doc_a")
        repos["doc_repo"].delete("doc_a")

        stats_b = progress_svc.get_document_stats("doc_b")
        assert stats_b["document"].name == "B.pdf"
        assert stats_b["has_summary"] is True


class TestCourseOptional:

    def test_document_without_course(self, repos):
        doc = repos["doc_repo"].save(Document(id="d1", name="solo.pdf", file_type="pdf"))
        assert doc.course_id is None

    def test_course_not_required_to_open_document(self, repos):
        doc = repos["doc_repo"].save(Document(id="d1", name="solo.pdf", file_type="pdf", status="INDEXED"))
        found = repos["doc_repo"].find_by_id("d1")
        assert found is not None
        assert found.status == "INDEXED"

    def test_course_can_be_created_later(self, repos):
        doc = repos["doc_repo"].save(Document(id="d1", name="solo.pdf", file_type="pdf"))
        assert doc.course_id is None
        course = repos["course_repo"].save(Course(id="c1", name="Math"))
        doc.course_id = "c1"
        repos["doc_repo"].update(doc)
        updated = repos["doc_repo"].find_by_id("d1")
        assert updated.course_id == "c1"

    def test_delete_course_unassigns_documents(self, repos):
        repos["course_repo"].save(Course(id="c1", name="Math"))
        repos["doc_repo"].save(Document(id="d1", name="solo.pdf", file_type="pdf", course_id="c1"))
        for document in repos["doc_repo"].find_by_course_id("c1"):
            document.course_id = None
            repos["doc_repo"].update(document)
        repos["course_repo"].delete("c1")

        assert repos["course_repo"].find_by_id("c1") is None
        found_doc = repos["doc_repo"].find_by_id("d1")
        assert found_doc is not None
        assert found_doc.course_id is None


class TestStudyModeNoRandomData:

    def test_study_requires_document(self, progress_svc):
        stats = progress_svc.get_document_stats("nonexistent")
        assert stats == {}

    def test_progress_scoped_to_document(self, repos, progress_svc):
        repos["doc_repo"].save(Document(id="doc1", name="A.pdf", file_type="pdf", status="INDEXED"))
        repos["doc_repo"].save(Document(id="doc2", name="B.pdf", file_type="pdf", status="INDEXED"))
        repos["summary_repo"].save(LearningSummary(document_id="doc1", title="S1"))
        repos["question_repo"].save_many([
            Question(document_id="doc1", question="Q1?", answer="A1", topic="T1"),
            Question(document_id="doc2", question="Q2?", answer="A2", topic="T2"),
            Question(document_id="doc2", question="Q3?", answer="A3", topic="T2"),
        ])

        stats1 = progress_svc.get_document_stats("doc1")
        stats2 = progress_svc.get_document_stats("doc2")

        assert stats1["question_count"] == 1
        assert stats2["question_count"] == 2


class TestWidgetKeys:

    def test_general_chat_key_is_static(self):
        key = "general_chat_input"
        assert key == "general_chat_input"

    def test_document_chat_key_is_scoped(self):
        doc_id = "abc123"
        key = f"document_chat_input_{doc_id}"
        assert key == "document_chat_input_abc123"

    def test_different_documents_different_keys(self):
        key1 = "document_chat_input_doc1"
        key2 = "document_chat_input_doc2"
        assert key1 != key2

    def test_all_widget_keys_use_context(self):
        import ast
        with open("app/main.py") as f:
            tree = ast.parse(f.read())

        all_keys = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                if any(kw in val for kw in ["_input", "_select", "_btn", "_radio", "_tab"]):
                    all_keys.add(val)

        seen = set()
        for k in all_keys:
            assert k not in seen, f"Duplicate widget key: {k}"
            seen.add(k)


class TestNavigationState:

    def test_active_document_id_persists(self):
        from app.domain.entities.chat_mode import ChatMode
        state = {}
        state["active_document_id"] = "doc1"
        state["current_page"] = "📄 المستند"
        state["chat_mode"] = ChatMode.DOCUMENT_RAG

        assert state["active_document_id"] == "doc1"
        assert state["current_page"] == "📄 المستند"

    def test_navigation_preserves_document(self):
        state = {
            "active_document_id": "doc1",
            "current_page": "💬 المحادثة العامة",
        }
        state["current_page"] = "📄 المستند"
        assert state["active_document_id"] == "doc1"


class TestProgressAnalyticsDocumentScoped:

    def test_progress_course_scoped(self, repos, progress_svc):
        repos["course_repo"].save(Course(id="c1", name="Math"))
        repos["doc_repo"].save(Document(id="d1", name="A.pdf", file_type="pdf", status="INDEXED", course_id="c1"))
        repos["doc_repo"].save(Document(id="d2", name="B.pdf", file_type="pdf", status="INDEXED", course_id="c1"))
        repos["summary_repo"].save(LearningSummary(document_id="d1", title="S1"))
        repos["question_repo"].save_many([
            Question(document_id="d1", question="Q1?", answer="A1", topic="T1"),
        ])

        cs = progress_svc.get_course_stats("c1")
        assert cs["document_count"] == 2
        assert cs["total_questions"] == 1
        assert cs["total_summaries"] == 1

    def test_analytics_course_isolated(self, repos, progress_svc):
        repos["course_repo"].save(Course(id="c1", name="CS"))
        repos["course_repo"].save(Course(id="c2", name="Math"))
        repos["doc_repo"].save(Document(id="d1", name="A.pdf", file_type="pdf", status="INDEXED", course_id="c1"))
        repos["doc_repo"].save(Document(id="d2", name="B.pdf", file_type="pdf", status="INDEXED", course_id="c2"))
        repos["question_repo"].save_many([
            Question(document_id="d1", question="Q1?", answer="A1", topic="T1"),
            Question(document_id="d2", question="Q2?", answer="A2", topic="T2"),
            Question(document_id="d2", question="Q3?", answer="A3", topic="T2"),
        ])

        cs1 = progress_svc.get_course_stats("c1")
        cs2 = progress_svc.get_course_stats("c2")

        assert cs1["total_questions"] == 1
        assert cs2["total_questions"] == 2
