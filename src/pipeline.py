from src.embeddings import TextEmbeddingModelWrapper
from src.vector_store import VectorStore
from src.query_expander import QueryExpander,create_gemini_expander
import os

class RAGPipeline:
    """
    Central orchestrator.
    Handles ingestion + both retrieval strategies.
    All dependencies are injected — nothing is created internally.
    """

    def __init__(
        self,
        embedding_model: TextEmbeddingModelWrapper,
        vector_store: VectorStore,
        query_expander: QueryExpander = None,
    ):
        self._embedding_model = embedding_model
        self._vector_store = vector_store
        self._query_expander = query_expander
        self._is_ingested = False

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest(self, corpus_metadata: list) -> dict:
        """Embed and store all corpus chunks."""
        for entry in corpus_metadata:
            embedding = self._embedding_model.embed_single(entry["chunk_text"])
            self._vector_store.add(entry["chunk_text"], embedding, metadata=entry)

        self._is_ingested = True
        return {
            "chunks_ingested": self._vector_store.count(),
            "embedding_dim": self._embedding_model._model.get_sentence_embedding_dimension(),
            "status": "success",
        }

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve_strategy_a(self, query: str, top_k: int = 3) -> dict:
        """Strategy A: raw query → embed → search."""
        query_embedding = self._embedding_model.embed_single(query)
        results = self._vector_store.search(query_embedding, top_k)
        return {
            "strategy": "A",
            "original_query": query,
            "query_used_for_search": query,
            "results": results,
            "top_k": top_k,
        }

    def retrieve_strategy_b(self, query: str, top_k: int = 3) -> dict:
        """Strategy B: query → LLM expansion → embed expanded query → search."""
        if self._query_expander is None:
            raise ValueError("query_expander is required for Strategy B but was not provided.")

        expanded_query = self._query_expander.expand(query)
        expanded_embedding = self._embedding_model.embed_single(expanded_query)
        results = self._vector_store.search(expanded_embedding, top_k)
        return {
            "strategy": "B",
            "original_query": query,
            "expanded_query": expanded_query,
            "query_used_for_search": expanded_query,
            "results": results,
            "top_k": top_k,
        }

    def compare(self, query: str, top_k: int = 3) -> dict:
        """Run both strategies and compute overlap / unique sets."""
        result_a = self.retrieve_strategy_a(query, top_k)
        result_b = self.retrieve_strategy_b(query, top_k)

        ids_a = {r["chunk_id"] for r in result_a["results"]}
        ids_b = {r["chunk_id"] for r in result_b["results"]}

        return {
            "query": query,
            "strategy_a": result_a,
            "strategy_b": result_b,
            "overlap": sorted(ids_a & ids_b),
            "unique_to_a": sorted(ids_a - ids_b),
            "unique_to_b": sorted(ids_b - ids_a),
        }
    