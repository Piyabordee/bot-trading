"""Tests for risk scoring."""

import pytest
from decimal import Decimal

from bot_trading.risk.scoring import RiskScorer, RiskFactors
from bot_trading.ai.schema import AIAnalysisResult, SymbolRecommendation, PortfolioRisk, TradingAction, Sentiment


@pytest.fixture
def sample_analysis():
    """Create sample AI analysis for testing."""
    return AIAnalysisResult(
        overall_sentiment=Sentiment.NEUTRAL,
        symbols={
            "AAPL": {
                "action": TradingAction.BUY,
                "confidence": 0.75,
                "risk_score": 5,
                "reasoning": "Test",
                "position_size_pct": 0.08,
                "entry_price": 175.0,
                "stop_loss": 170.0,
                "target_price": 185.0,
            }
        },
        portfolio_risk=PortfolioRisk(
            current_exposure=0.1,
            recommended_max_exposure=0.2,
            risk_factors=[],
        ),
    )


def test_risk_scorer_creates_factors(sample_analysis):
    """Test risk scorer extracts risk factors."""
    scorer = RiskScorer()
    factors = scorer.analyze_risk_factors(sample_analysis)

    assert factors.symbol == "AAPL"
    assert factors.ai_risk_score == 5
    assert factors.confidence == 0.75


def test_risk_scorer_calculates_position_size(sample_analysis):
    """Test position size calculation based on risk."""
    scorer = RiskScorer(portfolio_value=Decimal("10000"))

    size = scorer.calculate_position_size(
        analysis=sample_analysis,
        symbol="AAPL",
        entry_price=Decimal("175"),
        stop_loss=Decimal("170"),
        risk_per_trade_pct=0.02,  # 2% risk
    )

    # With $175 entry and $5 stop loss distance:
    # 2% of $10k = $200 risk
    # $200 / $5 = 40 shares max
    assert size > 0
    assert size <= 100


def test_risk_scorer_adjusts_for_high_risk():
    """Test size reduction for high-risk symbols."""
    high_risk_analysis = AIAnalysisResult(
        overall_sentiment=Sentiment.NEUTRAL,
        symbols={
            "TSLA": {
                "action": TradingAction.BUY,
                "confidence": 0.5,
                "risk_score": 8,  # High risk!
                "reasoning": "Test",
                "position_size_pct": 0.05,
            }
        },
        portfolio_risk=PortfolioRisk(
            current_exposure=0.0,
            recommended_max_exposure=0.2,
            risk_factors=["High volatility"],
        ),
    )

    scorer = RiskScorer(portfolio_value=Decimal("10000"))

    # High risk should reduce position
    factors = scorer.analyze_risk_factors(high_risk_analysis)
    assert factors.risk_multiplier < 1.0
