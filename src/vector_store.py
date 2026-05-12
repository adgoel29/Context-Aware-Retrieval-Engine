import faiss
import numpy as np


class VectorStore:
    """
    FAISS-backed vector store.
    Supports cosine similarity (IndexFlatIP with L2-normalized vectors)
    and Euclidean distance (IndexFlatL2).
    """

    def __init__(self, embedding_dim: int = 384, similarity_metric: str = "cosine"):
        self._embedding_dim = embedding_dim
        self._similarity_metric = similarity_metric
        self._chunks: list = []
        self._metadata: list = []
        self._index = self._build_index()

    def _build_index(self):
        if self._similarity_metric == "cosine":
            return faiss.IndexFlatIP(self._embedding_dim)   # inner product = cosine when normalized
        return faiss.IndexFlatL2(self._embedding_dim)

    def _maybe_normalize(self, vec: np.ndarray) -> np.ndarray:
        if self._similarity_metric == "cosine":
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
        return vec


    def add(self, chunk_text: str, embedding: np.ndarray, metadata: dict = None) -> None:
        vec = self._maybe_normalize(embedding).astype("float32")
        self._index.add(vec.reshape(1, -1))
        self._chunks.append(chunk_text)
        self._metadata.append(metadata or {})

    def add_batch(self, chunks: list, embeddings: list, metadata_list: list = None) -> None:
        metadata_list = metadata_list or [{}] * len(chunks)
        for chunk, emb, meta in zip(chunks, embeddings, metadata_list):
            self.add(chunk, emb, meta)


    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> list:
        vec = self._maybe_normalize(query_embedding).astype("float32")
        scores, indices = self._index.search(vec.reshape(1, -1), top_k)

        results = []
        for rank, (idx, score) in enumerate(zip(indices[0], scores[0]), start=1):
            if idx == -1:           
                continue
            results.append({
                "rank": rank,
                "chunk_id": int(idx),
                "chunk_text": self._chunks[idx],
                "score": float(score),
                "metadata": self._metadata[idx],
            })
        return results

    def count(self) -> int:
        return self._index.ntotal

    def reset(self) -> None:
        self._index = self._build_index()
        self._chunks = []
        self._metadata = []