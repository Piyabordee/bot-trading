"""src/bot_trading/gui/panels/signals.py"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTextEdit,
)
from PyQt6.QtCore import Qt

from bot_trading.core.state_manager import StateManager, ManualSignal
from bot_trading.controllers.trading_controller import TradingController
from decimal import Decimal


class SignalsPanel(QWidget):
    """Panel for manual signal entry and management.

    Features:
    - Form to add new signals
    - Table of pending signals
    - Execute button for each signal
    """

    def __init__(
        self,
        state_manager: StateManager,
        trading_controller: TradingController,
    ) -> None:
        """Initialize SignalsPanel.

        Args:
            state_manager: Application state manager
            trading_controller: Trading controller
        """
        super().__init__()
        self._state_manager = state_manager
        self._trading_controller = trading_controller
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Add Signal section
        add_label = QLabel("Add New Signal:")
        add_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(add_label)

        # Signal form
        form_layout = QFormLayout()

        self._symbol_input = QLineEdit()
        self._symbol_input.setPlaceholderText("AAPL")
        form_layout.addRow("Symbol:", self._symbol_input)

        self._action_input = QComboBox()
        self._action_input.addItems(["buy", "sell", "hold"])
        form_layout.addRow("Action:", self._action_input)

        self._quantity_input = QSpinBox()
        self._quantity_input.setRange(1, 1000000)
        self._quantity_input.setValue(100)
        form_layout.addRow("Quantity:", self._quantity_input)

        self._price_input = QDoubleSpinBox()
        self._price_input.setRange(0, 1000000)
        self._price_input.setDecimals(2)
        self._price_input.setSpecialValueText("Market")
        form_layout.addRow("Price (optional):", self._price_input)

        self._risk_score_input = QSpinBox()
        self._risk_score_input.setRange(1, 10)
        self._risk_score_input.setValue(5)
        form_layout.addRow("Risk Score:", self._risk_score_input)

        self._reason_input = QTextEdit()
        self._reason_input.setPlaceholderText("Reason for trade...")
        self._reason_input.setMaximumHeight(60)
        form_layout.addRow("Reason:", self._reason_input)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self._add_button = QPushButton("Add to List")
        self._add_button.clicked.connect(self._on_add_signal)
        self._clear_button = QPushButton("Clear")
        self._clear_button.clicked.connect(self._on_clear_form)
        button_layout.addWidget(self._add_button)
        button_layout.addWidget(self._clear_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Signals table
        signals_label = QLabel("Pending Signals:")
        signals_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(signals_label)

        self._signals_table = QTableWidget()
        self._signals_table.setColumnCount(6)
        self._signals_table.setHorizontalHeaderLabels([
            "Symbol", "Action", "Quantity", "Risk", "Reason", "Execute"
        ])
        self._signals_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self._signals_table)

    def _connect_signals(self) -> None:
        """Connect to state manager signals."""
        self._state_manager.signals_updated.connect(self._update_signals_table)

    def _on_add_signal(self) -> None:
        """Handle add signal button click."""
        symbol = self._symbol_input.text().strip().upper()
        if not symbol:
            return

        action = self._action_input.currentText()
        quantity = Decimal(str(self._quantity_input.value()))
        price_val = self._price_input.value()
        price = Decimal(str(price_val)) if price_val > 0 else None
        risk_score = self._risk_score_input.value()
        reason = self._reason_input.toPlainText().strip()

        signal = ManualSignal(
            symbol=symbol,
            action=action,
            quantity=quantity,
            price=price,
            risk_score=risk_score,
            reason=reason,
        )

        self._state_manager.add_signal(signal)
        self._on_clear_form()

    def _on_clear_form(self) -> None:
        """Clear the signal input form."""
        self._symbol_input.clear()
        self._action_input.setCurrentIndex(0)
        self._quantity_input.setValue(100)
        self._price_input.setValue(0)
        self._risk_score_input.setValue(5)
        self._reason_input.clear()

    def _update_signals_table(self) -> None:
        """Update the signals table."""
        signals = self._state_manager.signals
        self._signals_table.setRowCount(len(signals))

        for row, signal in enumerate(signals):
            self._signals_table.setItem(row, 0, QTableWidgetItem(signal.symbol))
            self._signals_table.setItem(row, 1, QTableWidgetItem(signal.action))
            self._signals_table.setItem(row, 2, QTableWidgetItem(str(signal.quantity)))

            risk_item = QTableWidgetItem(f"{signal.risk_score}/10")
            self._signals_table.setItem(row, 3, risk_item)

            reason_item = QTableWidgetItem(signal.reason[:50] + "..." if len(signal.reason) > 50 else signal.reason)
            self._signals_table.setItem(row, 4, reason_item)

            # Execute button
            execute_btn = QPushButton("▶")
            execute_btn.clicked.connect(lambda checked, idx=row: self._on_execute_signal(idx))
            self._signals_table.setCellWidget(row, 5, execute_btn)

    def _on_execute_signal(self, index: int) -> None:
        """Handle execute button click."""
        signals = self._state_manager.signals
        if 0 <= index < len(signals):
            signal = signals[index]
            result = self._trading_controller.execute_signal(signal)
            # TODO: Show result dialog
