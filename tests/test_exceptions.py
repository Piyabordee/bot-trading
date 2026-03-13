# tests/test_exceptions.py
import pytest
from bot_trading.exceptions import (
    TradingAnalysisError,
    APIError,
    InsufficientDataError,
    StrategyNotFoundError,
    RiskLimitExceededError,
    InvalidConfigError,
)

def test_api_error_can_be_raised_and_caught():
    with pytest.raises(APIError) as exc_info:
        raise APIError("Cannot connect to API")
    assert str(exc_info.value) == "Cannot connect to API"

def test_api_error_is_trading_analysis_error():
    with pytest.raises(TradingAnalysisError):
        raise APIError("Test")

def test_insufficient_data_error():
    with pytest.raises(InsufficientDataError) as exc_info:
        raise InsufficientDataError("Not enough bars")
    assert "Not enough bars" in str(exc_info.value)

def test_strategy_not_found_error():
    with pytest.raises(StrategyNotFoundError):
        raise StrategyNotFoundError("unknown_strategy")

def test_risk_limit_exceeded_error():
    with pytest.raises(RiskLimitExceededError):
        raise RiskLimitExceededError("Position exceeds 10%")

def test_invalid_config_error():
    with pytest.raises(InvalidConfigError):
        raise InvalidConfigError("Invalid parameter")
