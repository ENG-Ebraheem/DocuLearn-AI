class DocuLearnError(Exception):
    """Base exception for DocuLearn AI."""

    pass


class DocumentProcessingError(DocuLearnError):
    """Raised when document processing fails."""

    pass


class UnsupportedFileTypeError(DocumentProcessingError):
    """Raised when an unsupported file type is provided."""

    def __init__(self, file_type: str) -> None:
        self.file_type = file_type
        super().__init__(f"Unsupported file type: {file_type}")


class ExtractionError(DocumentProcessingError):
    """Raised when text extraction from a document fails."""

    pass


class EmbeddingError(DocuLearnError):
    """Raised when embedding generation fails."""

    pass


class VectorStoreError(DocuLearnError):
    """Raised when a vector store operation fails."""

    pass


class LLMError(DocuLearnError):
    """Raised when an LLM call fails."""

    pass


class DatabaseError(DocuLearnError):
    """Raised when a database operation fails."""

    pass


class RetrievalError(DocuLearnError):
    """Raised when retrieval from the vector store fails."""

    pass


class ConfigurationError(DocuLearnError):
    """Raised when there is a configuration problem."""

    pass
