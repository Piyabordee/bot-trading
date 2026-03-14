"""Tests for end-to-end trading analyzer."""

from unittest.mock import Mock

from bot_trading.ai.analyzer import TradingAnalyzer
from bot_trading.providers.mock import MockProvider


def test_analyzer_initialization():
    """Test analyzer initialization."""
    provider = MockProvider()
    analyzer = TradingAnalyzer(provider=provider, api_key="test-key")

    assert analyzer.provider is not None
    assert analyzer.pipeline is not None


def test_analyzer_full_analysis():
    """Test end-to-end analysis flow."""
    # Mock AI response - use return_value for the method that gets called
    mock_ai_client = Mock()
    mock_ai_client.generate_json_analysis.return_value = '''{
        "overall_sentiment": "neutral",
        "symbols": {
            "AAPL": {
                "action": "HOLD",
                "confidence": 0.6,
                "risk_score": 5,
                "reasoning": "Waiting for better entry",
                "position_size_pct": 0.0
            }
        },
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": []
        }
    }'''

    provider = MockProvider()
    analyzer = TradingAnalyzer(provider=provider, api_key="test-key")
    analyzer.ai_client = mock_ai_client  # Inject mock

    result = analyzer.analyze(symbols=["AAPL"])

    assert result is not None
    assert result.overall_sentiment.value == "neutral"
    assert result.symbols["AAPL"].action.value == "HOLD"


def test_analyzer_includes_risk_summary():
    """Test analyzer provides risk summary."""
    # Mock AI response
    mock_ai_client = Mock()
    mock_ai_client.generate_json_analysis.return_value = '''{
        "overall_sentiment": "neutral",
        "symbols": {},
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": []
        }
    }'''

    provider = MockProvider()
    analyzer = TradingAnalyzer(provider=provider, api_key="test-key")
    analyzer.ai_client = mock_ai_client  # Inject mock

    summary = analyzer.analyze_with_risk_summary(symbols=["AAPL"])

    assert "Trading Analysis Report" in summary
