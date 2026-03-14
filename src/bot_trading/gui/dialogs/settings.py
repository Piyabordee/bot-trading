"""src/bot_trading/gui/dialogs/settings.py"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from bot_trading.controllers.settings_controller import SettingsController
from bot_trading.core.state_manager import TradingMode


class SettingsDialog(QDialog):
    """Dialog for application settings.

    Allows user to configure:
    - API keys
    - Trading mode (paper/real)
    - Risk limits
    """

    def __init__(self, settings_controller: SettingsController) -> None:
        """Initialize SettingsDialog.

        Args:
            settings_controller: Settings controller
        """
        super().__init__()
        self._settings_controller = settings_controller
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        # Settings form
        form_layout = QFormLayout()

        self._api_key_input = QLineEdit()
        self._api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("API Key:", self._api_key_input)

        self._api_secret_input = QLineEdit()
        self._api_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("API Secret:", self._api_secret_input)

        self._trading_mode_input = QComboBox()
        self._trading_mode_input.addItems(["paper", "real"])
        form_layout.addRow("Trading Mode:", self._trading_mode_input)

        layout.addLayout(form_layout)

        # Warning label for real trading
        self._warning_label = QLabel()
        self._warning_label.setWordWrap(True)
        self._warning_label.setStyleSheet("color: red; padding: 10px;")
        layout.addWidget(self._warning_label)

        # Update warning when mode changes
        self._trading_mode_input.currentTextChanged.connect(self._update_warning)

        # Buttons
        button_layout = QHBoxLayout()
        self._save_button = QPushButton("Save")
        self._save_button.clicked.connect(self._on_save)
        self._cancel_button = QPushButton("Cancel")
        self._cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self._save_button)
        button_layout.addWidget(self._cancel_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _load_settings(self) -> None:
        """Load settings from controller."""
        settings = self._settings_controller.get_settings()
        self._api_key_input.setText(settings.get("api_key", ""))
        self._api_secret_input.setText(settings.get("api_secret", ""))

        mode = settings.get("trading_mode", "paper")
        index = 0 if mode == "paper" else 1
        self._trading_mode_input.setCurrentIndex(index)

        self._update_warning()

    def _update_warning(self) -> None:
        """Update warning label based on trading mode."""
        if self._trading_mode_input.currentText() == "real":
            self._warning_label.setText(
                "⚠️ WARNING: Real trading mode uses REAL MONEY. "
                "Make sure you understand the risks."
            )
        else:
            self._warning_label.setText("")

    def _on_save(self) -> None:
        """Handle save button click."""
        api_key = self._api_key_input.text().strip()
        api_secret = self._api_secret_input.text().strip()
        trading_mode = self._trading_mode_input.currentText()

        # Validate API keys for real mode
        if trading_mode == "real":
            if not self._settings_controller.validate_api_keys(api_key, api_secret):
                QMessageBox.warning(
                    self,
                    "Invalid API Keys",
                    "Please enter valid API keys for real trading mode."
                )
                return

        # Save settings
        self._settings_controller.save_api_keys(api_key, api_secret)

        mode_enum = TradingMode.REAL if trading_mode == "real" else TradingMode.PAPER
        self._settings_controller.set_trading_mode(mode_enum)

        QMessageBox.information(self, "Settings", "Settings saved successfully.")
        self.accept()
