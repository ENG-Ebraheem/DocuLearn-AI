"""Application-facing façade used by the presentation layer.

The façade intentionally exposes product actions rather than database, FAISS, or SDK objects.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

logger = logging.getLogger(__name__)

from app.application.services.document_processing_pipeline import (
    DocumentProcessingPipeline,
)
from app.application.services.learning import (
    GenerateFlashcardsUseCase,
    GenerateKeyConceptsUseCase,
    GenerateQuestionsUseCase,
    GenerateQuizUseCase,
    GenerateSummaryUseCase,
    LearningProgressService,
    QuizScoringService,
)
from app.application.services.rag.context_builder import ContextBuilder
from app.application.services.rag.hybrid_retriever import HybridRetriever
from app.application.services.rag.lexical_retriever import LexicalRetriever
from app.application.services.rag.qa_service import QAService
from app.application.services.rag.retriever import Retriever
from app.config.settings import settings
from app.domain.entities.chat_message import ChatMessage
from app.domain.entities.conversation import Conversation
from app.domain.entities.course import Course
from app.domain.entities.learning import FlashcardReview, QuizSession


@dataclass
class PlatformService:
    """Use cases and read models required by the DocuLearn presentation."""

    session: object
    doc_repo: object
    chunk_repo: object
    conv_repo: object
    msg_repo: object
    summary_repo: object
    concept_repo: object
    question_repo: object
    quiz_repo: object
    flashcard_repo: object
    topic_repo: object
    course_repo: object
    embedding_provider: object
    vector_store: object
    llm_provider: object

    def close(self) -> None:
        self.session.close()

    # Library and organization -------------------------------------------------
    def list_documents(self):
        return self.doc_repo.find_all()

    def health_check(self) -> dict:
        """Perform application readiness check across core dependencies."""
        db_ok = False
        try:
            self.doc_repo.find_all()
            db_ok = True
        except Exception as e:
            logger.error("Health check DB error: %s", e)

        vector_ok = False
        try:
            vector_ok = self.vector_store is not None
        except Exception as e:
            logger.error("Health check VectorStore error: %s", e)

        embedding_ok = False
        try:
            embedding_ok = self.embedding_provider is not None
        except Exception as e:
            logger.error("Health check EmbeddingProvider error: %s", e)

        llm_ok = settings.is_api_key_configured or self.llm_provider.is_available()

        all_ok = db_ok and vector_ok and embedding_ok
        status = "healthy" if all_ok else "degraded"

        return {
            "status": status,
            "database": db_ok,
            "vector_store": vector_ok,
            "embedding_provider": embedding_ok,
            "llm_configured": llm_ok,
            "details": {
                "environment": settings.environment,
                "llm_provider": settings.llm_provider,
                "llm_model": settings.llm_model,
            },
        }

    def get_document(self, document_id: str):
        return self.doc_repo.find_by_id(document_id)

    def list_indexed_documents(self):
        return [doc for doc in self.list_documents() if doc.status == "INDEXED"]

    def list_courses(self):
        return self.course_repo.find_all()

    def create_course(self, name: str):
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("اسم المادة مطلوب.")
        return self.course_repo.save(Course(name=clean_name))

    def ingest_uploaded_document(
        self, file_name: str, content: bytes, course_id: str | None = None
    ):
        if len(content) > settings.max_upload_size_bytes:
            raise ValueError(f"حجم الملف يتجاوز الحد المسموح به ({settings.max_upload_size_mb} ميجابايت).")

        raw_name = Path(file_name).name
        safe_name = re.sub(r"[\x00-\x1f\x7f]", "", raw_name).strip() or "document.pdf"
        suffix = Path(safe_name).suffix.lower()

        if suffix not in settings.allowed_extensions:
            raise ValueError("نوع الملف غير مدعوم.")

        logger.info("Document upload initiated: name=%s, size=%d bytes", safe_name, len(content))

        storage_name = f"{uuid4().hex}{suffix}"
        path = settings.uploads_path / storage_name
        path.write_bytes(content)

        result = DocumentProcessingPipeline().ingest(
            file_path=str(path),
            document_repo=self.doc_repo,
            chunk_repo=self.chunk_repo,
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
            document_name=safe_name,
        )
        result.document.file_path = str(path)
        if course_id:
            result.document.course_id = course_id
        result.document = self.doc_repo.update(result.document)
        return result

    def delete_document(self, document_id: str) -> None:
        document = self.get_document(document_id)
        if document is None:
            raise ValueError("المستند غير موجود.")

        self.summary_repo.delete_by_document_id(document_id)
        self.concept_repo.delete_by_document_id(document_id)
        self.question_repo.delete_by_document_id(document_id)
        self.quiz_repo.delete_quizzes_by_document_id(document_id)
        self.flashcard_repo.delete_by_document_id(document_id)
        self.topic_repo.delete_by_document_id(document_id)
        for conversation in self.conv_repo.find_by_document_id(document_id):
            self.msg_repo.delete_by_conversation_id(conversation.id)
            self.conv_repo.delete(conversation.id)
        self.chunk_repo.delete_by_document_id(document_id)
        self.vector_store.delete_by_document_id(document_id)
        self.doc_repo.delete(document_id)

        if document.file_path:
            path = Path(document.file_path)
            if path.exists() and path.parent.resolve() == settings.uploads_path.resolve():
                path.unlink()

    def delete_course(self, course_id: str) -> None:
        course = self.course_repo.find_by_id(course_id)
        if course is None:
            raise ValueError("المادة غير موجودة.")
        for document in self.doc_repo.find_by_course_id(course_id):
            document.course_id = None
            self.doc_repo.update(document)
        self.course_repo.delete(course_id)

    # Progress and analytics ---------------------------------------------------
    def progress_service(self) -> LearningProgressService:
        return LearningProgressService(
            doc_repo=self.doc_repo,
            chunk_repo=self.chunk_repo,
            summary_repo=self.summary_repo,
            concept_repo=self.concept_repo,
            question_repo=self.question_repo,
            quiz_repo=self.quiz_repo,
            flashcard_repo=self.flashcard_repo,
            topic_repo=self.topic_repo,
        )

    def global_stats(self):
        return self.progress_service().get_stats()

    def document_stats(self, document_id: str):
        return self.progress_service().get_document_stats(document_id)

    def document_topics(self, document_id: str):
        return self.progress_service().get_document_topics(document_id)

    def course_stats(self, course_id: str):
        return self.progress_service().get_course_stats(course_id)

    def _create_hybrid_retriever(self):
        dense_retriever = Retriever(
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
        )
        lexical_retriever = LexicalRetriever(chunk_repo=self.chunk_repo)
        return HybridRetriever(
            dense_retriever=dense_retriever,
            lexical_retriever=lexical_retriever,
        )

    # Chat ---------------------------------------------------------------------
    def _qa_service(self) -> QAService:
        retriever = self._create_hybrid_retriever()
        return QAService(
            retriever=retriever,
            context_builder=ContextBuilder(),
            llm_provider=self.llm_provider,
        )

    def answer_document_question(self, query: str, document_id: str, history: list[dict]):
        return self._qa_service().ask(query=query, document_id=document_id, history=history)

    def answer_general_question(self, query: str, history: list[dict]):
        return self._qa_service().general_chat(query=query, history=history)

    def get_document_conversation(self, document_id: str):
        conversations = self.conv_repo.find_by_document_id(document_id)
        if conversations:
            return conversations[0]
        document = self.get_document(document_id)
        title = f"محادثة - {document.name if document else 'مستند'}"
        return self.conv_repo.save(Conversation(document_id=document_id, title=title))

    def document_messages(self, document_id: str):
        conversation = self.get_document_conversation(document_id)
        return conversation, self.msg_repo.find_by_conversation_id(conversation.id)

    def save_document_message(
        self, conversation_id: str, role: str, content: str, sources: list | None = None
    ):
        return self.msg_repo.save(
            ChatMessage(
                conversation_id=conversation_id,
                role=role,
                content=content,
                sources=sources or [],
            )
        )

    # Learning -----------------------------------------------------------------
    def _learning_retriever(self):
        return self._create_hybrid_retriever()

    def summary_for(self, document_id: str):
        return self.summary_repo.find_by_document_id(document_id)

    def generate_summary(self, document_id: str):
        return GenerateSummaryUseCase(
            retriever=self._learning_retriever(),
            context_builder=ContextBuilder(),
            llm_provider=self.llm_provider,
            summary_repo=self.summary_repo,
        ).execute(document_id)

    def delete_summary(self, document_id: str) -> None:
        self.summary_repo.delete_by_document_id(document_id)

    def concepts_for(self, document_id: str):
        return self.concept_repo.find_by_document_id(document_id)

    def generate_concepts(self, document_id: str):
        return GenerateKeyConceptsUseCase(
            retriever=self._learning_retriever(),
            context_builder=ContextBuilder(),
            llm_provider=self.llm_provider,
            concept_repo=self.concept_repo,
        ).execute(document_id)

    def delete_concepts(self, document_id: str) -> None:
        self.concept_repo.delete_by_document_id(document_id)

    def questions_for(self, document_id: str):
        return self.question_repo.find_by_document_id(document_id)

    def generate_questions(self, document_id: str):
        return GenerateQuestionsUseCase(
            retriever=self._learning_retriever(),
            context_builder=ContextBuilder(),
            llm_provider=self.llm_provider,
            question_repo=self.question_repo,
        ).execute(document_id)

    def delete_questions(self, document_id: str) -> None:
        self.question_repo.delete_by_document_id(document_id)

    def quiz_for(self, document_id: str):
        quizzes = self.quiz_repo.find_quizzes_by_document_id(document_id)
        if not quizzes:
            return None, []
        quiz = quizzes[0]
        return quiz, self.quiz_repo.find_questions_by_quiz_id(quiz.id)

    def generate_quiz(self, document_id: str):
        return GenerateQuizUseCase(
            retriever=self._learning_retriever(),
            context_builder=ContextBuilder(),
            llm_provider=self.llm_provider,
            quiz_repo=self.quiz_repo,
        ).execute(document_id)

    def start_quiz(self, quiz_id: str):
        return self.quiz_repo.save_session(QuizSession(quiz_id=quiz_id))

    def submit_quiz(self, session_id: str, answers: list[dict]):
        return QuizScoringService(quiz_repo=self.quiz_repo).submit_session(
            session_id=session_id, answers=answers
        )

    def quiz_results(self, session_id: str):
        return QuizScoringService(quiz_repo=self.quiz_repo).get_results(session_id)

    def reset_quiz_sessions(self, quiz_id: str) -> None:
        self.quiz_repo.delete_sessions_by_quiz_id(quiz_id)

    def flashcards_for(self, document_id: str):
        return self.flashcard_repo.find_by_document_id(document_id)

    def generate_flashcards(self, document_id: str):
        return GenerateFlashcardsUseCase(
            retriever=self._learning_retriever(),
            context_builder=ContextBuilder(),
            llm_provider=self.llm_provider,
            flashcard_repo=self.flashcard_repo,
        ).execute(document_id)

    def review_flashcard(self, flashcard_id: str, rating: str):
        return self.flashcard_repo.save_review(
            FlashcardReview(flashcard_id=flashcard_id, rating=rating)
        )
