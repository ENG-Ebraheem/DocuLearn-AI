import pytest
from app.services.text_processing.chunker import (
    TextChunker,
    TextChunk,
)


class TestTextChunker:

    def test_split_empty_string(self):
        chunker = TextChunker(chunk_size=100, overlap=10)
        assert chunker.split("") == []

    def test_split_whitespace_only(self):
        chunker = TextChunker(chunk_size=100, overlap=10)
        assert chunker.split("   \n\n   ") == []

    def test_split_short_text_single_chunk(self):
        chunker = TextChunker(chunk_size=1000, overlap=100)
        text = "Short text."
        chunks = chunker.split(text)
        assert len(chunks) == 1
        assert chunks[0].content == "Short text."
        assert chunks[0].chunk_index == 0

    def test_split_long_text_multiple_chunks(self):
        chunker = TextChunker(chunk_size=50, overlap=10)
        text = "word " * 20  # 100 chars
        chunks = chunker.split(text)
        assert len(chunks) > 1

    def test_chunks_have_sequential_indices(self):
        chunker = TextChunker(chunk_size=50, overlap=10)
        text = "word " * 20
        chunks = chunker.split(text)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_all_content_is_covered(self):
        chunker = TextChunker(chunk_size=50, overlap=10)
        text = "The quick brown fox jumps over the lazy dog. " * 5
        chunks = chunker.split(text)
        combined = " ".join(c.content for c in chunks)
        for word in text.split():
            assert word in combined

    def test_overlap_smaller_than_chunk_size(self):
        with pytest.raises(ValueError):
            TextChunker(chunk_size=100, overlap=100)

    def test_overlap_greater_than_chunk_size_raises(self):
        with pytest.raises(ValueError):
            TextChunker(chunk_size=50, overlap=60)

    def test_chunks_are_stripped(self):
        chunker = TextChunker(chunk_size=20, overlap=5)
        text = "  hello   world  "
        chunks = chunker.split(text)
        for chunk in chunks:
            assert chunk.content == chunk.content.strip()

    def test_chunk_dataclass_fields(self):
        chunk = TextChunk(content="test", chunk_index=0)
        assert chunk.content == "test"
        assert chunk.chunk_index == 0
