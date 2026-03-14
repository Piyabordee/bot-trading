"""src/bot_trading/controllers/app_controller.py"""

from pathlib import Path

from bot_trading.core.state_manager import StateManager, TradingMode
from bot_trading.core.data_store import DataStore
from bot_trading.core.notification_manager import NotificationManager
from bot_trading.controllers.trading_controller import TradingController
from bot_trading.controllers.settings_controller import SettingsController
from bot_trading.providers.base import BaseProvider


class AppController:
    """Root controller for the application.

    Initializes and coordinates all sub-controllers:
    - StateManager (central state)
    - DataStore (persistence)
    - NotificationManager (desktop notifications)
    - TradingController (trading operations)
    - SettingsController (configuration)

    This is the main entry point for business logic.
    The GUI layer interacts with this controller.
    """

    def __init__(self, provider: BaseProvider, data_dir: Path | str | None = None) -> None:
        """Initialize AppController and all sub-controllers.

        Args:
            provider: Trading provider (paper or real)
            data_dir: Directory for data storage
        """
        # Initialize core components
        self._data_dir = Path(data_dir) if data_dir else Path.cwd() / "data"
        self._data_store = DataStore(data_dir=self._data_dir)
        self._state_manager = StateManager()
        self._notification_manager = NotificationManager()

        # Initialize controllers
        self._trading_controller = TradingController(
            state_manager=self._state_manager,
            provider=provider,
            notification_manager=self._notification_manager,
        )
        self._settings_controller = SettingsController(
            state_manager=self._state_manager,
            data_store=self._data_store,
        )

    @property
    def state_manager(self) -> StateManager:
        """Get the state manager."""
        return self._state_manager

    @property
    def trading_controller(self) -> TradingController:
        """Get the trading controller."""
        return self._trading_controller

    @property
    def settings_controller(self) -> SettingsController:
        """Get the settings controller."""
        return self._settings_controller

    @property
    def notification_manager(self) -> NotificationManager:
        """Get the notification manager."""
        return self._notification_manager

    def startup(self) -> None:
        """Initialize application on startup.

        Loads saved state and settings.
        """
        # Load settings
        settings = self._data_store.load_settings()
        if settings:
            # Restore trading mode
            trading_mode_str = settings.get("trading_mode", "paper")
            if trading_mode_str == "real":
                self._state_manager.set_trading_mode(TradingMode.REAL)

        # Load pending signals
        signals = self._data_store.load_signals()
        for signal in signals:
            self._state_manager.add_signal(signal)

        # Initial portfolio refresh
        self._trading_controller.refresh_portfolio()

    def shutdown(self) -> None:
        """Clean up and save state on shutdown.

        Saves current application state.
        """
        # Save current state
        state = {
            "trading_mode": self._state_manager.trading_mode.value,
            "last_update": self._state_manager.signals[0].created_at.isoformat()
            if self._state_manager.signals
            else None,
        }
        self._data_store.save_state(state)

        # Save pending signals
        self._data_store.clear_signals()
        for signal in self._state_manager.signals:
            self._data_store.save_signal(signal)

    def get_trading_mode(self) -> TradingMode:
        """Get current trading mode.

        Returns:
            Current trading mode
        """
        return self._state_manager.trading_mode

    def refresh_portfolio(self) -> None:
        """Refresh portfolio data from provider."""
        self._trading_controller.refresh_portfolio()
