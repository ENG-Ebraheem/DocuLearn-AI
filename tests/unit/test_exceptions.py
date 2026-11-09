from app.core.exceptions import (
    DocuLearnError,
    UnsupportedFileTypeError,
    ExtractionError,
    EmbeddingError,
    VectorStoreError,
    LLMError,
    DatabaseError,
    RetrievalError,
    ConfigurationError,
)


class TestExceptions:

    def test_base_exception(self):
        with raise_doculearn_error():
            raise DocuLearnError("test")

    def test_unsupported_file_type(self):
        try:
            raise UnsupportedFileTypeError(".xyz")
        except UnsupportedFileTypeError as e:
            assert e.file_type == ".xyz"
            assert ".xyz" in str(e)

    def test_extraction_error(self):
        with raise_extraction_error():
            raise ExtractionError("extract failed")

    def test_embedding_error(self):
        with raise_embedding_error():
            raise EmbeddingError("embed failed")

    def test_inheritance_chain(self):
        assert issubclass(UnsupportedFileTypeError, DocuLearnError)
        assert issubclass(ExtractionError, DocuLearnError)
        assert issubclass(EmbeddingError, DocuLearnError)
        assert issubclass(VectorStoreError, DocuLearnError)
        assert issubclass(LLMError, DocuLearnError)
        assert issubclass(DatabaseError, DocuLearnError)
        assert issubclass(RetrievalError, DocuLearnError)
        assert issubclass(ConfigurationError, DocuLearnError)


import pytest


class raise_doculearn_error:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return exc_type is not None and issubclass(
            exc_type, DocuLearnError
        )


class raise_extraction_error:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return exc_type is not None and issubclass(
            exc_type, ExtractionError
        )


class raise_embedding_error:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return exc_type is not None and issubclass(
            exc_type, EmbeddingError
        )
