"""Tests for base strategy module."""

import pytest
from bot_trading.strategy.base import BaseStrategy, Signal


def test_base_strategy_is_abstract():
    """BaseStrategy should not be instantiable directly."""
    with pytest.raises(TypeError):
        BaseStrategy()  # type: ignore


def test_concrete_strategy_can_generate_signals():
    """Concrete strategy should implement generate_signals."""

    class SimpleStrategy(BaseStrategy):
        def generate_signals(self):
            return [Signal(symbol="AAPL", action="hold", confidence=1.0)]

    strategy = SimpleStrategy()
    signals = strategy.generate_signals()
    assert len(signals) == 1
    assert signals[0].symbol == "AAPL"
