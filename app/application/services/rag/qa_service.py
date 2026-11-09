"""Grounded document Q&A and separate general-AI chat."""

from __future__ import annotations

import logging

from app.application.services.rag.answer_response import AnswerResponse, Source
from app.application.services.rag.context_builder import ContextBuilder
from app.application.services.rag.prompt_builder import PromptBuilder
from app.application.services.rag.retriever import Retriever
from app.config.settings import settings
from app.core.exceptions import LLMError
from app.domain.repositories.llm_provider import LLMProvider
from app.infrastructure.llm.gemini_provider import FallbackLLMProvider

logger = logging.getLogger(__name__)

INSUFFICIENT_CONTEXT_MESSAGE = "لا توجد معلومات كافية في المستند للإجابة عن هذا السؤال."


class QAService:
    """End-to-end document QA that only answers with sufficiently relevant context."""

    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilder | None = None,
        llm_provider: LLMProvider | None = None,
        min_context_score: float | None = None,
    ) -> None:
        self.retriever = retriever
        self.context_builder = context_builder or ContextBuilder()
        self.llm_provider = llm_provider or FallbackLLMProvider()
        self.prompt_builder = PromptBuilder()
        self.min_context_score = (
            settings.rag_min_context_score
            if min_context_score is None
            else min_context_score
        )

    def ask(
        self,
        query: str,
        document_id: str | None = None,
        history: list[dict] | None = None,
    ) -> AnswerResponse:
        """Answer from one document only after retrieval and context validation."""
        retrieved = self.retriever.retrieve(query=query, document_id=document_id)
        context = self.context_builder.build(query=query, retrieved_chunks=retrieved)

        if not self._has_sufficient_context(context.chunks):
            return self._insufficient_context_response()

        sources = self._build_sources(context.chunks)
        confidence = self._estimate_confidence(context.chunks)
        if not self.llm_provider.is_available():
            return self._offline_response(sources, confidence)

        prompt = self.prompt_builder.build(
            query=query,
            context_chunks=context.chunks,
            history=history,
        )
        instruction = self.prompt_builder.build_instruction(language="ar")
        try:
            answer_text = self.llm_provider.generate(
                prompt=prompt,
                system_instruction=instruction,
            )
        except LLMError as error:
            logger.error("LLM generation failed: %s", error)
            return self._offline_response(sources, confidence)

        return AnswerResponse(
            answer=answer_text,
            sources=sources,
            confidence=confidence,
            model_used=self.llm_provider.model_name,
            has_sufficient_context=True,
        )

    def _has_sufficient_context(self, chunks: list) -> bool:
        if not chunks:
            return False
        return max(chunk.score for chunk in chunks) >= self.min_context_score

    def _insufficient_context_response(self) -> AnswerResponse:
        """Keep weak matches out of the answer and prompt a deliberate user choice."""
        return AnswerResponse(
            answer=INSUFFICIENT_CONTEXT_MESSAGE,
            sources=[],
            confidence=0.0,
            model_used="none",
            has_sufficient_context=False,
        )

    def _offline_response(self, sources: list[Source], confidence: float) -> AnswerResponse:
        excerpts = "\n".join(
            f"{index}. {source.document_name}: {source.excerpt}"
            for index, source in enumerate(sources, 1)
        )
        return AnswerResponse(
            answer=(
                "لا يمكن الاتصال بالنموذج اللغوي حاليًا. "
                "إليك المقاطع ذات الصلة من المستند:\n\n"
                f"{excerpts}"
            ),
            sources=sources,
            confidence=confidence,
            model_used="none",
            has_sufficient_context=True,
        )

    def _build_sources(self, chunks) -> list[Source]:
        return [
            Source(
                document_id=chunk.document_id,
                document_name=chunk.document_name,
                page=chunk.metadata.get("page"),
                chunk_id=chunk.chunk_id,
                score=chunk.score,
                excerpt=chunk.content[:200],
            )
            for chunk in chunks
        ]

    def general_chat(
        self,
        query: str,
        history: list[dict] | None = None,
    ) -> AnswerResponse:
        """Answer a general question without retrieval or document sources."""
        if not self.llm_provider.is_available():
            return AnswerResponse(
                answer="تعذر الاتصال بالنموذج اللغوي حاليًا. حاول مرة أخرى.",
                sources=[],
                confidence=0.0,
                model_used="none",
                has_sufficient_context=False,
            )

        history_text = PromptBuilder._format_history(PromptBuilder(), history) if history else ""
        parts = []
        if history_text:
            parts.append(f"المحادثة السابقة:\n{history_text}")
        parts.append(f"السؤال:\n{query}")
        try:
            answer_text = self.llm_provider.generate(
                prompt="\n\n".join(parts),
                system_instruction=(
                    "أنت مساعد ذكي عام. أجب على أسئلة المستخدم بشكل واضح ومفيد. "
                    "استخدم نفس لغة السؤال. إذا لم تكن متأكدًا، قل ذلك بوضوح."
                ),
            )
        except LLMError:
            return AnswerResponse(
                answer="حدث خطأ أثناء إنشاء الإجابة. حاول مرة أخرى.",
                sources=[],
                confidence=0.0,
                model_used="none",
                has_sufficient_context=False,
            )

        return AnswerResponse(
            answer=answer_text,
            sources=[],
            confidence=1.0,
            model_used=self.llm_provider.model_name,
            has_sufficient_context=False,
        )

    def _estimate_confidence(self, chunks) -> float:
        return min(max(chunk.score for chunk in chunks), 1.0) if chunks else 0.0
