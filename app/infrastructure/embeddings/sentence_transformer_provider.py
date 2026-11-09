from sentence_transformers import SentenceTransformer

from app.config.settings import settings
from app.core.exceptions import EmbeddingError
from app.domain.repositories.embedding_provider import (
    EmbeddingProvider,
)


class SentenceTransformerEmbeddingProvider(
    EmbeddingProvider
):
    _instance: SentenceTransformer | None = None
    _model_name: str | None = None

    def __init__(
        self,
        model_name: str | None = None,
    ) -> None:
        self._model_name = (
            model_name or settings.embedding_model
        )

    def _get_model(self) -> SentenceTransformer:
        if (
            SentenceTransformerEmbeddingProvider._instance
            is None
            or SentenceTransformerEmbeddingProvider._model_name
            != self._model_name
        ):
            try:
                SentenceTransformerEmbeddingProvider._instance = SentenceTransformer(
                    self._model_name
                )
                SentenceTransformerEmbeddingProvider._model_name = (
                    self._model_name
                )
            except Exception as e:
                raise EmbeddingError(
                    f"Failed to load embedding model "
                    f"'{self._model_name}': {e}"
                ) from e

        return (
            SentenceTransformerEmbeddingProvider._instance
        )

    @property
    def dimension(self) -> int:
        model = self._get_model()
        return model.get_embedding_dimension()

    def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            raise EmbeddingError(
                "Cannot create embedding for empty text."
            )

        try:
            model = self._get_model()
            embedding = model.encode(
                text,
                normalize_embeddings=True,
            )
            return embedding.tolist()
        except EmbeddingError:
            raise
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
            model = self._get_model()
            embeddings = model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            return embeddings.tolist()
        except EmbeddingError:
            raise
        except Exception as e:
            raise EmbeddingError(
                f"Failed to generate embeddings: {e}"
            ) from e
