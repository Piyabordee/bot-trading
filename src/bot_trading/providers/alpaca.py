"""Alpaca Paper Trading provider adapter.

This adapter connects to Alpaca's paper trading environment only.
It will NOT connect to live trading endpoints.

TODO: Implement full order submission and management
TODO: Add proper error handling for network failures
TODO: Add retry logic for transient errors
"""
import os
from decimal import Decimal
from typing import cast

# Alpaca SDK is optional for scaffold mode
# TODO: Uncomment and install alpaca-py when implementing full API integration
# try:
#     from alpaca.trading.client import TradingClient
#     from alpaca.trading.requests import MarketOrderRequest
#     from alpaca.trading.enums import OrderSide, TimeInForce
#     ALPACA_AVAILABLE = True
# except ImportError:
#     ALPACA_AVAILABLE = False
ALPACA_AVAILABLE = True  # Set to True for scaffold stub mode

from bot_trading.providers.base import (
    BaseProvider,
    Account,
    Position,
    Order,
)


class AlpacaProvider(BaseProvider):
    """Alpaca Paper Trading provider adapter.

    This adapter connects to Alpaca's paper trading environment only.
    It will NOT connect to live trading endpoints.

    TODO: Implement full order submission and management
    TODO: Add proper error handling for network failures
    TODO: Add retry logic for transient errors
    """

    PAPER_URL = "https://paper-api.alpaca.markets"

    def __init__(self) -> None:
        """Initialize Alpaca Paper Trading client.

        Raises:
            ValueError: If API credentials are not configured
            ImportError: If alpaca-trade-api is not installed
        """
        if not ALPACA_AVAILABLE:
            raise ImportError(
                "alpaca-trade-api is required for AlpacaProvider. "
                "Install with: pip install alpaca-trade-api"
            )

        api_key = os.getenv("ALPACA_API_KEY", "")
        api_secret = os.getenv("ALPACA_API_SECRET", "")

        if not api_key or api_secret in ("your_paper_api_key_here", ""):
            raise ValueError(
                "Alpaca API credentials not configured. "
                "Set ALPACA_API_KEY and ALPACA_API_SECRET in .env"
            )

        self.base_url = os.getenv("ALPACA_BASE_URL", self.PAPER_URL)

        # Safety: verify we're using paper URL
        if "paper" not in self.base_url:
            raise ValueError(
                f"Refusing to connect to non-paper URL: {self.base_url}. "
                "This is a paper-trading-only demo bot."
            )

        # TODO: Initialize actual TradingClient when implementing full flow
        # self.client = TradingClient(api_key=api_key, secret_key=api_secret, paper=True)
        self._api_key = api_key
        self._api_secret = api_secret

    def get_account(self) -> Account:
        """Get current account information from Alpaca.

        TODO: Implement actual API call when client is initialized
        """
        # TODO: return Account from actual API
        raise NotImplementedError("get_account: TODO - implement when adding full API integration")

    def get_positions(self) -> list[Position]:
        """Get all open positions.

        TODO: Implement actual API call
        """
        raise NotImplementedError("get_positions: TODO - implement when adding full API integration")

    def get_latest_price(self, symbol: str) -> Decimal:
        """Get latest price for a symbol.

        TODO: Implement actual API call
        """
        raise NotImplementedError("get_latest_price: TODO - implement when adding full API integration")

    def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        order_type: str = "market",
        price: Decimal | None = None,
    ) -> Order:
        """Submit a new order to Alpaca.

        TODO: Implement actual order submission
        """
        raise NotImplementedError("submit_order: TODO - implement when adding full API integration")

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order.

        TODO: Implement actual order cancellation
        """
        raise NotImplementedError("cancel_order: TODO - implement when adding full API integration")

    def list_open_orders(self) -> list[Order]:
        """List all open orders.

        TODO: Implement actual API call
        """
        raise NotImplementedError("list_open_orders: TODO - implement when adding full API integration")
