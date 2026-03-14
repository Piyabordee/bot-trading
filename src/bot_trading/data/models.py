"""Data models for AI market context and analysis."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class SymbolAnalysis:
    """Analysis data for a single symbol.

    Contains technical indicators and metrics computed from
    historical price data for AI consumption.
    """

    symbol: str
    current_price: Decimal
    sma_20: Decimal | None = None  # Simple Moving Average 20-day
    ema_12: Decimal | None = None  # Exponential Moving Average 12-day
    rsi_14: float | None = None  # Relative Strength Index 14-period
    macd: Decimal | None = None  # MACD line
    macd_signal: Decimal | None = None  # MACD signal line
    volume_avg: int | None = None  # Average volume
    price_change_pct: float | None = None  # Price change % over period
    volatility: float | None = None  # Historical volatility


@dataclass
class MarketContext:
    """Market context bundle for AI analysis.

    Aggregates account state, positions, and symbol analysis
    into a single structure for prompt generation.
    """

    date: date
    account_equity: Decimal
    cash: Decimal
    buying_power: Decimal
    positions: dict[str, Decimal]  # symbol -> quantity
    symbols: list[str]  # Symbols to analyze
    symbol_data: dict[str, SymbolAnalysis]  # symbol -> analysis
