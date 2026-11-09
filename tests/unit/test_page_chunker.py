import pytest
from app.services.text_processing.chunker import (
    TextChunker,
)


class TestPageAwareChunking:

    def test_split_pages_basic(self):
        chunker = TextChunker(
            chunk_size=100, overlap=10
        )
        pages = ["Page one content here.", "Page two content here."]
        chunks = chunker.split_pages(pages)
        assert len(chunks) >= 2
        assert chunks[0].page == 1
        assert chunks[1].page == 2

    def test_split_pages_preserves_index(
        self,
    ):
        chunker = TextChunker(
            chunk_size=100, overlap=10
        )
        pages = [
            "A" * 50,
            "B" * 50,
            "C" * 50,
        ]
        chunks = chunker.split_pages(pages)
        indices = [c.chunk_index for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_split_pages_empty(self):
        chunker = TextChunker()
        assert chunker.split_pages([]) == []

    def test_split_pages_skips_empty_pages(
        self,
    ):
        chunker = TextChunker(
            chunk_size=100, overlap=10
        )
        pages = ["Content.", "", "More."]
        chunks = chunker.split_pages(pages)
        pages_found = [c.page for c in chunks]
        assert 2 not in pages_found

    def test_split_pages_long_page_splits(
        self,
    ):
        chunker = TextChunker(
            chunk_size=50, overlap=10
        )
        pages = ["A" * 200]
        chunks = chunker.split_pages(pages)
        assert len(chunks) > 1
        assert all(c.page == 1 for c in chunks)

    def test_split_fallback_no_pages(self):
        chunker = TextChunker(
            chunk_size=100, overlap=10
        )
        text = "Some plain text content."
        chunks = chunker.split(text)
        assert len(chunks) >= 1
        assert chunks[0].page is None
