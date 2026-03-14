"""Tests for AI output config schema."""

import json

from pydantic import ValidationError

from bot_trading.ai.schema import (
    AIAnalysisResult,
    SymbolRecommendation,
    PortfolioRisk,
    Sentiment,
    TradingAction,
)


def test_valid_minimal_schema():
    """Test minimal valid schema validation."""
    data = {
        "overall_sentiment": "neutral",
        "symbols": {},
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": [],
        }
    }

    result = AIAnalysisResult.model_validate(data)
    assert result.overall_sentiment == Sentiment.NEUTRAL


def test_valid_full_schema():
    """Test full valid schema with all fields."""
    data = {
        "overall_sentiment": "bullish",
        "symbols": {
            "AAPL": {
                "action": "BUY",
                "confidence": 0.75,
                "risk_score": 4,
                "reasoning": "Strong momentum with reasonable valuation",
                "entry_price": 175.50,
                "stop_loss": 170.00,
                "target_price": 185.00,
                "position_size_pct": 0.08,
            }
        },
        "portfolio_risk": {
            "current_exposure": 0.15,
            "recommended_max_exposure": 0.2,
            "risk_factors": ["Market near all-time highs"],
        }
    }

    result = AIAnalysisResult.model_validate(data)
    assert result.symbols["AAPL"].action == TradingAction.BUY
    assert result.symbols["AAPL"].confidence == 0.75


def test_invalid_action():
    """Test validation rejects invalid action."""
    data = {
        "overall_sentiment": "neutral",
        "symbols": {
            "AAPL": {
                "action": "INVALID_ACTION",
                "confidence": 0.5,
                "risk_score": 5,
                "reasoning": "test",
            }
        },
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": [],
        }
    }

    try:
        AIAnalysisResult.model_validate(data)
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected


def test_risk_score_range():
    """Test risk score must be 1-10."""
    data = {
        "overall_sentiment": "neutral",
        "symbols": {
            "AAPL": {
                "action": "HOLD",
                "confidence": 0.5,
                "risk_score": 15,  # Invalid!
                "reasoning": "test",
            }
        },
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": [],
        }
    }

    try:
        AIAnalysisResult.model_validate(data)
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected


def test_json_roundtrip():
    """Test JSON serialization/deserialization."""
    original = AIAnalysisResult(
        overall_sentiment=Sentiment.BEARISH,
        symbols={
            "MSFT": {
                "action": TradingAction.SELL,
                "confidence": 0.6,
                "risk_score": 6,
                "reasoning": "Technical breakdown",
                "position_size_pct": 0.0,
            }
        },
        portfolio_risk=PortfolioRisk(
            current_exposure=0.1,
            recommended_max_exposure=0.15,
            risk_factors=["Increasing volatility"],
        ),
    )

    # Serialize
    json_str = original.model_dump_json()

    # Deserialize
    restored = AIAnalysisResult.model_validate_json(json_str)

    assert restored.overall_sentiment == Sentiment.BEARISH
    assert restored.symbols["MSFT"].action == TradingAction.SELL
