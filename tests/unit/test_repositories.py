import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.database import Base
from app.infrastructure.database.repositories.document_repository_impl import (
    DocumentRepositoryImpl,
)
from app.infrastructure.database.repositories.chunk_repository_impl import (
    ChunkRepositoryImpl,
)
from app.infrastructure.database.repositories.conversation_repository_impl import (
    ConversationRepositoryImpl,
)
from app.infrastructure.database.repositories.chat_message_repository_impl import (
    ChatMessageRepositoryImpl,
)
from app.domain.entities.document import Document
from app.domain.entities.chunk import Chunk
from app.domain.entities.conversation import Conversation
from app.domain.entities.chat_message import ChatMessage


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestDocumentRepositoryImpl:

    def test_save_and_find(self, db_session):
        repo = DocumentRepositoryImpl(db_session)
        doc = Document(
            name="test.pdf",
            file_type="pdf",
            content="Hello",
        )
        saved = repo.save(doc)
        assert saved.id == doc.id
        assert saved.name == "test.pdf"

        found = repo.find_by_id(doc.id)
        assert found is not None
        assert found.name == "test.pdf"

    def test_find_all(self, db_session):
        repo = DocumentRepositoryImpl(db_session)
        repo.save(
            Document(
                name="a.pdf", file_type="pdf", content="a"
            )
        )
        repo.save(
            Document(
                name="b.pdf", file_type="pdf", content="b"
            )
        )
        all_docs = repo.find_all()
        assert len(all_docs) == 2

    def test_update_status(self, db_session):
        repo = DocumentRepositoryImpl(db_session)
        doc = Document(
            name="test.pdf",
            file_type="pdf",
            content="Hello",
        )
        repo.save(doc)

        doc.status = "INDEXED"
        updated = repo.update(doc)
        assert updated.status == "INDEXED"

    def test_delete(self, db_session):
        repo = DocumentRepositoryImpl(db_session)
        doc = Document(
            name="test.pdf",
            file_type="pdf",
            content="Hello",
        )
        repo.save(doc)

        assert repo.delete(doc.id) is True
        assert repo.find_by_id(doc.id) is None

    def test_find_nonexistent(self, db_session):
        repo = DocumentRepositoryImpl(db_session)
        assert repo.find_by_id("nonexistent") is None

    def test_save_with_metadata(self, db_session):
        repo = DocumentRepositoryImpl(db_session)
        doc = Document(
            name="test.pdf",
            file_type="pdf",
            content="Hello",
            metadata={"key": "value"},
        )
        saved = repo.save(doc)
        found = repo.find_by_id(saved.id)
        assert found.metadata == {"key": "value"}


class TestChunkRepositoryImpl:

    def test_save_many(self, db_session):
        repo = ChunkRepositoryImpl(db_session)
        chunks = [
            Chunk(
                document_id="doc1",
                content=f"Chunk {i}",
                chunk_index=i,
            )
            for i in range(3)
        ]
        saved = repo.save_many(chunks)
        assert len(saved) == 3

    def test_find_by_document_id(self, db_session):
        repo = ChunkRepositoryImpl(db_session)
        chunks = [
            Chunk(
                document_id="doc1",
                content=f"Chunk {i}",
                chunk_index=i,
            )
            for i in range(5)
        ]
        repo.save_many(chunks)

        found = repo.find_by_document_id("doc1")
        assert len(found) == 5
        assert found[0].chunk_index == 0

    def test_delete_by_document_id(self, db_session):
        repo = ChunkRepositoryImpl(db_session)
        chunks = [
            Chunk(
                document_id="doc1",
                content=f"Chunk {i}",
                chunk_index=i,
            )
            for i in range(3)
        ]
        repo.save_many(chunks)

        assert (
            repo.delete_by_document_id("doc1") is True
        )
        assert (
            len(repo.find_by_document_id("doc1")) == 0
        )


class TestConversationRepositoryImpl:

    def test_save_and_find(self, db_session):
        repo = ConversationRepositoryImpl(db_session)
        conv = Conversation(
            document_id="doc1",
            title="Test Chat",
        )
        saved = repo.save(conv)
        assert saved.id == conv.id

        found = repo.find_by_id(conv.id)
        assert found is not None
        assert found.title == "Test Chat"

    def test_find_by_document_id(self, db_session):
        repo = ConversationRepositoryImpl(db_session)
        repo.save(
            Conversation(
                document_id="doc1", title="Chat 1"
            )
        )
        repo.save(
            Conversation(
                document_id="doc1", title="Chat 2"
            )
        )
        repo.save(
            Conversation(
                document_id="doc2", title="Chat 3"
            )
        )

        found = repo.find_by_document_id("doc1")
        assert len(found) == 2


class TestChatMessageRepositoryImpl:

    def test_save_and_list(self, db_session):
        repo = ChatMessageRepositoryImpl(db_session)
        msg = ChatMessage(
            conversation_id="conv1",
            role="user",
            content="Hello",
        )
        saved = repo.save(msg)

        messages = repo.find_by_conversation_id(
            "conv1"
        )
        assert len(messages) == 1
        assert messages[0].content == "Hello"

    def test_delete_by_conversation(self, db_session):
        repo = ChatMessageRepositoryImpl(db_session)
        repo.save(
            ChatMessage(
                conversation_id="conv1",
                role="user",
                content="Hi",
            )
        )
        repo.save(
            ChatMessage(
                conversation_id="conv1",
                role="assistant",
                content="Hello!",
            )
        )

        assert (
            repo.delete_by_conversation_id("conv1")
            is True
        )
        assert (
            len(repo.find_by_conversation_id("conv1"))
            == 0
        )
