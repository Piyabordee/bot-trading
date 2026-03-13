"""Risk management limits and checks.

Enforces:
- Max position size per trade
- Max portfolio exposure
- Daily loss limit
- Duplicate order protection

TODO: Add daily loss limit tracking
TODO: Add market hours validation
"""

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal


@dataclass
class RiskCheckResult:
    """Result of a risk limit check."""

    allowed: bool
    reason: str = ""


@dataclass
class OrderRecord:
    """Record of a submitted order for duplicate detection."""

    symbol: str
    side: str
    timestamp: datetime


class RiskLimits:
    """Risk management limits and checks.

    Enforces:
    - Max position size per trade
    - Max portfolio exposure
    - Daily loss limit
    - Duplicate order protection

    TODO: Add daily loss limit tracking
    TODO: Add market hours validation
    """

    def __init__(
        self,
        max_position_size: Decimal = Decimal("1000"),
        max_portfolio_exposure: Decimal = Decimal("0.2"),
        daily_loss_limit: Decimal = Decimal("500"),
        portfolio_value: Decimal = Decimal("0"),
    ) -> None:
        self.max_position_size = max_position_size
        self.max_portfolio_exposure = max_portfolio_exposure
        self.daily_loss_limit = daily_loss_limit
        self.portfolio_value = portfolio_value
        self._order_history: deque[OrderRecord] = deque()

    def check_order_size(self, quantity: Decimal) -> RiskCheckResult:
        """Check if order size is within limits.

        Args:
            quantity: Order quantity

        Returns:
            RiskCheckResult indicating if order is allowed
        """
        if quantity > self.max_position_size:
            return RiskCheckResult(
                allowed=False,
                reason=f"Order size {quantity} exceeds maximum {self.max_position_size}",
            )
        return RiskCheckResult(allowed=True)

    def check_portfolio_exposure(
        self,
        new_value: Decimal,
        current_exposure: Decimal = Decimal("0"),
    ) -> RiskCheckResult:
        """Check if new position would exceed portfolio exposure limit.

        Args:
            new_value: Value of new position
            current_exposure: Current total exposure

        Returns:
            RiskCheckResult indicating if position is allowed
        """
        total_exposure = current_exposure + new_value
        max_allowed = self.portfolio_value * self.max_portfolio_exposure

        if total_exposure > max_allowed:
            return RiskCheckResult(
                allowed=False,
                reason=f"Total exposure {total_exposure} exceeds maximum {max_allowed}",
            )
        return RiskCheckResult(allowed=True)

    def check_duplicate_order(
        self,
        symbol: str,
        side: str,
        within_seconds: int = 30,
    ) -> RiskCheckResult:
        """Check for duplicate orders within time window.

        Args:
            symbol: Trading symbol
            side: Order side ('buy' or 'sell')
            within_seconds: Time window to check for duplicates

        Returns:
            RiskCheckResult indicating if order is allowed
        """
        cutoff = datetime.now() - timedelta(seconds=within_seconds)

        for record in self._order_history:
            if record.timestamp < cutoff:
                continue
            if record.symbol == symbol and record.side == side:
                return RiskCheckResult(
                    allowed=False,
                    reason=f"Duplicate order for {symbol} {side} within {within_seconds}s",
                )

        return RiskCheckResult(allowed=True)

    def record_order(self, symbol: str, side: str) -> None:
        """Record an order for duplicate detection.

        Args:
            symbol: Trading symbol
            side: Order side
        """
        self._order_history.append(OrderRecord(symbol=symbol, side=side, timestamp=datetime.now()))

        # Clean old records
        cutoff = datetime.now() - timedelta(seconds=300)  # Keep 5 minutes
        while self._order_history and self._order_history[0].timestamp < cutoff:
            self._order_history.popleft()
