"""Core business logic for Phase 3.

This module contains the fundamental state management, persistence,
and notification infrastructure that both controllers and GUI depend on.
"""

from bot_trading.core.state_manager import StateManager, TradingMode
from bot_trading.core.data_store import DataStore
from bot_trading.core.notification_manager import NotificationManager, NotificationType

__all__ = [
    "StateManager",
    "TradingMode",
    "DataStore",
    "NotificationManager",
    "NotificationType",
]
