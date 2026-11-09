from pathlib import Path

from app.domain.entities.document import Document
from app.infrastructure.document_processing.pdf_extractor import PDFExtractor
from app.infrastructure.document_processing.docx_extractor import DOCXExtractor
from app.infrastructure.document_processing.excel_extractor import ExcelExtractor
from app.infrastructure.document_processing.text_extractor import TextExtractor
from app.core.exceptions import UnsupportedFileTypeError


EXTRACTORS = {
    ".pdf": PDFExtractor,
    ".docx": DOCXExtractor,
    ".xlsx": ExcelExtractor,
    ".txt": TextExtractor,
}

SUPPORTED_EXTENSIONS = set(EXTRACTORS.keys())


class DocumentExtractor:

    @staticmethod
    def extract(file_path: str) -> Document:
        extension = Path(file_path).suffix.lower()

        extractor_class = EXTRACTORS.get(extension)

        if extractor_class is None:
            raise UnsupportedFileTypeError(extension)

        return extractor_class.extract(file_path)
