"""src/bot_trading/core/state_manager.py"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Callable

from PyQt6.QtCore import QObject, pyqtSignal

from bot_trading.providers.base import Account, Position, Order


class TradingMode(Enum):
    """Trading mode: paper trading or real money."""

    PAPER = "paper"
    REAL = "real"


@dataclass
class ManualSignal:
    """Manually entered trading signal."""

    symbol: str
    action: str  # "buy", "sell", "hold"
    quantity: Decimal
    price: Decimal | None = None  # None = market price
    risk_score: int = 5  # 1-10
    reason: str = ""
    source: str = "manual"
    created_at: datetime = field(default_factory=datetime.now)

    def to_execution_signal(self) -> "Signal":
        """Convert to strategy.Signal for execution."""
        from bot_trading.strategy.base import Signal

        return Signal(
            symbol=self.symbol,
            action=self.action,
            confidence=1.0,  # Manual = full confidence
            quantity=self.quantity,
            reason=self.reason,
        )


class StateManager(QObject):
    """Central state manager with Qt signals for reactive updates.

    This is the single source of truth for application state.
    All state changes go through this manager, and Qt signals
    notify subscribers (GUI panels) of changes.

    Signals:
        trading_mode_changed: Emitted when trading mode changes
        portfolio_updated: Emitted when account/positions change
        signals_updated: Emitted when signal list changes
        orders_updated: Emitted when order history changes
        state_changed: Emitted when any state changes
    """

    # Qt signals for reactive updates
    trading_mode_changed = pyqtSignal(TradingMode)
    portfolio_updated = pyqtSignal()
    signals_updated = pyqtSignal()
    orders_updated = pyqtSignal()
    state_changed = pyqtSignal()

    def __init__(self) -> None:
        """Initialize StateManager with default values."""
        super().__init__()
        self._trading_mode: TradingMode = TradingMode.PAPER
        self._account: Account | None = None
        self._positions: dict[str, Position] = {}
        self._orders: list[Order] = []
        self._signals: list[ManualSignal] = []

    @property
    def trading_mode(self) -> TradingMode:
        """Get current trading mode."""
        return self._trading_mode

    def set_trading_mode(self, mode: TradingMode) -> None:
        """Set trading mode and emit signal.

        Args:
            mode: New trading mode (PAPER or REAL)
        """
        if self._trading_mode != mode:
            self._trading_mode = mode
            self.trading_mode_changed.emit(mode)
            self.state_changed.emit()

    @property
    def account(self) -> Account | None:
        """Get current account information."""
        return self._account

    def update_account(self, account: Account) -> None:
        """Update account information and emit signal.

        Args:
            account: New account data
        """
        self._account = account
        self.portfolio_updated.emit()
        self.state_changed.emit()

    @property
    def positions(self) -> dict[str, Position]:
        """Get current positions."""
        return self._positions

    def update_positions(self, positions: dict[str, Position]) -> None:
        """Update positions and emit signal.

        Args:
            positions: New position data keyed by symbol
        """
        self._positions = positions
        self.portfolio_updated.emit()
        self.state_changed.emit()

    @property
    def orders(self) -> list[Order]:
        """Get order history."""
        return self._orders.copy()

    def add_order(self, order: Order) -> None:
        """Add order to history and emit signal.

        Args:
            order: Order to add
        """
        self._orders.append(order)
        self.orders_updated.emit()
        self.state_changed.emit()

    @property
    def signals(self) -> list[ManualSignal]:
        """Get pending signals."""
        return self._signals.copy()

    def add_signal(self, signal: ManualSignal) -> None:
        """Add signal and emit signal.

        Args:
            signal: Signal to add
        """
        self._signals.append(signal)
        self.signals_updated.emit()
        self.state_changed.emit()

    def remove_signal(self, index: int) -> None:
        """Remove signal by index and emit signal.

        Args:
            index: Index of signal to remove

        Raises:
            IndexError: If index is out of range
        """
        if 0 <= index < len(self._signals):
            del self._signals[index]
            self.signals_updated.emit()
            self.state_changed.emit()

    def clear_signals(self) -> None:
        """Clear all signals."""
        self._signals.clear()
        self.signals_updated.emit()
        self.state_changed.emit()

    def get_portfolio_value(self) -> Decimal:
        """Get total portfolio value.

        Returns:
            Portfolio equity or 0 if no account data
        """
        return self._account.equity if self._account else Decimal("0")

    def get_cash(self) -> Decimal:
        """Get available cash.

        Returns:
            Cash balance or 0 if no account data
        """
        return self._account.cash if self._account else Decimal("0")

    def get_total_profit_loss(self) -> Decimal:
        """Calculate total unrealized P&L from positions.

        Returns:
            Total profit/loss across all positions
        """
        if not self._positions:
            return Decimal("0")

        total_pnl = Decimal("0")
        for pos in self._positions.values():
            # P&L = (current_price - avg_entry_price) * quantity
            pnl = (pos.current_price - pos.avg_entry_price) * pos.quantity
            total_pnl += pnl

        return total_pnl
