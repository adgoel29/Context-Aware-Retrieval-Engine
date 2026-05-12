import pytest
from src.pipeline import RAGPipeline

def test_ingest_sets_flag(mock_embedding_model, real_vector_store, mock_expander, sample_corpus):
    pipeline = RAGPipeline(mock_embedding_model, real_vector_store, mock_expander)
    pipeline.ingest(sample_corpus)
    assert pipeline._is_ingested == True

def test_ingest_returns_correct_count(mock_embedding_model, real_vector_store, mock_expander, sample_corpus):
    pipeline = RAGPipeline(mock_embedding_model, real_vector_store, mock_expander)
    result = pipeline.ingest(sample_corpus)
    assert result["chunks_ingested"] == 3

def test_strategy_a_returns_results(mock_embedding_model, real_vector_store, mock_expander, sample_corpus):
    pipeline = RAGPipeline(mock_embedding_model, real_vector_store, mock_expander)
    pipeline.ingest(sample_corpus)
    result = pipeline.retrieve_strategy_a("test query")
    assert result["strategy"] == "A"
    assert isinstance(result["results"], list)
    mock_expander.expand.assert_not_called()

def test_strategy_b_calls_expander(mock_embedding_model, real_vector_store, mock_expander, sample_corpus):
    pipeline = RAGPipeline(mock_embedding_model, real_vector_store, mock_expander)
    pipeline.ingest(sample_corpus)
    result = pipeline.retrieve_strategy_b("test query")
    mock_expander.expand.assert_called_once()
    assert result["strategy"] == "B"
    assert result["expanded_query"]

def test_strategy_b_raises_without_expander(mock_embedding_model, real_vector_store):
    pipeline = RAGPipeline(mock_embedding_model, real_vector_store, query_expander=None)
    with pytest.raises(ValueError):
        pipeline.retrieve_strategy_b("test query")

def test_compare_returns_both_strategies(mock_embedding_model, real_vector_store, mock_expander, sample_corpus):
    pipeline = RAGPipeline(mock_embedding_model, real_vector_store, mock_expander)
    pipeline.ingest(sample_corpus)
    result = pipeline.compare("test query")
    assert "strategy_a" in result and "strategy_b" in result
    assert all(k in result for k in ["overlap", "unique_to_a", "unique_to_b"])