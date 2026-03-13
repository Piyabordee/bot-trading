# tests/test_providers/test_alpaca_historical_bars.py
import os
from datetime import date, datetime
from decimal import Decimal
import pytest
from bot_trading.providers.alpaca import AlpacaProvider
from bot_trading.providers.base import Bar
from bot_trading.exceptions import APIError, InvalidConfigError

os.environ["ALPACA_API_KEY"] = "test_key"
os.environ["ALPACA_API_SECRET"] = "test_secret"
os.environ["ALPACA_BASE_URL"] = "https://paper-api.alpaca.markets"


def test_get_historical_bars_returns_bar_objects():
    """Should return list of Bar objects with OHLCV data."""
    from unittest.mock import Mock, patch

    # Mock the StockHistoricalDataClient class at source
    mock_bar = Mock()
    mock_bar.symbol = "AAPL"
    mock_bar.timestamp = datetime(2025, 3, 14, 9, 30)
    mock_bar.open = 150.0
    mock_bar.high = 151.0
    mock_bar.low = 149.5
    mock_bar.close = 150.5
    mock_bar.volume = 10000

    mock_bars_data = Mock()
    mock_bars_data.data = {"AAPL": [mock_bar]}

    mock_client_instance = Mock()
    mock_client_instance.get_stock_bars.return_value = mock_bars_data

    # Patch at the source module where the class is defined
    with patch(
        "alpaca.data.historical.StockHistoricalDataClient", return_value=mock_client_instance
    ):
        provider = AlpacaProvider()
        bars = provider.get_historical_bars(
            symbol="AAPL", start_date=date(2025, 3, 1), end_date=date(2025, 3, 14), timeframe="1Day"
        )

        assert isinstance(bars, list)
        for bar in bars:
            assert isinstance(bar, Bar)
            assert bar.symbol == "AAPL"
            assert isinstance(bar.open, Decimal)
            assert isinstance(bar.high, Decimal)
            assert isinstance(bar.low, Decimal)
            assert isinstance(bar.close, Decimal)
            assert isinstance(bar.volume, int)


def test_get_historical_bars_empty_result():
    """Should return empty list when no data available."""
    from unittest.mock import Mock, patch

    mock_bars_data = Mock()
    mock_bars_data.data = {}

    mock_client_instance = Mock()
    mock_client_instance.get_stock_bars.return_value = mock_bars_data

    with patch(
        "alpaca.data.historical.StockHistoricalDataClient", return_value=mock_client_instance
    ):
        provider = AlpacaProvider()
        bars = provider.get_historical_bars(
            symbol="INVALID",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 1, 5),
        )

        assert bars == []


def test_get_historical_bars_invalid_timeframe():
    """Should raise InvalidConfigError for invalid timeframe."""

    provider = AlpacaProvider()

    with pytest.raises(InvalidConfigError, match="Invalid timeframe"):
        provider.get_historical_bars(
            symbol="AAPL",
            start_date=date(2025, 3, 1),
            end_date=date(2025, 3, 5),
            timeframe="InvalidTimeframe",
        )


def test_get_historical_bars_handles_api_error():
    """Should raise APIError when API call fails."""
    from unittest.mock import Mock, patch

    mock_client_instance = Mock()
    mock_client_instance.get_stock_bars.side_effect = Exception("API Error")

    with patch(
        "alpaca.data.historical.StockHistoricalDataClient", return_value=mock_client_instance
    ):
        provider = AlpacaProvider()

        with pytest.raises(APIError, match="Failed to get historical bars"):
            provider.get_historical_bars(
                symbol="AAPL",
                start_date=date(2025, 3, 1),
                end_date=date(2025, 3, 5),
            )


def test_get_historical_bars_date_boundary():
    """Should handle start_date > end_date gracefully."""
    from unittest.mock import Mock, patch

    mock_bars_data = Mock()
    mock_bars_data.data = {}

    mock_client_instance = Mock()
    mock_client_instance.get_stock_bars.return_value = mock_bars_data

    with patch(
        "alpaca.data.historical.StockHistoricalDataClient", return_value=mock_client_instance
    ):
        provider = AlpacaProvider()

        bars = provider.get_historical_bars(
            symbol="AAPL",
            start_date=date(2025, 3, 10),
            end_date=date(2025, 3, 1),  # End before start
        )

        # Should return empty list or let API handle it
        assert isinstance(bars, list)
