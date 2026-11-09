from app.application.services.rag.retriever import (
    RetrievedChunk,
)


SYSTEM_INSTRUCTION_AR = (
    "أنت مساعد ذكي متخصص في شرح وتحليل المحتوى "
    "الوثائقي. أجب فقط بناءً على السياق المُعطى. "
    "إذا لم تجد الإجابة في السياق، قل ذلك بوضوح. "
    "استخدم نفس لغة السؤال في الإجابة. "
    "احتفظ بالمصطلحات التقنية بالغة الإنجليزية "
    "بين قوسين عند الضرورة."
)

SYSTEM_INSTRUCTION_EN = (
    "You are a helpful assistant specialized in "
    "document analysis. Answer ONLY based on the "
    "provided context. If the information is not "
    "in the context, say so clearly. Respond in "
    "the same language as the question. Keep "
    "English technical terms in parentheses when "
    "necessary."
)


class PromptBuilder:
    """Build grounded prompts for RAG QA."""

    def build(
        self,
        query: str,
        context_chunks: list[RetrievedChunk],
        history: list[dict] | None = None,
    ) -> str:
        context_text = self._format_chunks(
            context_chunks
        )

        history_text = ""
        if history:
            history_text = (
                self._format_history(history)
            )

        parts = []

        if history_text:
            parts.append(
                f"المحادثة السابقة:\n{history_text}"
            )

        parts.append(
            f"السياق المستخرج من المستند:\n"
            f"{context_text}"
        )
        parts.append(
            f"السؤال:\n{query}"
        )
        parts.append(
            "أجب بناءً على السياق فقط. "
            "إذا لم تجد الإجابة، قل: "
            "'لا تتوفر معلومات كافية في المستند "
            "للإجابة على هذا السؤال.'"
        )

        return "\n\n".join(parts)

    def build_instruction(
        self, language: str = "ar"
    ) -> str:
        if language == "ar":
            return SYSTEM_INSTRUCTION_AR
        return SYSTEM_INSTRUCTION_EN

    def _format_chunks(
        self,
        chunks: list[RetrievedChunk],
    ) -> str:
        parts = []

        for i, chunk in enumerate(chunks, 1):
            page = chunk.metadata.get("page")
            page_info = (
                f" (صفحة {page})" if page else ""
            )
            parts.append(
                f"[المصدر {i}] "
                f"({chunk.document_name}"
                f"{page_info}):\n"
                f"{chunk.content}"
            )

        return "\n\n---\n\n".join(parts)

    def _format_history(
        self,
        history: list[dict],
    ) -> str:
        lines = []

        for msg in history[-6:]:
            role = "المستخدم" if msg.get("role") == "user" else "المساعد"
            lines.append(f"{role}: {msg.get('content', '')}")

        return "\n".join(lines)
