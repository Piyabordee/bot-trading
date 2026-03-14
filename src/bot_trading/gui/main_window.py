"""src/bot_trading/gui/main_window.py"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QMenuBar,
    QStatusBar,
    QLabel,
    QPushButton,
)
from PyQt6.QtCore import Qt

from bot_trading.controllers.app_controller import AppController


class MainWindow(QMainWindow):
    """Main application window.

    Features:
    - Menu bar with File, View, Tools, Help menus
    - Tab widget with multiple panels
    - Status bar with trading mode indicator
    - Account summary display
    """

    def __init__(self, app_controller: AppController) -> None:
        """Initialize MainWindow.

        Args:
            app_controller: Application controller
        """
        super().__init__()
        self._app_controller = app_controller
        self._state_manager = app_controller.state_manager

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("AI Trading Risk Analyzer")
        self.resize(1200, 800)

        # Create menu bar
        self._create_menu_bar()

        # Create central widget with tab widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Account summary label
        self._account_summary = QLabel("Account: Loading...")
        self._account_summary.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(self._account_summary)

        # Tab widget for panels
        self._tab_widget = QTabWidget()
        layout.addWidget(self._tab_widget)

        # Status bar
        self._create_status_bar()

    def _create_menu_bar(self) -> None:
        """Create the menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        # View menu
        view_menu = menu_bar.addMenu("&View")

        # Tools menu
        tools_menu = menu_bar.addMenu("&Tools")

        # Help menu
        help_menu = menu_bar.addMenu("&Help")

    def _create_status_bar(self) -> None:
        """Create the status bar."""
        status_bar = self.statusBar()

        # Trading mode indicator
        self._mode_label = QLabel("Paper Mode")
        self._mode_label.setStyleSheet("color: green; font-weight: bold;")
        status_bar.addPermanentWidget(self._mode_label)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._on_refresh)
        status_bar.addPermanentWidget(refresh_btn)

    def _connect_signals(self) -> None:
        """Connect to state manager signals."""
        self._state_manager.portfolio_updated.connect(self._update_account_display)
        self._state_manager.trading_mode_changed.connect(self._update_mode_display)

    def _update_account_display(self) -> None:
        """Update account summary display."""
        account = self._state_manager.account
        if account:
            pnl = self._state_manager.get_total_profit_loss()
            pnl_sign = "+" if pnl >= 0 else ""
            text = (
                f"Equity: ${account.equity:,.2f} | "
                f"Cash: ${account.cash:,.2f} | "
                f"P&L: {pnl_sign}{pnl:,.2f}"
            )
            self._account_summary.setText(text)
        else:
            self._account_summary.setText("Account: Loading...")

    def _update_mode_display(self) -> None:
        """Update trading mode display in status bar."""
        from bot_trading.core.state_manager import TradingMode

        mode = self._state_manager.trading_mode
        if mode == TradingMode.REAL:
            self._mode_label.setText("Real Mode")
            self._mode_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self._mode_label.setText("Paper Mode")
            self._mode_label.setStyleSheet("color: green; font-weight: bold;")

    def _on_refresh(self) -> None:
        """Handle refresh button click."""
        self._app_controller.refresh_portfolio()
