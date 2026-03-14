"""tests/core/test_state_manager.py"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from PyQt6.QtCore import QObject, pyqtSignal

from bot_trading.core.state_manager import StateManager, TradingMode
from bot_trading.providers.base import Account, Position, Order


class TestStateManager:
    """Test StateManager functionality."""

    @pytest.fixture
    def state_manager(self, qtbot):
        """Create a StateManager instance for testing."""
        return StateManager()

    @pytest.fixture
    def sample_account(self):
        """Create a sample account for testing."""
        return Account(
            equity=Decimal("50000.00"),
            cash=Decimal("25000.00"),
            buying_power=Decimal("100000.00"),
            portfolio_value=Decimal("25000.00"),
        )

    @pytest.fixture
    def sample_position(self):
        """Create a sample position for testing."""
        return Position(
            symbol="AAPL",
            quantity=Decimal("100"),
            avg_entry_price=Decimal("150.00"),
            current_price=Decimal("175.00"),
            market_value=Decimal("17500.00"),
        )

    def test_initial_state(self, state_manager):
        """Test that StateManager starts with correct initial values."""
        assert state_manager.trading_mode == TradingMode.PAPER
        assert state_manager.account is None
        assert state_manager.positions == {}
        assert state_manager.orders == []
        assert state_manager.signals == []

    def test_trading_mode_defaults_to_paper(self, state_manager):
        """Test that trading mode defaults to PAPER for safety."""
        assert state_manager.trading_mode == TradingMode.PAPER

    def test_set_trading_mode_emits_signal(self, state_manager, qtbot):
        """Test that changing trading mode emits signal."""
        with qtbot.waitSignal(state_manager.trading_mode_changed, timeout=1000):
            state_manager.set_trading_mode(TradingMode.REAL)

        assert state_manager.trading_mode == TradingMode.REAL

    def test_set_trading_mode_to_paper_emits_signal(self, state_manager, qtbot):
        """Test that switching back to paper mode emits signal."""
        state_manager.set_trading_mode(TradingMode.REAL)

        with qtbot.waitSignal(state_manager.trading_mode_changed, timeout=1000):
            state_manager.set_trading_mode(TradingMode.PAPER)

        assert state_manager.trading_mode == TradingMode.PAPER

    def test_update_account_emits_signal(self, state_manager, sample_account, qtbot):
        """Test that updating account info emits portfolio_updated signal."""
        with qtbot.waitSignal(state_manager.portfolio_updated, timeout=1000):
            state_manager.update_account(sample_account)

        assert state_manager.account == sample_account
        assert state_manager.account.equity == Decimal("50000.00")

    def test_update_positions_emits_signal(self, state_manager, sample_position, qtbot):
        """Test that updating positions emits portfolio_updated signal."""
        positions = {"AAPL": sample_position}

        with qtbot.waitSignal(state_manager.portfolio_updated, timeout=1000):
            state_manager.update_positions(positions)

        assert state_manager.positions == positions
        assert "AAPL" in state_manager.positions

    def test_add_signal_emits_signal(self, state_manager, qtbot):
        """Test that adding a signal emits signals_updated."""
        from bot_trading.core.state_manager import ManualSignal

        signal = ManualSignal(
            symbol="AAPL",
            action="buy",
            quantity=Decimal("100"),
            risk_score=5,
            reason="Test signal",
        )

        with qtbot.waitSignal(state_manager.signals_updated, timeout=1000):
            state_manager.add_signal(signal)

        assert len(state_manager.signals) == 1
        assert state_manager.signals[0].symbol == "AAPL"

    def test_remove_signal_emits_signal(self, state_manager, qtbot):
        """Test that removing a signal emits signals_updated."""
        from bot_trading.core.state_manager import ManualSignal

        signal = ManualSignal(
            symbol="AAPL",
            action="buy",
            quantity=Decimal("100"),
            risk_score=5,
        )
        state_manager.add_signal(signal)

        with qtbot.waitSignal(state_manager.signals_updated, timeout=1000):
            state_manager.remove_signal(0)

        assert len(state_manager.signals) == 0

    def test_add_order_emits_signal(self, state_manager, qtbot):
        """Test that adding an order emits orders_updated."""
        order = Order(
            order_id="order_123",
            symbol="AAPL",
            side="buy",
            quantity=Decimal("100"),
            price=Decimal("175.00"),
            status="filled",
            created_at=datetime.now(),
        )

        with qtbot.waitSignal(state_manager.orders_updated, timeout=1000):
            state_manager.add_order(order)

        assert len(state_manager.orders) == 1
        assert state_manager.orders[0].order_id == "order_123"

    def test_clear_signals(self, state_manager):
        """Test clearing all signals."""
        from bot_trading.core.state_manager import ManualSignal

        signal1 = ManualSignal(symbol="AAPL", action="buy", quantity=Decimal("100"))
        signal2 = ManualSignal(symbol="MSFT", action="sell", quantity=Decimal("50"))
        state_manager.add_signal(signal1)
        state_manager.add_signal(signal2)

        state_manager.clear_signals()

        assert len(state_manager.signals) == 0

    def test_get_portfolio_value(self, state_manager, sample_account):
        """Test getting portfolio value."""
        state_manager.update_account(sample_account)
        assert state_manager.get_portfolio_value() == Decimal("50000.00")

    def test_get_portfolio_value_no_account(self, state_manager):
        """Test getting portfolio value when no account set."""
        assert state_manager.get_portfolio_value() == Decimal("0")

    def test_get_cash(self, state_manager, sample_account):
        """Test getting cash balance."""
        state_manager.update_account(sample_account)
        assert state_manager.get_cash() == Decimal("25000.00")

    def test_get_total_profit_loss(self, state_manager):
        """Test calculating total P&L from positions."""
        from bot_trading.core.state_manager import ManualSignal

        # Create positions with profit
        pos1 = Position(
            symbol="AAPL",
            quantity=Decimal("100"),
            avg_entry_price=Decimal("150.00"),
            current_price=Decimal("175.00"),
            market_value=Decimal("17500.00"),
        )
        pos2 = Position(
            symbol="MSFT",
            quantity=Decimal("50"),
            avg_entry_price=Decimal("300.00"),
            current_price=Decimal("280.00"),
            market_value=Decimal("14000.00"),
        )

        state_manager.update_positions({"AAPL": pos1, "MSFT": pos2})

        # AAPL: (175-150) * 100 = 2500 profit
        # MSFT: (280-300) * 50 = -1000 loss
        # Total: 1500 profit
        pnl = state_manager.get_total_profit_loss()
        assert pnl == Decimal("1500.00")

    def test_get_total_profit_loss_no_positions(self, state_manager):
        """Test P&L calculation with no positions."""
        assert state_manager.get_total_profit_loss() == Decimal("0")
