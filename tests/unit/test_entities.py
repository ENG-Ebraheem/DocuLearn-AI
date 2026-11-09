import pytest
from app.domain.entities.document import Document
from app.domain.entities.chunk import Chunk
from app.domain.entities.conversation import Conversation
from app.domain.entities.chat_message import ChatMessage


class TestDocument:

    def test_create_document(self):
        doc = Document(
            name="test.pdf",
            file_type="pdf",
            content="Hello world",
        )
        assert doc.name == "test.pdf"
        assert doc.file_type == "pdf"
        assert doc.content == "Hello world"
        assert doc.id is not None
        assert doc.status == "UPLOADED"

    def test_document_has_unique_id(self):
        doc1 = Document(name="a.pdf", file_type="pdf", content="a")
        doc2 = Document(name="b.pdf", file_type="pdf", content="b")
        assert doc1.id != doc2.id

    def test_document_default_metadata(self):
        doc = Document(name="a.pdf", file_type="pdf", content="a")
        assert doc.metadata == {}

    def test_document_optional_fields(self):
        doc = Document(
            name="a.pdf",
            file_type="pdf",
            content="a",
            pages=10,
            size=1024,
        )
        assert doc.pages == 10
        assert doc.size == 1024


class TestChunk:

    def test_create_chunk(self):
        chunk = Chunk(
            document_id="doc123",
            content="chunk content",
            chunk_index=0,
        )
        assert chunk.document_id == "doc123"
        assert chunk.content == "chunk content"
        assert chunk.chunk_index == 0
        assert chunk.id is not None

    def test_chunk_default_metadata(self):
        chunk = Chunk(content="test", chunk_index=0)
        assert chunk.metadata == {}


class TestConversation:

    def test_create_conversation(self):
        conv = Conversation(
            document_id="doc123",
            title="Test Chat",
        )
        assert conv.document_id == "doc123"
        assert conv.title == "Test Chat"
        assert conv.id is not None


class TestChatMessage:

    def test_create_message(self):
        msg = ChatMessage(
            conversation_id="conv123",
            role="user",
            content="What is this about?",
        )
        assert msg.conversation_id == "conv123"
        assert msg.role == "user"
        assert msg.content == "What is this about?"
        assert msg.id is not None

    def test_message_default_sources(self):
        msg = ChatMessage(content="test")
        assert msg.sources == []
