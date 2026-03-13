"""Configuration module with PAPER mode as default.

IMPORTANT: This is a paper-trading-only demo bot.
Live trading paths should remain disabled unless explicitly approved.
"""
import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class Config:
    """Application configuration with PAPER mode as default.

    IMPORTANT: This is a paper-trading-only demo bot.
    Live trading paths should remain disabled unless explicitly approved.
    """

    trading_mode: str = "paper"
    max_position_size: float = 1000.0
    max_portfolio_exposure: float = 0.2
    daily_loss_limit: float = 500.0
    log_level: str = "INFO"

    def __post_init__(self):
        """Load values from environment with safe defaults."""
        # ALWAYS default to paper mode
        self.trading_mode = os.getenv("TRADING_MODE", "paper").lower()

        # Safety check: if someone tries to set live via env, still default to paper
        # unless explicitly documented and approved
        if self.trading_mode not in ("paper", "live"):
            self.trading_mode = "paper"

        self.max_position_size = float(os.getenv("MAX_POSITION_SIZE", str(self.max_position_size)))
        self.max_portfolio_exposure = float(os.getenv("MAX_PORTFOLIO_EXPOSURE", str(self.max_portfolio_exposure)))
        self.daily_loss_limit = float(os.getenv("DAILY_LOSS_LIMIT", str(self.daily_loss_limit)))
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)

    @property
    def is_paper_mode(self) -> bool:
        """Check if running in paper trading mode."""
        return self.trading_mode == "paper"

    @property
    def is_live_mode(self) -> bool:
        """Check if running in live mode (should always be False for demo)."""
        return self.trading_mode == "live"


@lru_cache
def get_config() -> Config:
    """Get singleton configuration instance."""
    return Config()
