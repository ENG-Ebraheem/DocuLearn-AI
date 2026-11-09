from dataclasses import dataclass


@dataclass
class TextChunk:
    content: str
    chunk_index: int
    page: int | None = None


class TextChunker:
    """Split document text into manageable chunks.

    Supports page-aware splitting when pages_text
    is provided to split_pages().
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        overlap: int = 150,
    ):
        if overlap >= chunk_size:
            raise ValueError(
                "Overlap must be smaller than chunk size."
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str) -> list[TextChunk]:
        if not text.strip():
            return []

        chunks = []

        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size

            chunk = text[start:end]

            if chunk.strip():
                chunks.append(
                    TextChunk(
                        content=chunk.strip(),
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1

            start = end - self.overlap

        return chunks

    def split_pages(
        self,
        pages_text: list[str],
    ) -> list[TextChunk]:
        """Split page-by-page, preserving page numbers.

        Each chunk carries the page number it came from.
        """
        if not pages_text:
            return []

        chunks = []
        global_index = 0

        for page_num, page_content in enumerate(
            pages_text, 1
        ):
            if not page_content.strip():
                continue

            start = 0

            while start < len(page_content):
                end = start + self.chunk_size
                chunk_text = page_content[start:end]

                if chunk_text.strip():
                    chunks.append(
                        TextChunk(
                            content=chunk_text.strip(),
                            chunk_index=global_index,
                            page=page_num,
                        )
                    )
                    global_index += 1

                start = end - self.overlap

        return chunks
