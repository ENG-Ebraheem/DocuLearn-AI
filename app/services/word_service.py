# pyrefly: ignore [missing-import]
import docx

from app.models.document import Document


class WordService:

    @staticmethod
    def extract(file_path: str) -> Document:
        doc = docx.Document(file_path)

        paragraphs = []

        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                paragraphs.append(paragraph.text)

        content = "\n".join(paragraphs)

        return Document(
            name=file_path.split("\\")[-1],
            file_type="docx",
            content=content,
        )