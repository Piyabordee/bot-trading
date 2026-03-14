"""Example: How to read the trading analysis config in Python."""

import yaml
from pathlib import Path


def read_config(config_path: str | Path = "config/ai_analysis_config.yaml") -> dict:
    """Read YAML config file and return as Python dictionary.

    Args:
        config_path: Path to config file

    Returns:
        Dictionary with all config data
    """
    config_file = Path(config_path)

    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config


def print_summary(config: dict) -> None:
    """Print a summary of the config."""
    print("=" * 50)
    print("TRADING ANALYSIS SUMMARY")
    print("=" * 50)

    # Overall sentiment
    print(f"\n[Market] Sentiment: {config['overall_sentiment']}")

    # Symbols summary
    print(f"\n[Stocks] Analysis:")
    for symbol, data in config["symbols"].items():
        print(f"  {symbol}: {data['action']} (confidence: {data['confidence']}, risk: {data['risk_score']}/10)")

    # Portfolio risk
    risk = config["portfolio_risk"]
    print(f"\n[Money] Portfolio: {risk['current_exposure_pct']}% invested, max: {risk['max_exposure_pct']}%")

    # Watchlist
    print(f"\n[Watchlist] ({len(config['watchlist'])} symbols):")
    for item in config["watchlist"]:
        print(f"  {item['symbol']}: {item['reason']}")


def get_symbol_analysis(config: dict, symbol: str) -> dict | None:
    """Get analysis for a specific symbol.

    Args:
        config: Config dictionary
        symbol: Stock symbol (e.g., "AAPL")

    Returns:
        Symbol data dict or None if not found
    """
    return config["symbols"].get(symbol.upper())


def is_ready_to_execute(config: dict, symbol: str) -> bool:
    """Check if a symbol is ready to execute.

    Args:
        config: Config dictionary
        symbol: Stock symbol

    Returns:
        True if ready_to_execute is true
    """
    symbol_data = get_symbol_analysis(config, symbol)
    if symbol_data:
        return symbol_data.get("ready_to_execute", False)
    return False


# Example usage
if __name__ == "__main__":
    # Read config
    config = read_config()

    # Print summary
    print_summary(config)

    # Get specific symbol
    print("\n" + "=" * 50)
    print("AAPL DETAILED ANALYSIS")
    print("=" * 50)
    aapl = get_symbol_analysis(config, "AAPL")
    if aapl:
        print(f"Action: {aapl['action']}")
        print(f"Confidence: {aapl['confidence']}")
        print(f"News Sentiment: {aapl['news_sentiment']}")
        print(f"Social Sentiment: {aapl['social_sentiment']}")
        print(f"Trend: {aapl['technical_assessment']['trend']}")
        print(f"\nReasoning:\n{aapl['reasoning']}")
