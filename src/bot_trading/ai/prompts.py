"""Prompt templates for AI trading analysis.

Builds structured prompts that include market context,
account state, and clear instructions for AI analysis.
"""

from dataclasses import dataclass

from bot_trading.data.models import MarketContext


@dataclass
class PromptBuilderConfig:
    """Configuration for prompt building."""

    max_position_risk_pct: float = 0.10  # 10% default
    max_portfolio_exposure: float = 0.20
    include_technical_indicators: bool = True
    include_positions: bool = True
    temperature: float = 0.3


class PromptBuilder:
    """Build prompts for AI trading analysis.

    Creates structured, consistent prompts that include
    all necessary context for AI to generate trading analysis.
    """

    def __init__(
        self,
        max_position_risk_pct: float = 0.10,
        max_portfolio_exposure: float = 0.20,
    ) -> None:
        """Initialize prompt builder.

        Args:
            max_position_risk_pct: Max risk per position (decimal, e.g., 0.10 = 10%)
            max_portfolio_exposure: Max total portfolio exposure
        """
        self.max_position_risk_pct = max_position_risk_pct
        self.max_portfolio_exposure = max_portfolio_exposure

    def build_analysis_prompt(self, context: MarketContext) -> str:
        """Build complete analysis prompt from market context.

        Args:
            context: MarketContext with all market data

        Returns:
            Formatted prompt string for AI
        """
        sections = [
            self._build_system_instructions(),
            self._build_account_section(context),
            self._build_positions_section(context),
            self._build_market_data_section(context),
            self._build_output_format_section(),
        ]

        return "\n\n".join(filter(None, sections))

    def _build_system_instructions(self) -> str:
        """Build system instructions for AI."""
        return f"""# Trading Risk Analysis Request

You are a conservative trading risk analyst. Your role is to:
1. Analyze market data and identify potential risks
2. Provide clear, actionable recommendations
3. NEVER recommend risking more than {int(self.max_position_risk_pct * 100)}% of portfolio per trade
4. Explain your reasoning in simple terms
5. Highlight warning signs and red flags

Important:
- Focus on RISK MANAGEMENT, not profit maximization
- If conditions are unclear, recommend waiting/holding
- Always consider worst-case scenarios
- Be conservative with risk estimates"""

    def _build_account_section(self, context: MarketContext) -> str:
        """Build account information section."""
        return f"""## Account Information

- Date: {context.date}
- Portfolio Value: ${float(context.account_equity):,.2f}
- Cash Available: ${float(context.cash):,.2f}
- Buying Power: ${float(context.buying_power):,.2f}"""

    def _build_positions_section(self, context: MarketContext) -> str:
        """Build current positions section."""
        if not context.positions:
            return "## Current Positions\n\nNo open positions."

        position_lines = []
        for symbol, qty in context.positions.items():
            position_lines.append(f"- {symbol}: {qty} shares")

        return "## Current Positions\n\n" + "\n".join(position_lines)

    def _build_market_data_section(self, context: MarketContext) -> str:
        """Build market data section with symbols."""
        lines = ["## Market Data"]

        for symbol in context.symbols:
            if symbol not in context.symbol_data:
                continue

            analysis = context.symbol_data[symbol]
            symbol_lines = [
                f"\n### {symbol}",
                f"- Current Price: ${float(analysis.current_price):.2f}",
            ]

            if analysis.sma_20 is not None:
                diff_pct = ((float(analysis.current_price) - float(analysis.sma_20)) /
                           float(analysis.sma_20) * 100)
                symbol_lines.append(f"- 20-day SMA: ${float(analysis.sma_20):.2f} ({diff_pct:+.1f}%)")

            if analysis.rsi_14 is not None:
                rsi_status = "Neutral"
                if analysis.rsi_14 > 70:
                    rsi_status = "Overbought"
                elif analysis.rsi_14 < 30:
                    rsi_status = "Oversold"
                symbol_lines.append(f"- RSI(14): {analysis.rsi_14:.1f} ({rsi_status})")

            if analysis.price_change_pct is not None:
                symbol_lines.append(f"- {20}-day Change: {analysis.price_change_pct:+.1f}%")

            if analysis.volatility is not None:
                symbol_lines.append(f"- Volatility: {analysis.volatility:.4f}")

            if analysis.volume_avg is not None:
                symbol_lines.append(f"- Avg Volume: {analysis.volume_avg:,}")

            lines.extend(symbol_lines)

        return "\n".join(lines)

    def _build_output_format_section(self) -> str:
        """Build output format instructions."""
        return """## Required Output Format

Provide your analysis as JSON with this exact structure:

```json
{
  "overall_sentiment": "bullish|bearish|neutral",
  "symbols": {
    "AAPL": {
      "action": "BUY|SELL|HOLD",
      "confidence": 0.0-1.0,
      "risk_score": 1-10,
      "reasoning": "Brief explanation",
      "entry_price": null or number,
      "stop_loss": null or number,
      "target_price": null or number,
      "position_size_pct": 0.0-1.0,
      "warning": null or "risk warning"
    }
  },
  "portfolio_risk": {
    "current_exposure": 0.0-1.0,
    "recommended_max_exposure": 0.0-1.0,
    "risk_factors": ["list of concerns"]
  }
}
```

Risk Score Guide:
- 1-2: Very Low Risk - Safe to proceed
- 3-4: Low Risk - Proceed with caution
- 5-6: Medium Risk - Be conservative
- 7-8: High Risk - Consider reducing size
- 9-10: Very High Risk - Avoid or wait

Respond ONLY with valid JSON. No text outside the JSON structure."""
