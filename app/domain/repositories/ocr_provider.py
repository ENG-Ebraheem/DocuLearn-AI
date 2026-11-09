from abc import ABC, abstractmethod


class OCRProvider(ABC):
    """Abstraction for OCR processing.

    Implement later for scanned PDFs and image documents.
    """

    @abstractmethod
    def extract_text_from_image(
        self, image_bytes: bytes
    ) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass
