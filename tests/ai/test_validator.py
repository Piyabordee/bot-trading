"""Tests for config validator."""

import json

from bot_trading.ai.validator import ConfigValidator, ValidationError
from bot_trading.ai.schema import AIAnalysisResult


def test_validate_valid_json():
    """Test validation of valid JSON string."""
    json_str = '''{
        "overall_sentiment": "neutral",
        "symbols": {},
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": []
        }
    }'''

    validator = ConfigValidator()
    result = validator.validate_json(json_str)

    assert isinstance(result, AIAnalysisResult)
    assert result.overall_sentiment.value == "neutral"


def test_validate_invalid_json():
    """Test validation of invalid JSON."""
    json_str = '{"invalid": json}'

    validator = ConfigValidator()

    try:
        validator.validate_json(json_str)
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "Invalid JSON" in str(e)


def test_validate_invalid_schema():
    """Test validation of JSON with invalid schema."""
    json_str = '''{
        "overall_sentiment": "invalid",
        "symbols": {},
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": []
        }
    }'''

    validator = ConfigValidator()

    try:
        validator.validate_json(json_str)
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass  # Expected


def test_validate_extracts_json_from_markdown():
    """Test validator extracts JSON from markdown code blocks."""
    markdown = """Here's my analysis:

```json
{
    "overall_sentiment": "bullish",
    "symbols": {},
    "portfolio_risk": {
        "current_exposure": 0.0,
        "recommended_max_exposure": 0.2,
        "risk_factors": []
    }
}
```

That's my recommendation!"""

    validator = ConfigValidator()
    result = validator.validate_json(markdown)

    assert result.overall_sentiment.value == "bullish"


def test_validate_with_custom_limits():
    """Test validation with custom risk limits."""
    json_str = '''{
        "overall_sentiment": "neutral",
        "symbols": {
            "AAPL": {
                "action": "BUY",
                "confidence": 0.8,
                "risk_score": 5,
                "reasoning": "test",
                "position_size_pct": 0.15
            }
        },
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": []
        }
    }'''

    validator = ConfigValidator(max_position_risk_pct=0.10)

    try:
        validator.validate_json(json_str)
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "exceeds maximum" in str(e)
