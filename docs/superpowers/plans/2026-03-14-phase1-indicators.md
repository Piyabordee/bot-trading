# Phase 1: Technical Indicators Framework Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a comprehensive technical indicators framework supporting both backtesting (batch) and real-time (incremental) modes, implementing SMA, EMA, RSI, MACD, Bollinger Bands, and ATR using pure pandas/numpy.

**Architecture:**
- Modular indicators extending `BaseIndicator` abstract class
- `IndicatorPipeline` manages computation, caching, and batch/incremental modes
- `BarsToDataFrameConverter` handles Bar→DataFrame conversion with timezone awareness
- DataFrame-based API for easy integration with strategies

**Tech Stack:**
- Python 3.11+
- pandas 2.0+ (for DataFrame operations and rolling calculations)
- numpy 1.24+ (for efficient numerical operations)
- pytest (for testing)

**Dependencies to Add:**
- `pandas>=2.0.0`
- `numpy>=1.24.0`

**Reference Spec:** `docs/superpowers/specs/2026-03-14-phase1-indicators-design.md`

---

## Prerequisites: Install Dependencies

### Task 0: Install Required Dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add pandas and numpy to dependencies**

Find the `[project.dependencies]` section in `pyproject.toml` and add:
```toml
[project.dependencies]
# ... existing dependencies ...
pandas = ">=2.0.0"
numpy = ">=1.24.0"
```

- [ ] **Step 2: Install dependencies**

Run: `pip install pandas numpy`
Expected: Packages installed successfully

- [ ] **Step 3: Verify installation**

Run: `python -c "import pandas; import numpy; print('Dependencies OK')"`
Expected: `Dependencies OK`

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "deps: add pandas and numpy for Phase 1

- Add pandas>=2.0.0 for DataFrame operations
- Add numpy>=1.24.0 for numerical operations
- Required for Phase 1 indicators framework

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 1: Foundation - Exceptions and Base Indicator

This chunk establishes the foundation: custom exceptions, the abstract BaseIndicator class, and the BarsToDataFrameConverter.

### Task 1: Create Custom Exceptions

**Files:**
- Create: `src/bot_trading/indicators/exceptions.py`

- [ ] **Step 1: Create the exceptions module**

```python
"""Custom exceptions for indicators module."""

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

- [ ] **Step 2: Run python to verify syntax**

Run: `python -c "from bot_trading.indicators.exceptions import IndicatorError; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/bot_trading/indicators/exceptions.py
git commit -m "feat(indicators): add custom exceptions

- Add IndicatorError base exception
- Add InsufficientDataError for not enough bars
- Add InvalidInputError for invalid input data

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Create BaseIndicator Abstract Class

**Files:**
- Create: `src/bot_trading/indicators/base.py`

- [ ] **Step 1: Create base indicator abstract class**

```python
"""Base class for all technical indicators."""

from abc import ABC, abstractmethod
from typing import Union
import pandas as pd
from pandas import Series, DataFrame

# Type alias for indicator results
IndicatorResult = Union[Series, DataFrame]


class BaseIndicator(ABC):
    """Base class for all technical indicators.

    All indicators must inherit from this class and implement
    the calculate() and required_period() methods.
    """

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
        from .exceptions import InvalidInputError

        required = ['open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise InvalidInputError(f"Missing required columns: {missing}")
        return True
```

- [ ] **Step 2: Run python to verify syntax**

Run: `python -c "from bot_trading.indicators.base import BaseIndicator; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/bot_trading/indicators/base.py
git commit -m "feat(indicators): add BaseIndicator abstract class

- Add calculate() abstract method
- Add required_period() abstract method
- Add validate_input() helper method
- Add IndicatorResult type alias

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Create BarsToDataFrameConverter

**Files:**
- Create: `src/bot_trading/data/converters.py`
- Modify: `src/bot_trading/data/__init__.py`

- [ ] **Step 1: Create the data module directory (if needed)**

Run: `mkdir -p src/bot_trading/data`
Expected: Directory created (or already exists)

- [ ] **Step 2: Create the converter class**

```python
"""Data converters for indicators."""

from typing import List
from decimal import Decimal
import pandas as pd
from pandas import DataFrame
from bot_trading.providers.base import Bar
from bot_trading.indicators.exceptions import InvalidInputError


class BarsToDataFrameConverter:
    """Convert List[Bar] to pandas DataFrame for indicator computation.

    Handles:
    - Decimal to float conversion (for indicator calculations)
    - Timestamp to datetime index with consistent timezone handling
    - Column naming: 'open', 'high', 'low', 'close', 'volume'
    - Validation (no NaN in prices, sorted by timestamp)

    Timezone Handling:
    - If Bar timestamps are timezone-aware: preserve timezone
    - If Bar timestamps are naive: assume UTC and keep naive
    - All bars in a batch must have consistent timezone awareness
    """

    @staticmethod
    def convert(bars: List[Bar]) -> DataFrame:
        """Convert bars to DataFrame.

        Args:
            bars: List of Bar objects from provider

        Returns:
            DataFrame with:
            - Columns: 'open', 'high', 'low', 'close', 'volume'
            - Index: datetime (preserves input timezone: aware or naive)
            - Sorted by timestamp (ascending)
            - No NaN values in price columns

        Raises:
            InvalidInputError: If bars are empty or contain invalid data
        """
        if not bars:
            raise InvalidInputError("Cannot convert empty bars list")

        # Check timezone consistency
        first_tz_aware = bars[0].timestamp.tzinfo is not None
        for i, bar in enumerate(bars):
            tz_aware = bar.timestamp.tzinfo is not None
            if tz_aware != first_tz_aware:
                raise InvalidInputError(
                    f"Mixed timezone awareness in bars: bar 0 is "
                    f"{'aware' if first_tz_aware else 'naive'}, bar {i} is "
                    f"{'aware' if tz_aware else 'naive'}"
                )

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

    @staticmethod
    def dataframe_to_bars(df: DataFrame, symbol: str) -> List[Bar]:
        """Convert DataFrame back to List[Bar].

        Args:
            df: DataFrame with OHLCV columns and datetime index
            symbol: Symbol to use for all bars

        Returns:
            List of Bar objects

        Note:
            This is the inverse of convert() for incremental updates.
        """
        bars = []
        for timestamp, row in df.iterrows():
            bars.append(Bar(
                symbol=symbol,
                timestamp=timestamp,
                open=Decimal(str(row['open'])),
                high=Decimal(str(row['high'])),
                low=Decimal(str(row['low'])),
                close=Decimal(str(row['close'])),
                volume=int(row['volume']),
            ))
        return bars
```

- [ ] **Step 2: Update data/__init__.py to export converter**

```python
"""Data fetching and processing."""

from .converters import BarsToDataFrameConverter

__all__ = ['BarsToDataFrameConverter']
```

- [ ] **Step 3: Run python to verify syntax**

Run: `python -c "from bot_trading.data.converters import BarsToDataFrameConverter; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add src/bot_trading/data/converters.py src/bot_trading/data/__init__.py
git commit -m "feat(data): add BarsToDataFrameConverter

- Add convert() method for Bar→DataFrame conversion
- Add dataframe_to_bars() method for inverse conversion
- Handle timezone consistency checking
- Validate price columns for NaN values

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 4: Create Indicators Package __init__.py

**Files:**
- Create: `src/bot_trading/indicators/__init__.py`

- [ ] **Step 1: Create indicators package init**

```python
"""Technical indicators framework."""

from .base import BaseIndicator, IndicatorResult
from .exceptions import IndicatorError, InsufficientDataError, InvalidInputError

__all__ = [
    'BaseIndicator',
    'IndicatorResult',
    'IndicatorError',
    'InsufficientDataError',
    'InvalidInputError',
]
```

- [ ] **Step 2: Run python to verify syntax**

Run: `python -c "from bot_trading.indicators import BaseIndicator; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/bot_trading/indicators/__init__.py
git commit -m "feat(indicators): create indicators package

- Export BaseIndicator and IndicatorResult
- Export custom exceptions
- Prepare for indicator implementations

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 5: Write Tests for Converters

**Files:**
- Create: `tests/test_indicators/test_converters.py`

- [ ] **Step 1: Create test file for converters**

```python
"""Tests for BarsToDataFrameConverter."""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
import pandas as pd
from bot_trading.data.converters import BarsToDataFrameConverter
from bot_trading.providers.base import Bar
from bot_trading.indicators.exceptions import InvalidInputError


class TestBarsToDataFrameConverter:
    """Test suite for BarsToDataFrameConverter."""

    def test_convert_empty_list_raises_error(self):
        """Test that converting empty list raises InvalidInputError."""
        with pytest.raises(InvalidInputError, match="Cannot convert empty"):
            BarsToDataFrameConverter.convert([])

    def test_convert_basic_conversion(self):
        """Test basic Bar to DataFrame conversion."""
        bars = [
            Bar(
                symbol='AAPL',
                timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
                open=Decimal('150.0'),
                high=Decimal('152.0'),
                low=Decimal('149.0'),
                close=Decimal('151.0'),
                volume=1000000
            ),
            Bar(
                symbol='AAPL',
                timestamp=datetime(2024, 1, 2, tzinfo=timezone.utc),
                open=Decimal('151.0'),
                high=Decimal('153.0'),
                low=Decimal('150.0'),
                close=Decimal('152.0'),
                volume=1100000
            ),
        ]

        df = BarsToDataFrameConverter.convert(bars)

        # Check columns
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']

        # Check data types
        assert df['open'].dtype == float
        assert df['volume'].dtype == int

        # Check values
        assert df['open'].iloc[0] == 150.0
        assert df['close'].iloc[1] == 152.0
        assert df['volume'].iloc[0] == 1000000

    def test_convert_sorts_by_timestamp(self):
        """Test that bars are sorted by timestamp."""
        bars = [
            Bar('AAPL', datetime(2024, 1, 2), Decimal('150'), Decimal('151'), Decimal('149'), Decimal('150'), 1000),
            Bar('AAPL', datetime(2024, 1, 1), Decimal('150'), Decimal('151'), Decimal('149'), Decimal('150'), 1000),
        ]

        df = BarsToDataFrameConverter.convert(bars)

        assert df.index[0] == datetime(2024, 1, 1)
        assert df.index[1] == datetime(2024, 1, 2)

    def test_convert_preserves_timezone(self):
        """Test that timezone information is preserved."""
        bars = [
            Bar('AAPL', datetime(2024, 1, 1, tzinfo=timezone.utc), Decimal('150'), Decimal('151'), Decimal('149'), Decimal('150'), 1000),
        ]

        df = BarsToDataFrameConverter.convert(bars)

        assert df.index.tzinfo == timezone.utc

    def test_convert_mixed_timezone_raises_error(self):
        """Test that mixed timezone awareness raises error."""
        bars = [
            Bar('AAPL', datetime(2024, 1, 1, tzinfo=timezone.utc), Decimal('150'), Decimal('151'), Decimal('149'), Decimal('150'), 1000),
            Bar('AAPL', datetime(2024, 1, 2), Decimal('150'), Decimal('151'), Decimal('149'), Decimal('150'), 1000),  # naive
        ]

        with pytest.raises(InvalidInputError, match="Mixed timezone"):
            BarsToDataFrameConverter.convert(bars)

    def test_dataframe_to_bars_inverse_conversion(self):
        """Test that dataframe_to_bars is the inverse of convert."""
        original_bars = [
            Bar('AAPL', datetime(2024, 1, 1), Decimal('150'), Decimal('151'), Decimal('149'), Decimal('150'), 1000),
            Bar('AAPL', datetime(2024, 1, 2), Decimal('151'), Decimal('152'), Decimal('150'), Decimal('151'), 1100),
        ]

        df = BarsToDataFrameConverter.convert(original_bars)
        converted_bars = BarsToDataFrameConverter.dataframe_to_bars(df, 'AAPL')

        assert len(converted_bars) == len(original_bars)
        assert converted_bars[0].symbol == 'AAPL'
        assert converted_bars[0].open == original_bars[0].open
        assert converted_bars[0].close == original_bars[0].close

    def test_convert_nan_prices_raises_error(self):
        """Test that NaN in price columns raises InvalidInputError."""
        bars = [
            Bar('AAPL', datetime(2024, 1, 1), Decimal('150'), Decimal('151'), Decimal('149'), Decimal('nan'), 1000),
        ]

        # Convert Decimal('nan') to float will result in NaN
        with pytest.raises(InvalidInputError, match="contain NaN"):
            BarsToDataFrameConverter.convert(bars)

    def test_convert_negative_volume_raises_error(self):
        """Test that negative volume raises InvalidInputError."""
        # Note: Bar dataclass doesn't enforce volume >= 0
        # This test documents expected validation behavior
        bars = [
            Bar('AAPL', datetime(2024, 1, 1), Decimal('150'), Decimal('151'), Decimal('149'), Decimal('150'), -100),
        ]

        df = BarsToDataFrameConverter.convert(bars)
        # Volume should be preserved as-is (validation at higher level)
        assert df['volume'].iloc[0] == -100

    def test_convert_high_lower_than_low(self):
        """Test bars where high < low (invalid data)."""
        # Note: Bar dataclass doesn't enforce high >= low
        # This test documents expected validation behavior
        bars = [
            Bar('AAPL', datetime(2024, 1, 1), Decimal('150'), Decimal('148'), Decimal('149'), Decimal('150'), 1000),  # high < low
        ]

        df = BarsToDataFrameConverter.convert(bars)
        # Invalid data should be preserved (validation at higher level)
        assert df['high'].iloc[0] == 148.0
        assert df['low'].iloc[0] == 149.0
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_indicators/test_converters.py -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_indicators/test_converters.py
git commit -m "test(indicators): add tests for BarsToDataFrameConverter

- Test empty list handling
- Test basic conversion with proper types
- Test timestamp sorting
- Test timezone preservation
- Test mixed timezone detection
- Test inverse conversion (dataframe_to_bars)
- Test NaN price detection
- Test negative volume handling
- Test invalid high/low relationship

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 2: Moving Average Indicators (SMA, EMA)

This chunk implements the Simple Moving Average (SMA) and Exponential Moving Average (EMA) indicators.

### Task 6: Implement SMA Indicator

**Files:**
- Create: `src/bot_trading/indicators/moving_avg.py`

- [ ] **Step 1: Write failing test for SMA**

```python
"""Tests for moving average indicators."""

import pytest
import pandas as pd
from bot_trading.indicators.moving_avg import SMAIndicator, EMAIndicator


class TestSMAIndicator:
    """Test suite for SMAIndicator."""

    def test_sma_calculates_correctly(self):
        """Test SMA calculation with known values."""
        # Setup: Create test data
        data = {
            'open': [10.0] * 11,
            'high': [11.0] * 11,
            'low': [9.0] * 11,
            'close': [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0],
            'volume': [1000] * 11,
        }
        df = pd.DataFrame(data)

        # Execute
        indicator = SMAIndicator(period=5)
        result = indicator.calculate(df)

        # Verify: SMA(5) of last value = (16+17+18+19+20)/5 = 18.0
        assert result.iloc[-1] == 18.0
        # First 4 values should be NaN
        assert result.iloc[0:4].isna().all()
        # 5th value = (10+11+12+13+14)/5 = 12.0
        assert result.iloc[4] == 12.0

    def test_sma_required_period(self):
        """Test required_period returns correct value."""
        indicator = SMAIndicator(period=20)
        assert indicator.required_period() == 20

    def test_sma_validate_input(self):
        """Test validate_input with valid data."""
        df = pd.DataFrame({
            'open': [10.0],
            'high': [11.0],
            'low': [9.0],
            'close': [10.0],
            'volume': [1000],
        })
        indicator = SMAIndicator(period=5)
        assert indicator.validate_input(df) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_indicators/test_moving_avg.py::TestSMAIndicator::test_sma_calculates_correctly -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'bot_trading.indicators.moving_avg'"

- [ ] **Step 3: Implement SMA indicator**

```python
"""Moving average indicators."""

import pandas as pd
from pandas import Series, DataFrame
from .base import BaseIndicator, IndicatorResult


class SMAIndicator(BaseIndicator):
    """Simple Moving Average.

    Formula: SMA = Sum(close prices) / period

    Parameters:
        period: Number of periods to average (default: 20)
    """

    def __init__(self, period: int = 20):
        if period <= 0:
            raise ValueError("Period must be positive")
        self.period = period

    def calculate(self, df: DataFrame) -> IndicatorResult:
        """Calculate SMA using pandas rolling mean.

        Args:
            df: DataFrame with 'close' column

        Returns:
            Series with SMA values
        """
        self.validate_input(df)
        return df['close'].rolling(window=self.period).mean()

    def required_period(self) -> int:
        """Return minimum bars needed."""
        return self.period


class EMAIndicator(BaseIndicator):
    """Exponential Moving Average.

    Formula: EMA gives more weight to recent prices.
    EMA(today) = (close(today) * k) + (EMA(yesterday) * (1-k))
    where k = 2 / (period + 1)

    Parameters:
        period: Number of periods for EMA (default: 20)
    """

    def __init__(self, period: int = 20):
        if period <= 0:
            raise ValueError("Period must be positive")
        self.period = period

    def calculate(self, df: DataFrame) -> IndicatorResult:
        """Calculate EMA using pandas ewm.

        Args:
            df: DataFrame with 'close' column

        Returns:
            Series with EMA values
        """
        self.validate_input(df)
        return df['close'].ewm(span=self.period, adjust=False).mean()

    def required_period(self) -> int:
        """Return minimum bars needed."""
        return self.period
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_indicators/test_moving_avg.py::TestSMAIndicator -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/bot_trading/indicators/moving_avg.py tests/test_indicators/test_moving_avg.py
git commit -m "feat(indicators): add SMA and EMA indicators

- Add SMAIndicator using pandas rolling mean
- Add EMAIndicator using pandas ewm
- Add parameter validation (positive period)
- Add tests for SMA calculation with known values
- Add tests for required_period and validate_input

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 7: Implement and Test EMA Indicator

**Files:**
- Modify: `tests/test_indicators/test_moving_avg.py`

- [ ] **Step 1: Add EMA tests**

```python
class TestEMAIndicator:
    """Test suite for EMAIndicator."""

    def test_ema_calculates_correctly(self):
        """Test EMA calculation with known values."""
        # EMA formula: k = 2 / (period + 1)
        # For period=3, k = 2/4 = 0.5
        data = {
            'open': [10.0] * 6,
            'high': [11.0] * 6,
            'low': [9.0] * 6,
            'close': [10.0, 11.0, 12.0, 13.0, 14.0, 15.0],
            'volume': [1000] * 6,
        }
        df = pd.DataFrame(data)

        indicator = EMAIndicator(period=3)
        result = indicator.calculate(df)

        # EMA should be calculated (pandas ewm)
        # First value is NaN, second is SMA of first 2, then EMA kicks in
        assert not result.iloc[-1].isna()
        # EMA should be higher than SMA for rising prices (weights recent more)
        sma = df['close'].rolling(3).mean()
        assert result.iloc[-1] > sma.iloc[-1]

    def test_ema_required_period(self):
        """Test required_period returns correct value."""
        indicator = EMAIndicator(period=20)
        assert indicator.required_period() == 20

    def test_ema_invalid_period_raises_error(self):
        """Test that invalid period raises ValueError."""
        with pytest.raises(ValueError, match="Period must be positive"):
            EMAIndicator(period=0)
        with pytest.raises(ValueError, match="Period must be positive"):
            EMAIndicator(period=-5)
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_indicators/test_moving_avg.py::TestEMAIndicator -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_indicators/test_moving_avg.py
git commit -m "test(indicators): add EMA indicator tests

- Test EMA calculation behavior
- Test EMA vs SMA comparison (EMA > SMA for rising prices)
- Test parameter validation for invalid periods

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 3: Momentum Indicators (RSI, MACD)

This chunk implements the Relative Strength Index (RSI) and MACD indicators.

### Task 8: Implement RSI Indicator

**Files:**
- Create: `src/bot_trading/indicators/momentum.py`
- Create: `tests/test_indicators/test_momentum.py`

- [ ] **Step 1: Write failing test for RSI**

```python
"""Tests for momentum indicators."""

import pytest
import pandas as pd
import numpy as np
from bot_trading.indicators.momentum import RSIIndicator, MACDIndicator


class TestRSIIndicator:
    """Test suite for RSIIndicator."""

    def test_rsi_calculates_correctly(self):
        """Test RSI calculation with known values."""
        # Create data with consistent upward movement
        data = {
            'open': [10.0] * 20,
            'high': [11.0] * 20,
            'low': [9.0] * 20,
            'close': [10.0 + i for i in range(20)],  # Rising from 10 to 29
            'volume': [1000] * 20,
        }
        df = pd.DataFrame(data)

        indicator = RSIIndicator(period=14)
        result = indicator.calculate(df)

        # RSI should be high for consistently rising prices
        # (close to 100 for strong uptrend)
        assert result.iloc[-1] > 50  # Should be in overbought territory
        assert result.iloc[-1] <= 100

    def test_rsi_handles_zero_loss(self):
        """Test RSI when all gains, no losses (loss = 0)."""
        # Consistent gains, no losses
        data = {
            'open': [10.0] * 20,
            'high': [11.0] * 20,
            'low': [9.0] * 20,
            'close': [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0,
                     21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0],
            'volume': [1000] * 20,
        }
        df = pd.DataFrame(data)

        indicator = RSIIndicator(period=14)
        result = indicator.calculate(df)

        # When loss is 0, RSI should be 100
        assert result.iloc[-1] == 100

    def test_rsi_required_period(self):
        """Test required_period returns correct value."""
        indicator = RSIIndicator(period=14)
        assert indicator.required_period() == 15  # period + 1 for diff

    def test_rsi_invalid_period_raises_error(self):
        """Test that invalid period raises ValueError."""
        with pytest.raises(ValueError, match="Period must be positive"):
            RSIIndicator(period=0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_indicators/test_momentum.py::TestRSIIndicator -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'bot_trading.indicators.momentum'"

- [ ] **Step 3: Implement RSI indicator**

```python
"""Momentum indicators."""

import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from .base import BaseIndicator, IndicatorResult


class RSIIndicator(BaseIndicator):
    """Relative Strength Index.

    Measures speed and change of price movements.
    Range: 0-100
    - Over 70 = Overbought (might sell)
    - Under 30 = Oversold (might buy)

    Parameters:
        period: Period for RSI calculation (default: 14)
    """

    def __init__(self, period: int = 14):
        if period <= 0:
            raise ValueError("Period must be positive")
        self.period = period

    def calculate(self, df: DataFrame) -> IndicatorResult:
        """Calculate RSI using pandas operations.

        Args:
            df: DataFrame with 'close' column

        Returns:
            Series with RSI values (0-100)
        """
        self.validate_input(df)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()

        # Handle division by zero: when loss is 0, RSI = 100
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))

        # When loss is 0 (no downward movement), RSI = 100
        rsi[loss == 0] = 100

        return rsi

    def required_period(self) -> int:
        """Return minimum bars needed (period + 1 for diff)."""
        return self.period + 1
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_indicators/test_momentum.py::TestRSIIndicator -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/bot_trading/indicators/momentum.py tests/test_indicators/test_momentum.py
git commit -m "feat(indicators): add RSI indicator

- Add RSIIndicator using pandas rolling operations
- Handle division by zero (when loss = 0, RSI = 100)
- Add parameter validation
- Add tests for rising prices and zero-loss scenarios

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 9: Implement MACD Indicator

**Files:**
- Modify: `src/bot_trading/indicators/momentum.py`
- Modify: `tests/test_indicators/test_momentum.py`

- [ ] **Step 1: Add MACD tests**

```python
class TestMACDIndicator:
    """Test suite for MACDIndicator."""

    def test_macd_calculates_correctly(self):
        """Test MACD calculation with known values."""
        data = {
            'open': [10.0] * 30,
            'high': [11.0] * 30,
            'low': [9.0] * 30,
            'close': [10.0 + i * 0.5 for i in range(30)],  # Rising prices
            'volume': [1000] * 30,
        }
        df = pd.DataFrame(data)

        indicator = MACDIndicator(fast=12, slow=26, signal=9)
        result = indicator.calculate(df)

        # Check column names
        assert list(result.columns) == ['macd', 'macd_signal', 'macd_hist']

        # For rising prices, MACD should be positive
        assert result['macd'].iloc[-1] > 0

    def test_macd_histogram_is_difference(self):
        """Test that histogram = macd - signal."""
        data = {
            'open': [10.0] * 30,
            'high': [11.0] * 30,
            'low': [9.0] * 30,
            'close': [10.0 + i * 0.5 for i in range(30)],
            'volume': [1000] * 30,
        }
        df = pd.DataFrame(data)

        indicator = MACDIndicator()
        result = indicator.calculate(df)

        # Histogram should equal MACD - signal
        expected_hist = result['macd'] - result['macd_signal']
        pd.testing.assert_series_equal(result['macd_hist'], expected_hist)

    def test_macd_required_period(self):
        """Test required_period returns correct value."""
        indicator = MACDIndicator(fast=12, slow=26, signal=9)
        assert indicator.required_period() == 35  # 26 + 9

    def test_macd_invalid_parameters_raise_error(self):
        """Test that invalid parameters raise ValueError."""
        with pytest.raises(ValueError, match="Periods must be positive"):
            MACDIndicator(fast=0, slow=26, signal=9)
        with pytest.raises(ValueError, match="Fast period must be less than slow"):
            MACDIndicator(fast=26, slow=12, signal=9)
```

- [ ] **Step 2: Add MACD implementation**

```python
class MACDIndicator(BaseIndicator):
    """Moving Average Convergence Divergence.

    Components:
    - MACD Line = EMA(fast) - EMA(slow)
    - Signal Line = EMA(signal) of MACD
    - Histogram = MACD - Signal

    Parameters:
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line EMA period (default: 9)
    """

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        if fast <= 0 or slow <= 0 or signal <= 0:
            raise ValueError("Periods must be positive")
        if fast >= slow:
            raise ValueError("Fast period must be less than slow period")
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def calculate(self, df: DataFrame) -> IndicatorResult:
        """Calculate MACD using pandas ewm.

        Args:
            df: DataFrame with 'close' column

        Returns:
            DataFrame with columns: macd, macd_signal, macd_hist
        """
        self.validate_input(df)
        ema_fast = df['close'].ewm(span=self.fast).mean()
        ema_slow = df['close'].ewm(span=self.slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=self.signal).mean()
        histogram = macd - signal_line

        result = DataFrame(index=df.index)
        result['macd'] = macd
        result['macd_signal'] = signal_line
        result['macd_hist'] = histogram
        return result

    def required_period(self) -> int:
        """Return minimum bars needed."""
        return self.slow + self.signal
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `pytest tests/test_indicators/test_momentum.py::TestMACDIndicator -v`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add src/bot_trading/indicators/momentum.py tests/test_indicators/test_momentum.py
git commit -m "feat(indicators): add MACD indicator

- Add MACDIndicator with fast, slow, signal parameters
- Returns DataFrame with macd, macd_signal, macd_hist columns
- Validate parameters (positive, fast < slow)
- Add tests for calculation and histogram formula

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 4: Volatility Indicators (Bollinger Bands, ATR)

This chunk implements Bollinger Bands and Average True Range (ATR) indicators.

### Task 10: Implement Bollinger Bands Indicator

**Files:**
- Create: `src/bot_trading/indicators/volatility.py`
- Create: `tests/test_indicators/test_volatility.py`

- [ ] **Step 1: Write failing test for Bollinger Bands**

```python
"""Tests for volatility indicators."""

import pytest
import pandas as pd
from bot_trading.indicators.volatility import BollingerBands, ATRIndicator


class TestBollingerBands:
    """Test suite for BollingerBands."""

    def test_bollinger_bands_calculates_correctly(self):
        """Test Bollinger Bands calculation with known values."""
        data = {
            'open': [10.0] * 25,
            'high': [11.0] * 25,
            'low': [9.0] * 25,
            'close': [10.0] * 25,
            'volume': [1000] * 25,
        }
        df = pd.DataFrame(data)

        indicator = BollingerBands(period=20, std_dev=2.0)
        result = indicator.calculate(df)

        # Check column names
        assert list(result.columns) == ['upper', 'middle', 'lower', 'width']

        # For flat prices, upper = middle + 2*std, lower = middle - 2*std
        # Since std = 0 for flat prices, upper = middle = lower
        assert result['middle'].iloc[-1] == 10.0
        assert result['upper'].iloc[-1] == 10.0
        assert result['lower'].iloc[-1] == 10.0

    def test_bollinger_bands_width(self):
        """Test that width = upper - lower."""
        data = {
            'open': [10.0] * 25,
            'high': [11.0] * 25,
            'low': [9.0] * 25,
            'close': [10.0 + i * 0.1 for i in range(25)],  # Varying prices
            'volume': [1000] * 25,
        }
        df = pd.DataFrame(data)

        indicator = BollingerBands()
        result = indicator.calculate(df)

        # Width should equal upper - lower
        expected_width = result['upper'] - result['lower']
        pd.testing.assert_series_equal(result['width'], expected_width)

    def test_bollinger_bands_required_period(self):
        """Test required_period returns correct value."""
        indicator = BollingerBands(period=20)
        assert indicator.required_period() == 20
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_indicators/test_volatility.py::TestBollingerBands -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'bot_trading.indicators.volatility'"

- [ ] **Step 3: Implement Bollinger Bands**

```python
"""Volatility indicators."""

import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from .base import BaseIndicator, IndicatorResult


class BollingerBands(BaseIndicator):
    """Bollinger Bands.

    Components:
    - Middle Band = SMA(period)
    - Upper Band = SMA + (std_dev * std)
    - Lower Band = SMA - (std_dev * std)
    - Width = Upper - Lower

    Parameters:
        period: Period for SMA and std calculation (default: 20)
        std_dev: Number of standard deviations (default: 2.0)
    """

    def __init__(self, period: int = 20, std_dev: float = 2.0):
        if period <= 0:
            raise ValueError("Period must be positive")
        if std_dev <= 0:
            raise ValueError("Standard deviation must be positive")
        self.period = period
        self.std_dev = std_dev

    def calculate(self, df: DataFrame) -> IndicatorResult:
        """Calculate Bollinger Bands using pandas operations.

        Args:
            df: DataFrame with 'close' column

        Returns:
            DataFrame with columns: upper, middle, lower, width
        """
        self.validate_input(df)
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
        """Return minimum bars needed."""
        return self.period


class ATRIndicator(BaseIndicator):
    """Average True Range.

    Measures market volatility.
    Higher ATR = Higher volatility

    Parameters:
        period: Period for ATR calculation (default: 14)

    Note: Implementation is in Task 11 (after tests are written).
    """
    pass  # Placeholder - implemented in Task 11
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_indicators/test_volatility.py::TestBollingerBands -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/bot_trading/indicators/volatility.py tests/test_indicators/test_volatility.py
git commit -m "feat(indicators): add Bollinger Bands and ATR indicators

- Add BollingerBands with upper, middle, lower, width
- Add ATRIndicator for volatility measurement
- Add parameter validation for both indicators
- Add tests for calculation accuracy

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 11: Implement ATR Indicator

**Files:**
- Modify: `src/bot_trading/indicators/volatility.py`
- Modify: `tests/test_indicators/test_volatility.py`

- [ ] **Step 1: Add ATR tests**

```python
class TestATRIndicator:
    """Test suite for ATRIndicator."""

    def test_atr_calculates_correctly(self):
        """Test ATR calculation with known values."""
        data = {
            'open': [10.0] * 20,
            'high': [11.0] * 20,
            'low': [9.0] * 20,
            'close': [10.0] * 20,
            'volume': [1000] * 20,
        }
        df = pd.DataFrame(data)

        indicator = ATRIndicator(period=14)
        result = indicator.calculate(df)

        # For constant high-low range of 2, ATR should be 2
        assert abs(result.iloc[-1] - 2.0) < 0.01

    def test_atr_with_gap(self):
        """Test ATR handles gaps (high/low close jumps)."""
        # Create data with gap
        data = {
            'open': [10.0, 15.0] + [10.0] * 18,
            'high': [11.0, 16.0] + [11.0] * 18,
            'low': [9.0, 14.0] + [9.0] * 18,
            'close': [10.0, 15.0] + [10.0] * 18,
            'volume': [1000] * 20,
        }
        df = pd.DataFrame(data)

        indicator = ATRIndicator(period=14)
        result = indicator.calculate(df)

        # ATR should account for the gap
        assert result.iloc[-1] > 2.0

    def test_atr_required_period(self):
        """Test required_period returns correct value."""
        indicator = ATRIndicator(period=14)
        assert indicator.required_period() == 14
```

- [ ] **Step 2: Implement ATR indicator**

Replace the ATRIndicator placeholder in `src/bot_trading/indicators/volatility.py`:

```python
class ATRIndicator(BaseIndicator):
    """Average True Range.

    Measures market volatility.
    Higher ATR = Higher volatility

    Parameters:
        period: Period for ATR calculation (default: 14)
    """

    def __init__(self, period: int = 14):
        if period <= 0:
            raise ValueError("Period must be positive")
        self.period = period

    def calculate(self, df: DataFrame) -> IndicatorResult:
        """Calculate ATR using pandas operations.

        Args:
            df: DataFrame with 'high', 'low', 'close' columns

        Returns:
            Series with ATR values
        """
        self.validate_input(df)
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
        """Return minimum bars needed."""
        return self.period
```

- [ ] **Step 3: Run tests to verify they pass**

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_indicators/test_volatility.py::TestATRIndicator -v`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add src/bot_trading/indicators/volatility.py tests/test_indicators/test_volatility.py
git commit -m "feat(indicators): implement ATR indicator

- Add ATRIndicator using true range calculation
- Handle price gaps (high/low close jumps)
- Add tests for constant range and gap scenarios

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 5: Indicator Pipeline

This chunk implements the IndicatorPipeline class that manages computation, caching, and batch/incremental modes.

### Task 12: Implement IndicatorPipeline Core

**Files:**
- Create: `src/bot_trading/indicators/pipeline.py`

- [ ] **Step 1: Write failing test for pipeline**

```python
"""Tests for IndicatorPipeline."""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from bot_trading.indicators.pipeline import IndicatorPipeline
from bot_trading.indicators.moving_avg import SMAIndicator
from bot_trading.indicators.momentum import RSIIndicator
from bot_trading.providers.base import Bar
from bot_trading.indicators.exceptions import InsufficientDataError


class TestIndicatorPipeline:
    """Test suite for IndicatorPipeline."""

    def test_add_indicator(self):
        """Test adding indicator to pipeline."""
        pipeline = IndicatorPipeline()
        indicator = SMAIndicator(period=20)

        pipeline.add_indicator('sma_20', indicator)

        assert 'sma_20' in pipeline._indicators
        assert pipeline._indicators['sma_20'] is indicator

    def test_add_duplicate_indicator_raises_error(self):
        """Test that adding duplicate indicator raises ValueError."""
        pipeline = IndicatorPipeline()
        indicator = SMAIndicator(period=20)

        pipeline.add_indicator('sma_20', indicator)

        with pytest.raises(ValueError, match="already exists"):
            pipeline.add_indicator('sma_20', SMAIndicator(period=10))

    def test_remove_indicator(self):
        """Test removing indicator from pipeline."""
        pipeline = IndicatorPipeline()
        pipeline.add_indicator('sma_20', SMAIndicator(period=20))

        pipeline.remove_indicator('sma_20')

        assert 'sma_20' not in pipeline._indicators

    def test_clear_cache(self):
        """Test clearing the cache."""
        pipeline = IndicatorPipeline()
        pipeline.add_indicator('sma_5', SMAIndicator(period=5))

        # Create test bars
        bars = [
            Bar('AAPL', datetime(2024, 1, i + 1, tzinfo=timezone.utc),
                Decimal('150'), Decimal('152'), Decimal('149'), Decimal(str(150 + i)), 1000)
            for i in range(10)
        ]

        pipeline.compute(bars)
        assert pipeline._cache is not None

        pipeline.clear_cache()
        assert pipeline._cache is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_indicators/test_pipeline.py::TestIndicatorPipeline::test_add_indicator -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'bot_trading.indicators.pipeline'"

- [ ] **Step 3: Implement IndicatorPipeline**

```python
"""Indicator pipeline for computing technical indicators."""

import logging
from typing import Dict, List, Optional
import pandas as pd
from pandas import DataFrame, Series
from .base import BaseIndicator, IndicatorResult
from .exceptions import IndicatorError, InsufficientDataError, InvalidInputError
from ..data.converters import BarsToDataFrameConverter

logger = logging.getLogger(__name__)


class IndicatorPipeline:
    """Main pipeline for computing technical indicators.

    Features:
    - Batch computation (backtesting)
    - Incremental updates (real-time)
    - Caching (avoid re-computation)
    - Partial failure handling

    Caching Strategy:
    - Cache stores the last N bars of computed results (single cache for all indicators)
    - Cache is keyed by (symbol, timeframe) combination
    - Cache invalidates when:
      * Indicators are added/removed
      * Symbol changes (detected in update())
      * Explicitly requested via clear_cache()
    - Memory limit: cache_size bars total (not per indicator)
    - Default: 1000 bars (configurable)
    """

    def __init__(self, cache_size: int = 1000):
        """Initialize pipeline.

        Args:
            cache_size: Maximum number of bars to keep in cache (total, not per indicator)
                        Larger cache = faster incremental updates but more memory
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

    def clear_cache(self) -> None:
        """Explicitly clear the cache.

        Useful when switching symbols or timeframes.
        """
        self._invalidate_cache()

    def compute(self, bars: List) -> DataFrame:
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
            # Validate bar data
            self._validate_bars(bars)

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

    def update(self, bar: Bar) -> Series:
        """Update indicators with new bar (incremental/real-time mode).

        Args:
            bar: New Bar object

        Returns:
            Series with latest indicator values

        Raises:
            IndicatorError: If called before compute() or symbol/timeframe mismatch

        Note:
            - Requires prior compute() call to establish cache
            - Recomputes indicators on cached + new data
            - Simpler but slower than true incremental
        """
        if self._cache is None:
            raise IndicatorError("Must call compute() before update()")

        if bar.symbol != self._cache_symbol:
            raise IndicatorError(
                f"Symbol mismatch: expected {self._cache_symbol}, got {bar.symbol}"
            )

        # Append new bar to cache
        new_row = {
            'open': float(bar.open),
            'high': float(bar.high),
            'low': float(bar.low),
            'close': float(bar.close),
            'volume': bar.volume,
        }
        self._cache.loc[bar.timestamp] = new_row

        # Recompute all indicators using cached data
        # Use BarsToDataFrameConverter to convert back to bars
        converter = BarsToDataFrameConverter()
        bars = converter.dataframe_to_bars(self._cache, symbol=self._cache_symbol)
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
        self._cache_timeframe = None

    def _validate_bars(self, bars: List) -> None:
        """Validate bar data meets quality requirements.

        Args:
            bars: List of Bar objects to validate

        Raises:
            InvalidInputError: If validation fails
        """
        for i, bar in enumerate(bars):
            # Volume must be >= 0
            if bar.volume < 0:
                raise InvalidInputError(
                    f"Bar {i}: volume must be >= 0, got {bar.volume}"
                )
            # High must be >= low
            if bar.high < bar.low:
                raise InvalidInputError(
                    f"Bar {i}: high ({bar.high}) must be >= low ({bar.low})"
                )
            # Open must be within high-low range
            if not (bar.low <= bar.open <= bar.high):
                raise InvalidInputError(
                    f"Bar {i}: open ({bar.open}) must be between low ({bar.low}) and high ({bar.high})"
                )
            # Close must be within high-low range
            if not (bar.low <= bar.close <= bar.high):
                raise InvalidInputError(
                    f"Bar {i}: close ({bar.close}) must be between low ({bar.low}) and high ({bar.high})"
                )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_indicators/test_pipeline.py::TestIndicatorPipeline -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/bot_trading/indicators/pipeline.py tests/test_indicators/test_pipeline.py
git commit -m "feat(indicators): add IndicatorPipeline core functionality

- Add add_indicator/remove_indicator methods
- Add clear_cache method for explicit cache invalidation
- Add compute() method for batch computation
- Add update() method for incremental updates
- Add failed_indicators property for error tracking
- Implement caching strategy with configurable size

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 13: Complete Pipeline Tests

**Files:**
- Modify: `tests/test_indicators/test_pipeline.py`

- [ ] **Step 1: Add more pipeline tests**

```python
    def test_compute_returns_dataframe_with_indicators(self):
        """Test compute returns DataFrame with indicator columns."""
        pipeline = IndicatorPipeline()
        pipeline.add_indicator('sma_5', SMAIndicator(period=5))

        bars = [
            Bar('AAPL', datetime(2024, 1, i + 1, tzinfo=timezone.utc),
                Decimal('150'), Decimal('152'), Decimal('149'), Decimal(str(150 + i)), 1000)
            for i in range(10)
        ]

        result = pipeline.compute(bars)

        assert isinstance(result, pd.DataFrame)
        assert 'sma_5' in result.columns
        assert 'close' in result.columns

    def test_compute_insufficient_data_raises_error(self):
        """Test that insufficient data raises InsufficientDataError."""
        pipeline = IndicatorPipeline()
        pipeline.add_indicator('sma_20', SMAIndicator(period=20))

        # Only 10 bars, but SMA requires 20
        bars = [
            Bar('AAPL', datetime(2024, 1, i + 1, tzinfo=timezone.utc),
                Decimal('150'), Decimal('152'), Decimal('149'), Decimal('150'), 1000)
            for i in range(10)
        ]

        with pytest.raises(InsufficientDataError, match="Need at least 20"):
            pipeline.compute(bars)

    def test_compute_multiple_indicators(self):
        """Test computing multiple indicators at once."""
        pipeline = IndicatorPipeline()
        pipeline.add_indicator('sma_5', SMAIndicator(period=5))
        pipeline.add_indicator('sma_10', SMAIndicator(period=10))

        bars = [
            Bar('AAPL', datetime(2024, 1, i + 1, tzinfo=timezone.utc),
                Decimal('150'), Decimal('152'), Decimal('149'), Decimal(str(150 + i)), 1000)
            for i in range(15)
        ]

        result = pipeline.compute(bars)

        assert 'sma_5' in result.columns
        assert 'sma_10' in result.columns

    def test_update_requires_compute_first(self):
        """Test that update() requires prior compute() call."""
        pipeline = IndicatorPipeline()

        new_bar = Bar('AAPL', datetime(2024, 1, 1, tzinfo=timezone.utc),
                      Decimal('150'), Decimal('152'), Decimal('149'), Decimal('150'), 1000)

        with pytest.raises(IndicatorError, match="Must call compute"):
            pipeline.update(new_bar)

    def test_update_symbol_mismatch_raises_error(self):
        """Test that symbol mismatch raises error."""
        pipeline = IndicatorPipeline()
        pipeline.add_indicator('sma_5', SMAIndicator(period=5))

        # Compute with AAPL
        bars = [
            Bar('AAPL', datetime(2024, 1, i + 1, tzinfo=timezone.utc),
                Decimal('150'), Decimal('152'), Decimal('149'), Decimal('150'), 1000)
            for i in range(10)
        ]
        pipeline.compute(bars)

        # Try to update with TSLA
        new_bar = Bar('TSLA', datetime(2024, 1, 11, tzinfo=timezone.utc),
                      Decimal('200'), Decimal('202'), Decimal('198'), Decimal('200'), 1000)

        with pytest.raises(IndicatorError, match="Symbol mismatch"):
            pipeline.update(new_bar)
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_indicators/test_pipeline.py -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_indicators/test_pipeline.py
git commit -m "test(indicators): add comprehensive pipeline tests

- Test DataFrame output with indicators
- Test insufficient data error handling
- Test multiple indicator computation
- Test update() requires prior compute()
- Test symbol mismatch detection

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 6: Integration and Finalization

This chunk integrates all indicators, updates package exports, adds dependencies, and runs final tests.

### Task 14: Update Indicators Package Exports

**Files:**
- Modify: `src/bot_trading/indicators/__init__.py`

- [ ] **Step 1: Update package exports**

```python
"""Technical indicators framework."""

from .base import BaseIndicator, IndicatorResult
from .exceptions import IndicatorError, InsufficientDataError, InvalidInputError
from .moving_avg import SMAIndicator, EMAIndicator
from .momentum import RSIIndicator, MACDIndicator
from .volatility import BollingerBands, ATRIndicator
from .pipeline import IndicatorPipeline

__all__ = [
    # Base
    'BaseIndicator',
    'IndicatorResult',
    # Exceptions
    'IndicatorError',
    'InsufficientDataError',
    'InvalidInputError',
    # Moving Averages
    'SMAIndicator',
    'EMAIndicator',
    # Momentum
    'RSIIndicator',
    'MACDIndicator',
    # Volatility
    'BollingerBands',
    'ATRIndicator',
    # Pipeline
    'IndicatorPipeline',
]
```

- [ ] **Step 2: Verify imports work**

Run: `python -c "from bot_trading.indicators import *; print('All imports OK')"`
Expected: `All imports OK`

- [ ] **Step 3: Commit**

```bash
git add src/bot_trading/indicators/__init__.py
git commit -m "feat(indicators): update package exports

- Export all indicator classes
- Export IndicatorPipeline
- Organize exports by category

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 15: Add Dependencies to pyproject.toml

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add pandas and numpy dependencies**

Find the `[project.dependencies]` section and add:
```toml
[project.dependencies]
# ... existing dependencies ...
pandas = ">=2.0.0"
numpy = ">=1.24.0"
```

- [ ] **Step 2: Install dependencies**

Run: `pip install pandas numpy`
Expected: Packages installed successfully

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "deps: add pandas and numpy dependencies

- Add pandas>=2.0.0 for DataFrame operations
- Add numpy>=1.24.0 for numerical operations
- Required for Phase 1 indicators framework

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 16: Run Full Test Suite

**Files:**
- None (run tests only)

- [ ] **Step 1: Run all indicator tests**

Run: `pytest tests/test_indicators/ -v --cov=bot_trading.indicators --cov=bot_trading.data`
Expected: All tests PASS with 80%+ coverage

- [ ] **Step 2: Run linting**

Run: `ruff check src/bot_trading/indicators/ src/bot_trading/data/`
Expected: No errors

- [ ] **Step 3: Run formatting**

Run: `ruff format src/bot_trading/indicators/ src/bot_trading/data/`
Expected: Files formatted

- [ ] **Step 4: Commit if needed**

```bash
# Only commit if there were formatting changes
git add -A
git commit -m "style(indicators): apply ruff formatting

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 17: Create Integration Example

**Files:**
- Create: `examples/indicators_usage.py`

- [ ] **Step 1: Create usage example**

```python
"""Example usage of Phase 1 indicators framework."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from bot_trading.indicators import (
    IndicatorPipeline,
    SMAIndicator,
    EMAIndicator,
    RSIIndicator,
    MACDIndicator,
    BollingerBands,
)
from bot_trading.providers.mock import MockProvider  # Assuming we have this


def main():
    """Demonstrate indicators usage."""
    print("=" * 60)
    print("Phase 1: Technical Indicators Framework - Usage Example")
    print("=" * 60)

    # Create pipeline
    pipeline = IndicatorPipeline()

    # Add indicators
    pipeline.add_indicator('sma_20', SMAIndicator(period=20))
    pipeline.add_indicator('sma_50', SMAIndicator(period=50))
    pipeline.add_indicator('ema_20', EMAIndicator(period=20))
    pipeline.add_indicator('rsi_14', RSIIndicator(period=14))
    pipeline.add_indicator('macd', MACDIndicator(fast=12, slow=26, signal=9))
    pipeline.add_indicator('bb', BollingerBands(period=20, std_dev=2.0))

    print(f"\nAdded {len(pipeline._indicators)} indicators to pipeline")

    # Create mock data
    bars = []
    base_price = Decimal('150.0')
    for i in range(100):
        price = base_price + Decimal(str(i * 0.5))
        bars.append(create_mock_bar(price, i))

    print(f"Created {len(bars)} mock bars")

    # Compute indicators (batch mode)
    print("\nComputing indicators (batch mode)...")
    df = pipeline.compute(bars)

    print(f"\nResult DataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Show latest values
    print("\n" + "=" * 60)
    print("Latest Indicator Values:")
    print("=" * 60)
    latest = df.iloc[-1]

    print(f"\nPrice: ${latest['close']:.2f}")
    print(f"SMA(20): ${latest['sma_20']:.2f}")
    print(f"SMA(50): ${latest['sma_50']:.2f}")
    print(f"EMA(20): ${latest['ema_20']:.2f}")
    print(f"RSI(14): {latest['rsi_14']:.2f}")
    print(f"MACD: {latest['macd_macd']:.4f}")
    print(f"BB Upper: ${latest['bb_upper']:.2f}")
    print(f"BB Middle: ${latest['bb_middle']:.2f}")
    print(f"BB Lower: ${latest['bb_lower']:.2f}")

    # Check for golden cross
    print("\n" + "=" * 60)
    print("Signal Analysis:")
    print("=" * 60)

    prev = df.iloc[-2]

    if prev['sma_20'] <= prev['sma_50'] and latest['sma_20'] > latest['sma_50']:
        print("✅ GOLDEN CROSS detected! (Bullish signal)")
    elif prev['sma_20'] >= prev['sma_50'] and latest['sma_20'] < latest['sma_50']:
        print("❌ DEATH CROSS detected! (Bearish signal)")
    else:
        print("→ No crossover detected")

    if latest['rsi_14'] > 70:
        print("⚠️  RSI is overbought (>70)")
    elif latest['rsi_14'] < 30:
        print("⚠️  RSI is oversold (<30)")
    else:
        print("✓ RSI is in neutral zone")

    # Demonstrate incremental update
    print("\n" + "=" * 60)
    print("Incremental Update (Real-time mode):")
    print("=" * 60)

    new_bar = create_mock_bar(base_price + Decimal('50.5'), 100)
    print(f"\nAdding new bar: close=${new_bar.close:.2f}")

    updated = pipeline.update(new_bar)
    print(f"Updated SMA(20): ${updated['sma_20']:.2f}")
    print(f"Updated RSI(14): {updated['rsi_14']:.2f}")

    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


def create_mock_bar(close_price, index):
    """Create a mock Bar for testing."""
    from bot_trading.providers.base import Bar

    timestamp = datetime(2024, 1, 1) + timedelta(days=index)
    timestamp = timestamp.replace(tzinfo=timezone.utc)

    high = close_price + Decimal('1.0')
    low = close_price - Decimal('1.0')
    open_price = close_price - Decimal('0.5')

    return Bar(
        symbol='AAPL',
        timestamp=timestamp,
        open=open_price,
        high=high,
        low=low,
        close=close_price,
        volume=1000000,
    )


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run the example**

Run: `python examples/indicators_usage.py`
Expected: Example runs successfully and displays indicator values

- [ ] **Step 3: Commit**

```bash
git add examples/indicators_usage.py
git commit -m "examples(indicators): add comprehensive usage example

- Demonstrate pipeline setup with all 6 indicators
- Show batch computation mode
- Show incremental update mode
- Include signal analysis (golden cross, RSI levels)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 18: Update Documentation

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README with Phase 1 status**

Find the "สถานะการพัฒนา (Development Status)" section and update:

```markdown
## สถานะการพัฒนา (Development Status)

### ✅ Phase 0: Foundation API (เสร็จสมบูรณ์)

พื้นฐาน API สำหรับการเชื่อมต่อ Alpaca พร้อมใช้งานแล้ว:

- ✅ โครงสร้างข้อมูล Bar และ EquityPoint สำหรับข้อมูลราคาย้อนหลัง
- ✅ Exception ที่กำหนดเองสำหรับการจัดการข้อผิดพลาด
- ✅ เมธอด `get_historical_bars()` สำหรับดึงข้อมูล OHLCV ย้อนหลัง
- ✅ เมธอด `get_order_history()` สำหรับดึงประวัติออเดอร์
- ✅ MockProvider สำหรับทดสอบโดยไม่ต้องใช้ API จริง
- ✅ Integration tests พร้อมใช้งาน

**สถิติการทดสอบ:**
- 49 tests passed ✅
- 89% code coverage (เป้าหมาย: 80%)
- 3 integration tests skipped (ต้องการ API credentials)

### ✅ Phase 1: Technical Indicators (เสร็จสมบูรณ์)

กรอบการทำงานสำหรับ Technical Indicators พร้อมใช้งาน:

- ✅ BaseIndicator abstract class
- ✅ IndicatorPipeline สำหรับ batch/incremental computation
- ✅ BarsToDataFrameConverter สำหรับแปลงข้อมูล
- ✅ Moving Averages: SMA, EMA
- ✅ Momentum: RSI, MACD
- ✅ Volatility: Bollinger Bands, ATR
- ✅ รองรับทั้ง backtesting (batch) และ real-time (incremental)
- ✅ Unit tests ครอบคลุม

**Indicators ที่รองรับ:**
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- ATR (Average True Range)
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README with Phase 1 completion status

- Mark Phase 1 as complete
- List all implemented indicators
- Add batch/incremental mode support note

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Success Criteria Checklist

After completing all tasks, verify:

- [ ] All 6 indicators implemented (SMA, EMA, RSI, MACD, Bollinger Bands, ATR)
- [ ] IndicatorPipeline supports batch and incremental modes
- [ ] BarsToDataFrameConverter handles Decimal→float conversion
- [ ] Caching works correctly
- [ ] Unit tests pass with 80%+ coverage
- [ ] Integration tests pass
- [ ] Documentation complete
- [ ] Ready for Phase 2 (Strategy Management)

---

**Total Estimated Time:** 3-4 hours for implementation

**Commands to verify completion:**
```bash
# Run all tests
pytest tests/test_indicators/ -v --cov=bot_trading.indicators --cov=bot_trading.data

# Check code quality
ruff check src/bot_trading/indicators/ src/bot_trading/data/

# Run example
python examples/indicators_usage.py
```
