"""Data pipeline for fetching and transforming market data.

Fetches historical data from providers, calculates technical indicators,
and bundles everything into AI-friendly context objects.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from bot_trading.data.models import MarketContext, SymbolAnalysis
from bot_trading.providers.base import Bar

if TYPE_CHECKING:
    from bot_trading.providers.base import BaseProvider


class DataPipeline:
    """Pipeline for fetching and transforming market data.

    Orchestrates data fetching from providers and computes
    technical indicators for AI analysis.
    """

    def __init__(self, provider: "BaseProvider") -> None:
        """Initialize pipeline with a data provider.

        Args:
            provider: BaseProvider instance (Mock, Alpaca, etc.)
        """
        self.provider = provider

    def fetch_historical_bars(
        self,
        symbols: list[str],
        start_date: date,
        end_date: date,
        timeframe: str = "1Day",
    ) -> dict[str, list[Bar]]:
        """Fetch historical bars for multiple symbols.

        Args:
            symbols: List of symbols to fetch
            start_date: Start date
            end_date: End date
            timeframe: Bar timeframe

        Returns:
            Dictionary mapping symbol to list of bars
        """
        result = {}
        for symbol in symbols:
            bars = self.provider.get_historical_bars(symbol, start_date, end_date, timeframe)
            result[symbol] = bars
        return result

    def calculate_sma(self, bars: list[Bar], period: int) -> Decimal | None:
        """Calculate Simple Moving Average.

        Args:
            bars: List of historical bars
            period: SMA period

        Returns:
            SMA value or None if insufficient data
        """
        if len(bars) < period:
            return None

        recent_bars = bars[-period:]
        total = sum(b.close for b in recent_bars)
        return total / Decimal(period)

    def calculate_rsi(self, bars: list[Bar], period: int = 14) -> float | None:
        """Calculate Relative Strength Index.

        Args:
            bars: List of historical bars
            period: RSI period

        Returns:
            RSI value (0-100) or None if insufficient data
        """
        if len(bars) < period + 1:
            return None

        # Calculate price changes
        gains = []
        losses = []

        for i in range(len(bars) - 1, len(bars) - period - 1, -1):
            change = float(bars[i].close - bars[i - 1].close)
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_volatility(self, bars: list[Bar], period: int = 20) -> float | None:
        """Calculate historical volatility (standard deviation of returns).

        Args:
            bars: List of historical bars
            period: Lookback period

        Returns:
            Volatility as float or None if insufficient data
        """
        if len(bars) < period + 1:
            return None

        recent_bars = bars[-period - 1:]
        returns = []

        for i in range(1, len(recent_bars)):
            prev_close = float(recent_bars[i - 1].close)
            curr_close = float(recent_bars[i].close)
            if prev_close > 0:
                returns.append((curr_close - prev_close) / prev_close)

        if not returns:
            return None

        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        return variance ** 0.5

    def create_symbol_analysis(
        self,
        symbol: str,
        bars: list[Bar],
        lookback_days: int = 20,
    ) -> SymbolAnalysis:
        """Create SymbolAnalysis from historical bars.

        Args:
            symbol: Trading symbol
            bars: Historical bars
            lookback_days: Days to look back for indicators

        Returns:
            SymbolAnalysis with computed indicators
        """
        latest_bar = bars[-1] if bars else None

        if not latest_bar:
            raise ValueError(f"No bars available for {symbol}")

        # Calculate indicators
        sma_20 = self.calculate_sma(bars, 20)
        rsi_14 = self.calculate_rsi(bars, 14)
        volatility = self.calculate_volatility(bars)

        # Calculate price change
        price_change_pct = None
        if len(bars) >= lookback_days:
            old_price = float(bars[-lookback_days].close)
            new_price = float(latest_bar.close)
            if old_price > 0:
                price_change_pct = ((new_price - old_price) / old_price) * 100

        # Calculate average volume
        volume_avg = None
        if len(bars) >= 20:
            volume_avg = sum(b.volume for b in bars[-20:]) // 20

        return SymbolAnalysis(
            symbol=symbol,
            current_price=latest_bar.close,
            sma_20=sma_20,
            rsi_14=rsi_14,
            volume_avg=volume_avg,
            price_change_pct=price_change_pct,
            volatility=volatility,
        )

    def create_market_context(
        self,
        symbols: list[str],
        lookback_days: int = 20,
    ) -> MarketContext:
        """Create complete market context for AI analysis.

        Args:
            symbols: Symbols to analyze
            lookback_days: Historical lookback period

        Returns:
            MarketContext with all data bundled
        """
        # Fetch account info
        account = self.provider.get_account()

        # Fetch positions
        positions = self.provider.get_positions()
        position_dict = {p.symbol: p.quantity for p in positions}

        # Fetch historical data
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days + 50)  # Buffer for indicators

        all_bars = self.fetch_historical_bars(symbols, start_date, end_date)

        # Create symbol analysis
        symbol_data = {}
        for symbol in symbols:
            if symbol in all_bars and all_bars[symbol]:
                symbol_data[symbol] = self.create_symbol_analysis(
                    symbol, all_bars[symbol], lookback_days
                )

        return MarketContext(
            date=end_date,
            account_equity=account.equity,
            cash=account.cash,
            buying_power=account.buying_power,
            positions=position_dict,
            symbols=symbols,
            symbol_data=symbol_data,
        )
