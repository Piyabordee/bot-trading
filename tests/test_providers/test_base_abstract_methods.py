# tests/test_providers/test_base_abstract_methods.py
import pytest
from datetime import date, datetime
from decimal import Decimal
from bot_trading.providers.base import BaseProvider, Bar, Order, Account, Position

def test_base_provider_requires_get_historical_bars():
    """Concrete provider must implement get_historical_bars."""

    class IncompleteProvider(BaseProvider):
        def get_account(self) -> Account:
            return Account(
                equity=Decimal("100000"),
                cash=Decimal("100000"),
                buying_power=Decimal("100000"),
                portfolio_value=Decimal("100000")
            )

        def get_positions(self) -> list[Position]:
            return []

        def get_latest_price(self, symbol: str) -> Decimal:
            return Decimal("100")

        def submit_order(self, symbol: str, side: str, quantity: Decimal, order_type: str = "market", price: Decimal | None = None) -> Order:
            return Order(
                order_id="test",
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                status="filled",
                created_at=datetime.now()
            )

        def cancel_order(self, order_id: str) -> bool:
            return True

        def list_open_orders(self) -> list[Order]:
            return []

        # Missing: get_historical_bars and get_order_history

    with pytest.raises(TypeError, match="abstract"):
        # Should fail because abstract methods not implemented
        provider = IncompleteProvider()

def test_base_provider_requires_get_order_history():
    """Concrete provider must implement get_order_history."""

    class IncompleteProvider(BaseProvider):
        def get_account(self) -> Account:
            return Account(
                equity=Decimal("100000"),
                cash=Decimal("100000"),
                buying_power=Decimal("100000"),
                portfolio_value=Decimal("100000")
            )

        def get_positions(self) -> list[Position]:
            return []

        def get_latest_price(self, symbol: str) -> Decimal:
            return Decimal("100")

        def submit_order(self, symbol: str, side: str, quantity: Decimal, order_type: str = "market", price: Decimal | None = None) -> Order:
            return Order(
                order_id="test",
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                status="filled",
                created_at=datetime.now()
            )

        def cancel_order(self, order_id: str) -> bool:
            return True

        def list_open_orders(self) -> list[Order]:
            return []

        def get_historical_bars(self, symbol: str, start_date: date, end_date: date, timeframe: str = "1Day") -> list[Bar]:
            return [Bar(symbol="AAPL", timestamp=datetime.now(),
                       open=Decimal("100"), high=Decimal("101"),
                       low=Decimal("99"), close=Decimal("100.5"), volume=1000)]

        # Missing: get_order_history

    with pytest.raises(TypeError, match="abstract"):
        provider = IncompleteProvider()

def test_concrete_provider_can_be_instantiated_with_all_methods():
    """Provider with all methods should be instantiable."""

    class CompleteProvider(BaseProvider):
        def get_account(self) -> Account:
            return Account(
                equity=Decimal("100000"),
                cash=Decimal("100000"),
                buying_power=Decimal("100000"),
                portfolio_value=Decimal("100000")
            )

        def get_positions(self) -> list[Position]:
            return []

        def get_latest_price(self, symbol: str) -> Decimal:
            return Decimal("100")

        def submit_order(self, symbol: str, side: str, quantity: Decimal, order_type: str = "market", price: Decimal | None = None) -> Order:
            return Order(
                order_id="1",
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                status="filled",
                created_at=datetime.now()
            )

        def cancel_order(self, order_id: str) -> bool:
            return True

        def list_open_orders(self) -> list[Order]:
            return []

        def get_historical_bars(self, symbol: str, start_date: date, end_date: date, timeframe: str = "1Day") -> list[Bar]:
            return [Bar(symbol="AAPL", timestamp=datetime.now(),
                       open=Decimal("100"), high=Decimal("101"),
                       low=Decimal("99"), close=Decimal("100.5"), volume=1000)]

        def get_order_history(self, days: int = 7) -> list[Order]:
            return []

    # Should not raise
    provider = CompleteProvider()
    assert provider is not None
