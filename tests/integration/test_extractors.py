import pytest
from pathlib import Path
from app.infrastructure.document_processing import (
    DocumentExtractor,
    SUPPORTED_EXTENSIONS,
)
from app.core.exceptions import (
    UnsupportedFileTypeError,
    ExtractionError,
)


class TestDocumentExtractor:

    def test_supported_extensions(self):
        assert ".pdf" in SUPPORTED_EXTENSIONS
        assert ".docx" in SUPPORTED_EXTENSIONS
        assert ".xlsx" in SUPPORTED_EXTENSIONS
        assert ".txt" in SUPPORTED_EXTENSIONS

    def test_unsupported_extension_raises(self):
        with pytest.raises(UnsupportedFileTypeError):
            DocumentExtractor.extract("test.xyz")

    def test_extract_txt(self):
        file_path = "data/uploads/test.txt"
        if Path(file_path).exists():
            doc = DocumentExtractor.extract(file_path)
            assert doc.file_type == "txt"
            assert doc.content is not None
            assert len(doc.content) > 0
            assert doc.name == "test.txt"

    def test_extract_pdf(self):
        file_path = "data/uploads/test.pdf"
        if Path(file_path).exists():
            doc = DocumentExtractor.extract(file_path)
            assert doc.file_type == "pdf"
            assert doc.pages is not None
            assert doc.pages > 0

    def test_extract_docx(self):
        file_path = "data/uploads/test.docx"
        if Path(file_path).exists():
            doc = DocumentExtractor.extract(file_path)
            assert doc.file_type == "docx"
            assert doc.content is not None

    def test_extract_xlsx(self):
        file_path = "data/uploads/test.xlsx"
        if Path(file_path).exists():
            doc = DocumentExtractor.extract(file_path)
            assert doc.file_type == "xlsx"
            assert "Sheet:" in doc.content

    def test_nonexistent_file_raises(self):
        with pytest.raises(ExtractionError):
            DocumentExtractor.extract("nonexistent.pdf")
