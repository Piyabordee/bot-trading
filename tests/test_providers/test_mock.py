# tests/test_providers/test_mock.py
from datetime import date
from decimal import Decimal

from bot_trading.providers.mock import MockProvider
from bot_trading.providers.base import Bar, Account


def test_mock_provider_initialization():
    """MockProvider should initialize with default values."""
    provider = MockProvider()

    assert provider is not None
    assert provider.balance == Decimal("100000")


def test_mock_provider_get_account():
    """Should return Account with current balance."""
    provider = MockProvider()
    account = provider.get_account()

    assert isinstance(account, Account)
    assert account.cash == Decimal("100000")
    assert account.buying_power == Decimal("100000")


def test_mock_provider_get_positions_empty():
    """Should return empty list initially."""
    provider = MockProvider()
    positions = provider.get_positions()

    assert positions == []


def test_mock_provider_get_latest_price():
    """Should return price for known symbols."""
    provider = MockProvider()

    price = provider.get_latest_price("AAPL")
    assert price == Decimal("150.00")

    price = provider.get_latest_price("TSLA")
    assert price == Decimal("250.00")


def test_mock_provider_get_historical_bars():
    """Should return generated bar data."""
    provider = MockProvider()
    bars = provider.get_historical_bars(
        symbol="AAPL", start_date=date(2025, 3, 1), end_date=date(2025, 3, 5)
    )

    assert len(bars) > 0
    for bar in bars:
        assert isinstance(bar, Bar)
        assert bar.symbol == "AAPL"


def test_mock_provider_get_order_history():
    """Should return empty order history initially."""
    provider = MockProvider()
    orders = provider.get_order_history(days=7)

    assert orders == []


def test_mock_provider_state_persistence():
    """Should maintain state between submit_order and get_positions."""
    provider = MockProvider()

    # Submit a buy order
    _ = provider.submit_order("AAPL", "buy", Decimal("10"))

    # Check position is updated
    positions = provider.get_positions()
    assert len(positions) == 1
    assert positions[0].symbol == "AAPL"
    assert positions[0].quantity == Decimal("10")


def test_mock_provider_decimal_precision():
    """Should maintain Decimal precision for prices."""
    provider = MockProvider()

    price = provider.get_latest_price("AAPL")
    assert isinstance(price, Decimal)
    assert price.as_tuple().exponent >= -2  # At least 2 decimal places
