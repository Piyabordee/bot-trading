"""End-to-end trading analysis orchestrator.

Coordinates data pipeline, AI client, and risk scoring
to provide complete trading analysis.
"""

from dataclasses import dataclass
from unittest.mock import Mock

from bot_trading.ai.client import AIClient
from bot_trading.ai.prompts import PromptBuilder
from bot_trading.ai.schema import AIAnalysisResult
from bot_trading.ai.validator import ConfigValidator
from bot_trading.data.pipeline import DataPipeline
from bot_trading.risk.scoring import RiskScorer


@dataclass
class AnalyzerConfig:
    """Configuration for TradingAnalyzer."""

    ai_api_key: str
    max_position_risk_pct: float = 0.10
    max_portfolio_exposure: float = 0.20
    lookback_days: int = 20


class TradingAnalyzer:
    """End-to-end trading analysis.

    Flow:
    1. Fetch market data via DataPipeline
    2. Build prompt via PromptBuilder
    3. Get AI analysis via AIClient
    4. Validate via ConfigValidator
    5. Calculate position sizes via RiskScorer
    """

    def __init__(
        self,
        provider,  # BaseProvider
        api_key: str,
        max_position_risk_pct: float = 0.10,
        lookback_days: int = 20,
    ) -> None:
        """Initialize analyzer.

        Args:
            provider: BaseProvider instance
            api_key: Anthropic API key
            max_position_risk_pct: Max risk per position
            lookback_days: Historical lookback period
        """
        self.provider = provider
        self.pipeline = DataPipeline(provider)
        self.prompt_builder = PromptBuilder(max_position_risk_pct=max_position_risk_pct)
        self.ai_client = AIClient.for_testing(Mock())  # Placeholder, will be replaced in tests
        self.validator = ConfigValidator(max_position_risk_pct=max_position_risk_pct)
        self.risk_scorer = RiskScorer()
        self.lookback_days = lookback_days

        # Create real AI client if not testing
        if api_key != "test-key":
            self.ai_client = AIClient(api_key=api_key)

    def analyze(
        self,
        symbols: list[str],
    ) -> AIAnalysisResult:
        """Run complete trading analysis.

        Args:
            symbols: Symbols to analyze

        Returns:
            Validated AIAnalysisResult

        Raises:
            AIServiceError: If AI call fails
            ValidationError: If config validation fails
        """
        # Step 1: Fetch and prepare data
        context = self.pipeline.create_market_context(
            symbols=symbols,
            lookback_days=self.lookback_days,
        )

        # Step 2: Build prompt
        prompt = self.prompt_builder.build_analysis_prompt(context)

        # Step 3: Get AI analysis
        ai_response = self.ai_client.generate_json_analysis(prompt)

        # Step 4: Validate
        result = self.validator.validate_json(ai_response)

        return result

    def analyze_with_risk_summary(
        self,
        symbols: list[str],
    ) -> str:
        """Analyze and return human-readable summary.

        Args:
            symbols: Symbols to analyze

        Returns:
            Formatted summary string
        """
        result = self.analyze(symbols)

        lines = [
            f"=== Trading Analysis Report ===",
            f"Overall Sentiment: {result.overall_sentiment.value.upper()}",
            "",
        ]

        # Portfolio risk
        lines.extend([
            "Portfolio Risk:",
            f"  Current Exposure: {result.portfolio_risk.current_exposure:.1%}",
            f"  Recommended Max: {result.portfolio_risk.recommended_max_exposure:.1%}",
        ])

        if result.portfolio_risk.risk_factors:
            lines.append("  Risk Factors:")
            for factor in result.portfolio_risk.risk_factors:
                lines.append(f"    - {factor}")

        lines.append("")

        # Symbol recommendations
        for symbol, rec in result.symbols.items():
            summary = self.risk_scorer.get_recommendation_summary(result, symbol)
            lines.extend(["", f"=== {symbol} ===", summary])

        return "\n".join(lines)
