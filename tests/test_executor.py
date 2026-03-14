"""Tests for executor module."""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock
from bot_trading.execution.executor import Executor, ExecutionResult
from bot_trading.strategy.base import Signal
from bot_trading.providers.base import BaseProvider, Order
from bot_trading.risk.limits import RiskLimits


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


@pytest.fixture
def mock_provider():
    """Create a mock provider."""
    provider = Mock(spec=BaseProvider)
    provider.submit_order.return_value = Order(
        order_id="test_order_123",
        symbol="AAPL",
        side="buy",
        quantity=Decimal("100"),
        price=Decimal("175.50"),
        status="submitted",
        created_at=datetime.now(),
    )
    return provider


@pytest.fixture
def risk_limits():
    """Create RiskLimits instance."""
    return RiskLimits(
        max_position_size=1000,
        max_portfolio_exposure=Decimal("0.2"),
        daily_loss_limit=Decimal("500"),
    )


@pytest.fixture
def executor(mock_provider, risk_limits):
    """Create Executor instance."""
    return Executor(provider=mock_provider, risk_limits=risk_limits)


class TestExecutorRealExecution:
    """Test actual order execution."""

    def test_execute_valid_buy_order(self, executor, mock_provider):
        """Test executing a valid buy order."""
        signal = Signal(
            symbol="AAPL",
            action="buy",
            confidence=0.8,
            quantity=Decimal("100"),
            reason="Technical breakout",
        )

        result = executor.execute_signal(signal)

        assert result.executed is True
        assert result.order_id == "test_order_123"
        assert result.reason == ""
        mock_provider.submit_order.assert_called_once()

    def test_execute_valid_sell_order(self, executor, mock_provider):
        """Test executing a valid sell order."""
        signal = Signal(
            symbol="AAPL",
            action="sell",
            confidence=0.7,
            quantity=Decimal("50"),
            reason="Take profit",
        )

        result = executor.execute_signal(signal)

        assert result.executed is True
        assert result.order_id == "test_order_123"

    def test_execute_market_order_no_price(self, executor, mock_provider):
        """Test market order without price specified."""
        signal = Signal(
            symbol="AAPL",
            action="buy",
            confidence=0.8,
            quantity=Decimal("100"),
        )

        result = executor.execute_signal(signal)

        assert result.executed is True
        # Verify market order was submitted
        call_args = mock_provider.submit_order.call_args
        assert call_args[1]["order_type"] == "market"

    def test_execute_order_provider_failure(self, executor, mock_provider):
        """Test handling provider failure."""
        mock_provider.submit_order.side_effect = Exception("Provider error")

        signal = Signal(
            symbol="AAPL",
            action="buy",
            confidence=0.8,
            quantity=Decimal("100"),
        )

        result = executor.execute_signal(signal)

        assert result.executed is False
        assert "Provider error" in result.reason
