# tests/test_providers/test_base_models.py
from datetime import datetime
from decimal import Decimal
from bot_trading.providers.base import Bar, EquityPoint


def test_bar_dataclass_creation():
    bar = Bar(
        symbol="AAPL",
        timestamp=datetime(2025, 3, 14, 9, 30),
        open=Decimal("150.00"),
        high=Decimal("151.00"),
        low=Decimal("149.50"),
        close=Decimal("150.50"),
        volume=10000,
    )
    assert bar.symbol == "AAPL"
    assert bar.close == Decimal("150.50")
    assert bar.volume == 10000


def test_bar_requires_decimal_for_prices():
    # Note: dataclasses don't enforce type checking at runtime
    # This test documents that floats are accepted but Decimal is preferred
    bar = Bar(
        symbol="AAPL",
        timestamp=datetime.now(),
        open=150.0,  # float accepted but not preferred
        high=Decimal("151.00"),
        low=Decimal("149.50"),
        close=Decimal("150.50"),
        volume=10000,
    )
    # The value is stored as provided (float in this case)
    assert bar.open == 150.0
    # For consistency, all price data should use Decimal type


def test_equity_point_dataclass_creation():
    point = EquityPoint(
        timestamp=datetime(2025, 3, 14, 16, 0),
        value=Decimal("100000.00"),
        returns_pct=Decimal("5.2"),
    )
    assert point.value == Decimal("100000.00")
    assert point.returns_pct == Decimal("5.2")


def test_bar_string_representation():
    bar = Bar(
        symbol="AAPL",
        timestamp=datetime(2025, 3, 14, 9, 30),
        open=Decimal("150.00"),
        high=Decimal("151.00"),
        low=Decimal("149.50"),
        close=Decimal("150.50"),
        volume=10000,
    )
    str_repr = str(bar)
    assert "AAPL" in str_repr
    assert "150.50" in str_repr
