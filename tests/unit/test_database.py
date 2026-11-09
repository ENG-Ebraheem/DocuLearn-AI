import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.database import Base
from app.infrastructure.database.models.document_model import (
    DocumentModel,
)
from app.infrastructure.database.models.chunk_model import (
    ChunkModel,
)
from app.infrastructure.database.models.conversation_model import (
    ConversationModel,
)
from app.infrastructure.database.models.chat_message_model import (
    ChatMessageModel,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestDocumentModel:

    def test_create_document(self, db_session):
        model = DocumentModel(
            id="doc123",
            name="test.pdf",
            file_type="pdf",
            status="UPLOADED",
        )
        db_session.add(model)
        db_session.commit()

        loaded = db_session.get(DocumentModel, "doc123")
        assert loaded is not None
        assert loaded.name == "test.pdf"
        assert loaded.file_type == "pdf"
        assert loaded.status == "UPLOADED"

    def test_document_metadata(self, db_session):
        model = DocumentModel(
            id="doc456",
            name="test.pdf",
            file_type="pdf",
        )
        model.extra_metadata = {"key": "value"}
        db_session.add(model)
        db_session.commit()

        loaded = db_session.get(DocumentModel, "doc456")
        assert loaded.extra_metadata == {"key": "value"}


class TestChunkModel:

    def test_create_chunk(self, db_session):
        model = ChunkModel(
            id="chunk123",
            document_id="doc123",
            content="Hello world",
            chunk_index=0,
        )
        db_session.add(model)
        db_session.commit()

        loaded = db_session.get(ChunkModel, "chunk123")
        assert loaded is not None
        assert loaded.content == "Hello world"
        assert loaded.chunk_index == 0

    def test_chunks_by_document(self, db_session):
        for i in range(3):
            model = ChunkModel(
                id=f"chunk{i}",
                document_id="doc123",
                content=f"Chunk {i}",
                chunk_index=i,
            )
            db_session.add(model)

        db_session.commit()

        chunks = (
            db_session.query(ChunkModel)
            .filter(
                ChunkModel.document_id == "doc123"
            )
            .order_by(ChunkModel.chunk_index)
            .all()
        )

        assert len(chunks) == 3
        assert chunks[0].chunk_index == 0
        assert chunks[2].chunk_index == 2


class TestConversationModel:

    def test_create_conversation(self, db_session):
        model = ConversationModel(
            id="conv123",
            document_id="doc123",
            title="Test Chat",
        )
        db_session.add(model)
        db_session.commit()

        loaded = db_session.get(
            ConversationModel, "conv123"
        )
        assert loaded is not None
        assert loaded.title == "Test Chat"


class TestChatMessageModel:

    def test_create_message(self, db_session):
        model = ChatMessageModel(
            id="msg123",
            conversation_id="conv123",
            role="user",
            content="Hello",
        )
        db_session.add(model)
        db_session.commit()

        loaded = db_session.get(
            ChatMessageModel, "msg123"
        )
        assert loaded is not None
        assert loaded.role == "user"
        assert loaded.content == "Hello"
