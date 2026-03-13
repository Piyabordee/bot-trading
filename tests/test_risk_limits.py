"""Tests for risk limits module."""
from decimal import Decimal
from bot_trading.risk.limits import RiskLimits


def test_risk_limits_blocks_order_exceeding_max_position():
    """Should reject orders larger than max position size."""
    limits = RiskLimits(max_position_size=Decimal("1000"))
    result = limits.check_order_size(quantity=Decimal("1500"))
    assert result.allowed is False
    assert "exceeds maximum" in result.reason.lower()


def test_risk_limits_allows_order_within_limits():
    """Should allow orders within risk limits."""
    limits = RiskLimits(max_position_size=Decimal("1000"))
    result = limits.check_order_size(quantity=Decimal("500"))
    assert result.allowed is True


def test_risk_limits_enforces_portfolio_exposure():
    """Should check portfolio exposure limits."""
    limits = RiskLimits(
        max_position_size=Decimal("1000"),
        max_portfolio_exposure=Decimal("0.2"),
        portfolio_value=Decimal("100000")
    )
    result = limits.check_portfolio_exposure(new_value=Decimal("25000"))
    assert result.allowed is False
    assert "exposure" in result.reason.lower()


def test_risk_limits_blocks_duplicate_orders():
    """Should prevent duplicate orders for same symbol."""
    limits = RiskLimits()
    limits.record_order("AAPL", "buy")
    result = limits.check_duplicate_order("AAPL", "buy", within_seconds=60)
    assert result.allowed is False


def test_risk_limits_allows_different_symbols():
    """Should allow orders for different symbols."""
    limits = RiskLimits()
    limits.record_order("AAPL", "buy")
    result = limits.check_duplicate_order("TSLA", "buy", within_seconds=60)
    assert result.allowed is True
