import pytest
from pathlib import Path
from app.application.services.document_processing_pipeline import (
    DocumentProcessingPipeline,
)


class TestDocumentProcessingPipeline:

    def test_pipeline_returns_document_and_chunks(self):
        file_path = "data/uploads/test.txt"
        if not Path(file_path).exists():
            pytest.skip("test.txt not found")

        pipeline = DocumentProcessingPipeline(
            chunk_size=200,
            chunk_overlap=20,
        )
        document, chunks = pipeline.process(file_path)

        assert document is not None
        assert document.content is not None
        assert len(chunks) > 0

    def test_chunks_have_metadata(self):
        file_path = "data/uploads/test.txt"
        if not Path(file_path).exists():
            pytest.skip("test.txt not found")

        pipeline = DocumentProcessingPipeline(
            chunk_size=200,
            chunk_overlap=20,
        )
        document, chunks = pipeline.process(file_path)

        for chunk in chunks:
            assert "document_id" in chunk.metadata
            assert "document_name" in chunk.metadata
            assert "file_type" in chunk.metadata
            assert "chunk_index" in chunk.metadata
            assert "total_chunks" in chunk.metadata
            assert chunk.metadata["document_id"] == document.id

    def test_chunks_belong_to_document(self):
        file_path = "data/uploads/test.txt"
        if not Path(file_path).exists():
            pytest.skip("test.txt not found")

        pipeline = DocumentProcessingPipeline(
            chunk_size=200,
            chunk_overlap=20,
        )
        document, chunks = pipeline.process(file_path)

        for chunk in chunks:
            assert chunk.document_id == document.id

    def test_content_is_cleaned(self):
        file_path = "data/uploads/test.txt"
        if not Path(file_path).exists():
            pytest.skip("test.txt not found")

        pipeline = DocumentProcessingPipeline()
        document, _ = pipeline.process(file_path)

        assert "\r\n" not in document.content
        assert "\r" not in document.content

    def test_custom_chunk_size(self):
        file_path = "data/uploads/test.txt"
        if not Path(file_path).exists():
            pytest.skip("test.txt not found")

        pipeline = DocumentProcessingPipeline(
            chunk_size=100,
            chunk_overlap=10,
        )
        _, chunks = pipeline.process(file_path)

        for chunk in chunks:
            assert len(chunk.content) <= 200
