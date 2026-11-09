import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.services.platform_service import PlatformService
from app.domain.entities.chunk import Chunk
from app.domain.entities.document import Document
from app.infrastructure.database.database import Base
from app.infrastructure.database.repositories import (
    ChatMessageRepositoryImpl,
    ChunkRepositoryImpl,
    ConversationRepositoryImpl,
    CourseRepositoryImpl,
    DocumentRepositoryImpl,
    FlashcardRepositoryImpl,
    KeyConceptRepositoryImpl,
    LearningSummaryRepositoryImpl,
    QuestionRepositoryImpl,
    QuizRepositoryImpl,
    TopicRepositoryImpl,
)
from app.infrastructure.llm.fake_llm_provider import FakeLLMProvider


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestPhase7HardeningIntegration:

    def test_full_platform_end_to_end_journey(self, db_session):
        doc_repo = DocumentRepositoryImpl(db_session)
        chunk_repo = ChunkRepositoryImpl(db_session)
        course_repo = CourseRepositoryImpl(db_session)
        summary_repo = LearningSummaryRepositoryImpl(db_session)
        concept_repo = KeyConceptRepositoryImpl(db_session)
        question_repo = QuestionRepositoryImpl(db_session)
        quiz_repo = QuizRepositoryImpl(db_session)
        flashcard_repo = FlashcardRepositoryImpl(db_session)
        topic_repo = TopicRepositoryImpl(db_session)
        conv_repo = ConversationRepositoryImpl(db_session)
        msg_repo = ChatMessageRepositoryImpl(db_session)

        class FakeVectorStore:
            def add(self, chunks, embeddings): pass
            def save(self): pass
            def search(self, query_embedding, top_k=5, document_id=None): return []
            def delete_by_document_id(self, document_id): pass

        class FakeEmbeddings:
            def embed_text(self, text): return [0.1] * 384
            def embed_documents(self, texts): return [[0.1] * 384 for _ in texts]

        fake_llm = FakeLLMProvider(response="إجابة فحص الجودة والتكامل.")

        service = PlatformService(
            session=db_session,
            doc_repo=doc_repo,
            chunk_repo=chunk_repo,
            course_repo=course_repo,
            summary_repo=summary_repo,
            concept_repo=concept_repo,
            question_repo=question_repo,
            quiz_repo=quiz_repo,
            flashcard_repo=flashcard_repo,
            topic_repo=topic_repo,
            conv_repo=conv_repo,
            msg_repo=msg_repo,
            vector_store=FakeVectorStore(),
            embedding_provider=FakeEmbeddings(),
            llm_provider=fake_llm,
        )

        # 1. Health check
        health = service.health_check()
        assert health["status"] == "healthy"

        # 2. Ingest document
        result = service.ingest_uploaded_document("test_arabic.txt", "هذا نص تجريبي باللغة العربية للتعلم.".encode("utf-8"))
        doc_id = result.document.id
        assert result.document.status == "INDEXED"

        # 3. Create course and assign document
        course = service.create_course("مادة الذكاء الاصطناعي")
        result.document.course_id = course.id
        doc_repo.update(result.document)

        # 4. Generate summary and verify isolation
        summary = service.generate_summary(doc_id)
        assert summary is not None

        # 5. Delete document and verify cascade
        service.delete_document(doc_id)
        assert doc_repo.find_by_id(doc_id) is None
        assert summary_repo.find_by_document_id(doc_id) is None

        # 6. Verify course remains valid
        assert course_repo.find_by_id(course.id) is not None
