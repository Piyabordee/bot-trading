"""tests/controllers/test_trading_controller.py"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from bot_trading.controllers.trading_controller import TradingController, PreTradeCheckResult
from bot_trading.core.state_manager import StateManager, TradingMode, ManualSignal
from bot_trading.core.notification_manager import NotificationManager
from bot_trading.providers.base import BaseProvider, Account, Order


@pytest.fixture
def mock_provider():
    """Create a mock provider."""
    provider = Mock(spec=BaseProvider)
    provider.get_account.return_value = Account(
        equity=Decimal("50000.00"),
        cash=Decimal("25000.00"),
        buying_power=Decimal("100000.00"),
        portfolio_value=Decimal("25000.00"),
    )
    provider.get_positions.return_value = []
    return provider


@pytest.fixture
def state_manager(qtbot):
    """Create a StateManager instance."""
    return StateManager()


@pytest.fixture
def notification_manager(qtbot):
    """Create a NotificationManager instance."""
    return NotificationManager()


@pytest.fixture
def trading_controller(state_manager, mock_provider, notification_manager):
    """Create a TradingController instance."""
    return TradingController(
        state_manager=state_manager,
        provider=mock_provider,
        notification_manager=notification_manager,
    )


class TestTradingController:
    """Test TradingController functionality."""

    def test_initialization(self, trading_controller, state_manager):
        """Test that TradingController initializes correctly."""
        assert trading_controller.state_manager == state_manager
        assert trading_controller._provider is not None

    def test_refresh_portfolio_updates_state(
        self, trading_controller, mock_provider, state_manager, qtbot
    ):
        """Test that refresh_portfolio updates state."""
        with qtbot.waitSignal(state_manager.portfolio_updated, timeout=1000):
            trading_controller.refresh_portfolio()

        # Verify state was updated
        assert state_manager.account is not None
        assert state_manager.account.equity == Decimal("50000.00")

    def test_execute_signal_in_paper_mode(
        self, trading_controller, mock_provider, state_manager, qtbot
    ):
        """Test executing a signal in paper mode."""
        signal = ManualSignal(
            symbol="AAPL",
            action="buy",
            quantity=Decimal("100"),
            price=Decimal("175.50"),
            risk_score=5,
        )

        # Mock submit_order to return a proper order
        mock_provider.submit_order.return_value = Order(
            order_id="paper_order_123",
            symbol="AAPL",
            side="buy",
            quantity=Decimal("100"),
            price=Decimal("175.50"),
            status="submitted",
            created_at=datetime.now(),
        )
        mock_provider.get_latest_price.return_value = Decimal("175.50")

        result = trading_controller.execute_signal(signal)

        assert result.success is True
        assert result.order_id is not None

    def test_execute_signal_in_real_mode_with_api_key(
        self, trading_controller, mock_provider, state_manager
    ):
        """Test executing a signal in real mode with valid API keys."""
        # Set real mode
        state_manager.set_trading_mode(TradingMode.REAL)

        # Mock real provider
        real_provider = Mock(spec=BaseProvider)
        real_provider.submit_order.return_value = Order(
            order_id="real_order_123",
            symbol="AAPL",
            side="buy",
            quantity=Decimal("100"),
            price=Decimal("175.50"),
            status="submitted",
            created_at=datetime.now(),
        )
        real_provider.get_latest_price.return_value = Decimal("175.50")
        real_provider.get_account.return_value = Account(
            equity=Decimal("50000.00"),
            cash=Decimal("25000.00"),
            buying_power=Decimal("100000.00"),
            portfolio_value=Decimal("25000.00"),
        )
        real_provider.get_positions.return_value = []

        trading_controller._provider = real_provider

        signal = ManualSignal(
            symbol="AAPL",
            action="buy",
            quantity=Decimal("100"),
            price=Decimal("175.50"),
            risk_score=5,
        )

        result = trading_controller.execute_signal(signal, user_confirmed_real_mode=True)

        assert result.success is True
        assert result.order_id == "real_order_123"

    def test_execute_signal_insufficient_funds(
        self, trading_controller, mock_provider, state_manager
    ):
        """Test that execute_signal rejects orders with insufficient funds."""
        # Set up account with low buying power
        mock_provider.get_account.return_value = Account(
            equity=Decimal("10000.00"),
            cash=Decimal("5000.00"),
            buying_power=Decimal("10000.00"),  # Low buying power
            portfolio_value=Decimal("5000.00"),
        )
        mock_provider.get_latest_price.return_value = Decimal("200.00")

        # Refresh to update state
        trading_controller.refresh_portfolio()

        signal = ManualSignal(
            symbol="AAPL",
            action="buy",
            quantity=Decimal("1000"),  # Too many shares
            price=Decimal("200.00"),  # $200,000 needed
            risk_score=5,
        )

        result = trading_controller.execute_signal(signal)

        assert result.success is False
        assert "Insufficient" in result.message

    def test_pre_trade_checks_all_pass(self, trading_controller, state_manager):
        """Test pre-trade checks when all pass."""
        signal = ManualSignal(
            symbol="AAPL",
            action="buy",
            quantity=Decimal("100"),
            price=Decimal("175.50"),
            risk_score=5,
        )

        result = trading_controller._pre_trade_checks(signal)

        assert result.allowed is True
        assert len(result.failures) == 0

    def test_pre_trade_checks_real_mode_without_confirmation(
        self, trading_controller, state_manager
    ):
        """Test pre-trade checks for real mode without user confirmation."""
        state_manager.set_trading_mode(TradingMode.REAL)

        signal = ManualSignal(
            symbol="AAPL",
            action="buy",
            quantity=Decimal("100"),
            price=Decimal("175.50"),
            risk_score=5,
        )

        result = trading_controller._pre_trade_checks(
            signal, user_confirmed_real_mode=False
        )

        assert result.allowed is False
        assert "Real trading" in str(result.failures)

    def test_cancel_order(self, trading_controller, mock_provider):
        """Test cancelling an order."""
        order_id = "order_123"
        mock_provider.cancel_order.return_value = True

        result = trading_controller.cancel_order(order_id)

        assert result.success is True
        mock_provider.cancel_order.assert_called_once_with(order_id)

    def test_cancel_order_fails(self, trading_controller, mock_provider):
        """Test cancelling an order that fails."""
        order_id = "order_123"
        mock_provider.cancel_order.return_value = False

        result = trading_controller.cancel_order(order_id)

        assert result.success is False
        assert "Failed to cancel" in result.message

    def test_get_open_orders(self, trading_controller, mock_provider):
        """Test getting open orders."""
        mock_orders = [
            Order(
                order_id="order_1",
                symbol="AAPL",
                side="buy",
                quantity=Decimal("100"),
                price=Decimal("175.00"),
                status="open",
                created_at=datetime.now(),
            )
        ]
        mock_provider.list_open_orders.return_value = mock_orders

        orders = trading_controller.get_open_orders()

        assert len(orders) == 1
        assert orders[0].order_id == "order_1"

    def test_get_latest_price(self, trading_controller, mock_provider):
        """Test getting latest price for a symbol."""
        mock_provider.get_latest_price.return_value = Decimal("175.50")

        price = trading_controller.get_latest_price("AAPL")

        assert price == Decimal("175.50")
        mock_provider.get_latest_price.assert_called_once_with("AAPL")
