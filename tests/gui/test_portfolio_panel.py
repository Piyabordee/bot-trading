"""tests/gui/test_portfolio_panel.py"""

import pytest
from decimal import Decimal
from PyQt6.QtWidgets import QApplication

from bot_trading.gui.panels.portfolio import PortfolioPanel
from bot_trading.core.state_manager import StateManager
from bot_trading.providers.base import Position


@pytest.fixture
def app(qtbot):
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def state_manager(qtbot):
    """Create StateManager instance."""
    return StateManager()


@pytest.fixture
def portfolio_panel(app, state_manager, qtbot):
    """Create PortfolioPanel instance for testing."""
    panel = PortfolioPanel(state_manager)
    qtbot.addWidget(panel)
    return panel


class TestPortfolioPanel:
    """Test PortfolioPanel functionality."""

    def test_initialization(self, portfolio_panel):
        """Test that PortfolioPanel initializes correctly."""
        assert portfolio_panel._positions_table is not None

    def test_update_display_with_positions(self, portfolio_panel, state_manager):
        """Test updating display with positions."""
        position = Position(
            symbol="AAPL",
            quantity=Decimal("100"),
            avg_entry_price=Decimal("150.00"),
            current_price=Decimal("175.00"),
            market_value=Decimal("17500.00"),
        )

        state_manager.update_positions({"AAPL": position})

        # Table should have 1 row
        assert portfolio_panel._positions_table.rowCount() == 1
