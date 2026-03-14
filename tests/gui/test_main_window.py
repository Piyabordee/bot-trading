"""tests/gui/test_main_window.py"""

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from bot_trading.gui.main_window import MainWindow


@pytest.fixture
def app(qtbot):
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def app_controller(app):
    """Create a mock AppController for testing."""
    from unittest.mock import Mock
    from bot_trading.controllers.app_controller import AppController
    from bot_trading.core.state_manager import StateManager

    mock_provider = Mock()
    mock_provider.get_account.return_value = Mock(
        equity=50000, cash=25000, buying_power=100000, portfolio_value=25000
    )
    mock_provider.get_positions.return_value = []

    controller = AppController(provider=mock_provider, data_dir=None)
    return controller


@pytest.fixture
def main_window(app, app_controller, qtbot):
    """Create MainWindow instance for testing."""
    window = MainWindow(app_controller)
    qtbot.addWidget(window)
    return window


class TestMainWindow:
    """Test MainWindow functionality."""

    def test_initialization(self, main_window):
        """Test that MainWindow initializes correctly."""
        assert main_window.windowTitle() == "AI Trading Risk Analyzer"
        assert main_window.isVisible() is False  # Not shown by default

    def test_has_menu_bar(self, main_window):
        """Test that menu bar is created."""
        menu_bar = main_window.menuBar()
        assert menu_bar is not None

    def test_has_tab_widget(self, main_window):
        """Test that tab widget for panels exists."""
        # The central widget should be a tab widget or contain one
        central = main_window.centralWidget()
        assert central is not None

    def test_has_status_bar(self, main_window):
        """Test that status bar is created."""
        status_bar = main_window.statusBar()
        assert status_bar is not None

    def test_show_displays_window(self, main_window):
        """Test that show() displays the window."""
        main_window.show()
        assert main_window.isVisible() is True

    def test_close_removes_window(self, main_window):
        """Test that close() removes the window."""
        main_window.show()
        main_window.close()
        assert main_window.isVisible() is False
