"""src/bot_trading/controllers/settings_controller.py"""

from bot_trading.core.state_manager import StateManager, TradingMode
from bot_trading.core.data_store import DataStore


class SettingsController:
    """Controller for settings and configuration.

    Handles:
    - Loading/saving settings
    - API key management
    - Trading mode changes
    - Configuration validation

    Coordinates between StateManager and DataStore.
    """

    def __init__(
        self,
        state_manager: StateManager,
        data_store: DataStore,
    ) -> None:
        """Initialize SettingsController.

        Args:
            state_manager: Application state manager
            data_store: Data persistence layer
        """
        self._state_manager = state_manager
        self._data_store = data_store

    def get_settings(self) -> dict:
        """Get all settings.

        Returns:
            Settings dictionary
        """
        return self._data_store.load_settings()

    def save_settings(self, settings: dict) -> None:
        """Save settings to persistent storage.

        Args:
            settings: Settings dictionary to save
        """
        self._data_store.save_settings(settings)

    def set_trading_mode(self, mode: TradingMode) -> None:
        """Set trading mode and update state.

        Args:
            mode: New trading mode (PAPER or REAL)
        """
        self._state_manager.set_trading_mode(mode)

        # Also save to settings
        settings = self.get_settings()
        settings["trading_mode"] = mode.value
        self.save_settings(settings)

    def validate_api_keys(
        self, api_key: str | None, api_secret: str | None
    ) -> bool:
        """Validate API keys.

        Args:
            api_key: API key to validate
            api_secret: API secret to validate

        Returns:
            True if keys appear valid, False otherwise
        """
        # Basic validation: not empty and reasonable length
        if not api_key or not api_secret:
            return False

        if len(api_key) < 10 or len(api_secret) < 10:
            return False

        return True

    def save_api_keys(self, api_key: str, api_secret: str) -> None:
        """Save API keys to settings.

        Args:
            api_key: API key to save
            api_secret: API secret to save
        """
        settings = self.get_settings()
        settings["api_key"] = api_key
        settings["api_secret"] = api_secret
        self.save_settings(settings)

    def get_api_keys(self) -> dict:
        """Get stored API keys.

        Returns:
            Dictionary with api_key and api_secret
        """
        settings = self.get_settings()
        return {
            "api_key": settings.get("api_key", ""),
            "api_secret": settings.get("api_secret", ""),
        }
