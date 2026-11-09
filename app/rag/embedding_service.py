from sentence_transformers import SentenceTransformer

from app.config.settings import settings
from app.core.exceptions import EmbeddingError


class EmbeddingService:
    """Generate vector embeddings for text."""

    def __init__(
        self,
        model_name: str | None = None,
    ) -> None:
        self.model_name = (
            model_name or settings.embedding_model
        )
        try:
            self.model = SentenceTransformer(
                self.model_name
            )
        except Exception as e:
            raise EmbeddingError(
                f"Failed to load embedding model "
                f"'{self.model_name}': {e}"
            ) from e

    def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            raise EmbeddingError(
                "Cannot create embedding for empty text."
            )

        try:
            embedding = self.model.encode(
                text,
                normalize_embeddings=True,
            )
            return embedding.tolist()
        except Exception as e:
            raise EmbeddingError(
                f"Failed to generate embedding: {e}"
            ) from e

    def embed_documents(
        self, texts: list[str]
    ) -> list[list[float]]:
        if not texts:
            return []

        try:
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,
            )
            return embeddings.tolist()
        except Exception as e:
            raise EmbeddingError(
                f"Failed to generate embeddings: {e}"
            ) from e
