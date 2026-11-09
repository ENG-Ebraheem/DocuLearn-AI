import pytest
import tempfile

from app.infrastructure.embeddings.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from app.infrastructure.vector_store.faiss_vector_store import (
    FAISSVectorStore,
)
from app.application.services.rag.retriever import (
    Retriever,
)
from app.domain.entities.chunk import Chunk


class TestRAGQuality:

    def test_retrieves_relevant_chunk(self):
        provider = SentenceTransformerEmbeddingProvider()

        with tempfile.TemporaryDirectory() as tmpdir:
            store = FAISSVectorStore(
                dimension=provider.dimension,
                store_path=tmpdir,
            )

            chunks = [
                Chunk(
                    id="c1",
                    document_id="d1",
                    content="Object oriented programming uses classes and objects to organize code.",
                    chunk_index=0,
                    metadata={
                        "document_name": "cs.pdf",
                        "document_id": "d1",
                    },
                ),
                Chunk(
                    id="c2",
                    document_id="d1",
                    content="SQL databases store structured data in tables with rows and columns.",
                    chunk_index=1,
                    metadata={
                        "document_name": "db.pdf",
                        "document_id": "d1",
                    },
                ),
                Chunk(
                    id="c3",
                    document_id="d1",
                    content="HTML structures web pages using elements like div, p, and span.",
                    chunk_index=2,
                    metadata={
                        "document_name": "web.pdf",
                        "document_id": "d1",
                    },
                ),
            ]

            texts = [c.content for c in chunks]
            embeddings = provider.embed_documents(texts)
            store.add(chunks, embeddings)

            retriever = Retriever(
                embedding_provider=provider,
                vector_store=store,
                top_k=3,
            )

            results = retriever.retrieve(
                "What is object oriented programming?"
            )

            assert len(results) > 0
            assert (
                results[0].content
                == "Object oriented programming uses classes and objects to organize code."
            )
