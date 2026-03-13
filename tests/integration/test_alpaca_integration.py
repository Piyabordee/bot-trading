"""Integration tests for AlpacaProvider.

These tests require valid API credentials and will be skipped
in CI/CD unless credentials are available.
"""

import os
import pytest
from datetime import date, datetime
from decimal import Decimal

from bot_trading.providers.alpaca import AlpacaProvider
from bot_trading.exceptions import APIError


@pytest.mark.skipif(
    not all([os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_API_SECRET")]),
    reason="Alpaca credentials not available",
)
def test_alpaca_real_connection():
    """Test real connection to Alpaca Paper Trading API."""
    provider = AlpacaProvider()

    # Should not raise
    account = provider.get_account()
    assert account is not None
    assert account.cash >= 0


@pytest.mark.skipif(
    not all([os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_API_SECRET")]),
    reason="Alpaca credentials not available",
)
def test_alpaca_get_real_historical_data():
    """Test fetching real historical data."""
    provider = AlpacaProvider()

    bars = provider.get_historical_bars(
        symbol="AAPL", start_date=date(2025, 3, 1), end_date=date(2025, 3, 5), timeframe="1Day"
    )

    # Should have data for these trading days
    assert len(bars) > 0
    assert bars[0].symbol == "AAPL"
    assert bars[0].close > 0


@pytest.mark.skipif(
    not all([os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_API_SECRET")]),
    reason="Alpaca credentials not available",
)
def test_alpaca_paper_url_only(monkeypatch):
    """Should only connect to paper trading URL."""
    # Use monkeypatch for safer env var handling
    monkeypatch.setenv("ALPACA_BASE_URL", "https://api.alpaca.markets")

    with pytest.raises(ValueError, match="Refusing to connect"):
        AlpacaProvider()
