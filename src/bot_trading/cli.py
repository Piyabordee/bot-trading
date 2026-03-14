"""CLI entry point for trading analysis.

Usage:
    python -m bot_trading.cli --symbols AAPL,MSFT
"""

import os
import sys
import argparse

from bot_trading.ai.analyzer import TradingAnalyzer
from bot_trading.providers.mock import MockProvider


def main(argv: list[str] | None = None) -> int:
    """Run trading analysis CLI.

    Args:
        argv: Command line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="AI-powered trading risk analysis",
    )
    parser.add_argument(
        "--symbols",
        type=str,
        required=True,
        help="Comma-separated list of symbols to analyze",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("ANTHROPIC_API_KEY"),
        help="Anthropic API key (default: ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--max-risk",
        type=float,
        default=0.10,
        help="Max position risk as decimal (default: 0.10)",
    )

    args = parser.parse_args(argv)

    if not args.api_key:
        print("Error: ANTHROPIC_API_KEY environment variable or --api-key argument required")
        return 1

    symbols = [s.strip().upper() for s in args.symbols.split(",")]

    try:
        # Initialize
        provider = MockProvider()
        analyzer = TradingAnalyzer(
            provider=provider,
            api_key=args.api_key,
            max_position_risk_pct=args.max_risk,
        )

        # Run analysis
        print(f"Analyzing: {', '.join(symbols)}")
        print("")

        summary = analyzer.analyze_with_risk_summary(symbols=symbols)

        print(summary)
        print("")
        print("=== Analysis Complete ===")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
