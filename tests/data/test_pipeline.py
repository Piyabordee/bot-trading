"""Tests for data pipeline."""

from datetime import date, datetime, timedelta
from decimal import Decimal

from bot_trading.data.pipeline import DataPipeline
from bot_trading.providers.mock import MockProvider
from bot_trading.providers.base import Bar


def test_pipeline_fetches_historical_data():
    """Test pipeline fetches historical bars for symbols."""
    provider = MockProvider()
    pipeline = DataPipeline(provider=provider)

    end_date = date(2026, 3, 14)
    start_date = end_date - timedelta(days=30)

    bars = pipeline.fetch_historical_bars(
        symbols=["AAPL"],
        start_date=start_date,
        end_date=end_date,
    )

    assert "AAPL" in bars
    assert len(bars["AAPL"]) > 0


def test_pipeline_calculates_sma():
    """Test SMA calculation from historical bars."""
    provider = MockProvider()
    pipeline = DataPipeline(provider=provider)

    bars = [
        Bar(symbol="AAPL", timestamp=datetime.now(), open=Decimal("100"), high=Decimal("105"),
            low=Decimal("95"), close=Decimal(s), volume=1000)
        for s in [100, 102, 104, 103, 105, 107, 106, 108, 110, 109,
                  111, 113, 112, 114, 116, 115, 117, 119, 118, 120]
    ]

    sma = pipeline.calculate_sma(bars, period=20)
    assert sma == Decimal("110.45")


def test_pipeline_creates_market_context():
    """Test creating complete market context."""
    provider = MockProvider()
    pipeline = DataPipeline(provider=provider)

    context = pipeline.create_market_context(
        symbols=["AAPL", "MSFT"],
        lookback_days=20,
    )

    assert context.date is not None
    assert context.account_equity > 0
    assert "AAPL" in context.symbol_data
    assert context.symbol_data["AAPL"].current_price > 0
