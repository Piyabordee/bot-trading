"""Order execution logic with risk checks.

Flow:
1. Validate signal
2. Check risk limits
3. Submit order to provider
4. Log result
"""

import logging
from dataclasses import dataclass

from bot_trading.providers.base import BaseProvider
from bot_trading.risk.limits import RiskLimits
from bot_trading.strategy.base import Signal


logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of an execution attempt."""

    executed: bool
    signal: Signal
    reason: str = ""
    order_id: str | None = None


class Executor:
    """Executes trading signals with risk checks.

    Flow:
    1. Validate signal
    2. Check risk limits
    3. Submit order to provider
    4. Log result

    All orders are submitted through the configured provider.
    Risk checks are performed before every execution.
    """

    def __init__(self, provider: BaseProvider, risk_limits: RiskLimits) -> None:
        """Initialize executor.

        Args:
            provider: Trading provider (e.g., AlpacaProvider)
            risk_limits: Risk management limits
        """
        self.provider = provider
        self.risk_limits = risk_limits

    def execute_signal(self, signal: Signal) -> ExecutionResult:
        """Execute a trading signal with risk checks.

        Args:
            signal: Trading signal to execute

        Returns:
            ExecutionResult with execution status
        """
        # Validate signal
        if signal.action not in ("buy", "sell"):
            return ExecutionResult(
                executed=False, signal=signal, reason=f"Invalid action: {signal.action}"
            )

        if not signal.quantity or signal.quantity <= 0:
            return ExecutionResult(
                executed=False, signal=signal, reason="Invalid quantity"
            )

        # Check risk limits
        size_check = self.risk_limits.check_order_size(signal.quantity)
        if not size_check.allowed:
            logger.warning(f"Order rejected by risk limits: {size_check.reason}")
            return ExecutionResult(
                executed=False, signal=signal, reason=f"Risk check failed: {size_check.reason}"
            )

        # Check for duplicates
        duplicate_check = self.risk_limits.check_duplicate_order(
            signal.symbol, signal.action
        )
        if not duplicate_check.allowed:
            logger.warning(f"Duplicate order blocked: {duplicate_check.reason}")
            return ExecutionResult(
                executed=False,
                signal=signal,
                reason=f"Duplicate check failed: {duplicate_check.reason}",
            )

        # Submit order to provider
        try:
            order = self.provider.submit_order(
                symbol=signal.symbol,
                side=signal.action,
                quantity=signal.quantity,
                order_type="market",  # Default to market orders
                price=None,  # Market orders have no price
            )

            logger.info(
                f"Order submitted: {signal.action} {signal.quantity} {signal.symbol} "
                f"(order_id: {order.order_id})"
            )

            return ExecutionResult(
                executed=True,
                signal=signal,
                order_id=order.order_id,
                reason="",
            )

        except Exception as e:
            logger.error(f"Order submission failed: {e}")
            return ExecutionResult(
                executed=False,
                signal=signal,
                reason=f"Order submission failed: {e}",
            )
