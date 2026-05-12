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
    
metadata = [
    {
        "id": 0,
        "topic": "batman",
        "chunk_text": "A billionaire vigilante protects Gotham City using advanced gadgets, detective skills, and martial arts after witnessing tragedy in childhood."
    },

    {
        "id": 1,
        "topic": "harry_potter",
        "chunk_text": "A young wizard attends a magical boarding school where students learn spells, potion-making, and defense against dark forces."
    },

    {
        "id": 2,
        "topic": "breaking_bad",
        "chunk_text": "A chemistry teacher secretly enters the illegal drug trade after being diagnosed with cancer, slowly transforming into a ruthless criminal mastermind."
    },

    {
        "id": 3,
        "topic": "minecraft",
        "chunk_text": "Players gather resources, craft tools, construct buildings, and survive against hostile creatures inside a procedurally generated sandbox world."
    },

    {
        "id": 4,
        "topic": "interstellar",
        "chunk_text": "Astronauts travel through a wormhole searching for habitable planets as Earth faces ecological collapse and food shortages."
    },

    {
        "id": 5,
        "topic": "friends",
        "chunk_text": "A group of young adults navigate relationships, careers, and everyday life while spending time together in New York City."
    },

    {
        "id": 6,
        "topic": "attack_on_titan",
        "chunk_text": "Humanity hides behind enormous walls to survive against gigantic humanoid creatures that devour people."
    },

    {
        "id": 7,
        "topic": "john_wick",
        "chunk_text": "A retired assassin returns to the criminal underworld seeking revenge after a deeply personal loss."
    },

    {
        "id": 8,
        "topic": "pokemon",
        "chunk_text": "Trainers capture fantasy creatures, battle opponents, and collect gym badges while traveling across different regions."
    },

    {
        "id": 9,
        "topic": "game_of_thrones",
        "chunk_text": "Noble families compete for political power in a medieval fantasy world filled with dragons, betrayals, and warfare."
    }
]

# embedding_model = TextEmbeddingModelWrapper.from_pretrained("textembedding-gecko@001")
# vector_store = VectorStore(similarity_metric="cosine")
# query_expander = create_gemini_expander("AIzaSyDNdyBLe6ZkFAlaHd88h80EGhLzGOlRs2k")

# ans=RAGPipeline(embedding_model,vector_store,query_expander)
# ans.ingest(metadata)
# print(ans.retrieve_strategy_b("endless world",3))