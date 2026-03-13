"""Alpaca Paper Trading provider adapter.

This adapter connects to Alpaca's paper trading environment only.
It will NOT connect to live trading endpoints.

TODO: Implement full order submission and management
TODO: Add proper error handling for network failures
TODO: Add retry logic for transient errors
"""

import os
from datetime import date, datetime, timedelta
from decimal import Decimal

from bot_trading.exceptions import APIError, InvalidConfigError
from bot_trading.providers.base import (
    BaseProvider,
    Account,
    Position,
    Order,
    Bar,
)

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
            ImportError: If alpaca-py SDK is not installed
        """
        if not ALPACA_AVAILABLE:
            raise ImportError(
                "alpaca-py SDK is required for AlpacaProvider. Install with: pip install alpaca-py"
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
        raise NotImplementedError(
            "get_positions: TODO - implement when adding full API integration"
        )

    def get_latest_price(self, symbol: str) -> Decimal:
        """Get latest price for a symbol.

        TODO: Implement actual API call
        """
        raise NotImplementedError(
            "get_latest_price: TODO - implement when adding full API integration"
        )

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
        raise NotImplementedError(
            "list_open_orders: TODO - implement when adding full API integration"
        )

    def get_historical_bars(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        timeframe: str = "1Day",
    ) -> list[Bar]:
        """Get historical OHLCV bars for a symbol.

        Args:
            symbol: Trading symbol (e.g., "AAPL")
            start_date: Start date for historical data
            end_date: End date for historical data
            timeframe: Bar timeframe ("1Minute", "5Minute", "15Minute", "1Hour", "1Day")

        Returns:
            List of Bar objects with OHLCV data

        Raises:
            APIError: If API call fails
            InvalidConfigError: If timeframe is invalid
        """
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

        try:
            # Map timeframe string to TimeFrame objects
            # TimeFrame is constructed with (amount, unit)
            timeframe_map = {
                "1Minute": TimeFrame(1, TimeFrameUnit.Minute),
                "5Minute": TimeFrame(5, TimeFrameUnit.Minute),
                "15Minute": TimeFrame(15, TimeFrameUnit.Minute),
                "1Hour": TimeFrame(1, TimeFrameUnit.Hour),
                "1Day": TimeFrame(1, TimeFrameUnit.Day),
            }

            if timeframe not in timeframe_map:
                raise InvalidConfigError(
                    f"Invalid timeframe: {timeframe}. Valid options: {list(timeframe_map.keys())}"
                )

            tf = timeframe_map[timeframe]

            # Reuse existing credentials to create data client
            data_client = StockHistoricalDataClient(
                api_key=self._api_key, secret_key=self._api_secret
            )

            # Request bars
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol, timeframe=tf, start=start_date, end=end_date
            )

            bars_data = data_client.get_stock_bars(request_params)

            if not bars_data or not hasattr(bars_data, "data") or symbol not in bars_data.data:
                return []

            bars = []
            for bar_data in bars_data.data[symbol]:
                bars.append(
                    Bar(
                        symbol=symbol,
                        timestamp=bar_data.timestamp,
                        open=Decimal(str(bar_data.open)),
                        high=Decimal(str(bar_data.high)),
                        low=Decimal(str(bar_data.low)),
                        close=Decimal(str(bar_data.close)),
                        volume=int(bar_data.volume),
                    )
                )

            return bars

        except InvalidConfigError:
            raise
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Failed to get historical bars: {e}")

    def get_order_history(self, days: int = 7) -> list[Order]:
        """Get order history for the last N days.

        Args:
            days: Number of days to look back (default: 7)

        Returns:
            List of Order objects

        Raises:
            APIError: If API call fails
        """
        try:
            from alpaca.trading.client import TradingClient
            from alpaca.trading.requests import GetOrdersRequest

            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)

            # Create trading client
            client = TradingClient(
                api_key=self._api_key,
                secret_key=self._api_secret,
                paper=True,
            )

            # Use alpaca-py SDK to get orders
            request_params = GetOrdersRequest(
                status="all", after=start_time, until=end_time, limit=500
            )

            orders_data = client.get_orders(filter=request_params)

            orders = []
            for order_data in orders_data:
                # Convert API response to Order dataclass
                # Note: Order model expects 'created_at' but API gives 'filled_at'
                orders.append(
                    Order(
                        order_id=str(order_data.id),
                        symbol=order_data.symbol,
                        side=order_data.side.name.lower(),
                        quantity=Decimal(str(order_data.qty)) if order_data.qty else Decimal("0"),
                        price=(
                            Decimal(str(order_data.filled_avg_price))
                            if order_data.filled_avg_price
                            else None
                        ),
                        status=order_data.status.name.lower(),
                        created_at=order_data.filled_at or order_data.created_at,
                    )
                )

            return orders

        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Failed to get order history: {e}")
