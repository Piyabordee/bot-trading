"""Tests for AI context data models."""

from datetime import date
from decimal import Decimal

from bot_trading.data.models import MarketContext, SymbolAnalysis


def test_market_context_creation():
    """Test MarketContext dataclass creation."""
    context = MarketContext(
        date=date(2026, 3, 14),
        account_equity=Decimal("10000"),
        cash=Decimal("5000"),
        buying_power=Decimal("10000"),
        positions={},
        symbols=["AAPL", "MSFT"],
        symbol_data={},
    )
    assert context.date == date(2026, 3, 14)
    assert context.account_equity == Decimal("10000")
    assert context.cash == Decimal("5000")
    assert context.buying_power == Decimal("10000")
    assert context.positions == {}
    assert context.symbols == ["AAPL", "MSFT"]
    assert context.symbol_data == {}


def test_symbol_analysis_creation():
    """Test SymbolAnalysis dataclass creation."""
    analysis = SymbolAnalysis(
        symbol="AAPL",
        current_price=Decimal("175.50"),
        sma_20=Decimal("170.00"),
        rsi_14=65.5,
        volume_avg=50000000,
    )
    assert analysis.symbol == "AAPL"
    assert analysis.current_price == Decimal("175.50")
    assert analysis.sma_20 == Decimal("170.00")
    assert analysis.rsi_14 == 65.5
    assert analysis.volume_avg == 50000000


def test_symbol_analysis_with_optional_fields():
    """Test SymbolAnalysis with all optional fields."""
    analysis = SymbolAnalysis(
        symbol="MSFT",
        current_price=Decimal("380.00"),
        sma_20=Decimal("375.00"),
        ema_12=Decimal("378.00"),
        rsi_14=58.5,
        macd=Decimal("2.50"),
        macd_signal=Decimal("2.30"),
        volume_avg=30000000,
        price_change_pct=2.5,
        volatility=0.18,
    )
    assert analysis.symbol == "MSFT"
    assert analysis.ema_12 == Decimal("378.00")
    assert analysis.macd == Decimal("2.50")
    assert analysis.price_change_pct == 2.5
    assert analysis.volatility == 0.18


def test_symbol_analysis_minimal():
    """Test SymbolAnalysis with only required fields."""
    analysis = SymbolAnalysis(
        symbol="TSLA",
        current_price=Decimal("200.00"),
    )
    assert analysis.symbol == "TSLA"
    assert analysis.current_price == Decimal("200.00")
    assert analysis.sma_20 is None
    assert analysis.rsi_14 is None


def test_market_context_with_symbol_data():
    """Test MarketContext with populated symbol_data."""
    symbol_data = {
        "AAPL": SymbolAnalysis(
            symbol="AAPL",
            current_price=Decimal("175.50"),
            sma_20=Decimal("170.00"),
        ),
        "MSFT": SymbolAnalysis(
            symbol="MSFT",
            current_price=Decimal("380.00"),
            rsi_14=60.0,
        ),
    }

    context = MarketContext(
        date=date(2026, 3, 14),
        account_equity=Decimal("10000"),
        cash=Decimal("5000"),
        buying_power=Decimal("10000"),
        positions={},
        symbols=["AAPL", "MSFT"],
        symbol_data=symbol_data,
    )

    assert len(context.symbol_data) == 2
    assert context.symbol_data["AAPL"].symbol == "AAPL"
    assert context.symbol_data["MSFT"].rsi_14 == 60.0
