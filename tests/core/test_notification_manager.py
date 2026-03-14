"""tests/core/test_notification_manager.py"""

import pytest
from unittest.mock import Mock, patch
from PyQt6.QtCore import QObject

from bot_trading.core.notification_manager import (
    NotificationManager,
    NotificationType,
    NotificationPriority,
)


@pytest.fixture
def notification_manager(qtbot):
    """Create a NotificationManager instance for testing."""
    return NotificationManager()


class TestNotificationManager:
    """Test NotificationManager functionality."""

    def test_initialization(self, notification_manager):
        """Test that NotificationManager initializes correctly."""
        assert notification_manager.enabled is True
        assert notification_manager.min_priority == NotificationPriority.NORMAL

    def test_send_notification_when_enabled(self, notification_manager):
        """Test sending notification when enabled."""
        with patch.object(notification_manager, "_show_desktop_notification") as mock_show:
            notification_manager.send(
                title="Test Title",
                message="Test Message",
                notification_type=NotificationType.TRADE_EXECUTED,
            )

            mock_show.assert_called_once()

    def test_send_notification_when_disabled(self, notification_manager):
        """Test that notifications are not sent when disabled."""
        notification_manager.disable()

        with patch.object(notification_manager, "_show_desktop_notification") as mock_show:
            notification_manager.send(
                title="Test Title",
                message="Test Message",
                notification_type=NotificationType.TRADE_EXECUTED,
            )

            mock_show.assert_not_called()

    def test_low_priority_filtered(self, notification_manager):
        """Test that low priority notifications are filtered when min is NORMAL."""
        notification_manager.min_priority = NotificationPriority.NORMAL

        with patch.object(notification_manager, "_show_desktop_notification") as mock_show:
            notification_manager.send(
                title="Low Priority",
                message="This should be filtered",
                notification_type=NotificationType.TRADE_EXECUTED,
                priority=NotificationPriority.LOW,
            )

            mock_show.assert_not_called()

    def test_trade_executed_notification(self, notification_manager):
        """Test TRADE_EXECUTED notification type."""
        with patch.object(notification_manager, "_show_desktop_notification") as mock_show:
            notification_manager.trade_executed(symbol="AAPL", quantity="100", side="buy")

            mock_show.assert_called_once()
            call_args = mock_show.call_args
            assert "AAPL" in call_args[1]["title"]
            assert "100" in call_args[1]["message"]

    def test_order_filled_notification(self, notification_manager):
        """Test ORDER_FILLED notification type."""
        with patch.object(notification_manager, "_show_desktop_notification") as mock_show:
            notification_manager.order_filled(
                order_id="order_123", symbol="MSFT", quantity="50"
            )

            mock_show.assert_called_once()

    def test_error_notification(self, notification_manager):
        """Test ERROR notification type."""
        with patch.object(notification_manager, "_show_desktop_notification") as mock_show:
            notification_manager.error(message="Something went wrong")

            mock_show.assert_called_once()
            call_args = mock_show.call_args
            assert call_args[1]["notification_type"] == NotificationType.ERROR

    def test_risk_limit_warning(self, notification_manager):
        """Test RISK_LIMIT warning notification."""
        with patch.object(notification_manager, "_show_desktop_notification") as mock_show:
            notification_manager.risk_limit_warning(limit_type="exposure", current="85%")

            mock_show.assert_called_once()

    @patch("bot_trading.core.notification_manager.QSystemTrayIcon")
    def test_system_tray_icon_setup(self, mock_tray_icon, notification_manager):
        """Test that system tray icon is set up correctly."""
        # Tray icon should be created
        assert notification_manager._tray_icon is not None

    def test_enable_disable(self, notification_manager):
        """Test enabling and disabling notifications."""
        notification_manager.disable()
        assert notification_manager.enabled is False

        notification_manager.enable()
        assert notification_manager.enabled is True
