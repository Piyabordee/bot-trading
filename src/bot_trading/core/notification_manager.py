"""src/bot_trading/core/notification_manager.py"""

from enum import Enum
from typing import Literal

from PyQt6.QtWidgets import QSystemTrayIcon, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QObject, pyqtSignal


class NotificationType(Enum):
    """Types of notifications."""

    TRADE_EXECUTED = "trade_executed"
    ORDER_FILLED = "order_filled"
    ORDER_CANCELLED = "order_cancelled"
    RISK_LIMIT = "risk_limit"
    ERROR = "error"
    INFO = "info"


class NotificationPriority(Enum):
    """Priority levels for notifications."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


class NotificationManager(QObject):
    """Desktop notification manager.

    Provides cross-platform desktop notifications using Qt's
    QSystemTrayIcon. Includes type-specific helper methods for
    common notification scenarios.
    """

    notification_sent = pyqtSignal(str, str)  # title, message

    def __init__(self) -> None:
        """Initialize NotificationManager."""
        super().__init__()
        self._enabled: bool = True
        self._min_priority: NotificationPriority = NotificationPriority.NORMAL
        self._tray_icon: QSystemTrayIcon | None = None

        # Set up system tray icon for notifications
        self._setup_tray_icon()

    def _setup_tray_icon(self) -> None:
        """Set up system tray icon for notifications."""
        app = QApplication.instance()
        if app is None:
            return

        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self._tray_icon = QSystemTrayIcon()
        self._tray_icon.show()

    @property
    def enabled(self) -> bool:
        """Check if notifications are enabled."""
        return self._enabled

    def enable(self) -> None:
        """Enable notifications."""
        self._enabled = True

    def disable(self) -> None:
        """Disable notifications."""
        self._enabled = False

    @property
    def min_priority(self) -> NotificationPriority:
        """Get minimum priority level to display."""
        return self._min_priority

    @min_priority.setter
    def min_priority(self, priority: NotificationPriority) -> None:
        """Set minimum priority level to display."""
        self._min_priority = priority

    def send(
        self,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.NORMAL,
    ) -> None:
        """Send a desktop notification.

        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Priority level (for filtering)
        """
        # Check if notifications are enabled
        if not self._enabled:
            return

        # Check priority filter
        if priority.value < self._min_priority.value:
            return

        self._show_desktop_notification(
            title=title,
            message=message,
            notification_type=notification_type,
        )

        self.notification_sent.emit(title, message)

    def _show_desktop_notification(
        self,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
    ) -> None:
        """Show the actual desktop notification.

        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
        """
        if self._tray_icon is None:
            return

        # Use system tray icon for notification
        self._tray_icon.showMessage(
            title,
            message,
            icon=QSystemTrayIcon.MessageIcon.Information,
            msecs=3000,  # Show for 3 seconds
        )

    # Type-specific notification methods

    def trade_executed(self, symbol: str, quantity: str, side: str) -> None:
        """Send notification for executed trade.

        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: Order side (buy/sell)
        """
        self.send(
            title=f"Trade Executed: {side.upper()} {symbol}",
            message=f"Successfully {side} {quantity} shares of {symbol}",
            notification_type=NotificationType.TRADE_EXECUTED,
            priority=NotificationPriority.NORMAL,
        )

    def order_filled(
        self, order_id: str, symbol: str, quantity: str, price: str | None = None
    ) -> None:
        """Send notification for filled order.

        Args:
            order_id: Order ID
            symbol: Trading symbol
            quantity: Filled quantity
            price: Fill price (optional)
        """
        message = f"Order {order_id} filled: {quantity} shares of {symbol}"
        if price:
            message += f" at ${price}"

        self.send(
            title=f"Order Filled: {symbol}",
            message=message,
            notification_type=NotificationType.ORDER_FILLED,
            priority=NotificationPriority.NORMAL,
        )

    def order_cancelled(self, order_id: str, symbol: str, reason: str = "") -> None:
        """Send notification for cancelled order.

        Args:
            order_id: Order ID
            symbol: Trading symbol
            reason: Cancellation reason (optional)
        """
        message = f"Order {order_id} for {symbol} cancelled"
        if reason:
            message += f": {reason}"

        self.send(
            title=f"Order Cancelled: {symbol}",
            message=message,
            notification_type=NotificationType.ORDER_CANCELLED,
            priority=NotificationPriority.LOW,
        )

    def risk_limit_warning(self, limit_type: str, current: str, limit: str = "") -> None:
        """Send notification for risk limit warning.

        Args:
            limit_type: Type of limit (exposure, position_size, etc.)
            current: Current value
            limit: Limit value (optional)
        """
        if limit:
            message = f"{limit_type} at {current} (limit: {limit})"
        else:
            message = f"{limit_type} at {current}"

        self.send(
            title="Risk Limit Warning",
            message=message,
            notification_type=NotificationType.RISK_LIMIT,
            priority=NotificationPriority.HIGH,
        )

    def error(self, message: str) -> None:
        """Send error notification.

        Args:
            message: Error message
        """
        self.send(
            title="Error",
            message=message,
            notification_type=NotificationType.ERROR,
            priority=NotificationPriority.URGENT,
        )

    def info(self, title: str, message: str) -> None:
        """Send info notification.

        Args:
            title: Notification title
            message: Notification message
        """
        self.send(
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.LOW,
        )
