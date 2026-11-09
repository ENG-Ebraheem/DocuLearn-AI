from app.models.document import Document


class TextService:

    @staticmethod
    def extract(file_path: str) -> Document:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()

        return Document(
            name=file_path.split("\\")[-1],
            file_type="txt",
            content=content,
        )