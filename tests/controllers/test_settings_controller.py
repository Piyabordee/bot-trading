"""tests/controllers/test_settings_controller.py"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from bot_trading.controllers.settings_controller import SettingsController
from bot_trading.core.state_manager import StateManager, TradingMode
from bot_trading.core.data_store import DataStore


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory."""
    return tmp_path / "data"


@pytest.fixture
def data_store(temp_data_dir):
    """Create a DataStore instance."""
    return DataStore(data_dir=temp_data_dir)


@pytest.fixture
def state_manager(qtbot):
    """Create a StateManager instance."""
    return StateManager()


@pytest.fixture
def settings_controller(state_manager, data_store):
    """Create a SettingsController instance."""
    return SettingsController(
        state_manager=state_manager,
        data_store=data_store,
    )


class TestSettingsController:
    """Test SettingsController functionality."""

    def test_get_settings(self, settings_controller, data_store):
        """Test getting settings."""
        # Save some settings first
        data_store.save_settings({"api_key": "test_key", "mode": "paper"})

        settings = settings_controller.get_settings()

        assert settings["api_key"] == "test_key"
        assert settings["mode"] == "paper"

    def test_get_settings_empty(self, settings_controller):
        """Test getting settings when none exist."""
        settings = settings_controller.get_settings()

        assert settings == {}

    def test_save_settings(self, settings_controller, data_store):
        """Test saving settings."""
        new_settings = {
            "api_key": "new_key",
            "api_secret": "new_secret",
            "trading_mode": "paper",
        }

        settings_controller.save_settings(new_settings)

        # Verify they were saved
        loaded = data_store.load_settings()
        assert loaded["api_key"] == "new_key"

    def test_set_trading_mode_updates_state(
        self, settings_controller, state_manager, qtbot
    ):
        """Test that set_trading_mode updates StateManager."""
        with qtbot.waitSignal(state_manager.trading_mode_changed, timeout=1000):
            settings_controller.set_trading_mode(TradingMode.REAL)

        assert state_manager.trading_mode == TradingMode.REAL

    def test_set_trading_mode_paper(self, settings_controller, state_manager, qtbot):
        """Test switching to paper trading mode."""
        state_manager.set_trading_mode(TradingMode.REAL)

        with qtbot.waitSignal(state_manager.trading_mode_changed, timeout=1000):
            settings_controller.set_trading_mode(TradingMode.PAPER)

        assert state_manager.trading_mode == TradingMode.PAPER

    def test_validate_api_keys_valid(self, settings_controller):
        """Test API key validation with valid keys."""
        is_valid = settings_controller.validate_api_keys(
            api_key="test_key_123", api_secret="test_secret_456"
        )

        assert is_valid is True

    def test_validate_api_keys_invalid_empty(self, settings_controller):
        """Test API key validation with empty keys."""
        is_valid = settings_controller.validate_api_keys(
            api_key="", api_secret=""
        )

        assert is_valid is False

    def test_validate_api_keys_invalid_none(self, settings_controller):
        """Test API key validation with None keys."""
        is_valid = settings_controller.validate_api_keys(
            api_key=None, api_secret=None
        )

        assert is_valid is False

    def test_save_api_keys(self, settings_controller, data_store):
        """Test saving API keys."""
        settings_controller.save_api_keys(
            api_key="my_key", api_secret="my_secret"
        )

        settings = data_store.load_settings()
        assert settings["api_key"] == "my_key"
        assert settings["api_secret"] == "my_secret"

    def test_get_api_keys(self, settings_controller, data_store):
        """Test getting API keys."""
        data_store.save_settings({
            "api_key": "stored_key",
            "api_secret": "stored_secret",
        })

        keys = settings_controller.get_api_keys()

        assert keys["api_key"] == "stored_key"
        assert keys["api_secret"] == "stored_secret"
