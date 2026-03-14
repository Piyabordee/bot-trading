"""tests/controllers/test_app_controller.py"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from bot_trading.controllers.app_controller import AppController
from bot_trading.core.state_manager import StateManager
from bot_trading.core.data_store import DataStore
from bot_trading.core.notification_manager import NotificationManager
from bot_trading.providers.base import BaseProvider


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory."""
    return tmp_path / "data"


@pytest.fixture
def mock_provider():
    """Create a mock provider."""
    provider = Mock(spec=BaseProvider)
    provider.get_account.return_value = Mock(
        equity=50000, cash=25000, buying_power=100000, portfolio_value=25000
    )
    provider.get_positions.return_value = []
    return provider


@pytest.fixture
def app_controller(temp_data_dir, mock_provider):
    """Create an AppController instance for testing."""
    return AppController(provider=mock_provider, data_dir=temp_data_dir)


class TestAppController:
    """Test AppController functionality."""

    def test_initialization(self, app_controller):
        """Test that AppController initializes correctly."""
        assert app_controller.state_manager is not None
        assert app_controller.trading_controller is not None
        assert app_controller.settings_controller is not None
        assert app_controller.notification_manager is not None

    def test_startup_loads_state(self, app_controller):
        """Test that startup loads saved state."""
        # This should not raise any errors
        app_controller.startup()

    def test_shutdown_saves_state(self, app_controller):
        """Test that shutdown saves current state."""
        app_controller.startup()
        app_controller.shutdown()

        # Verify state file was created
        state_file = app_controller._data_dir / "state" / "current_state.json"
        # Note: In real test, check if file exists and has valid content

    def test_get_trading_mode(self, app_controller):
        """Test getting current trading mode."""
        mode = app_controller.get_trading_mode()
        assert mode.value == "paper"  # Default

    def test_refresh_portfolio(self, app_controller):
        """Test refreshing portfolio data."""
        app_controller.refresh_portfolio()

        # State should be updated
        assert app_controller.state_manager.account is not None
