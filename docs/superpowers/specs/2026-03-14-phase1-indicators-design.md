# Phase 1: Technical Indicators Framework - Design Document

**Date:** 2026-03-14
**Status:** Proposed
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

### 1.3 Out of Scope

- Strategy implementation (Phase 2)
- Backtesting engine (Phase 3)
- Live trading execution logic

---

## 2. Architecture

### 2.1 Component Diagram

```
Provider (Bar data)
    ↓
Data Utilities (Bar→DataFrame)
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
│   ├── moving_avg.py        # SMA, EMA
│   ├── momentum.py          # RSI, MACD
│   ├── volatility.py        # Bollinger Bands, ATR
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
        └── test_pipeline.py
```

---

## 3. Core API Design

### 3.1 BaseIndicator (Abstract Class)

```python
class BaseIndicator(ABC):
    """Base class for all technical indicators."""

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.Series | pd.DataFrame:
        """Calculate indicator values.

        Args:
            df: DataFrame with 'close', 'high', 'low', 'volume' columns

        Returns:
            pd.Series or pd.DataFrame: Indicator values
        """
        pass

    @abstractmethod
    def required_period(self) -> int:
        """Return minimum bars needed for calculation."""
        pass
```

### 3.2 IndicatorPipeline

```python
class IndicatorPipeline:
    """Main pipeline for computing technical indicators.

    Features:
    - Batch computation (backtesting)
    - Incremental updates (real-time)
    - Caching (avoid re-computation)
    """

    def add_indicator(self, name: str, indicator: BaseIndicator) -> None
    def remove_indicator(self, name: str) -> None
    def compute(self, bars: List[Bar]) -> pd.DataFrame
    def update(self, new_bar: Bar) -> pd.Series
```

### 3.3 Usage Example

```python
# Setup
pipeline = IndicatorPipeline()
pipeline.add_indicator('sma_20', SMAIndicator(period=20))
pipeline.add_indicator('rsi_14', RSIIndicator(period=14))

# Batch mode (backtesting)
bars = provider.get_historical_bars('AAPL', start, end)
df = pipeline.compute(bars)

# Real-time mode
latest = pipeline.update(new_bar)
```

---

## 4. Indicator Specifications

### 4.1 Moving Averages

| Indicator | Parameters | Output | Use Case |
|-----------|-----------|--------|----------|
| SMA | period (default: 20) | Series | Trend identification, S/R levels |
| EMA | period (default: 20) | Series | Trend (weights recent data more) |

### 4.2 Momentum

| Indicator | Parameters | Output | Use Case |
|-----------|-----------|--------|----------|
| RSI | period (default: 14) | Series | Overbought/oversold (>70/<30) |
| MACD | fast=12, slow=26, signal=9 | DataFrame (3 cols) | Reversal signals |

### 4.3 Volatility

| Indicator | Parameters | Output | Use Case |
|-----------|-----------|--------|----------|
| Bollinger Bands | period=20, std_dev=2.0 | DataFrame (4 cols) | Volatility, breakouts |
| ATR | period (default: 14) | Series | Volatility, stop loss |

---

## 5. Error Handling

### 5.1 Exception Types

- `IndicatorError`: Base exception
- `InsufficientDataError`: Not enough bars to compute
- `InvalidInputError`: Input data missing required columns

### 5.2 Error Handling Strategy

1. Validate input before computation
2. Check minimum data requirements
3. Track failed indicators (log warning, continue)
4. Re-raise critical errors for caller to handle

---

## 6. Testing Strategy

### 6.1 Unit Tests

- Test each indicator independently
- Verify calculations with known values
- Test edge cases (insufficient data, empty input)

### 6.2 Integration Tests

- Test Pipeline with multiple indicators
- Test batch vs incremental modes
- Test caching behavior

### 6.3 Test Coverage Target

- Minimum: 80%
- Preferred: 90%+

---

## 7. Dependencies

```toml
[project.dependencies]
pandas = ">=2.0.0"
numpy = ">=1.24.0"
TA-Lib = ">=0.4.28"

[project.optional-dependencies]
indicators = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "ta>=0.11.0",  # Fallback if TA-Lib unavailable
]
```

---

## 8. Integration Points

### 8.1 With Strategy (Phase 2)

```python
class MyStrategy(BaseStrategy):
    def __init__(self, provider):
        self.pipeline = IndicatorPipeline()
        # Add indicators...

    def generate_signals(self) -> list[Signal]:
        df = self.pipeline.compute(bars)
        # Generate signals from indicator values...
```

### 8.2 With Main Loop (Future)

```python
# In main trading loop
while True:
    bars = provider.get_historical_bars(...)
    indicators = pipeline.compute(bars)
    signals = strategy.generate_signals(indicators)
    # Execute...
```

---

## 9. Success Criteria

- [ ] All 6 indicators implemented (SMA, EMA, RSI, MACD, BB, ATR)
- [ ] IndicatorPipeline supports batch and incremental modes
- [ ] Caching works correctly
- [ ] Unit tests pass with 80%+ coverage
- [ ] Integration tests pass
- [ ] Documentation complete
- [ ] Ready for Phase 2 (Strategy Management)

---

## 10. Open Questions

None at this time.

---

## 11. Change Log

| Date | Change |
|------|--------|
| 2026-03-14 | Initial design document |
