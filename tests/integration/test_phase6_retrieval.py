import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application.services.rag.context_builder import ContextBuilder
from app.application.services.rag.hybrid_retriever import HybridRetriever
from app.application.services.rag.lexical_retriever import LexicalRetriever
from app.application.services.rag.qa_service import QAService
from app.domain.entities.chunk import Chunk
from app.domain.entities.document import Document
from app.infrastructure.database.database import Base
from app.infrastructure.database.repositories.chunk_repository_impl import ChunkRepositoryImpl
from app.infrastructure.database.repositories.document_repository_impl import DocumentRepositoryImpl
from app.infrastructure.llm.fake_llm_provider import FakeLLMProvider


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestPhase6HybridRetrievalIntegration:

    def test_hybrid_rag_qa_returns_sources(self, db_session):
        doc_repo = DocumentRepositoryImpl(db_session)
        chunk_repo = ChunkRepositoryImpl(db_session)

        doc = doc_repo.save(Document(id="doc_ai", name="AI_Intro.pdf", file_type="pdf", status="INDEXED"))
        chunk_repo.save(
            Chunk(
                id="chunk_ai_1",
                document_id="doc_ai",
                chunk_index=0,
                content="الذكاء الاصطناعي هو علم أنظمة الحاسوب الأذكى من الأفراد.",
                metadata={"document_name": "AI_Intro.pdf", "page": 1},
            )
        )

        class FakeDenseRetriever:
            top_k = 5
            def retrieve(self, query, top_k=5, document_id=None):
                return []

        dense_retriever = FakeDenseRetriever()
        lexical_retriever = LexicalRetriever(chunk_repo=chunk_repo)
        hybrid_retriever = HybridRetriever(
            dense_retriever=dense_retriever,
            lexical_retriever=lexical_retriever,
        )

        fake_llm = FakeLLMProvider(response="الذكاء الاصطناعي هو علم الحاسوب.")
        qa_service = QAService(
            retriever=hybrid_retriever,
            context_builder=ContextBuilder(),
            llm_provider=fake_llm,
            min_context_score=0.1,
        )

        response = qa_service.ask(query="الذكاء الاصطناعي", document_id="doc_ai")
        assert response.has_sufficient_context is True
        assert len(response.sources) >= 1
        assert response.sources[0].document_name == "AI_Intro.pdf"

    def test_document_isolation_in_hybrid_search(self, db_session):
        doc_repo = DocumentRepositoryImpl(db_session)
        chunk_repo = ChunkRepositoryImpl(db_session)

        doc_a = doc_repo.save(Document(id="doc_a", name="DocA.pdf", file_type="pdf", status="INDEXED"))
        doc_b = doc_repo.save(Document(id="doc_b", name="DocB.pdf", file_type="pdf", status="INDEXED"))

        chunk_repo.save(
            Chunk(
                id="chunk_a",
                document_id="doc_a",
                chunk_index=0,
                content="هذا الجزء ينتمي إلى المستند أ حصرياً.",
                metadata={"document_name": "DocA.pdf", "page": 1},
            )
        )
        chunk_repo.save(
            Chunk(
                id="chunk_b",
                document_id="doc_b",
                chunk_index=0,
                content="هذا الجزء ينتمي إلى المستند ب حصرياً.",
                metadata={"document_name": "DocB.pdf", "page": 1},
            )
        )

        lexical_retriever = LexicalRetriever(chunk_repo=chunk_repo)
        results_a = lexical_retriever.retrieve(query="المستند", document_id="doc_a")

        assert len(results_a) == 1
        assert results_a[0].document_id == "doc_a"
