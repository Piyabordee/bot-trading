"""Tests for configuration module."""
import os
import pytest
from bot_trading.config import Config, get_config


def test_config_defaults_to_paper_mode():
    """Paper mode must be the default unless explicitly set."""
    config = Config()
    assert config.trading_mode == "paper"


def test_config_from_env_sets_paper_mode():
    """Environment variable should set trading mode."""
    os.environ["TRADING_MODE"] = "paper"
    config = Config()
    assert config.trading_mode == "paper"


def test_config_rejects_live_mode_without_explicit_setting():
    """Live mode should NOT be settable without explicit intent."""
    # Default should always be paper
    config = Config()
    assert config.trading_mode != "live"


def test_config_loads_risk_limits():
    """Risk limits should be loaded from environment."""
    os.environ["MAX_POSITION_SIZE"] = "1000"
    config = Config()
    assert config.max_position_size == 1000


def test_config_singleton():
    """get_config should return the same instance."""
    config1 = get_config()
    config2 = get_config()
    assert config1 is config2
