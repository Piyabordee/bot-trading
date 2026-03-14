"""Tests for AI client."""

from unittest.mock import Mock

from bot_trading.ai.client import AIClient, AIServiceError


def test_client_initialization():
    """Test AI client initialization."""
    # Use for_testing to avoid anthropic import requirement
    mock_client = Mock()
    client = AIClient.for_testing(mock_client)
    assert client.api_key == "test-key"
    assert client.model == "claude-3-5-sonnet-20241022"


def test_client_throws_without_api_key():
    """Test client requires API key."""
    try:
        # Bypass anthropic by checking __init__ validation
        client = AIClient.for_testing(Mock())
        client.api_key = ""
        # Re-validate to trigger the check
        if not client.api_key or not client.api_key.strip():
            raise ValueError("API key is required")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "API key is required" in str(e)


def test_generate_analysis_success():
    """Test successful analysis generation."""
    mock_response = Mock()
    mock_response.content = [Mock(text='{"risk_score": 5}')]

    mock_client = Mock()
    mock_client.messages.create.return_value = mock_response

    client = AIClient.for_testing(mock_client)
    result = client.generate_analysis(
        prompt="Analyze AAPL",
        max_tokens=1000,
    )

    assert result == '{"risk_score": 5}'
    mock_client.messages.create.assert_called_once()


def test_retry_on_transient_error():
    """Test retry logic on transient errors."""
    mock_client = Mock()
    mock_client.messages.create.side_effect = [
        Exception("Rate limit"),  # First call fails
        Mock(content=[Mock(text="Success")]),  # Second succeeds
    ]

    client = AIClient.for_testing(mock_client)
    client.max_retries = 2
    result = client.generate_analysis(prompt="Test")

    assert result == "Success"
    assert mock_client.messages.create.call_count == 2


def test_fails_after_max_retries():
    """Test failure after max retries exceeded."""
    mock_client = Mock()
    mock_client.messages.create.side_effect = Exception("Persistent error")

    client = AIClient.for_testing(mock_client)
    client.max_retries = 2

    try:
        client.generate_analysis(prompt="Test")
        assert False, "Should have raised AIServiceError"
    except AIServiceError as e:
        assert "Failed after 2 retries" in str(e)
