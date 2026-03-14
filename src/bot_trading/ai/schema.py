"""AI output config schema using Pydantic.

Defines the schema for AI-generated trading analysis configs.
Must be both AI-friendly (simple structure) and Python-readable
(strict validation, clear errors).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TradingAction(str, Enum):
    """Valid trading actions."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Sentiment(str, Enum):
    """Overall market sentiment."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class SymbolRecommendation(BaseModel):
    """AI recommendation for a single symbol.

    Contains action, confidence, risk score, and optional
    price levels for position management.
    """

    action: TradingAction
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence level 0-1")
    risk_score: int = Field(ge=1, le=10, description="Risk score 1-10")
    reasoning: str = Field(min_length=1, description="Explanation for recommendation")
    entry_price: float | None = Field(None, ge=0, description="Suggested entry price")
    stop_loss: float | None = Field(None, ge=0, description="Suggested stop loss")
    target_price: float | None = Field(None, ge=0, description="Price target")
    position_size_pct: float = Field(
        ge=0.0,
        le=1.0,
        description="Position size as % of portfolio",
    )
    warning: str | None = Field(None, description="Risk warning if applicable")

    @field_validator("position_size_pct")
    @classmethod
    def position_size_not_zero_when_buying(cls, v: float, info) -> float:
        """Ensure position size > 0 when action is BUY."""
        if info.data.get("action") == TradingAction.BUY and v == 0:
            raise ValueError("position_size_pct must be > 0 for BUY orders")
        return v

    @field_validator("entry_price", "stop_loss", "target_price")
    @classmethod
    def prices_consistent(cls, v: float | None, info) -> float | None:
        """Validate price relationships."""
        if v is None:
            return v

        action = info.data.get("action")
        entry = info.data.get("entry_price")
        stop = info.data.get("stop_loss")

        if action == TradingAction.BUY and entry and stop:
            if stop >= entry:
                raise ValueError("stop_loss must be below entry_price for BUY")

        return v


class PortfolioRisk(BaseModel):
    """Portfolio-level risk assessment."""

    current_exposure: float = Field(ge=0.0, le=1.0, description="Current portfolio exposure")
    recommended_max_exposure: float = Field(
        ge=0.0,
        le=1.0,
        description="Recommended max exposure",
    )
    risk_factors: list[str] = Field(default_factory=list, description="List of risk concerns")


class AIAnalysisResult(BaseModel):
    """Complete AI analysis result.

    This is the core output schema that AI must generate.
    It's designed to be simple enough for AI to get right,
    but structured enough for Python to validate strictly.
    """

    overall_sentiment: Sentiment
    symbols: dict[str, SymbolRecommendation] = Field(
        default_factory=dict,
        description="Symbol-specific recommendations",
    )
    portfolio_risk: PortfolioRisk

    @field_validator("overall_sentiment", mode="before")
    @classmethod
    def normalize_sentiment(cls, v: str) -> str:
        """Normalize sentiment to lowercase."""
        if isinstance(v, str):
            return v.lower()
        return v

    def get_recommendation(self, symbol: str) -> SymbolRecommendation | None:
        """Get recommendation for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            SymbolRecommendation or None if not found
        """
        return self.symbols.get(symbol)

    def is_high_risk(self, symbol: str) -> bool:
        """Check if symbol recommendation is high risk (score >= 7).

        Args:
            symbol: Trading symbol

        Returns:
            True if risk score >= 7
        """
        rec = self.get_recommendation(symbol)
        return rec is not None and rec.risk_score >= 7


# Type alias for convenience
AIConfig = AIAnalysisResult
