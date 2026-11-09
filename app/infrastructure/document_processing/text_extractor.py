from pathlib import Path

from app.domain.entities.document import Document
from app.core.exceptions import ExtractionError


class TextExtractor:

    @staticmethod
    def extract(file_path: str) -> Document:
        try:
            with open(
                file_path, "r", encoding="utf-8"
            ) as file:
                content = file.read()
        except Exception as e:
            raise ExtractionError(
                f"Failed to read text file: {e}"
            ) from e

        return Document(
            name=Path(file_path).name,
            file_type="txt",
            content=content,
            file_path=file_path,
        )
