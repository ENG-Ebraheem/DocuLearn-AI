"""Hybrid Retrieval System combining Dense Vector Search and Lexical BM25 Search."""

from __future__ import annotations

from typing import Literal

from app.application.services.rag.lexical_retriever import LexicalRetriever
from app.application.services.rag.retriever import RetrievedChunk, Retriever


class HybridRetriever:
    """Fuses Dense Vector Search and Lexical Keyword Search using RRF or Weighted Fusion."""

    def __init__(
        self,
        dense_retriever: Retriever,
        lexical_retriever: LexicalRetriever | None = None,
        fusion_method: Literal["weighted", "rrf"] = "weighted",
        dense_weight: float = 0.7,
        lexical_weight: float = 0.3,
        rrf_k: int = 60,
    ) -> None:
        self.dense_retriever = dense_retriever
        self.lexical_retriever = lexical_retriever
        self.fusion_method = fusion_method
        self.dense_weight = dense_weight
        self.lexical_weight = lexical_weight
        self.rrf_k = rrf_k
        self.top_k = dense_retriever.top_k

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        document_id: str | None = None,
    ) -> list[RetrievedChunk]:
        k = top_k or self.top_k
        candidate_k = max(k * 2, 10)

        dense_chunks = self.dense_retriever.retrieve(
            query=query, top_k=candidate_k, document_id=document_id
        )

        lexical_chunks: list[RetrievedChunk] = []
        if self.lexical_retriever:
            lexical_chunks = self.lexical_retriever.retrieve(
                query=query, top_k=candidate_k, document_id=document_id
            )

        if not lexical_chunks:
            return dense_chunks[:k]
        if not dense_chunks:
            return lexical_chunks[:k]

        if self.fusion_method == "rrf":
            return self._reciprocal_rank_fusion(dense_chunks, lexical_chunks, k)
        return self._weighted_score_fusion(dense_chunks, lexical_chunks, k)

    def _weighted_score_fusion(
        self,
        dense_chunks: list[RetrievedChunk],
        lexical_chunks: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        max_dense = max((c.score for c in dense_chunks), default=1.0) or 1.0
        max_lex = max((c.score for c in lexical_chunks), default=1.0) or 1.0

        chunk_map: dict[str, RetrievedChunk] = {}
        scores: dict[str, float] = {}

        for chunk in dense_chunks:
            norm_score = chunk.score / max_dense
            chunk_map[chunk.chunk_id] = chunk
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + self.dense_weight * norm_score

        for chunk in lexical_chunks:
            norm_score = chunk.score / max_lex
            if chunk.chunk_id not in chunk_map:
                chunk_map[chunk.chunk_id] = chunk
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + self.lexical_weight * norm_score

        fused: list[RetrievedChunk] = []
        for chunk_id, combined_score in scores.items():
            orig = chunk_map[chunk_id]
            fused.append(
                RetrievedChunk(
                    chunk_id=orig.chunk_id,
                    document_id=orig.document_id,
                    document_name=orig.document_name,
                    chunk_index=orig.chunk_index,
                    content=orig.content,
                    score=combined_score,
                    metadata=orig.metadata,
                )
            )

        fused.sort(key=lambda c: c.score, reverse=True)
        return fused[:top_k]

    def _reciprocal_rank_fusion(
        self,
        dense_chunks: list[RetrievedChunk],
        lexical_chunks: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        chunk_map: dict[str, RetrievedChunk] = {}
        rrf_scores: dict[str, float] = {}

        for rank, chunk in enumerate(dense_chunks, 1):
            chunk_map[chunk.chunk_id] = chunk
            rrf_scores[chunk.chunk_id] = rrf_scores.get(chunk.chunk_id, 0.0) + (1.0 / (self.rrf_k + rank))

        for rank, chunk in enumerate(lexical_chunks, 1):
            if chunk.chunk_id not in chunk_map:
                chunk_map[chunk.chunk_id] = chunk
            rrf_scores[chunk.chunk_id] = rrf_scores.get(chunk.chunk_id, 0.0) + (1.0 / (self.rrf_k + rank))

        fused: list[RetrievedChunk] = []
        for chunk_id, score in rrf_scores.items():
            orig = chunk_map[chunk_id]
            fused.append(
                RetrievedChunk(
                    chunk_id=orig.chunk_id,
                    document_id=orig.document_id,
                    document_name=orig.document_name,
                    chunk_index=orig.chunk_index,
                    content=orig.content,
                    score=score,
                    metadata=orig.metadata,
                )
            )

        fused.sort(key=lambda c: c.score, reverse=True)
        return fused[:top_k]
