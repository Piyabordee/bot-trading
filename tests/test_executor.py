"""Tests for executor module."""
import pytest
from decimal import Decimal
from unittest.mock import Mock
from bot_trading.execution.executor import Executor
from bot_trading.strategy.base import Signal
from bot_trading.providers.base import BaseProvider


def test_executor_requires_provider_and_risk_limits():
    """Executor should require provider and risk limits."""
    with pytest.raises(TypeError):
        Executor()  # type: ignore


def test_executor_validates_risk_before_execution():
    """Executor should check risk limits before executing orders."""
    mock_provider = Mock(spec=BaseProvider)
    mock_risk = Mock()
    mock_risk.check_order_size.return_value = Mock(allowed=False, reason="Too large")

    executor = Executor(provider=mock_provider, risk_limits=mock_risk)
    signal = Signal(symbol="AAPL", action="buy", confidence=0.8, quantity=Decimal("100"))

    result = executor.execute_signal(signal)
    assert result.executed is False
    assert "risk" in result.reason.lower() or "failed" in result.reason.lower()
