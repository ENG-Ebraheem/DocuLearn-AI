from pathlib import Path

from app.domain.entities.document import Document
from app.infrastructure.document_processing import DocumentExtractor
from app.core.exceptions import UnsupportedFileTypeError


class DocumentService:

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".xlsx",
        ".txt",
    }

    @staticmethod
    def extract(file_path: str) -> Document:
        return DocumentExtractor.extract(file_path)
