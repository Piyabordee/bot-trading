"""src/bot_trading/controllers/trading_controller.py"""

from dataclasses import dataclass
from decimal import Decimal

from bot_trading.core.state_manager import (
    StateManager,
    TradingMode,
    ManualSignal,
)
from bot_trading.core.notification_manager import NotificationManager
from bot_trading.providers.base import BaseProvider, Order


@dataclass
class PreTradeCheckResult:
    """Result of pre-trade safety checks."""

    allowed: bool
    failures: list[str]


@dataclass
class ExecutionResult:
    """Result of signal execution."""

    success: bool
    message: str
    order_id: str | None = None


class TradingController:
    """Controller for trading operations.

    Handles:
    - Executing manual signals
    - Pre-trade safety checks
    - Order cancellation
    - Portfolio refresh
    - Getting market data

    Coordinates between StateManager, Provider, and NotificationManager.
    """

    def __init__(
        self,
        state_manager: StateManager,
        provider: BaseProvider,
        notification_manager: NotificationManager,
    ) -> None:
        """Initialize TradingController.

        Args:
            state_manager: Application state manager
            provider: Trading provider (paper or real)
            notification_manager: Notification manager
        """
        self._state_manager = state_manager
        self._provider = provider
        self._notification_manager = notification_manager

    @property
    def state_manager(self) -> StateManager:
        """Get state manager."""
        return self._state_manager

    def refresh_portfolio(self) -> None:
        """Refresh portfolio data from provider and update state.

        Fetches account and positions from provider and emits
        portfolio_updated signal.
        """
        account = self._provider.get_account()
        positions = self._provider.get_positions()

        # Update state
        self._state_manager.update_account(account)

        # Convert positions list to dict keyed by symbol
        positions_dict = {pos.symbol: pos for pos in positions}
        self._state_manager.update_positions(positions_dict)

    def execute_signal(
        self, signal: ManualSignal, user_confirmed_real_mode: bool = False
    ) -> ExecutionResult:
        """Execute a trading signal.

        Args:
            signal: ManualSignal to execute
            user_confirmed_real_mode: Whether user confirmed real trading mode

        Returns:
            ExecutionResult with execution status
        """
        # Run pre-trade checks
        check_result = self._pre_trade_checks(signal, user_confirmed_real_mode)
        if not check_result.allowed:
            return ExecutionResult(
                success=False,
                message=f"Pre-trade checks failed: {', '.join(check_result.failures)}",
            )

        # Execute the order
        try:
            order = self._submit_order(signal)

            # Record in state
            self._state_manager.add_order(order)

            # Send notification
            self._notification_manager.trade_executed(
                symbol=signal.symbol,
                quantity=str(signal.quantity),
                side=signal.action,
            )

            return ExecutionResult(
                success=True,
                message="Order submitted successfully",
                order_id=order.order_id,
            )

        except Exception as e:
            self._notification_manager.error(f"Order execution failed: {e}")
            return ExecutionResult(success=False, message=f"Execution failed: {e}")

    def _pre_trade_checks(
        self, signal: ManualSignal, user_confirmed_real_mode: bool = False
    ) -> PreTradeCheckResult:
        """Run pre-trade safety checks.

        Args:
            signal: Signal to check
            user_confirmed_real_mode: Whether user confirmed real mode

        Returns:
            PreTradeCheckResult with check outcomes
        """
        failures = []

        # Check 1: Real trading mode confirmation
        if (
            self._state_manager.trading_mode == TradingMode.REAL
            and not user_confirmed_real_mode
        ):
            failures.append("Real trading mode requires explicit confirmation")

        # Check 2: Valid quantity
        if signal.quantity <= 0:
            failures.append("Quantity must be positive")

        # Check 3: Valid action
        if signal.action not in ("buy", "sell"):
            failures.append(f"Invalid action: {signal.action}")

        # Check 4: Sufficient funds for buy orders
        if signal.action == "buy":
            account = self._state_manager.account
            if account is None:
                self.refresh_portfolio()
                account = self._state_manager.account

            if account:
                # Calculate required amount
                price = signal.price or self._provider.get_latest_price(signal.symbol)
                required = price * signal.quantity

                if required > account.buying_power:
                    failures.append(
                        f"Insufficient funds: need ${required}, have ${account.buying_power}"
                    )

        # Check 5: Position exists for sell orders
        if signal.action == "sell":
            positions = self._state_manager.positions
            if signal.symbol not in positions:
                failures.append(f"No position in {signal.symbol} to sell")

        return PreTradeCheckResult(allowed=len(failures) == 0, failures=failures)

    def _submit_order(self, signal: ManualSignal) -> Order:
        """Submit order to provider.

        Args:
            signal: Signal to submit

        Returns:
            Order object from provider
        """
        # Determine price
        price = signal.price
        if price is None:
            price = self._provider.get_latest_price(signal.symbol)

        # Determine order type
        order_type = "limit" if signal.price else "market"

        # Submit order
        order = self._provider.submit_order(
            symbol=signal.symbol,
            side=signal.action,
            quantity=signal.quantity,
            order_type=order_type,
            price=price,
        )

        return order

    def cancel_order(self, order_id: str) -> ExecutionResult:
        """Cancel an order.

        Args:
            order_id: Order ID to cancel

        Returns:
            ExecutionResult with cancellation status
        """
        try:
            success = self._provider.cancel_order(order_id)

            if success:
                self._notification_manager.order_cancelled(
                    order_id=order_id, symbol="", reason="User cancelled"
                )
                return ExecutionResult(success=True, message="Order cancelled")
            else:
                return ExecutionResult(success=False, message="Failed to cancel order")

        except Exception as e:
            return ExecutionResult(success=False, message=f"Cancellation failed: {e}")

    def get_open_orders(self) -> list[Order]:
        """Get all open orders.

        Returns:
            List of open orders
        """
        return self._provider.list_open_orders()

    def get_latest_price(self, symbol: str) -> Decimal:
        """Get latest price for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Latest price
        """
        return self._provider.get_latest_price(symbol)
