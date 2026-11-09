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
from app.domain.repositories.flashcard_repository import (
    FlashcardRepository,
)
from app.domain.entities.learning import Flashcard
from app.core.exceptions import LLMError

logger = logging.getLogger(__name__)


class GenerateFlashcardsUseCase:

    SYSTEM_INSTRUCTION = (
        "أنت مساعد متخصص في إنشاء بطاقات تعليمية "
        "(Flashcards). "
        "أرجع JSON فقط: "
        '[{"front": "السؤال على البطاقة", '
        '"back": "الإجابة", '
        '"topic": "الموضوع"}]'
    )

    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilder,
        llm_provider: LLMProvider,
        flashcard_repo: FlashcardRepository,
    ) -> None:
        self.retriever = retriever
        self.context_builder = context_builder
        self.llm_provider = llm_provider
        self.flashcard_repo = flashcard_repo

    def execute(
        self,
        document_id: str,
        count: int = 10,
    ) -> list[Flashcard]:
        existing = (
            self.flashcard_repo.find_by_document_id(
                document_id
            )
        )
        if existing:
            return existing

        query = (
            "المفاهيم والتعريفات والحقائق المهمة "
            "في هذا المستند."
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

        prompt = (
            f"السياق:\n{context.context_text}\n\n"
            f"أنشئ {count} بطاقات تعليمية. "
            "أرجع JSON فقط:\n"
            '[{"front": "السؤال", '
            '"back": "الإجابة", '
            '"topic": "الموضوع"}]'
        )

        try:
            raw = self.llm_provider.generate(
                prompt=prompt,
                system_instruction=self.SYSTEM_INSTRUCTION,
                temperature=0.4,
            )
        except LLMError as e:
            logger.error(
                f"Flashcards generation failed: {e}"
            )
            raise

        parsed = self._parse_json_array(raw)

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

        flashcards = []
        for item in parsed:
            fc = Flashcard(
                document_id=document_id,
                front=item.get("front", ""),
                back=item.get("back", ""),
                topic=item.get("topic", ""),
                sources=sources,
            )
            if fc.front and fc.back:
                flashcards.append(fc)

        if flashcards:
            return self.flashcard_repo.save_many(
                flashcards
            )
        return flashcards

    def _parse_json_array(self, raw: str) -> list:
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
            result = json.loads(text)
            if isinstance(result, list):
                return result
            return []
        except json.JSONDecodeError:
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(
                        text[start:end]
                    )
                except json.JSONDecodeError:
                    pass
            return []
