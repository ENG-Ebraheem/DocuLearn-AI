import json
import logging

from app.application.services.rag.retriever import (
    Retriever,
)
from app.application.services.rag.context_builder import (
    ContextBuilder,
)
from app.domain.repositories.llm_provider import (
    LLMProvider,
)
from app.domain.repositories.learning_summary_repository import (
    LearningSummaryRepository,
)
from app.domain.entities.learning import (
    LearningSummary,
)
from app.core.exceptions import LLMError

logger = logging.getLogger(__name__)


class GenerateSummaryUseCase:

    SYSTEM_INSTRUCTION = (
        "أنت مساعد متخصص في إنشاء ملخصات تعليمية "
        "من المستندات. أجب بصيغة JSON فقط. "
        "لا ت добав أي نص قبل أو بعد JSON. "
        "الـ JSON يجب أن يحتوي على: "
        "title (string), overview (string), "
        "sections (list of objects مع title وcontent), "
        "key_takeaways (list of strings)."
    )

    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilder,
        llm_provider: LLMProvider,
        summary_repo: LearningSummaryRepository,
    ) -> None:
        self.retriever = retriever
        self.context_builder = context_builder
        self.llm_provider = llm_provider
        self.summary_repo = summary_repo

    def execute(
        self,
        document_id: str,
        summary_length: str = "medium",
    ) -> LearningSummary:
        existing = self.summary_repo.find_by_document_id(
            document_id
        )
        if existing:
            return existing

        query = (
            "الملخص العام للمستند: العنوان، "
            "المحتوى الرئيسي، الأقسام، "
            "وأهم النقاط."
        )

        retrieved = self.retriever.retrieve(
            query=query,
            document_id=document_id,
            top_k=8,
        )

        context = self.context_builder.build(
            query=query,
            retrieved_chunks=retrieved,
        )

        length_instruction = {
            "short": "ملخص موجز في 3-4 جمل.",
            "medium": "ملخص متوسط يغطي النقاط الرئيسية.",
            "detailed": "ملخص تفصيلي يغطي جميع الأقسام.",
        }.get(summary_length, "ملخص متوسط.")

        prompt = (
            f"السياق:\n{context.context_text}\n\n"
            f"المطلوب: {length_instruction}\n\n"
            "أرجع JSON فقط:\n"
            "{\n"
            '  "title": "عنوان المستند",\n'
            '  "overview": "نظرة عامة",\n'
            '  "sections": [\n'
            '    {"title": "قسم", "content": "محتوى"}\n'
            "  ],\n"
            '  "key_takeaways": ["نقطة 1", "نقطة 2"]\n'
            "}"
        )

        try:
            raw = self.llm_provider.generate(
                prompt=prompt,
                system_instruction=self.SYSTEM_INSTRUCTION,
                temperature=0.3,
            )
        except LLMError as e:
            logger.error(f"Summary generation failed: {e}")
            raise

        parsed = self._parse_json(raw)

        sources = [
            {
                "chunk_id": c.chunk_id,
                "document_id": c.document_id,
                "document_name": c.document_name,
                "page": c.metadata.get("page"),
                "score": c.score,
            }
            for c in context.chunks
        ]

        summary = LearningSummary(
            document_id=document_id,
            title=parsed.get("title", ""),
            overview=parsed.get("overview", ""),
            sections=parsed.get("sections", []),
            key_takeaways=parsed.get(
                "key_takeaways", []
            ),
            sources=sources,
            summary_length=summary_length,
        )

        return self.summary_repo.save(summary)

    def _parse_json(self, raw: str) -> dict:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [
                l
                for l in lines
                if not l.strip().startswith("```")
            ]
            text = "\n".join(lines)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(
                        text[start:end]
                    )
                except json.JSONDecodeError:
                    pass

            return {
                "title": "ملخص المستند",
                "overview": text[:500]
                if text
                else "",
                "sections": [],
                "key_takeaways": [],
            }
