"""Lexical (BM25 / Keyword) search implementation with Arabic normalization support."""

from __future__ import annotations

import math
import re
from typing import Sequence

from app.application.services.rag.retriever import RetrievedChunk
from app.domain.entities.chunk import Chunk
from app.domain.repositories.chunk_repository import ChunkRepository
from app.services.text_processing.normalizer import ArabicNormalizer


class LexicalRetriever:
    """Ranks chunks using BM25 keyword matching with Arabic normalization."""

    def __init__(
        self,
        chunk_repo: ChunkRepository,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self.chunk_repo = chunk_repo
        self.k1 = k1
        self.b = b

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        document_id: str | None = None,
    ) -> list[RetrievedChunk]:
        normalized_query = ArabicNormalizer.normalize_search(query)
        query_tokens = self._tokenize(normalized_query)
        if not query_tokens:
            return []

        chunks: Sequence[Chunk] = (
            self.chunk_repo.find_by_document_id(document_id)
            if document_id
            else self.chunk_repo.find_all()
        )
        if not chunks:
            return []

        # Corpus statistics
        doc_tokens = [
            self._tokenize(ArabicNormalizer.normalize_search(c.content))
            for c in chunks
        ]
        doc_lengths = [len(tokens) for tokens in doc_tokens]
        avg_doc_len = sum(doc_lengths) / max(len(doc_lengths), 1)
        num_docs = len(chunks)

        # Document frequencies for query terms
        df: dict[str, int] = {}
        for token in set(query_tokens):
            df[token] = sum(1 for dt in doc_tokens if token in dt)

        # Calculate BM25 scores
        scored_chunks: list[RetrievedChunk] = []
        for i, chunk in enumerate(chunks):
            tokens = doc_tokens[i]
            length = doc_lengths[i]
            if length == 0:
                continue

            score = 0.0
            term_counts: dict[str, int] = {}
            for token in tokens:
                term_counts[token] = term_counts.get(token, 0) + 1

            for token in set(query_tokens):
                tf = term_counts.get(token, 0)
                if tf == 0:
                    continue

                doc_freq = df.get(token, 0)
                # IDF calculation with smoothing
                idf = math.log((num_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
                denom = tf + self.k1 * (1 - self.b + self.b * (length / max(avg_doc_len, 1)))
                score += idf * ((tf * (self.k1 + 1)) / max(denom, 1e-6))

            if score > 0.0:
                scored_chunks.append(
                    RetrievedChunk(
                        chunk_id=chunk.id,
                        document_id=chunk.document_id,
                        document_name=chunk.metadata.get("document_name", ""),
                        chunk_index=chunk.chunk_index,
                        content=chunk.content,
                        score=score,
                        metadata=chunk.metadata,
                    )
                )

        scored_chunks.sort(key=lambda item: item.score, reverse=True)
        return scored_chunks[:top_k]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        words = re.findall(r"\w+", text.lower())
        return [w for w in words if len(w) > 1]
