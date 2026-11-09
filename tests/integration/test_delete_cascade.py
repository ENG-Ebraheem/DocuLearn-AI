import pytest
import json
import tempfile

from app.infrastructure.llm.fake_llm_provider import (
    FakeLLMProvider,
)
from app.infrastructure.embeddings.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from app.infrastructure.vector_store.faiss_vector_store import (
    FAISSVectorStore,
)
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
from app.domain.entities.document import (
    Document,
)
from app.domain.entities.chunk import Chunk
from app.domain.entities.conversation import (
    Conversation,
)
from app.domain.entities.chat_message import (
    ChatMessage,
)
from app.domain.entities.learning import (
    LearningSummary,
    KeyConcept,
    Question,
    Quiz,
    QuizQuestion,
    Flashcard,
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
        "msg_repo": ChatMessageRepositoryImpl(db),
        "summary_repo": LearningSummaryRepositoryImpl(db),
        "concept_repo": KeyConceptRepositoryImpl(db),
        "question_repo": QuestionRepositoryImpl(db),
        "quiz_repo": QuizRepositoryImpl(db),
        "flashcard_repo": FlashcardRepositoryImpl(db),
        "topic_repo": TopicRepositoryImpl(db),
    }


class TestDeleteCascade:

    def test_delete_cleans_all_learning_data(
        self, db, repos
    ):
        doc = repos["doc_repo"].save(
            Document(
                id="doc_del1",
                name="test.pdf",
                file_type="pdf",
                status="INDEXED",
            )
        )

        repos["summary_repo"].save(
            LearningSummary(
                document_id="doc_del1",
                title="S",
            )
        )
        repos["concept_repo"].save_many(
            [
                KeyConcept(
                    document_id="doc_del1",
                    term="T",
                    definition="D",
                )
            ]
        )
        repos["question_repo"].save_many(
            [
                Question(
                    document_id="doc_del1",
                    question="Q?",
                    answer="A",
                )
            ]
        )
        quiz = repos["quiz_repo"].save_quiz(
            Quiz(
                document_id="doc_del1",
                title="Q",
            )
        )
        repos["quiz_repo"].save_question(
            QuizQuestion(
                quiz_id=quiz.id,
                question="QQ?",
                correct_answer="A",
            )
        )
        repos["flashcard_repo"].save_many(
            [
                Flashcard(
                    document_id="doc_del1",
                    front="F",
                    back="B",
                )
            ]
        )
        repos["topic_repo"].save(
            Topic(
                document_id="doc_del1",
                name="T",
            )
        )

        conv = repos["conv_repo"].save(
            Conversation(
                document_id="doc_del1",
            )
        )
        repos["msg_repo"].save(
            ChatMessage(
                conversation_id=conv.id,
                role="user",
                content="msg",
            )
        )
        repos["chunk_repo"].save_many(
            [
                Chunk(
                    id="ch1",
                    document_id="doc_del1",
                    content="text",
                    chunk_index=0,
                )
            ]
        )

        assert repos["summary_repo"].find_by_document_id("doc_del1")
        assert repos["concept_repo"].find_by_document_id("doc_del1")
        assert repos["question_repo"].find_by_document_id("doc_del1")
        assert repos["quiz_repo"].find_quizzes_by_document_id("doc_del1")
        assert repos["flashcard_repo"].find_by_document_id("doc_del1")
        assert repos["topic_repo"].find_by_document_id("doc_del1")
        assert repos["conv_repo"].find_by_document_id("doc_del1")
        assert repos["chunk_repo"].find_by_document_id("doc_del1")

        repos["summary_repo"].delete_by_document_id("doc_del1")
        repos["concept_repo"].delete_by_document_id("doc_del1")
        repos["question_repo"].delete_by_document_id("doc_del1")
        repos["quiz_repo"].delete_quizzes_by_document_id("doc_del1")
        repos["flashcard_repo"].delete_by_document_id("doc_del1")
        repos["topic_repo"].delete_by_document_id("doc_del1")
        for c in repos["conv_repo"].find_by_document_id("doc_del1"):
            repos["msg_repo"].delete_by_conversation_id(c.id)
            repos["conv_repo"].delete(c.id)
        repos["chunk_repo"].delete_by_document_id("doc_del1")
        repos["doc_repo"].delete("doc_del1")

        assert repos["summary_repo"].find_by_document_id("doc_del1") is None
        assert len(repos["concept_repo"].find_by_document_id("doc_del1")) == 0
        assert len(repos["question_repo"].find_by_document_id("doc_del1")) == 0
        assert len(repos["quiz_repo"].find_quizzes_by_document_id("doc_del1")) == 0
        assert len(repos["flashcard_repo"].find_by_document_id("doc_del1")) == 0
        assert len(repos["topic_repo"].find_by_document_id("doc_del1")) == 0
        assert len(repos["conv_repo"].find_by_document_id("doc_del1")) == 0
        assert len(repos["chunk_repo"].find_by_document_id("doc_del1")) == 0
        assert repos["doc_repo"].find_by_id("doc_del1") is None

    def test_delete_nonexistent_document(self, db, repos):
        result = repos["doc_repo"].delete("nonexistent")
        assert result is False

    def test_delete_preserves_other_documents(
        self, db, repos
    ):
        repos["doc_repo"].save(
            Document(
                id="doc1",
                name="a.pdf",
                file_type="pdf",
                status="INDEXED",
            )
        )
        repos["doc_repo"].save(
            Document(
                id="doc2",
                name="b.pdf",
                file_type="pdf",
                status="INDEXED",
            )
        )
        repos["summary_repo"].save(
            LearningSummary(
                document_id="doc1",
                title="S1",
            )
        )
        repos["summary_repo"].save(
            LearningSummary(
                document_id="doc2",
                title="S2",
            )
        )
        repos["chunk_repo"].save_many(
            [
                Chunk(
                    id="ch1",
                    document_id="doc1",
                    content="text1",
                    chunk_index=0,
                ),
                Chunk(
                    id="ch2",
                    document_id="doc2",
                    content="text2",
                    chunk_index=0,
                ),
            ]
        )

        repos["summary_repo"].delete_by_document_id("doc1")
        repos["chunk_repo"].delete_by_document_id("doc1")
        repos["doc_repo"].delete("doc1")

        assert repos["doc_repo"].find_by_id("doc1") is None
        assert repos["doc_repo"].find_by_id("doc2") is not None
        assert repos["summary_repo"].find_by_document_id("doc2") is not None
        assert len(repos["chunk_repo"].find_by_document_id("doc2")) == 1

    def test_duplicate_question_save_handled(
        self, db, repos
    ):
        repos["question_repo"].save_many(
            [
                Question(
                    document_id="doc1",
                    question="Q?",
                    answer="A",
                ),
            ]
        )
        existing = repos["question_repo"].find_by_document_id("doc1")
        assert len(existing) == 1

        repos["question_repo"].delete_by_document_id("doc1")
        repos["question_repo"].save_many(
            [
                Question(
                    document_id="doc1",
                    question="Q?",
                    answer="A",
                ),
            ]
        )
        existing = repos["question_repo"].find_by_document_id("doc1")
        assert len(existing) == 1

    def test_quiz_session_update_does_not_duplicate(
        self, db, repos
    ):
        from app.domain.entities.learning import (
            QuizSession,
        )

        quiz = repos["quiz_repo"].save_quiz(
            Quiz(document_id="doc1", title="T")
        )
        session = repos["quiz_repo"].save_session(
            QuizSession(quiz_id=quiz.id)
        )
        sid = session.id

        repos["quiz_repo"].save_session(
            QuizSession(
                id=sid,
                quiz_id=quiz.id,
                status="completed",
                score=3,
                percentage=75.0,
            )
        )

        found = repos["quiz_repo"].find_session_by_id(sid)
        assert found is not None
        assert found.status == "completed"
        assert found.score == 3
        assert found.percentage == 75.0
