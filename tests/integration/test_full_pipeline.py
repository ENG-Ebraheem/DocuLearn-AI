import pytest
import tempfile
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.database import Base
from app.infrastructure.database.repositories.document_repository_impl import (
    DocumentRepositoryImpl,
)
from app.infrastructure.database.repositories.chunk_repository_impl import (
    ChunkRepositoryImpl,
)
from app.infrastructure.embeddings.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from app.infrastructure.vector_store.faiss_vector_store import (
    FAISSVectorStore,
)
from app.application.services.document_processing_pipeline import (
    DocumentProcessingPipeline,
)
from app.application.services.rag.retriever import (
    Retriever,
)
from app.application.services.rag.context_builder import (
    ContextBuilder,
)
from app.application.services.rag.reranker import (
    PassThroughReranker,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestFullPipeline:

    def test_ingest_and_retrieve(self, db_session):
        file_path = "data/uploads/test.txt"
        if not Path(file_path).exists():
            pytest.skip("test.txt not found")

        doc_repo = DocumentRepositoryImpl(db_session)
        chunk_repo = ChunkRepositoryImpl(db_session)
        embedding_provider = (
            SentenceTransformerEmbeddingProvider()
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            vector_store = FAISSVectorStore(
                dimension=embedding_provider.dimension,
                store_path=tmpdir,
            )

            pipeline = DocumentProcessingPipeline(
                chunk_size=200,
                chunk_overlap=20,
            )

            result = pipeline.ingest(
                file_path=file_path,
                document_repo=doc_repo,
                chunk_repo=chunk_repo,
                embedding_provider=embedding_provider,
                vector_store=vector_store,
            )

            assert result.indexed is True
            assert result.document.status == "INDEXED"
            assert len(result.chunks) > 0

            retriever = Retriever(
                embedding_provider=embedding_provider,
                vector_store=vector_store,
                top_k=3,
            )

            retrieved = retriever.retrieve(
                "What is this document about?"
            )

            assert len(retrieved) > 0
            assert retrieved[0].document_id == result.document.id

            builder = ContextBuilder(max_chunks=3)
            context = builder.build(
                "What is this document about?",
                retrieved,
            )

            assert len(context.chunks) > 0
            assert len(context.sources) > 0

    def test_persistence_across_restarts(
        self, db_session
    ):
        file_path = "data/uploads/test.txt"
        if not Path(file_path).exists():
            pytest.skip("test.txt not found")

        doc_repo = DocumentRepositoryImpl(db_session)
        chunk_repo = ChunkRepositoryImpl(db_session)
        embedding_provider = (
            SentenceTransformerEmbeddingProvider()
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            vs1 = FAISSVectorStore(
                dimension=embedding_provider.dimension,
                store_path=tmpdir,
            )

            pipeline = DocumentProcessingPipeline(
                chunk_size=200,
                chunk_overlap=20,
            )

            result = pipeline.ingest(
                file_path=file_path,
                document_repo=doc_repo,
                chunk_repo=chunk_repo,
                embedding_provider=embedding_provider,
                vector_store=vs1,
            )

            vs2 = FAISSVectorStore(
                dimension=embedding_provider.dimension,
                store_path=tmpdir,
            )

            retriever = Retriever(
                embedding_provider=embedding_provider,
                vector_store=vs2,
                top_k=3,
            )

            retrieved = retriever.retrieve(
                "What is this document about?"
            )

            assert len(retrieved) > 0
            assert (
                retrieved[0].document_id
                == result.document.id
            )
