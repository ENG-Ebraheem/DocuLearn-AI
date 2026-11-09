import pymupdf
from pathlib import Path

from app.domain.entities.document import Document
from app.core.exceptions import ExtractionError


class PDFExtractor:

    @staticmethod
    def extract(file_path: str) -> Document:
        try:
            pdf = pymupdf.open(file_path)
        except Exception as e:
            raise ExtractionError(
                f"Failed to open PDF: {e}"
            ) from e

        pages_text = []

        for page in pdf:
            text = page.get_text()
            pages_text.append(text)

        content = "\n\n".join(pages_text)

        return Document(
            name=Path(file_path).name,
            file_type="pdf",
            content=content,
            pages=len(pdf),
            file_path=file_path,
            metadata={
                "pages_text": pages_text,
                "total_pages": len(pdf),
            },
        )
