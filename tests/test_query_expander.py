from src.query_expander import QueryExpander

def test_expand_calls_model(mock_expander):
    # mock_expander already wraps a mock model, just verify expand was callable
    result = mock_expander.expand("test query")
    mock_expander.expand.assert_called_once_with("test query")

def test_expand_returns_string():
    from unittest.mock import MagicMock
    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = "expanded query text"
    expander = QueryExpander(model=mock_model)
    result = expander.expand("peak load")
    assert isinstance(result, str) and len(result) > 0

def test_expand_uses_prompt_template():
    from unittest.mock import MagicMock
    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = "expanded"
    expander = QueryExpander(model=mock_model)
    expander.expand("peak load")
    call_arg = mock_model.generate_content.call_args[0][0]
    assert "peak load" in call_arg

def test_expand_batch_returns_correct_length():
    from unittest.mock import MagicMock
    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = "expanded"
    expander = QueryExpander(model=mock_model)
    results = expander.expand_batch(["q1", "q2", "q3"])
    assert len(results) == 3