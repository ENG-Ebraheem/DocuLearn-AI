"""Application composition root.

Only this module knows the concrete SQLAlchemy, FAISS, embedding, and LLM classes.
"""

from __future__ import annotations

from functools import lru_cache

from app.application.services.platform_service import PlatformService
from app.infrastructure.database import get_session, init_db
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
from app.infrastructure.embeddings import SentenceTransformerEmbeddingProvider
from app.infrastructure.llm.gemini_provider import FallbackLLMProvider
from app.infrastructure.vector_store import FAISSVectorStore


@lru_cache(maxsize=1)
def _shared_resources() -> tuple[object, object, object]:
    """Reuse costly and stateless resources across Streamlit reruns."""
    return (
        SentenceTransformerEmbeddingProvider(),
        FAISSVectorStore(),
        FallbackLLMProvider(),
    )


def create_platform_service() -> PlatformService:
    """Create one request-scoped database session with shared heavy resources."""
    init_db()
    session = get_session()
    embedding_provider, vector_store, llm_provider = _shared_resources()
    return PlatformService(
        session=session,
        doc_repo=DocumentRepositoryImpl(session),
        chunk_repo=ChunkRepositoryImpl(session),
        conv_repo=ConversationRepositoryImpl(session),
        msg_repo=ChatMessageRepositoryImpl(session),
        summary_repo=LearningSummaryRepositoryImpl(session),
        concept_repo=KeyConceptRepositoryImpl(session),
        question_repo=QuestionRepositoryImpl(session),
        quiz_repo=QuizRepositoryImpl(session),
        flashcard_repo=FlashcardRepositoryImpl(session),
        topic_repo=TopicRepositoryImpl(session),
        course_repo=CourseRepositoryImpl(session),
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        llm_provider=llm_provider,
    )
