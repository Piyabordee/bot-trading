"""Tests for CLI entry point."""

from unittest.mock import Mock, patch

from bot_trading.cli import main


@patch("bot_trading.cli.TradingAnalyzer")
@patch("bot_trading.cli.MockProvider")
def test_cli_runs_analysis(mock_provider, mock_analyzer, capsys):
    """Test CLI runs analysis and outputs results."""
    # Mock analyzer
    mock_result = Mock()
    mock_result.overall_sentiment.value = "neutral"
    mock_result.symbols = {}
    mock_result.portfolio_risk.current_exposure = 0.0
    mock_result.portfolio_risk.recommended_max_exposure = 0.2
    mock_result.portfolio_risk.risk_factors = []

    mock_analyzer.return_value.analyze_with_risk_summary.return_value = "Test Analysis"

    # Run CLI with new subcommand structure
    try:
        main(["analyze", "--symbols", "AAPL,MSFT", "--api-key", "test-key"])
    except SystemExit:
        pass  # CLI may exit

    captured = capsys.readouterr()
    assert "Analysis" in captured.out or "Test Analysis" in captured.out
