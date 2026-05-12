import numpy as np
from src.vector_store import VectorStore

def make_random_vec():
    return np.random.rand(384).astype("float32")

def test_add_increases_count(real_vector_store):
    real_vector_store.add("some text", make_random_vec())
    assert real_vector_store.count() == 1

def test_add_batch_increases_count(real_vector_store):
    vecs = [make_random_vec() for _ in range(3)]
    real_vector_store.add_batch(["a", "b", "c"], vecs)
    assert real_vector_store.count() == 3

def test_search_returns_top_k(real_vector_store):
    for i in range(5):
        real_vector_store.add(f"chunk {i}", make_random_vec())
    results = real_vector_store.search(make_random_vec(), top_k=3)
    assert len(results) == 3

def test_search_result_structure(real_vector_store):
    real_vector_store.add("some chunk", make_random_vec(), {"topic": "test"})
    result = real_vector_store.search(make_random_vec(), top_k=1)[0]
    assert all(k in result for k in ["rank", "chunk_text", "score", "metadata", "chunk_id"])

def test_cosine_similarity_ranking(real_vector_store):
    query = np.ones(384, dtype="float32")
    real_vector_store.add("identical", query.copy())
    real_vector_store.add("opposite", -query.copy())
    results = real_vector_store.search(query, top_k=2)
    assert results[0]["chunk_text"] == "identical"

def test_reset_clears_store(real_vector_store):
    real_vector_store.add("text", make_random_vec())
    real_vector_store.reset()
    assert real_vector_store.count() == 0