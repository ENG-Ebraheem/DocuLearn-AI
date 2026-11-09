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
from app.domain.repositories.quiz_repository import (
    QuizRepository,
)
from app.domain.entities.learning import (
    Quiz,
    QuizQuestion,
)
from app.core.exceptions import LLMError

logger = logging.getLogger(__name__)


class GenerateQuizUseCase:

    SYSTEM_INSTRUCTION = (
        "أنت مساعد متخصص في إنشاء اختبارات تعليمية. "
        "أرجع JSON فقط: "
        '{"title": "...", "description": "...", '
        '"questions": [{"question": "...", '
        '"type": "MCQ|TRUE_FALSE|SHORT_ANSWER", '
        '"options": ["أ", "ب", "ج", "د"], '
        '"correct_answer": "أ", '
        '"explanation": "...", '
        '"difficulty": "EASY|MEDIUM|HARD", '
        '"topic": "..."}]}'
    )

    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilder,
        llm_provider: LLMProvider,
        quiz_repo: QuizRepository,
    ) -> None:
        self.retriever = retriever
        self.context_builder = context_builder
        self.llm_provider = llm_provider
        self.quiz_repo = quiz_repo

    def execute(
        self,
        document_id: str,
        number_of_questions: int = 5,
        difficulty: str = "MEDIUM",
        question_types: list | None = None,
    ) -> Quiz:
        query = (
            "المحتوى التعليمي الرئيسي والتعريفات "
            "والعمليات في المستند."
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

        types_str = "MCQ, TRUE_FALSE, SHORT_ANSWER"
        if question_types:
            types_str = ", ".join(question_types)

        prompt = (
            f"السياق:\n{context.context_text}\n\n"
            f"أنشئ اختباراً بـ{number_of_questions} "
            f"أسئلة. الصعوبة: {difficulty}. "
            f"الأنواع: {types_str}. "
            "أرجع JSON فقط:\n"
            '{"title": "عنوان الاختبار", '
            '"description": "وصف", '
            '"questions": [{"question": "السؤال", '
            f'"type": "MCQ", '
            '"options": ["أ", "ب", "ج", "د"], '
            '"correct_answer": "أ", '
            '"explanation": "الشرح", '
            f'"difficulty": "{difficulty}", '
            '"topic": "الموضوع"}]}'
        )

        try:
            raw = self.llm_provider.generate(
                prompt=prompt,
                system_instruction=self.SYSTEM_INSTRUCTION,
                temperature=0.4,
            )
        except LLMError as e:
            logger.error(
                f"Quiz generation failed: {e}"
            )
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

        quiz = Quiz(
            document_id=document_id,
            title=parsed.get("title", "اختبار"),
            description=parsed.get("description", ""),
            difficulty=difficulty,
            question_types=question_types or [],
            number_of_questions=number_of_questions,
        )
        quiz = self.quiz_repo.save_quiz(quiz)

        quiz_questions = []
        for i, q in enumerate(
            parsed.get("questions", [])
        ):
            qq = QuizQuestion(
                quiz_id=quiz.id,
                question=q.get("question", ""),
                question_type=q.get("type", "MCQ"),
                options=q.get("options", []),
                correct_answer=q.get(
                    "correct_answer", ""
                ),
                explanation=q.get("explanation", ""),
                difficulty=q.get(
                    "difficulty", difficulty
                ),
                topic=q.get("topic", ""),
                sources=sources,
                order_index=i,
            )
            if qq.question and qq.correct_answer:
                quiz_questions.append(qq)

        if quiz_questions:
            self.quiz_repo.save_questions(
                quiz_questions
            )

        return quiz

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
            result = json.loads(text)
            if isinstance(result, dict):
                return result
            return {}
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
                "title": "اختبار",
                "questions": [],
            }
