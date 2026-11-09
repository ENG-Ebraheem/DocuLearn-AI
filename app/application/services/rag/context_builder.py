from dataclasses import dataclass, field

from app.application.services.rag.retriever import (
    RetrievedChunk,
)


@dataclass
class BuiltContext:
    context_text: str
    chunks: list[RetrievedChunk]
    sources: list[dict]
    query: str


class ContextBuilder:

    def __init__(
        self,
        max_chunks: int = 5,
        max_context_length: int = 4000,
    ) -> None:
        self.max_chunks = max_chunks
        self.max_context_length = max_context_length

    def build(
        self,
        query: str,
        retrieved_chunks: list[RetrievedChunk],
    ) -> BuiltContext:
        unique_chunks = self._deduplicate(
            retrieved_chunks
        )

        selected = unique_chunks[: self.max_chunks]

        context_text = self._format_context(selected)

        if (
            len(context_text) > self.max_context_length
        ):
            context_text = context_text[
                : self.max_context_length
            ]

        sources = self._build_sources(selected)

        return BuiltContext(
            context_text=context_text,
            chunks=selected,
            sources=sources,
            query=query,
        )

    def _deduplicate(
        self,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        seen = set()
        unique = []

        for chunk in chunks:
            if chunk.chunk_id not in seen:
                seen.add(chunk.chunk_id)
                unique.append(chunk)

        return unique

    def _format_context(
        self, chunks: list[RetrievedChunk]
    ) -> str:
        parts = []

        for i, chunk in enumerate(chunks, 1):
            page = chunk.metadata.get("page")
            page_info = (
                f", صفحة {page}" if page else ""
            )
            parts.append(
                f"[المصدر {i}] "
                f"({chunk.document_name}"
                f"{page_info})\n"
                f"{chunk.content}"
            )

        return "\n\n---\n\n".join(parts)

    def _build_sources(
        self, chunks: list[RetrievedChunk]
    ) -> list[dict]:
        sources = []

        for chunk in chunks:
            sources.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "document_name": chunk.document_name,
                    "chunk_index": chunk.chunk_index,
                    "page": chunk.metadata.get("page"),
                    "score": chunk.score,
                    "excerpt": chunk.content[:200]
                    + "..."
                    if len(chunk.content) > 200
                    else chunk.content,
                }
            )

        return sources
