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
from app.domain.repositories.question_repository import (
    QuestionRepository,
)
from app.domain.entities.learning import Question
from app.core.exceptions import LLMError

logger = logging.getLogger(__name__)


class GenerateQuestionsUseCase:

    SYSTEM_INSTRUCTION = (
        "أنت مساعد متخصص في إنشاء أسئلة تعليمية "
        "من المستندات. "
        "أرجع JSON فقط: "
        '[{"question": "...", "answer": "...", '
        '"difficulty": "EASY|MEDIUM|HARD", '
        '"question_type": "DEFINITION|UNDERSTANDING|'
        'COMPARISON|APPLICATION|ANALYSIS", '
        '"topic": "..."}]'
    )

    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilder,
        llm_provider: LLMProvider,
        question_repo: QuestionRepository,
    ) -> None:
        self.retriever = retriever
        self.context_builder = context_builder
        self.llm_provider = llm_provider
        self.question_repo = question_repo

    def execute(
        self,
        document_id: str,
        difficulty: str = "MEDIUM",
        count: int = 5,
    ) -> list[Question]:
        existing = (
            self.question_repo.find_by_document_id(
                document_id
            )
        )
        if existing:
            return existing

        query = (
            "المحتوى التعليمي الرئيسي في المستند "
            "والتعريفات والمفاهيم والعمليات."
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
            f"أنشئ {count} أسئلة "
            f"بمستوى صعوبة {difficulty}. "
            "أرجع JSON فقط:\n"
            '[{"question": "السؤال", '
            '"answer": "الإجابة", '
            f'"difficulty": "{difficulty}", '
            '"question_type": "UNDERSTANDING", '
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
                f"Questions generation failed: {e}"
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

        questions = []
        for item in parsed:
            q = Question(
                document_id=document_id,
                question=item.get("question", ""),
                answer=item.get("answer", ""),
                difficulty=item.get(
                    "difficulty", difficulty
                ),
                question_type=item.get(
                    "question_type", "UNDERSTANDING"
                ),
                topic=item.get("topic", ""),
                sources=sources,
            )
            if q.question and q.answer:
                questions.append(q)

        if questions:
            return self.question_repo.save_many(
                questions
            )
        return questions

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
