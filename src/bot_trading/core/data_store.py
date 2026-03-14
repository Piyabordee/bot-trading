"""src/bot_trading/core/data_store.py"""

import csv
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from bot_trading.core.state_manager import ManualSignal
from bot_trading.providers.base import Order


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal and datetime objects."""

    def default(self, obj: Any) -> Any:
        """Convert Decimal and datetime to JSON-serializable types."""
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


class DataStore:
    """File-based persistence for application state and history.

    Stores:
    - Settings (API keys, preferences)
    - Application state (for recovery)
    - Pending signals (JSON)
    - Trade history (CSV)
    - Order history (CSV)
    """

    def __init__(self, data_dir: Path | str | None = None) -> None:
        """Initialize DataStore with directory structure.

        Args:
            data_dir: Root directory for data files. Defaults to ./data
        """
        if data_dir is None:
            data_dir = Path.cwd() / "data"
        else:
            data_dir = Path(data_dir)

        self._data_dir = data_dir
        self._state_dir = data_dir / "state"
        self._history_dir = data_dir / "history"
        self._signals_dir = data_dir / "signals"

        # Create directories
        self._state_dir.mkdir(parents=True, exist_ok=True)
        self._history_dir.mkdir(parents=True, exist_ok=True)
        self._signals_dir.mkdir(parents=True, exist_ok=True)

    # Settings

    def save_settings(self, settings: dict[str, Any]) -> None:
        """Save settings to JSON file.

        Args:
            settings: Settings dictionary to save
        """
        settings_file = self._state_dir / "settings.json"
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)

    def load_settings(self) -> dict[str, Any]:
        """Load settings from JSON file.

        Returns:
            Settings dictionary, or empty dict if file doesn't exist
        """
        settings_file = self._state_dir / "settings.json"
        if not settings_file.exists():
            return {}

        with open(settings_file) as f:
            return json.load(f)

    # State

    def save_state(self, state: dict[str, Any]) -> None:
        """Save application state to JSON file.

        Args:
            state: State dictionary to save
        """
        state_file = self._state_dir / "current_state.json"
        with open(state_file, "w") as f:
            json.dump(state, f, cls=DecimalEncoder, indent=2)

    def load_state(self) -> dict[str, Any]:
        """Load application state from JSON file.

        Returns:
            State dictionary, or empty dict if file doesn't exist
        """
        state_file = self._state_dir / "current_state.json"
        if not state_file.exists():
            return {}

        with open(state_file) as f:
            return json.load(f)

    # Signals

    def save_signal(self, signal: ManualSignal) -> None:
        """Save a signal to pending signals file.

        Args:
            signal: Signal to save
        """
        signals_file = self._signals_dir / "pending_signals.json"

        # Load existing signals
        existing = []
        if signals_file.exists():
            with open(signals_file) as f:
                existing = json.load(f)

        # Add new signal
        signal_data = {
            "symbol": signal.symbol,
            "action": signal.action,
            "quantity": str(signal.quantity),
            "price": str(signal.price) if signal.price else None,
            "risk_score": signal.risk_score,
            "reason": signal.reason,
            "source": signal.source,
            "created_at": signal.created_at.isoformat(),
        }
        existing.append(signal_data)

        # Save all signals
        with open(signals_file, "w") as f:
            json.dump(existing, f, cls=DecimalEncoder, indent=2)

    def load_signals(self) -> list[ManualSignal]:
        """Load pending signals from file.

        Returns:
            List of ManualSignal objects
        """
        signals_file = self._signals_dir / "pending_signals.json"
        if not signals_file.exists():
            return []

        with open(signals_file) as f:
            data = json.load(f)

        signals = []
        for item in data:
            signals.append(
                ManualSignal(
                    symbol=item["symbol"],
                    action=item["action"],
                    quantity=Decimal(item["quantity"]),
                    price=Decimal(item["price"]) if item.get("price") else None,
                    risk_score=item.get("risk_score", 5),
                    reason=item.get("reason", ""),
                    source=item.get("source", "manual"),
                    created_at=datetime.fromisoformat(item["created_at"]),
                )
            )

        return signals

    def clear_signals(self) -> None:
        """Clear all pending signals."""
        signals_file = self._signals_dir / "pending_signals.json"
        if signals_file.exists():
            signals_file.unlink()

    # Trades

    def save_trade(self, trade: dict[str, Any]) -> None:
        """Save a trade record to CSV file.

        Args:
            trade: Trade record with keys: timestamp, symbol, action,
                   quantity, price, order_id
        """
        today_str = date.today().strftime("%Y_%m_%d")
        trades_file = self._history_dir / f"trades_{today_str}.csv"

        file_exists = trades_file.exists()

        with open(trades_file, "a", newline="") as f:
            fieldnames = ["timestamp", "symbol", "action", "quantity", "price", "order_id"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(trade)

    def load_trades(self, date: date) -> list[dict[str, Any]]:
        """Load trades for a specific date.

        Args:
            date: Date to load trades for

        Returns:
            List of trade dictionaries
        """
        date_str = date.strftime("%Y_%m_%d")
        trades_file = self._history_dir / f"trades_{date_str}.csv"

        if not trades_file.exists():
            return []

        with open(trades_file) as f:
            reader = csv.DictReader(f)
            return list(reader)

    # Orders

    def save_order(self, order: Order) -> None:
        """Save an order record to CSV file.

        Args:
            order: Order object to save
        """
        today_str = date.today().strftime("%Y_%m_%d")
        orders_file = self._history_dir / f"orders_{today_str}.csv"

        file_exists = orders_file.exists()

        with open(orders_file, "a", newline="") as f:
            fieldnames = [
                "order_id",
                "symbol",
                "side",
                "quantity",
                "price",
                "status",
                "created_at",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(
                {
                    "order_id": order.order_id,
                    "symbol": order.symbol,
                    "side": order.side,
                    "quantity": str(order.quantity),
                    "price": str(order.price) if order.price else "",
                    "status": order.status,
                    "created_at": order.created_at.isoformat(),
                }
            )
