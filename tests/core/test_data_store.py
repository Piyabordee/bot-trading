"""tests/core/test_data_store.py"""

import pytest
import json
import csv
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import Mock, patch

from bot_trading.core.data_store import DataStore
from bot_trading.core.state_manager import ManualSignal
from bot_trading.providers.base import Order


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def data_store(temp_data_dir):
    """Create a DataStore instance with temp directory."""
    return DataStore(data_dir=temp_data_dir)


class TestDataStore:
    """Test DataStore persistence functionality."""

    def test_initialization_creates_directories(self, data_store, temp_data_dir):
        """Test that DataStore creates required subdirectories."""
        assert (temp_data_dir / "state").exists()
        assert (temp_data_dir / "history").exists()
        assert (temp_data_dir / "signals").exists()

    def test_save_and_load_settings(self, data_store):
        """Test saving and loading settings."""
        settings = {
            "api_key": "test_key",
            "api_secret": "test_secret",
            "trading_mode": "paper",
        }

        data_store.save_settings(settings)
        loaded = data_store.load_settings()

        assert loaded == settings

    def test_load_settings_returns_default_when_missing(self, data_store):
        """Test that load_settings returns default dict when file missing."""
        settings = data_store.load_settings()
        assert settings == {}

    def test_save_and_load_state(self, data_store):
        """Test saving and loading application state."""
        state = {
            "trading_mode": "paper",
            "last_update": "2026-03-14T12:00:00",
            "symbols": ["AAPL", "MSFT"],
        }

        data_store.save_state(state)
        loaded = data_store.load_state()

        assert loaded["trading_mode"] == "paper"
        assert loaded["symbols"] == ["AAPL", "MSFT"]

    def test_load_state_returns_empty_when_missing(self, data_store):
        """Test that load_state returns empty dict when file missing."""
        state = data_store.load_state()
        assert state == {}

    def test_save_signal(self, data_store):
        """Test saving a single signal."""
        signal = ManualSignal(
            symbol="AAPL",
            action="buy",
            quantity=Decimal("100"),
            price=Decimal("175.50"),
            risk_score=5,
            reason="Test signal",
        )

        data_store.save_signal(signal)

        # Check file exists
        signal_file = data_store._signals_dir / "pending_signals.json"
        assert signal_file.exists()

        # Load and verify
        with open(signal_file) as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["symbol"] == "AAPL"
        assert data[0]["action"] == "buy"

    def test_load_signals(self, data_store):
        """Test loading signals from file."""
        # First save some signals
        signal1 = ManualSignal(symbol="AAPL", action="buy", quantity=Decimal("100"))
        signal2 = ManualSignal(symbol="MSFT", action="sell", quantity=Decimal("50"))

        data_store.save_signal(signal1)
        data_store.save_signal(signal2)

        # Load them back
        signals = data_store.load_signals()

        assert len(signals) == 2
        assert signals[0].symbol == "AAPL"
        assert signals[1].symbol == "MSFT"

    def test_clear_signals(self, data_store):
        """Test clearing all signals."""
        signal = ManualSignal(symbol="AAPL", action="buy", quantity=Decimal("100"))
        data_store.save_signal(signal)

        data_store.clear_signals()

        signals = data_store.load_signals()
        assert len(signals) == 0

    def test_save_trade_to_csv(self, data_store):
        """Test saving a trade record to CSV."""
        trade = {
            "timestamp": "2026-03-14T12:00:00",
            "symbol": "AAPL",
            "action": "buy",
            "quantity": "100",
            "price": "175.50",
            "order_id": "order_123",
        }

        data_store.save_trade(trade)

        # Check file exists with today's date
        today_str = date.today().strftime("%Y_%m_%d")
        csv_file = data_store._history_dir / f"trades_{today_str}.csv"
        assert csv_file.exists()

        # Verify content
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["symbol"] == "AAPL"
        assert rows[0]["action"] == "buy"

    def test_save_order_to_csv(self, data_store):
        """Test saving an order record to CSV."""
        order = Order(
            order_id="order_123",
            symbol="AAPL",
            side="buy",
            quantity=Decimal("100"),
            price=Decimal("175.50"),
            status="filled",
            created_at=datetime.now(),
        )

        data_store.save_order(order)

        # Check file exists
        today_str = date.today().strftime("%Y_%m_%d")
        csv_file = data_store._history_dir / f"orders_{today_str}.csv"
        assert csv_file.exists()

        # Verify content
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["order_id"] == "order_123"
        assert rows[0]["symbol"] == "AAPL"

    def test_load_trades_for_date(self, data_store):
        """Test loading trades for a specific date."""
        trade1 = {
            "timestamp": "2026-03-14T12:00:00",
            "symbol": "AAPL",
            "action": "buy",
            "quantity": "100",
            "price": "175.50",
            "order_id": "order_1",
        }
        trade2 = {
            "timestamp": "2026-03-14T13:00:00",
            "symbol": "MSFT",
            "action": "sell",
            "quantity": "50",
            "price": "380.00",
            "order_id": "order_2",
        }

        data_store.save_trade(trade1)
        data_store.save_trade(trade2)

        trades = data_store.load_trades(date.today())

        assert len(trades) == 2
        assert trades[0]["symbol"] == "AAPL"
        assert trades[1]["symbol"] == "MSFT"

    def test_decimal_serialization(self, data_store):
        """Test that Decimal values are properly serialized."""
        signal = ManualSignal(
            symbol="AAPL",
            action="buy",
            quantity=Decimal("100.12345678"),  # High precision
            price=Decimal("175.50"),
        )

        data_store.save_signal(signal)
        signals = data_store.load_signals()

        # Decimal should be preserved
        assert signals[0].quantity == Decimal("100.12345678")
