import json
from pathlib import Path

import faiss
import numpy as np

from app.config.settings import settings
from app.domain.entities.chunk import Chunk
from app.domain.repositories.vector_store_repository import (
    VectorStoreRepository,
)
from app.core.exceptions import VectorStoreError


class FAISSVectorStore(VectorStoreRepository):

    def __init__(
        self,
        dimension: int = 384,
        store_path: str | None = None,
    ) -> None:
        self.dimension = dimension
        self.store_path = Path(
            store_path or settings.vector_store_path
        )
        self.store_path.mkdir(
            parents=True, exist_ok=True
        )

        self.index = faiss.IndexFlatIP(dimension)
        self.id_map: dict[int, str] = {}
        self.metadata_store: dict[str, dict] = {}
        self._next_id = 0

        self._load()

    def add(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> list[str]:
        if len(chunks) != len(embeddings):
            raise VectorStoreError(
                "Chunks and embeddings count mismatch"
            )

        vectors = np.array(
            embeddings, dtype=np.float32
        )

        ids = []

        for i, chunk in enumerate(chunks):
            faiss_id = self._next_id
            self._next_id += 1

            self.id_map[faiss_id] = chunk.id
            self.metadata_store[chunk.id] = {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "metadata": chunk.metadata,
                "embedding": embeddings[i],
            }

            ids.append(chunk.id)

        self.index.add(vectors)

        return ids

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        document_id: str | None = None,
    ) -> list[tuple[Chunk, float]]:
        if self.index.ntotal == 0:
            return []

        query = np.array(
            [query_embedding], dtype=np.float32
        )

        if document_id is not None:
            return self._filtered_search(
                query, top_k, document_id
            )

        actual_k = min(top_k, self.index.ntotal)

        scores, indices = self.index.search(
            query, actual_k
        )

        results = []

        for score, idx in zip(
            scores[0], indices[0]
        ):
            if idx == -1:
                continue

            chunk_id = self.id_map.get(idx)

            if chunk_id is None:
                continue

            meta = self.metadata_store.get(chunk_id)

            if meta is None:
                continue

            chunk = Chunk(
                id=meta["chunk_id"],
                document_id=meta["document_id"],
                content=meta["content"],
                chunk_index=meta["chunk_index"],
                metadata=meta["metadata"],
            )

            results.append(
                (chunk, float(score))
            )

        return results

    def _filtered_search(
        self,
        query: np.ndarray,
        top_k: int,
        document_id: str,
    ) -> list[tuple[Chunk, float]]:
        filtered_indices = []
        filtered_chunk_ids = []

        for faiss_id, cid in self.id_map.items():
            meta = self.metadata_store.get(cid)
            if (
                meta
                and meta["document_id"] == document_id
            ):
                filtered_indices.append(faiss_id)
                filtered_chunk_ids.append(cid)

        if not filtered_indices:
            return []

        vectors = np.array(
            [
                self.index.reconstruct(i)
                for i in filtered_indices
            ],
            dtype=np.float32,
        )

        scores = (query @ vectors.T).flatten()
        k = min(top_k, len(scores))
        top_idx = np.argpartition(scores, -k)[-k:]
        top_idx = top_idx[
            np.argsort(scores[top_idx])[::-1]
        ]

        results = []
        for idx in top_idx:
            score = float(scores[idx])
            cid = filtered_chunk_ids[idx]
            meta = self.metadata_store[cid]

            chunk = Chunk(
                id=meta["chunk_id"],
                document_id=meta["document_id"],
                content=meta["content"],
                chunk_index=meta["chunk_index"],
                metadata=meta["metadata"],
            )

            results.append((chunk, score))

        return results

    def delete_by_document_id(
        self, document_id: str
    ) -> bool:
        ids_to_remove = set()

        for chunk_id, meta in self.metadata_store.items():
            if meta["document_id"] == document_id:
                ids_to_remove.add(chunk_id)

        if not ids_to_remove:
            return False

        for chunk_id in ids_to_remove:
            del self.metadata_store[chunk_id]

        self._rebuild_index()
        return True

    def count(self) -> int:
        return self.index.ntotal

    def save(self) -> None:
        index_path = self.store_path / "index.faiss"
        meta_path = self.store_path / "metadata.json"
        id_map_path = self.store_path / "id_map.json"

        faiss.write_index(
            self.index, str(index_path)
        )

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata_store, f, indent=2)

        with open(id_map_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    str(k): v
                    for k, v in self.id_map.items()
                },
                f,
                indent=2,
            )

    def _load(self) -> None:
        index_path = self.store_path / "index.faiss"
        meta_path = self.store_path / "metadata.json"
        id_map_path = self.store_path / "id_map.json"

        if not index_path.exists():
            return

        try:
            self.index = faiss.read_index(
                str(index_path)
            )

            if meta_path.exists():
                with open(
                    meta_path, "r", encoding="utf-8"
                ) as f:
                    self.metadata_store = json.load(f)

            if id_map_path.exists():
                with open(
                    id_map_path, "r", encoding="utf-8"
                ) as f:
                    raw = json.load(f)
                    self.id_map = {
                        int(k): v
                        for k, v in raw.items()
                    }

            if self.id_map:
                self._next_id = max(self.id_map.keys()) + 1
            else:
                self._next_id = 0

        except Exception as e:
            raise VectorStoreError(
                f"Failed to load vector store: {e}"
            ) from e

    def _rebuild_index(self) -> None:
        new_index = faiss.IndexFlatIP(self.dimension)
        new_id_map: dict[int, str] = {}
        new_metadata: dict[str, dict] = {}
        new_next_id = 0

        remaining = list(self.metadata_store.values())

        if not remaining:
            self.index = new_index
            self.id_map = new_id_map
            self.metadata_store = new_metadata
            self._next_id = 0
            self.save()
            return

        remaining.sort(
            key=lambda x: x["chunk_index"]
        )

        embeddings_list = [
            c["embedding"] for c in remaining
        ]

        vectors = np.array(
            embeddings_list, dtype=np.float32
        )

        for chunk_data in remaining:
            faiss_id = new_next_id
            new_next_id += 1
            new_id_map[faiss_id] = chunk_data[
                "chunk_id"
            ]
            new_metadata[chunk_data["chunk_id"]] = (
                chunk_data
            )

        new_index.add(vectors)

        self.index = new_index
        self.id_map = new_id_map
        self.metadata_store = new_metadata
        self._next_id = new_next_id

        self.save()
