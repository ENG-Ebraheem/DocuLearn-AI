import pandas as pd

from app.models.document import Document


class ExcelService:

    @staticmethod
    def extract(file_path: str) -> Document:
        sheets = pd.read_excel(
            file_path,
            sheet_name=None
        )

        sections = []

        for sheet_name, dataframe in sheets.items():

            sections.append(
                f"Sheet: {sheet_name}"
            )

            sections.append(
                dataframe.to_string(index=False)
            )

        content = "\n\n".join(sections)

        return Document(
            name=file_path.split("\\")[-1],
            file_type="xlsx",
            content=content,
        )