"""Abstract base class for trading providers.

All provider adapters must implement this interface to ensure
consistent behavior across different brokers/exchanges.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal


@dataclass
class Account:
    """Account information."""

    equity: Decimal
    cash: Decimal
    buying_power: Decimal
    portfolio_value: Decimal


@dataclass
class Position:
    """Open position information."""

    symbol: str
    quantity: Decimal
    avg_entry_price: Decimal
    current_price: Decimal
    market_value: Decimal


@dataclass
class Order:
    """Order information."""

    order_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: Decimal
    price: Decimal | None
    status: str
    created_at: datetime


@dataclass
class Bar:
    """OHLCV price bar for historical data."""

    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


@dataclass
class EquityPoint:
    """Equity curve point for backtest results."""

    timestamp: datetime
    value: Decimal
    returns_pct: Decimal  # Returns from start of period


class BaseProvider(ABC):
    """Abstract base class for trading providers.

    All provider adapters must implement this interface to ensure
    consistent behavior across different brokers/exchanges.
    """

    @abstractmethod
    def get_account(self) -> Account:
        """Get current account information."""
        pass

    @abstractmethod
    def get_positions(self) -> list[Position]:
        """Get all open positions."""
        pass

    @abstractmethod
    def get_latest_price(self, symbol: str) -> Decimal:
        """Get latest price for a symbol."""
        pass

    @abstractmethod
    def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        order_type: str = "market",
        price: Decimal | None = None,
    ) -> Order:
        """Submit a new order.

        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            quantity: Order quantity
            order_type: 'market' or 'limit'
            price: Limit price (required for limit orders)

        Returns:
            Order object with order_id and status
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order."""
        pass

    @abstractmethod
    def list_open_orders(self) -> list[Order]:
        """List all open orders."""
        pass
