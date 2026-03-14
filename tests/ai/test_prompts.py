"""Tests for prompt builder."""

import pytest
from datetime import date
from decimal import Decimal

from bot_trading.ai.prompts import PromptBuilder
from bot_trading.data.models import MarketContext, SymbolAnalysis


@pytest.fixture
def sample_context():
    """Create sample market context for testing."""
    return MarketContext(
        date=date(2026, 3, 14),
        account_equity=Decimal("10000"),
        cash=Decimal("5000"),
        buying_power=Decimal("10000"),
        positions={},
        symbols=["AAPL"],
        symbol_data={
            "AAPL": SymbolAnalysis(
                symbol="AAPL",
                current_price=Decimal("175.50"),
                sma_20=Decimal("170.00"),
                rsi_14=65.5,
                volume_avg=50000000,
                price_change_pct=5.2,
                volatility=0.02,
            )
        },
    )


def test_prompt_builder_creates_basic_prompt(sample_context):
    """Test basic prompt creation."""
    builder = PromptBuilder()
    prompt = builder.build_analysis_prompt(sample_context)

    assert "AAPL" in prompt
    assert "175.50" in prompt
    assert "65.5" in prompt
    assert "10,000.00" in prompt  # Formatted with commas


def test_prompt_builder_includes_risk_instructions(sample_context):
    """Test prompt includes risk management instructions."""
    builder = PromptBuilder()
    prompt = builder.build_analysis_prompt(sample_context)

    assert "risk" in prompt.lower()
    assert "10%" in prompt  # Default risk limit


def test_prompt_builder_custom_risk_limit(sample_context):
    """Test custom risk limit in prompt."""
    builder = PromptBuilder(max_position_risk_pct=0.05)
    prompt = builder.build_analysis_prompt(sample_context)

    assert "5%" in prompt
