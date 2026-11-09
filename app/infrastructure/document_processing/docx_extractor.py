import docx
from pathlib import Path

from app.domain.entities.document import Document
from app.core.exceptions import ExtractionError


class DOCXExtractor:

    @staticmethod
    def extract(file_path: str) -> Document:
        try:
            doc = docx.Document(file_path)
        except Exception as e:
            raise ExtractionError(
                f"Failed to open DOCX: {e}"
            ) from e

        paragraphs = []

        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                paragraphs.append(paragraph.text)

        content = "\n".join(paragraphs)

        return Document(
            name=Path(file_path).name,
            file_type="docx",
            content=content,
            file_path=file_path,
        )
