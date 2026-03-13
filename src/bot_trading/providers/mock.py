"""Mock provider for testing without API calls."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from random import Random
from typing import Optional

from bot_trading.providers.base import (
    BaseProvider,
    Account,
    Position,
    Order,
    Bar,
)


class MockProvider(BaseProvider):
    """Mock provider for testing and development.

    Provides realistic mock data without requiring API credentials.
    Note: Skips weekends but does not account for exchange holidays.
    """

    # Default mock prices
    DEFAULT_PRICES = {
        "AAPL": Decimal("150.00"),
        "TSLA": Decimal("250.00"),
        "MSFT": Decimal("380.00"),
        "GOOGL": Decimal("140.00"),
        "AMZN": Decimal("180.00"),
    }

    def __init__(
        self,
        balance: Decimal = Decimal("100000"),
        prices: Optional[dict[str, Decimal]] = None,
    ) -> None:
        """Initialize MockProvider.

        Args:
            balance: Starting account balance
            prices: Custom price map (uses DEFAULT_PRICES if None)
        """
        self.balance = balance
        self._prices = prices or self.DEFAULT_PRICES
        self._positions: dict[str, Decimal] = {}
        self._orders: list[Order] = []
        self._rng = Random(42)  # Fixed seed for reproducibility

    def get_account(self) -> Account:
        """Get current account information."""
        total_value = self.balance
        for symbol, quantity in self._positions.items():
            price = self._prices.get(symbol, Decimal("100"))
            total_value += price * quantity

        return Account(
            equity=total_value,
            cash=self.balance,
            portfolio_value=total_value,
            buying_power=self.balance,
        )

    def get_positions(self) -> list[Position]:
        """Get current positions."""
        positions = []
        for symbol, quantity in self._positions.items():
            if quantity > 0:
                price = self._prices.get(symbol, Decimal("100"))
                positions.append(
                    Position(
                        symbol=symbol,
                        quantity=quantity,
                        avg_entry_price=price,
                        current_price=price,
                        market_value=price * quantity,
                    )
                )
        return positions

    def get_latest_price(self, symbol: str) -> Decimal:
        """Get latest price for a symbol."""
        if symbol not in self._prices:
            # Generate random price for unknown symbols
            self._prices[symbol] = Decimal(str(100 + self._rng.random() * 100))
        return self._prices[symbol]

    def get_historical_bars(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        timeframe: str = "1Day",
    ) -> list[Bar]:
        """Get historical OHLCV bars.

        Note: Skips weekends (Mon-Fri only) but does not account for holidays.
        """
        bars = []
        current_date = start_date
        base_price = float(self.get_latest_price(symbol))

        while current_date <= end_date:
            # Skip weekends (weekday() < 5 means Mon-Fri)
            if current_date.weekday() < 5:
                # Generate realistic price movement
                day_offset = (current_date - start_date).days
                daily_change = (self._rng.random() - 0.5) * 0.02  # ±1% daily
                day_price = base_price * (1 + daily_change * day_offset * 0.1)

                open_price = day_price * (1 + (self._rng.random() - 0.5) * 0.01)
                high_price = max(open_price, day_price) * (1 + self._rng.random() * 0.005)
                low_price = min(open_price, day_price) * (1 - self._rng.random() * 0.005)
                close_price = day_price
                volume = int(self._rng.random() * 1000000 + 500000)

                bars.append(
                    Bar(
                        symbol=symbol,
                        timestamp=datetime.combine(current_date, datetime.min.time()),
                        open=Decimal(f"{open_price:.2f}"),
                        high=Decimal(f"{high_price:.2f}"),
                        low=Decimal(f"{low_price:.2f}"),
                        close=Decimal(f"{close_price:.2f}"),
                        volume=volume,
                    )
                )

            current_date += timedelta(days=1)

        return bars

    def get_order_history(self, days: int = 7) -> list[Order]:
        """Get order history."""
        cutoff = datetime.now() - timedelta(days=days)
        return [o for o in self._orders if o.created_at >= cutoff]

    def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        order_type: str = "market",
        price: Optional[Decimal] = None,
    ) -> Order:
        """Submit a new order."""
        order = Order(
            order_id=f"mock-{len(self._orders) + 1}",
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            status="filled",
            created_at=datetime.now(),
        )
        self._orders.append(order)

        # Update position
        if side == "buy":
            self._positions[symbol] = self._positions.get(symbol, Decimal("0")) + quantity
            self.balance -= self.get_latest_price(symbol) * quantity
        else:
            self._positions[symbol] = self._positions.get(symbol, Decimal("0")) - quantity
            self.balance += self.get_latest_price(symbol) * quantity

        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order (mock - always returns True)."""
        return True

    def list_open_orders(self) -> list[Order]:
        """List open orders (mock - returns empty list)."""
        return []
