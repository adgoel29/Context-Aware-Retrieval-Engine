import pytest
import numpy as np
from src.vector_store import VectorStore
from src.embeddings import EmbeddingResult

@pytest.fixture
def sample_corpus():
    return [
        {"id": 0, "topic": "load_balancing", "chunk_text": "The load balancer distributes traffic"},
        {"id": 1, "topic": "caching", "chunk_text": "Redis stores frequently accessed data"},
        {"id": 2, "topic": "autoscaling", "chunk_text": "Horizontal scaling adds more instances"},
    ]

@pytest.fixture
def fake_embedding():
    return np.full((384,), 0.1, dtype=np.float32)

@pytest.fixture
def mock_embedding_model(mocker, fake_embedding):
    mock = mocker.MagicMock()
    mock.embed_single.return_value = fake_embedding
    mock.get_embeddings.return_value = [EmbeddingResult(values=fake_embedding)]
    mock._model.get_sentence_embedding_dimension.return_value = 384
    return mock

@pytest.fixture
def mock_expander(mocker):
    mock = mocker.MagicMock()
    mock.expand.return_value = "autoscaling load balancer traffic spike horizontal scaling"
    return mock

@pytest.fixture
def real_vector_store():
    return VectorStore(similarity_metric="cosine")