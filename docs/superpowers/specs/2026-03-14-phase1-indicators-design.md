# Phase 1: Technical Indicators Framework - Design Document

**Date:** 2026-03-14
**Status:** Proposed (Revised v2)
**Author:** Claude Code
**Phase:** Phase 1 - Technical Indicators

---

## 1. Overview

### 1.1 Purpose

Create a comprehensive technical indicators framework to support both backtesting and real-time trading for the paper trading bot.

### 1.2 Scope

- **Indicators to implement:** SMA, EMA, RSI, MACD, Bollinger Bands, ATR
- **Modes supported:** Batch (backtesting) and Incremental (real-time)
- **Framework type:** Full Framework with caching, pipeline management, and DataFrame integration
- **Implementation:** Pure pandas/numpy (no TA-Lib dependency for easy Windows installation)

### 1.3 Out of Scope

- Strategy implementation (Phase 2)
- Backtesting engine (Phase 3)
- Live trading execution logic
- TA-Lib integration (can be added later as optional optimization)

---

## 2. Architecture

### 2.1 Component Diagram

```
Provider (Bar data)
    ↓
Data Utilities (Bar→DataFrame converter)
    ↓
IndicatorPipeline (caching, batch/inc)
    ↓
┌───────────┬───────────┬───────────┐
│MovingAvg  │ Momentum  │ Volatility│
│SMA, EMA   │RSI, MACD  │BB, ATR    │
└───────────┴───────────┴───────────┘
    ↓
DataFrame (OHLCV + all indicators)
    ↓
Strategy
```

### 2.2 File Structure

```
src/bot_trading/
├── indicators/
│   ├── __init__.py          # Export all indicators
│   ├── base.py              # BaseIndicator abstract class
│   ├── moving_avg.py        # SMA, EMA (pure pandas)
│   ├── momentum.py          # RSI, MACD (pure pandas/numpy)
│   ├── volatility.py        # Bollinger Bands, ATR (pure pandas/numpy)
│   ├── pipeline.py          # IndicatorPipeline (core)
│   └── exceptions.py        # Custom exceptions
│
├── data/
│   ├── __init__.py          # Data utilities
│   └── converters.py        # Bar → DataFrame converter
│
└── tests/
    └── test_indicators/     # Unit tests
        ├── test_base.py
        ├── test_moving_avg.py
        ├── test_momentum.py
        ├── test_volatility.py
        ├── test_pipeline.py
        └── test_converters.py
```

### 2.3 Data Flow Example

```
Input (List[Bar]):
  Bar(symbol='AAPL', timestamp='2024-01-01', open=150.0, high=152.0, low=149.0, close=151.0, volume=1000000)
  Bar(symbol='AAPL', timestamp='2024-01-02', open=151.0, high=153.0, low=150.0, close=152.0, volume=1100000)
  ...

↓ BarsToDataFrameConverter.convert()

Output (pd.DataFrame):
                    open   high    low   close  volume
timestamp
2024-01-01         150.0  152.0  149.0  151.0  1000000
2024-01-02         151.0  153.0  150.0  152.0  1100000
...

↓ IndicatorPipeline.compute()

Final (pd.DataFrame with indicators):
                    open   high    low   close  volume  sma_20  rsi_14  macd  ...
timestamp
2024-01-01         150.0  152.0  149.0  151.0  1000000     NaN     NaN   NaN  ...
2024-01-02         151.0  153.0  150.0  152.0  1100000     NaN     NaN   NaN  ...
...
2024-02-01         155.0  157.0  154.0  156.0   900000   151.5    65.2  1.2  ...
```

---

## 3. Core API Design

### 3.1 Type Definitions

```python
from typing import Union
from pandas import Series, DataFrame

IndicatorResult = Union[Series, DataFrame]
```

### 3.2 BaseIndicator (Abstract Class)

```python
class BaseIndicator(ABC):
    """Base class for all technical indicators."""

    @abstractmethod
    def calculate(self, df: DataFrame) -> IndicatorResult:
        """Calculate indicator values.

        Args:
            df: DataFrame with 'open', 'high', 'low', 'close', 'volume' columns
                All price columns are float type
                Index is datetime (timezone-aware or naive, handled consistently)

        Returns:
            IndicatorResult: pd.Series for single-value indicators,
                           pd.DataFrame for multi-value indicators (e.g., MACD)
                           Same index as input DataFrame
        """
        pass

    @abstractmethod
    def required_period(self) -> int:
        """Return minimum bars needed for calculation.

        The first (required_period - 1) rows will be NaN.
        """
        pass

    def validate_input(self, df: DataFrame) -> bool:
        """Validate DataFrame has required columns.

        Required columns: open, high, low, close, volume

        Returns:
            True if valid

        Raises:
            InvalidInputError: If columns are missing or invalid
        """
        required = ['open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise InvalidInputError(f"Missing required columns: {missing}")
        return True
```

### 3.3 Bar → DataFrame Converter

```python
# data/converters.py

class BarsToDataFrameConverter:
    """Convert List[Bar] to pandas DataFrame for indicator computation.

    Handles:
    - Decimal to float conversion (for indicator calculations)
    - Timestamp to datetime index
    - Column naming: 'open', 'high', 'low', 'close', 'volume'
    - Validation (no NaN in prices, sorted by timestamp)
    """

    @staticmethod
    def convert(bars: List[Bar]) -> DataFrame:
        """Convert bars to DataFrame.

        Args:
            bars: List of Bar objects from provider

        Returns:
            DataFrame with:
            - Columns: 'open', 'high', 'low', 'close', 'volume' (all float except volume is int)
            - Index: datetime (timezone-aware if input has timezone, else naive)
            - Sorted by timestamp (ascending)
            - No NaN values in price columns

        Raises:
            InvalidInputError: If bars are empty or contain invalid data
        """
        if not bars:
            raise InvalidInputError("Cannot convert empty bars list")

        data = {
            'open': [float(b.open) for b in bars],
            'high': [float(b.high) for b in bars],
            'low': [float(b.low) for b in bars],
            'close': [float(b.close) for b in bars],
            'volume': [b.volume for b in bars],
        }

        df = DataFrame(data, index=[b.timestamp for b in bars])
        df.index.name = 'timestamp'
        df.sort_index(inplace=True)

        # Validate
        if df[['open', 'high', 'low', 'close']].isna().any().any():
            raise InvalidInputError("Price columns contain NaN values")

        return df
```

### 3.4 IndicatorPipeline

```python
# indicators/pipeline.py

class IndicatorPipeline:
    """Main pipeline for computing technical indicators.

    Features:
    - Batch computation (backtesting)
    - Incremental updates (real-time)
    - Caching (avoid re-computation)
    - Partial failure handling

    Caching Strategy:
    - Each indicator caches its last N output values (N = max required_period)
    - Cache is stored per (symbol, timeframe) combination
    - Cache invalidates when indicators are added/removed
    - Memory limit: 1000 bars per indicator (configurable)
    """

    def __init__(self, cache_size: int = 1000):
        """Initialize pipeline.

        Args:
            cache_size: Maximum bars to cache per indicator
        """
        self._indicators: Dict[str, BaseIndicator] = {}
        self._cache: Optional[DataFrame] = None
        self._cache_symbol: Optional[str] = None
        self._cache_timeframe: Optional[str] = None
        self._failed_indicators: List[str] = []
        self._cache_size = cache_size

    def add_indicator(self, name: str, indicator: BaseIndicator) -> None:
        """Add an indicator to the pipeline.

        Args:
            name: Unique name for this indicator (used as column name)
            indicator: BaseIndicator instance

        Raises:
            ValueError: If name already exists
        """
        if name in self._indicators:
            raise ValueError(f"Indicator '{name}' already exists")
        self._indicators[name] = indicator
        self._invalidate_cache()

    def remove_indicator(self, name: str) -> None:
        """Remove an indicator from the pipeline.

        Args:
            name: Indicator name to remove
        """
        self._indicators.pop(name, None)
        self._invalidate_cache()

    def compute(self, bars: List[Bar]) -> DataFrame:
        """Compute all indicators on historical data (batch mode).

        Args:
            bars: List of Bar objects

        Returns:
            DataFrame with OHLCV + all indicator columns
            First N rows will have NaN for indicators (N = max required_period)

        Raises:
            InsufficientDataError: If not enough bars for indicators
            InvalidInputError: If bar data is invalid

        Note:
            Failed indicators are logged and return NaN columns.
            Check .failed_indicators after compute() to see failures.
        """
        try:
            # Convert bars to DataFrame
            converter = BarsToDataFrameConverter()
            df = converter.convert(bars)

            # Check minimum data requirement
            if self._indicators:
                min_period = max(ind.required_period() for ind in self._indicators.values())
                if len(bars) < min_period:
                    raise InsufficientDataError(
                        f"Need at least {min_period} bars, got {len(bars)}"
                    )

            # Reset failed indicators
            self._failed_indicators = []

            # Compute each indicator
            for name, indicator in self._indicators.items():
                try:
                    result = indicator.calculate(df)

                    # Handle Series vs DataFrame output
                    if isinstance(result, Series):
                        df[name] = result
                    elif isinstance(result, DataFrame):
                        # Multi-column indicator (e.g., MACD)
                        for col in result.columns:
                            df[f"{name}_{col}"] = result[col]
                    else:
                        raise InvalidInputError(
                            f"Indicator {name} returned invalid type: {type(result)}"
                        )

                except Exception as e:
                    logger.warning(f"Failed to compute {name}: {e}")
                    self._failed_indicators.append(name)
                    # Add NaN column so schema is consistent
                    df[name] = float('nan')

            # Update cache
            self._cache = df.tail(self._cache_size).copy()
            self._cache_symbol = bars[0].symbol if bars else None

            return df

        except (InsufficientDataError, InvalidInputError):
            raise  # Re-raise for caller to handle
        except Exception as e:
            logger.error(f"Pipeline computation failed: {e}")
            raise IndicatorError(f"Pipeline failed: {e}")

    def update(self, new_bar: Bar) -> Series:
        """Update indicators with new bar (incremental/real-time mode).

        Args:
            new_bar: New bar data

        Returns:
            Series with latest indicator values

        Raises:
            IndicatorError: If called before compute() or symbol mismatch

        Note:
            - Requires prior compute() call to establish cache
            - Recomputes indicators on cached + new data
            - Slower than true incremental but simpler and more robust
        """
        if self._cache is None:
            raise IndicatorError("Must call compute() before update()")

        if new_bar.symbol != self._cache_symbol:
            raise IndicatorError(
                f"Symbol mismatch: expected {self._cache_symbol}, got {new_bar.symbol}"
            )

        # Append new bar to cache
        new_row = {
            'open': float(new_bar.open),
            'high': float(new_bar.high),
            'low': float(new_bar.low),
            'close': float(new_bar.close),
            'volume': new_bar.volume,
        }
        self._cache.loc[new_bar.timestamp] = new_row

        # Recompute all indicators (incremental optimization TODO)
        # For now, simpler to recompute on full cached dataset
        bars = self._dataframe_to_bars(self._cache)
        df = self.compute(bars)

        # Return latest values
        return df.iloc[-1]

    @property
    def failed_indicators(self) -> List[str]:
        """List of indicators that failed in last compute() call."""
        return self._failed_indicators.copy()

    def _invalidate_cache(self) -> None:
        """Clear cache when indicators change."""
        self._cache = None
        self._cache_symbol = None
```

---

## 4. Indicator Specifications

### 4.1 Moving Averages (Pure Pandas Implementation)

| Indicator | Parameters | Output Type | Column Name(s) | Use Case |
|-----------|-----------|-------------|----------------|----------|
| SMA | period (default: 20) | Series | `sma_{period}` | Trend identification, S/R levels |
| EMA | period (default: 20) | Series | `ema_{period}` | Trend (weights recent data more) |

**Implementation (SMA):**
```python
class SMAIndicator(BaseIndicator):
    def __init__(self, period: int = 20):
        self.period = period

    def calculate(self, df: DataFrame) -> Series:
        return df['close'].rolling(window=self.period).mean()

    def required_period(self) -> int:
        return self.period
```

**Implementation (EMA):**
```python
class EMAIndicator(BaseIndicator):
    def __init__(self, period: int = 20):
        self.period = period

    def calculate(self, df: DataFrame) -> Series:
        return df['close'].ewm(span=self.period, adjust=False).mean()

    def required_period(self) -> int:
        return self.period
```

### 4.2 Momentum Indicators

| Indicator | Parameters | Output Type | Column Name(s) | Use Case |
|-----------|-----------|-------------|----------------|----------|
| RSI | period (default: 14) | Series | `rsi_{period}` | Overbought/oversold (>70/<30) |
| MACD | fast=12, slow=26, signal=9 | DataFrame | `macd_{fast}_{slow}_{signal}`, `macd_{fast}_{slow}_{signal}_signal_line`, `macd_{fast}_{slow}_{signal}_histogram` | Reversal signals |

**Implementation (RSI):**
```python
class RSIIndicator(BaseIndicator):
    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, df: DataFrame) -> Series:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def required_period(self) -> int:
        return self.period + 1  # Need one extra for diff()
```

**Implementation (MACD):**
```python
class MACDIndicator(BaseIndicator):
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def calculate(self, df: DataFrame) -> DataFrame:
        ema_fast = df['close'].ewm(span=self.fast).mean()
        ema_slow = df['close'].ewm(span=self.slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=self.signal).mean()
        histogram = macd - signal_line

        result = DataFrame(index=df.index)
        result['macd'] = macd
        result['signal_line'] = signal_line
        result['histogram'] = histogram
        return result

    def required_period(self) -> int:
        return self.slow + self.signal
```

### 4.3 Volatility Indicators

| Indicator | Parameters | Output Type | Column Name(s) | Use Case |
|-----------|-----------|-------------|----------------|----------|
| Bollinger Bands | period=20, std_dev=2.0 | DataFrame | `bb_{period}_upper`, `bb_{period}_middle`, `bb_{period}_lower`, `bb_{period}_width` | Volatility, breakouts |
| ATR | period (default: 14) | Series | `atr_{period}` | Volatility, stop loss |

**Implementation (Bollinger Bands):**
```python
class BollingerBands(BaseIndicator):
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev

    def calculate(self, df: DataFrame) -> DataFrame:
        middle = df['close'].rolling(window=self.period).mean()
        std = df['close'].rolling(window=self.period).std()
        upper = middle + (std * self.std_dev)
        lower = middle - (std * self.std_dev)

        result = DataFrame(index=df.index)
        result['upper'] = upper
        result['middle'] = middle
        result['lower'] = lower
        result['width'] = upper - lower
        return result

    def required_period(self) -> int:
        return self.period
```

**Implementation (ATR):**
```python
class ATRIndicator(BaseIndicator):
    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, df: DataFrame) -> Series:
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())

        true_range = DataFrame({
            'hl': high_low,
            'hc': high_close,
            'lc': low_close
        }).max(axis=1)

        return true_range.rolling(window=self.period).mean()

    def required_period(self) -> int:
        return self.period
```

---

## 5. Error Handling

### 5.1 Exception Types

```python
# indicators/exceptions.py

class IndicatorError(Exception):
    """Base exception for indicator errors."""
    pass

class InsufficientDataError(IndicatorError):
    """Raised when not enough bars to compute indicator."""
    pass

class InvalidInputError(IndicatorError):
    """Raised when input data is invalid (missing columns, NaN, etc.)."""
    pass
```

### 5.2 Error Handling Strategy

**Validation Rules:**
1. DataFrame must have columns: open, high, low, close, volume
2. Minimum rows: max(indicator.required_period() for all indicators)
3. No NaN or infinite values in price columns
4. Timestamps must be monotonically increasing
5. Volume must be >= 0
6. High >= Low (basic price sanity check)

**Partial Failure Handling:**
```
When compute() encounters an indicator error:
1. Log warning with indicator name and reason
2. Continue computing remaining indicators
3. Return DataFrame with NaN for failed indicators
4. Set .failed_indicators attribute on pipeline

Example:
    pipeline.compute(bars)
    # Returns: DataFrame with sma_20, rsi_14 (NaN), macd (all cols)
    # pipeline.failed_indicators = ['rsi_14']
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

Test each indicator independently with known values:

```python
# Example test data and expected values
# Test: SMA(5) on [10, 11, 12, 13, 14, 15] should give 13.0 for last value
# (10 + 11 + 12 + 13 + 14) / 5 = 12.0
# (11 + 12 + 13 + 14 + 15) / 5 = 13.0
```

**Test Coverage:**
- Each indicator calculation with known values
- Edge cases: empty input, insufficient data, single value
- Input validation: missing columns, NaN values, unsorted timestamps
- Parameter validation: negative periods, zero periods

### 6.2 Integration Tests

- Test Pipeline with multiple indicators
- Test batch vs incremental modes
- Test caching behavior
- Test partial failure handling

### 6.3 Test Coverage Target

- Minimum: 80%
- Preferred: 90%+

---

## 7. Performance Considerations

### 7.1 Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Batch compute() | < 100ms for 1000 bars, 6 indicators | Using pure pandas/numpy |
| Incremental update() | < 50ms for single bar update | Recomputes on cached data |
| Memory | < 10MB per symbol/timeframe | 1000 bars × 6 indicators |

### 7.2 Optimization Strategy

1. **Vectorized operations:** All calculations use pandas/numpy vectorization
2. **Caching:** Store computed results to avoid re-computation
3. **Lazy evaluation:** Only compute indicators when requested
4. **Future optimization:** True incremental updates (compute only latest value)

---

## 8. Dependencies

```toml
[project.dependencies]
pandas = ">=2.0.0"
numpy = ">=1.24.0"

# Note: TA-Lib is NOT used in Phase 1 to avoid Windows installation issues.
# Can be added as optional optimization in later phases.
```

---

## 9. Integration Points

### 9.1 With Strategy (Phase 2)

```python
class MyStrategy(BaseStrategy):
    def __init__(self, provider):
        self.provider = provider
        self.pipeline = IndicatorPipeline()
        self.pipeline.add_indicator('sma_20', SMAIndicator(period=20))
        self.pipeline.add_indicator('sma_50', SMAIndicator(period=50))
        self.pipeline.add_indicator('rsi_14', RSIIndicator(period=14))

    def generate_signals(self) -> list[Signal]:
        # Get historical data
        bars = self.provider.get_historical_bars(
            symbol='AAPL',
            start_date=datetime.now() - timedelta(days=60),
            end_date=datetime.now()
        )

        # Compute indicators
        df = self.pipeline.compute(bars)

        # Check for signals
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        signals = []

        # Golden cross: SMA(20) crosses above SMA(50)
        if (prev['sma_20'] <= prev['sma_50'] and
            latest['sma_20'] > latest['sma_50']):

            # RSI confirmation: not overbought
            if latest['rsi_14'] < 70:
                signals.append(Signal(
                    symbol='AAPL',
                    action='buy',
                    confidence=0.8,
                    reason='Golden cross + RSI < 70'
                ))

        return signals
```

### 9.2 With Main Loop (Future)

```python
# In main trading loop
pipeline = IndicatorPipeline()
# ... add indicators ...

# Initial warmup
bars = provider.get_historical_bars('AAPL', ...)
pipeline.compute(bars)

while True:
    # Wait for new bar
    new_bar = wait_for_next_bar()

    # Incremental update
    indicators = pipeline.update(new_bar)

    # Generate and execute signals
    signals = strategy.generate_signals(indicators)
    for signal in signals:
        if risk_limits.check(signal):
            executor.execute(signal)
```

---

## 10. Configuration

Indicators are configured programmatically:

```python
# Preferred: Explicit object creation
pipeline = IndicatorPipeline()
pipeline.add_indicator('sma_20', SMAIndicator(period=20))
pipeline.add_indicator('rsi_14', RSIIndicator(period=14))

# Column naming: single indicator
# Result column: 'sma_20', 'rsi_14'

# Multi-output indicator (MACD)
# Result columns: 'macd_macd', 'macd_signal_line', 'macd_histogram'
```

---

## 11. Future Extensibility

### 11.1 Adding Custom Indicators

```python
# Users can create custom indicators by extending BaseIndicator
class MyCustomIndicator(BaseIndicator):
    def calculate(self, df: DataFrame) -> Series:
        # Custom calculation
        return df['close'] * 2  # Silly example

    def required_period(self) -> int:
        return 1

# Use in pipeline
pipeline.add_indicator('custom', MyCustomIndicator())
```

### 11.2 Indicator Composition

Indicators can use other indicators as input:

```python
# Example: RSI of SMA (oscillating indicator of trend)
class RSIofSMA(BaseIndicator):
    def __init__(self, sma_period: int = 20, rsi_period: int = 14):
        self.sma = SMAIndicator(period=sma_period)
        self.rsi = RSIIndicator(period=rsi_period)

    def calculate(self, df: DataFrame) -> Series:
        sma_values = self.sma.calculate(df)
        # Create temporary DataFrame for RSI calculation
        temp_df = DataFrame({'close': sma_values})
        return self.rsi.calculate(temp_df)

    def required_period(self) -> int:
        return self.sma.required_period() + self.rsi.required_period()
```

---

## 12. Success Criteria

- [ ] All 6 indicators implemented (SMA, EMA, RSI, MACD, BB, ATR) using pure pandas/numpy
- [ ] IndicatorPipeline supports batch and incremental modes
- [ ] Caching works correctly
- [ ] Bar→DataFrame converter handles Decimal to float conversion
- [ ] Unit tests pass with 80%+ coverage
- [ ] Integration tests pass
- [ ] Documentation complete
- [ ] Ready for Phase 2 (Strategy Management)

---

## 13. Open Questions

None at this time.

---

## 14. Change Log

| Date | Change |
|------|--------|
| 2026-03-14 | Initial design document |
| 2026-03-14 | Revised v2: Fixed critical issues per spec review |
| 2026-03-14 | Changed from TA-Lib to pure pandas/numpy implementation |
| 2026-03-14 | Added Bar→DataFrame converter specification |
| 2026-03-14 | Clarified incremental mode implementation |
| 2026-03-14 | Added caching implementation details |
| 2026-03-14 | Added input validation rules |
| 2026-03-14 | Specified multi-column indicator naming convention |
| 2026-03-14 | Added performance considerations |
| 2026-03-14 | Fixed type hint consistency |
