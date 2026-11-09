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
from app.domain.repositories.key_concept_repository import (
    KeyConceptRepository,
)
from app.domain.entities.learning import KeyConcept
from app.core.exceptions import LLMError

logger = logging.getLogger(__name__)


class GenerateKeyConceptsUseCase:

    SYSTEM_INSTRUCTION = (
        "أنت مساعد متخصص في استخراج المفاهيم "
        "الأساسية من المستندات. "
        "أرجع JSON فقط: "
        '[{"term": "...", "definition": "...", '
        '"explanation": "...", "importance": "...", '
        '"topic": "..."}]'
    )

    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilder,
        llm_provider: LLMProvider,
        concept_repo: KeyConceptRepository,
    ) -> None:
        self.retriever = retriever
        self.context_builder = context_builder
        self.llm_provider = llm_provider
        self.concept_repo = concept_repo

    def execute(
        self,
        document_id: str,
    ) -> list[KeyConcept]:
        existing = (
            self.concept_repo.find_by_document_id(
                document_id
            )
        )
        if existing:
            return existing

        query = (
            "المفاهيم والمصطلحات الأساسية في هذا "
            "المستند مع تعريفاتها وأهميتها."
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
            "استخرج المفاهيم الأساسية. "
            "أرجع JSON فقط:\n"
            '[{"term": "المصطلح", '
            '"definition": "التعريف", '
            '"explanation": "الشرح التفصيلي", '
            '"importance": "الأهمية", '
            '"topic": "الموضوع"}]'
        )

        try:
            raw = self.llm_provider.generate(
                prompt=prompt,
                system_instruction=self.SYSTEM_INSTRUCTION,
                temperature=0.3,
            )
        except LLMError as e:
            logger.error(
                f"Concepts generation failed: {e}"
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

        concepts = []
        for item in parsed:
            concepts.append(
                KeyConcept(
                    document_id=document_id,
                    term=item.get("term", ""),
                    definition=item.get(
                        "definition", ""
                    ),
                    explanation=item.get(
                        "explanation", ""
                    ),
                    importance=item.get(
                        "importance", ""
                    ),
                    topic=item.get("topic", ""),
                    sources=sources,
                )
            )

        if concepts:
            return self.concept_repo.save_many(
                concepts
            )
        return concepts

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
