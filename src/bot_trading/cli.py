"""CLI entry point for trading analysis.

Usage:
    python -m bot_trading.cli --symbols AAPL,MSFT
    python -m bot_trading.cli gui
"""

import os
import sys
import argparse

from PyQt6.QtWidgets import QApplication

from bot_trading.ai.analyzer import TradingAnalyzer
from bot_trading.providers.mock import MockProvider
from bot_trading.providers.alpaca import AlpacaProvider
from bot_trading.gui.main_window import MainWindow
from bot_trading.controllers.app_controller import AppController


def run_gui(mode: str = "paper") -> int:
    """Run the GUI application.

    Args:
        mode: Trading mode ("paper" or "real")

    Returns:
        Exit code (0 for success, 1 for error)
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    try:
        # Create provider based on mode
        if mode == "real":
            # For real mode, we would use AlpacaProvider with real credentials
            # For now, use MockProvider as a placeholder
            provider = MockProvider()
        else:
            provider = MockProvider()

        # Create app controller
        app_controller = AppController(provider=provider)
        app_controller.startup()

        # Create and show main window
        window = MainWindow(app_controller)
        window.show()

        return app.exec()

    except Exception as e:
        print(f"Error starting GUI: {e}")
        import traceback
        traceback.print_exc()
        return 1


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

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Analyze command (default behavior for backward compatibility)
    analyze_parser = subparsers.add_parser("analyze", help="Run trading analysis")
    analyze_parser.add_argument(
        "--symbols",
        type=str,
        required=True,
        help="Comma-separated list of symbols to analyze",
    )
    analyze_parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("ANTHROPIC_API_KEY"),
        help="Anthropic API key (default: ANTHROPIC_API_KEY env var)",
    )
    analyze_parser.add_argument(
        "--max-risk",
        type=float,
        default=0.10,
        help="Max position risk as decimal (default: 0.10)",
    )

    # GUI command
    gui_parser = subparsers.add_parser("gui", help="Launch GUI application")
    gui_parser.add_argument(
        "--mode",
        type=str,
        choices=["paper", "real"],
        default="paper",
        help="Trading mode (default: paper)",
    )

    args = parser.parse_args(argv)

    # If no subcommand specified, use old behavior for backward compatibility
    if args.command is None:
        # Try to parse as old-style arguments
        old_parser = argparse.ArgumentParser(
            description="AI-powered trading risk analysis",
        )
        old_parser.add_argument(
            "--symbols",
            type=str,
            required=True,
            help="Comma-separated list of symbols to analyze",
        )
        old_parser.add_argument(
            "--api-key",
            type=str,
            default=os.getenv("ANTHROPIC_API_KEY"),
            help="Anthropic API key (default: ANTHROPIC_API_KEY env var)",
        )
        old_parser.add_argument(
            "--max-risk",
            type=float,
            default=0.10,
            help="Max position risk as decimal (default: 0.10)",
        )
        old_args = old_parser.parse_args(argv)
        return run_analysis(old_args)

    if args.command == "gui":
        return run_gui(args.mode)

    if args.command == "analyze":
        return run_analysis(args)

    return 0


def run_analysis(args) -> int:
    """Run trading analysis.

    Args:
        args: Parsed arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
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
