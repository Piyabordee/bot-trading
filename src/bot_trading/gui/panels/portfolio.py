"""src/bot_trading/gui/panels/portfolio.py"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import Qt

from bot_trading.core.state_manager import StateManager


class PortfolioPanel(QWidget):
    """Panel displaying portfolio information.

    Shows:
    - Current positions table
    - Account summary
    - P&L calculations
    """

    def __init__(self, state_manager: StateManager) -> None:
        """Initialize PortfolioPanel.

        Args:
            state_manager: Application state manager
        """
        super().__init__()
        self._state_manager = state_manager
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Positions table
        self._positions_table = QTableWidget()
        self._positions_table.setColumnCount(5)
        self._positions_table.setHorizontalHeaderLabels([
            "Symbol", "Quantity", "Avg Price", "Current Price", "Market Value"
        ])
        self._positions_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self._positions_table)

    def _connect_signals(self) -> None:
        """Connect to state manager signals."""
        self._state_manager.portfolio_updated.connect(self._update_display)

    def _update_display(self) -> None:
        """Update the positions display."""
        positions = self._state_manager.positions

        self._positions_table.setRowCount(len(positions))

        for row, (symbol, pos) in enumerate(positions.items()):
            self._positions_table.setItem(row, 0, QTableWidgetItem(symbol))
            self._positions_table.setItem(row, 1, QTableWidgetItem(str(pos.quantity)))
            self._positions_table.setItem(
                row, 2, QTableWidgetItem(f"${pos.avg_entry_price:.2f}")
            )
            self._positions_table.setItem(
                row, 3, QTableWidgetItem(f"${pos.current_price:.2f}")
            )
            self._positions_table.setItem(
                row, 4, QTableWidgetItem(f"${pos.market_value:,.2f}")
            )
