import pytest
from app.infrastructure.embeddings.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)


class TestSentenceTransformerEmbeddingProvider:

    @pytest.fixture
    def provider(self):
        return SentenceTransformerEmbeddingProvider()

    def test_embed_text(self, provider):
        result = provider.embed_text(
            "Hello world"
        )
        assert isinstance(result, list)
        assert len(result) == 384

    def test_embed_text_normalization(self, provider):
        result = provider.embed_text("Test")
        norm = sum(x**2 for x in result) ** 0.5
        assert abs(norm - 1.0) < 0.01

    def test_embed_empty_raises(self, provider):
        from app.core.exceptions import EmbeddingError

        with pytest.raises(EmbeddingError):
            provider.embed_text("")

    def test_embed_documents(self, provider):
        texts = ["Hello", "World"]
        results = provider.embed_documents(texts)
        assert len(results) == 2
        assert len(results[0]) == 384

    def test_embed_documents_empty(self, provider):
        results = provider.embed_documents([])
        assert results == []

    def test_dimension(self, provider):
        assert provider.dimension == 384

    def test_singleton_model(self):
        p1 = SentenceTransformerEmbeddingProvider()
        p2 = SentenceTransformerEmbeddingProvider()
        m1 = p1._get_model()
        m2 = p2._get_model()
        assert m1 is m2
