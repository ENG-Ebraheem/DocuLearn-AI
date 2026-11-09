import pytest
from app.application.services.rag.prompt_builder import (
    PromptBuilder,
)
from app.application.services.rag.retriever import (
    RetrievedChunk,
)


@pytest.fixture
def builder():
    return PromptBuilder()


class TestPromptBuilder:

    def test_build_basic_prompt(self, builder):
        chunks = [
            RetrievedChunk(
                chunk_id="c1",
                document_id="d1",
                document_name="test.pdf",
                chunk_index=0,
                content="AI is transforming education.",
                score=0.9,
                metadata={"page": 5},
            ),
        ]
        prompt = builder.build(
            "What is AI?", chunks
        )
        assert "AI is transforming" in prompt
        assert "What is AI?" in prompt
        assert "المصدر 1" in prompt
        assert "صفحة 5" in prompt

    def test_build_with_history(self, builder):
        chunks = [
            RetrievedChunk(
                chunk_id="c1",
                document_id="d1",
                document_name="test.pdf",
                chunk_index=0,
                content="Content.",
                score=0.9,
                metadata={},
            ),
        ]
        history = [
            {"role": "user", "content": "Hello"},
            {
                "role": "assistant",
                "content": "Hi there!",
            },
        ]
        prompt = builder.build(
            "Follow up", chunks, history=history
        )
        assert "المحادثة السابقة" in prompt
        assert "Hello" in prompt
        assert "Hi there!" in prompt

    def test_instruction_arabic(self, builder):
        instr = builder.build_instruction("ar")
        assert "مساعد" in instr

    def test_instruction_english(self, builder):
        instr = builder.build_instruction("en")
        assert "assistant" in instr

    def test_format_chunks_no_page(self, builder):
        chunks = [
            RetrievedChunk(
                chunk_id="c1",
                document_id="d1",
                document_name="test.pdf",
                chunk_index=0,
                content="Content.",
                score=0.9,
                metadata={},
            ),
        ]
        prompt = builder.build("q", chunks)
        assert "صفحة" not in prompt
