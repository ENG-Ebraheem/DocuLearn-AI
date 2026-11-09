import pandas as pd
from pathlib import Path

from app.domain.entities.document import Document
from app.core.exceptions import ExtractionError


class ExcelExtractor:

    @staticmethod
    def extract(file_path: str) -> Document:
        try:
            sheets = pd.read_excel(
                file_path, sheet_name=None
            )
        except Exception as e:
            raise ExtractionError(
                f"Failed to open Excel: {e}"
            ) from e

        sections = []

        for sheet_name, dataframe in sheets.items():
            sections.append(f"Sheet: {sheet_name}")
            sections.append(
                dataframe.to_string(index=False)
            )

        content = "\n\n".join(sections)

        return Document(
            name=Path(file_path).name,
            file_type="xlsx",
            content=content,
            file_path=file_path,
            metadata={"sheet_names": list(sheets.keys())},
        )
