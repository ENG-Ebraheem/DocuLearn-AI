import pymupdf

from app.models.document import Document


class PDFService:

    @staticmethod
    def extract(file_path: str) -> Document:
        pdf = pymupdf.open(file_path)

        pages = []

        for page in pdf:
            text = page.get_text()
            pages.append(text)

        content = "\n\n".join(pages)

        return Document(
            name=file_path.split("\\")[-1],
            file_type="pdf",
            content=content,
            pages=len(pdf),
        )