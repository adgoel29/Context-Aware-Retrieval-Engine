from src.embeddings import TextEmbeddingModelWrapper
import numpy as np

def test_from_pretrained_returns_wrapper():
    model = TextEmbeddingModelWrapper.from_pretrained("textembedding-gecko@001")
    assert isinstance(model, TextEmbeddingModelWrapper)

def test_get_embeddings_returns_list():
    model = TextEmbeddingModelWrapper.from_pretrained("textembedding-gecko@001")
    result = model.get_embeddings(["test text"])
    assert isinstance(result, list)
    assert len(result) == 1

def test_embedding_dimension():
    model = TextEmbeddingModelWrapper.from_pretrained("textembedding-gecko@001")
    result = model.get_embeddings(["test"])
    assert result[0].values.shape == (384,)

def test_embed_single_returns_flat_array():
    model = TextEmbeddingModelWrapper.from_pretrained("textembedding-gecko@001")
    result = model.embed_single("test")
    assert result.ndim == 1

def test_model_name_mapping():
    model = TextEmbeddingModelWrapper.from_pretrained("textembedding-gecko@001")
    assert model._model_name == "all-MiniLM-L6-v2"