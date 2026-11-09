import logging
from dataclasses import dataclass

from app.domain.entities.document import Document
from app.domain.entities.chunk import Chunk
from app.domain.repositories.document_repository import (
    DocumentRepository,
)
from app.domain.repositories.chunk_repository import (
    ChunkRepository,
)
from app.domain.repositories.embedding_provider import (
    EmbeddingProvider,
)
from app.domain.repositories.vector_store_repository import (
    VectorStoreRepository,
)
from app.infrastructure.document_processing import DocumentExtractor
from app.services.text_processing.cleaner import TextCleaner
from app.services.text_processing.chunker import TextChunker
from app.services.text_processing.quality_analyzer import (
    TextQualityAnalyzer,
)
from app.config.settings import settings
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    document: Document
    chunks: list[Chunk]
    indexed: bool


class DocumentProcessingPipeline:

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = (
            chunk_overlap or settings.chunk_overlap
        )
        self.cleaner = TextCleaner()
        self.chunker = TextChunker(
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap,
        )
        self.quality_analyzer = TextQualityAnalyzer()

    def process(
        self, file_path: str, document_name: str | None = None
    ) -> tuple[Document, list[Chunk]]:
        document = DocumentExtractor.extract(file_path)
        if document_name:
            document.name = document_name

        cleaned_content = self.cleaner.clean(
            document.content
        )

        quality = self.quality_analyzer.analyze(
            cleaned_content
        )

        if quality.is_poor_quality:
            document.status = "NEEDS_OCR"
            logger.warning(
                f"Poor text quality for "
                f"{document.name}: "
                f"score={quality.quality_score:.2f}"
            )

        document.content = cleaned_content
        document.metadata["quality_score"] = (
            quality.quality_score
        )
        document.metadata["quality_metrics"] = {
            "char_count": quality.char_count,
            "arabic_ratio": quality.arabic_ratio,
            "replacement_ratio": (
                quality.replacement_ratio
            ),
            "suspicious_count": (
                quality.suspicious_count
            ),
        }

        pages_text = document.metadata.get(
            "pages_text"
        )

        if pages_text and len(pages_text) > 1:
            text_chunks = self.chunker.split_pages(
                pages_text
            )
        else:
            text_chunks = self.chunker.split(
                cleaned_content
            )

        chunks = self._build_chunks(
            document=document,
            text_chunks=text_chunks,
        )

        return document, chunks

    def ingest(
        self,
        file_path: str,
        document_repo: DocumentRepository,
        chunk_repo: ChunkRepository,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStoreRepository,
        document_name: str | None = None,
    ) -> IngestionResult:
        document, chunks = self.process(file_path, document_name=document_name)

        if document.status == "NEEDS_OCR":
            document.status = "UPLOADED"
            document.size = len(document.content)

            document = document_repo.save(document)

            return IngestionResult(
                document=document,
                chunks=[],
                indexed=False,
            )

        document.status = "PROCESSING"
        document.size = len(document.content)

        try:
            document = document_repo.save(document)
            logger.info(
                f"Document saved: {document.id}"
            )
        except Exception as e:
            logger.error(
                f"Failed to save document: {e}"
            )
            raise DocumentProcessingError(
                f"Failed to save document: {e}"
            ) from e

        try:
            saved_chunks = chunk_repo.save_many(chunks)
            logger.info(
                f"Chunks saved: {len(saved_chunks)}"
            )
        except Exception as e:
            logger.error(f"Failed to save chunks: {e}")
            document.status = "FAILED"
            document_repo.update(document)
            raise DocumentProcessingError(
                f"Failed to save chunks: {e}"
            ) from e

        try:
            texts = [c.content for c in saved_chunks]
            embeddings = (
                embedding_provider.embed_documents(texts)
            )
            logger.info(
                f"Embeddings generated: {len(embeddings)}"
            )
        except Exception as e:
            logger.error(
                f"Failed to generate embeddings: {e}"
            )
            document.status = "FAILED"
            document_repo.update(document)
            raise DocumentProcessingError(
                f"Failed to generate embeddings: {e}"
            ) from e

        try:
            vector_store.add(
                chunks=saved_chunks,
                embeddings=embeddings,
            )
            vector_store.save()
            logger.info("Vectors stored and persisted")
        except Exception as e:
            logger.error(
                f"Failed to store vectors: {e}"
            )
            document.status = "FAILED"
            document_repo.update(document)
            raise DocumentProcessingError(
                f"Failed to store vectors: {e}"
            ) from e

        document.status = "INDEXED"
        document = document_repo.update(document)
        logger.info(
            f"Document indexed: {document.id}"
        )

        return IngestionResult(
            document=document,
            chunks=saved_chunks,
            indexed=True,
        )

    def _build_chunks(
        self,
        document: Document,
        text_chunks: list,
    ) -> list[Chunk]:
        chunks = []

        for text_chunk in text_chunks:
            chunk_metadata = {
                "document_id": document.id,
                "document_name": document.name,
                "file_type": document.file_type,
                "chunk_index": text_chunk.chunk_index,
                "total_chunks": len(text_chunks),
            }

            if text_chunk.page is not None:
                chunk_metadata["page"] = text_chunk.page

            if document.pages:
                chunk_metadata["total_pages"] = (
                    document.pages
                )

            if document.metadata:
                safe_meta = {
                    k: v
                    for k, v in document.metadata.items()
                    if k != "pages_text"
                }
                chunk_metadata.update(safe_meta)

            chunk = Chunk(
                document_id=document.id,
                content=text_chunk.content,
                chunk_index=text_chunk.chunk_index,
                metadata=chunk_metadata,
            )

            chunks.append(chunk)

        return chunks
