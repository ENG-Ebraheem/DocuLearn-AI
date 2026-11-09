import re


class TextCleaner:
    """Clean and normalize extracted document text."""

    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""

        # Normalize line breaks
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Remove excessive spaces
        text = re.sub(r"[ \t]+", " ", text)

        # Remove excessive empty lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove spaces at the beginning/end of lines
        lines = [
            line.strip()
            for line in text.split("\n")
        ]

        text = "\n".join(lines)

        return text.strip()