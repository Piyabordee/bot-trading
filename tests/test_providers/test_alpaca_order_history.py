# tests/test_providers/test_alpaca_order_history.py
import os
from datetime import datetime
from decimal import Decimal
import pytest
from bot_trading.providers.alpaca import AlpacaProvider
from bot_trading.exceptions import APIError

# Mock credentials for testing
os.environ["ALPACA_API_KEY"] = "test_key"
os.environ["ALPACA_API_SECRET"] = "test_secret"
os.environ["ALPACA_BASE_URL"] = "https://paper-api.alpaca.markets"


def test_get_order_history_returns_list():
    """Should return list of orders from API."""
    # This test uses mocking - actual API call tests in integration tests
    from unittest.mock import Mock, patch

    with patch("alpaca.trading.client.TradingClient") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance

        # Mock order response
        mock_order = Mock()
        mock_order.id = "order_123"
        mock_order.symbol = "AAPL"
        mock_order.side = Mock(name="buy")
        mock_order.side.name = "BUY"
        mock_order.qty = Decimal("10")
        mock_order.filled_avg_price = Decimal("150.00")
        mock_order.status = Mock(name="filled")
        mock_order.status.name = "FILLED"
        mock_order.filled_at = datetime.now()

        mock_instance.get_orders.return_value = [mock_order]

        provider = AlpacaProvider()
        orders = provider.get_order_history(days=7)

        assert isinstance(orders, list)
        # Each order should be an Order dataclass
        for order in orders:
            assert hasattr(order, "order_id")
            assert hasattr(order, "symbol")
            assert hasattr(order, "side")


def test_get_order_history_handles_api_error():
    """Should raise APIError when API call fails."""
    from unittest.mock import Mock, patch

    with patch("alpaca.trading.client.TradingClient") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.get_orders.side_effect = Exception("API Error")

        provider = AlpacaProvider()

        with pytest.raises(APIError, match="Failed to get order history"):
            provider.get_order_history(days=7)


def test_get_order_history_empty_result():
    """Should return empty list when no orders."""
    from unittest.mock import Mock, patch

    with patch("alpaca.trading.client.TradingClient") as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.get_orders.return_value = []

        provider = AlpacaProvider()
        orders = provider.get_order_history(days=7)

        assert orders == []
