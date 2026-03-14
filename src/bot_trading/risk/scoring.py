"""Risk scoring algorithm.

Combines AI analysis with technical indicators to calculate
position sizes and risk adjustments.
"""

from dataclasses import dataclass
from decimal import Decimal

from bot_trading.ai.schema import AIAnalysisResult


@dataclass
class RiskFactors:
    """Risk factors for a trading decision."""

    symbol: str
    ai_risk_score: int  # 1-10 from AI
    confidence: float  # 0-1 from AI
    volatility: float | None = None  # Historical volatility
    distance_from_avg: float | None = None  # % distance from SMA
    rsi: float | None = None  # RSI value
    risk_multiplier: float = 1.0  # Size adjustment factor


class RiskScorer:
    """Calculate position sizes based on AI analysis and risk.

    Combines AI recommendations with technical risk metrics
    to determine safe position sizes.
    """

    def __init__(
        self,
        portfolio_value: Decimal = Decimal("10000"),
        max_risk_per_trade_pct: float = 0.02,  # 2% default
    ) -> None:
        """Initialize risk scorer.

        Args:
            portfolio_value: Total portfolio value
            max_risk_per_trade_pct: Max % of portfolio to risk per trade
        """
        self.portfolio_value = portfolio_value
        self.max_risk_per_trade_pct = max_risk_per_trade_pct

    def analyze_risk_factors(
        self,
        analysis: AIAnalysisResult,
        symbol: str | None = None,
    ) -> RiskFactors:
        """Extract risk factors from AI analysis.

        Args:
            analysis: AI analysis result
            symbol: Symbol to analyze (uses first if None)

        Returns:
            RiskFactors object
        """
        # Get symbol recommendation
        if symbol is None:
            if not analysis.symbols:
                raise ValueError("No symbols in analysis")
            symbol = next(iter(analysis.symbols.keys()))

        rec = analysis.symbols.get(symbol)
        if rec is None:
            raise ValueError(f"No recommendation for {symbol}")

        # Calculate risk multiplier based on AI score
        risk_multiplier = self._calculate_risk_multiplier(rec.risk_score)

        return RiskFactors(
            symbol=symbol,
            ai_risk_score=rec.risk_score,
            confidence=rec.confidence,
            risk_multiplier=risk_multiplier,
        )

    def calculate_position_size(
        self,
        analysis: AIAnalysisResult,
        symbol: str,
        entry_price: Decimal,
        stop_loss: Decimal,
        risk_per_trade_pct: float | None = None,
    ) -> int:
        """Calculate safe position size based on risk.

        Uses the standard formula:
        Position Size = (Portfolio * Risk%) / (Entry - Stop)

        Args:
            analysis: AI analysis result
            symbol: Trading symbol
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_per_trade_pct: Risk % per trade (uses default if None)

        Returns:
            Maximum safe position size in shares
        """
        if risk_per_trade_pct is None:
            risk_per_trade_pct = self.max_risk_per_trade_pct

        # Get risk factors
        factors = self.analyze_risk_factors(analysis, symbol)

        # Calculate dollar risk
        dollar_risk = float(self.portfolio_value) * risk_per_trade_pct

        # Apply risk multiplier
        dollar_risk *= factors.risk_multiplier

        # Calculate stop distance
        stop_distance = abs(float(entry_price) - float(stop_loss))

        if stop_distance == 0:
            return 0

        # Calculate position size
        shares = int(dollar_risk / stop_distance)

        return max(0, shares)

    def _calculate_risk_multiplier(self, ai_risk_score: int) -> float:
        """Calculate size multiplier based on AI risk score.

        Higher risk = smaller position.

        Args:
            ai_risk_score: AI risk score (1-10)

        Returns:
            Multiplier (0.1 to 1.0)
        """
        # Risk score to multiplier mapping
        # 1-2: 100% (very safe)
        # 3-4: 90%
        # 5-6: 75%
        # 7-8: 50%
        # 9-10: 25% (very risky)
        multipliers = {
            1: 1.0,
            2: 1.0,
            3: 0.9,
            4: 0.9,
            5: 0.75,
            6: 0.75,
            7: 0.5,
            8: 0.5,
            9: 0.25,
            10: 0.25,
        }

        return multipliers.get(ai_risk_score, 0.5)

    def get_recommendation_summary(
        self,
        analysis: AIAnalysisResult,
        symbol: str,
    ) -> str:
        """Get human-readable risk summary.

        Args:
            analysis: AI analysis result
            symbol: Trading symbol

        Returns:
            Formatted summary string
        """
        rec = analysis.symbols.get(symbol)
        if rec is None:
            return f"No recommendation for {symbol}"

        factors = self.analyze_risk_factors(analysis, symbol)

        lines = [
            f"Symbol: {symbol}",
            f"Action: {rec.action.value}",
            f"AI Risk Score: {rec.risk_score}/10",
            f"Confidence: {rec.confidence:.0%}",
            f"Risk Adjustment: {factors.risk_multiplier:.0%} of normal size",
        ]

        if rec.entry_price and rec.stop_loss:
            risk_per_share = abs(rec.entry_price - rec.stop_loss)
            lines.append(f"Risk per Share: ${risk_per_share:.2f}")

        if rec.warning:
            lines.append(f"WARNING: {rec.warning}")

        return "\n".join(lines)
