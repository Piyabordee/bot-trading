# Phase 0: Foundation API Work - Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement complete Alpaca API integration with historical data fetching, order history, and testing infrastructure.

**Architecture:** Update BaseProvider abstract class with new data models (Bar, EquityPoint) and methods (get_historical_bars, get_order_history), then implement fully in AlpacaProvider using alpaca-trade-api library. Create MockProvider for isolated testing.

**Tech Stack:** Python 3.11+, alpaca-trade-api, pytest, Decimal for precision

---

## Pre-Phase 0 Checklist

**Before starting any tasks:**

- [ ] **Step 0: Verify existing tests pass**

```bash
pytest tests/ -v
```

Expected: All existing tests pass

- [ ] **Step 1: Create git tag for current state**

```bash
git tag -a v0.1.0-scaffold -m "Scaffold baseline before Phase 0"
git push origin v0.1.0-scaffold
```

- [ ] **Step 2: Create test directories**

```bash
mkdir -p tests/test_providers tests/integration
```

- [ ] **Step 3: Verify .env.example exists**

```bash
cat .env.example
```

Expected: .env.example exists with ALPACA_API_KEY and ALPACA_API_SECRET placeholders

---

## Chunk 1: Data Models and Exceptions

This chunk creates the foundational data structures and custom exceptions that will be used throughout the system.

### Task 1.1: Create Exceptions Module

**Files:**
- Create: `src/bot_trading/exceptions.py`
- Test: `tests/test_exceptions.py`

**Purpose:** Define custom exception types for clear error handling across the application.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_exceptions.py
import pytest
from bot_trading.exceptions import (
    TradingAnalysisError,
    APIError,
    InsufficientDataError,
    StrategyNotFoundError,
    RiskLimitExceededError,
    InvalidConfigError,
)

def test_api_error_can_be_raised_and_caught():
    with pytest.raises(APIError) as exc_info:
        raise APIError("Cannot connect to API")
    assert str(exc_info.value) == "Cannot connect to API"

def test_api_error_is_trading_analysis_error():
    with pytest.raises(TradingAnalysisError):
        raise APIError("Test")

def test_insufficient_data_error():
    with pytest.raises(InsufficientDataError) as exc_info:
        raise InsufficientDataError("Not enough bars")
    assert "Not enough bars" in str(exc_info.value)

def test_strategy_not_found_error():
    with pytest.raises(StrategyNotFoundError):
        raise StrategyNotFoundError("unknown_strategy")

def test_risk_limit_exceeded_error():
    with pytest.raises(RiskLimitExceededError):
        raise RiskLimitExceededError("Position exceeds 10%")

def test_invalid_config_error():
    with pytest.raises(InvalidConfigError):
        raise InvalidConfigError("Invalid parameter")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_exceptions.py -v
```

Expected: `ModuleNotFoundError: No module named 'bot_trading.exceptions'`

- [ ] **Step 3: Write the exceptions module**

```python
# src/bot_trading/exceptions.py
"""Custom exceptions for the Trading Analysis Tool."""


class TradingAnalysisError(Exception):
    """Base exception for trading analysis tool."""
    pass


class APIError(TradingAnalysisError):
    """Raised when API call fails."""
    pass


class InsufficientDataError(TradingAnalysisError):
    """Raised when not enough data for analysis."""
    pass


class StrategyNotFoundError(TradingAnalysisError):
    """Raised when requested strategy is not found."""
    pass


class RiskLimitExceededError(TradingAnalysisError):
    """Raised when position exceeds risk limits."""
    pass


class InvalidConfigError(TradingAnalysisError):
    """Raised when strategy configuration is invalid."""
    pass
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_exceptions.py -v
```

Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/bot_trading/exceptions.py tests/test_exceptions.py
git commit -m "feat: add custom exceptions module

Add TradingAnalysisError base class and specific exception types:
- APIError: For API connection failures
- InsufficientDataError: When not enough data for analysis
- StrategyNotFoundError: When requested strategy doesn't exist
- RiskLimitExceededError: When position exceeds 10% limit
- InvalidConfigError: When configuration is invalid

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 1.2: Update BaseProvider with New Data Models

**Files:**
- Modify: `src/bot_trading/providers/base.py`
- Test: `tests/test_providers/test_base_models.py`

**Purpose:** Add Bar and EquityPoint dataclasses to BaseProvider for historical data and equity curve tracking.

**Note:** Existing models use:
- Order: `order_id`, `created_at`, `quantity` (Decimal)
- Position: `quantity` (Decimal)
- Account: No `account_id` field

- [ ] **Step 1: Write the failing test**

```python
# tests/test_providers/test_base_models.py
import pytest
from datetime import datetime, date
from decimal import Decimal
from bot_trading.providers.base import Bar, EquityPoint

def test_bar_dataclass_creation():
    bar = Bar(
        symbol="AAPL",
        timestamp=datetime(2025, 3, 14, 9, 30),
        open=Decimal("150.00"),
        high=Decimal("151.00"),
        low=Decimal("149.50"),
        close=Decimal("150.50"),
        volume=10000
    )
    assert bar.symbol == "AAPL"
    assert bar.close == Decimal("150.50")
    assert bar.volume == 10000

def test_bar_requires_decimal_for_prices():
    with pytest.raises(Exception):  # May raise TypeError or ValidationError
        Bar(
            symbol="AAPL",
            timestamp=datetime.now(),
            open=150.0,  # Should be Decimal
            high=Decimal("151.00"),
            low=Decimal("149.50"),
            close=Decimal("150.50"),
            volume=10000
        )

def test_equity_point_dataclass_creation():
    point = EquityPoint(
        timestamp=datetime(2025, 3, 14, 16, 0),
        value=Decimal("100000.00"),
        returns_pct=Decimal("5.2")
    )
    assert point.value == Decimal("100000.00")
    assert point.returns_pct == Decimal("5.2")

def test_bar_string_representation():
    bar = Bar(
        symbol="AAPL",
        timestamp=datetime(2025, 3, 14, 9, 30),
        open=Decimal("150.00"),
        high=Decimal("151.00"),
        low=Decimal("149.50"),
        close=Decimal("150.50"),
        volume=10000
    )
    str_repr = str(bar)
    assert "AAPL" in str_repr
    assert "150.50" in str_repr
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_providers/test_base_models.py -v
```

Expected: `ImportError: cannot import name 'Bar' from 'bot_trading.providers.base'`

- [ ] **Step 3: Add data models to BaseProvider**

Add the new imports and dataclasses after the existing Order model (after line 40):

```python
# src/bot_trading/providers/base.py
"""Abstract base class for trading providers.

All provider adapters must implement this interface to ensure
consistent behavior across different brokers/exchanges.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

# Keep existing Account, Position, Order dataclasses as-is
# ...

# NEW: Historical data models (add after Order dataclass)
@dataclass
class Bar:
    """OHLCV price bar for historical data."""
    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


@dataclass
class EquityPoint:
    """Equity curve point for backtest results."""
    timestamp: datetime
    value: Decimal
    returns_pct: Decimal  # Returns from start of period
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_providers/test_base_models.py -v
```

Expected: All 4 tests PASS

- [ ] **Step 5: Run linting**

```bash
ruff check src/bot_trading/providers/base.py
ruff format src/bot_trading/providers/base.py
```

Expected: No errors

- [ ] **Step 6: Commit**

```bash
git add src/bot_trading/providers/base.py tests/test_providers/test_base_models.py
git commit -m "feat: add Bar and EquityPoint data models

Add OHLCV bar and equity curve data models for:
- Historical price data storage
- Backtest equity curve tracking
- Use Decimal for price precision

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 1.3: Add New Abstract Methods to BaseProvider

**Files:**
- Modify: `src/bot_trading/providers/base.py`
- Test: `tests/test_providers/test_base_abstract_methods.py`

**Purpose:** Add get_historical_bars and get_order_history abstract methods to the interface.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_providers/test_base_abstract_methods.py
import pytest
from datetime import date, datetime
from decimal import Decimal
from bot_trading.providers.base import BaseProvider, Bar, Order, Account, Position

def test_base_provider_requires_get_historical_bars():
    """Concrete provider must implement get_historical_bars."""

    class IncompleteProvider(BaseProvider):
        def get_account(self) -> Account:
            return Account(
                equity=Decimal("100000"),
                cash=Decimal("100000"),
                buying_power=Decimal("100000"),
                portfolio_value=Decimal("100000")
            )

        def get_positions(self) -> list[Position]:
            return []

        def get_latest_price(self, symbol: str) -> Decimal:
            return Decimal("100")

        def submit_order(self, symbol: str, side: str, quantity: Decimal, order_type: str = "market", price: Optional[Decimal] = None) -> Order:
            return Order(
                order_id="test",
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                status="filled",
                created_at=datetime.now()
            )

        def cancel_order(self, order_id: str) -> bool:
            return True

        def list_open_orders(self) -> list[Order]:
            return []

        # Missing: get_historical_bars and get_order_history

    with pytest.raises(TypeError, match="abstract"):
        # Should fail because abstract methods not implemented
        provider = IncompleteProvider()

def test_base_provider_requires_get_order_history():
    """Concrete provider must implement get_order_history."""

    class IncompleteProvider(BaseProvider):
        def get_account(self) -> Account:
            return Account(
                equity=Decimal("100000"),
                cash=Decimal("100000"),
                buying_power=Decimal("100000"),
                portfolio_value=Decimal("100000")
            )

        def get_positions(self) -> list[Position]:
            return []

        def get_latest_price(self, symbol: str) -> Decimal:
            return Decimal("100")

        def submit_order(self, symbol: str, side: str, quantity: Decimal, order_type: str = "market", price: Optional[Decimal] = None) -> Order:
            return Order(
                order_id="test",
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                status="filled",
                created_at=datetime.now()
            )

        def cancel_order(self, order_id: str) -> bool:
            return True

        def list_open_orders(self) -> list[Order]:
            return []

        def get_historical_bars(self, symbol: str, start_date: date, end_date: date, timeframe: str = "1Day") -> list[Bar]:
            return [Bar(symbol="AAPL", timestamp=datetime.now(),
                       open=Decimal("100"), high=Decimal("101"),
                       low=Decimal("99"), close=Decimal("100.5"), volume=1000)]

        # Missing: get_order_history

    with pytest.raises(TypeError, match="abstract"):
        provider = IncompleteProvider()

def test_concrete_provider_can_be_instantiated_with_all_methods():
    """Provider with all methods should be instantiable."""

    class CompleteProvider(BaseProvider):
        def get_account(self) -> Account:
            return Account(
                equity=Decimal("100000"),
                cash=Decimal("100000"),
                buying_power=Decimal("100000"),
                portfolio_value=Decimal("100000")
            )

        def get_positions(self) -> list[Position]:
            return []

        def get_latest_price(self, symbol: str) -> Decimal:
            return Decimal("100")

        def submit_order(self, symbol: str, side: str, quantity: Decimal, order_type: str = "market", price: Optional[Decimal] = None) -> Order:
            return Order(
                order_id="1",
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                status="filled",
                created_at=datetime.now()
            )

        def cancel_order(self, order_id: str) -> bool:
            return True

        def list_open_orders(self) -> list[Order]:
            return []

        def get_historical_bars(self, symbol: str, start_date: date, end_date: date, timeframe: str = "1Day") -> list[Bar]:
            return [Bar(symbol="AAPL", timestamp=datetime.now(),
                       open=Decimal("100"), high=Decimal("101"),
                       low=Decimal("99"), close=Decimal("100.5"), volume=1000)]

        def get_order_history(self, days: int = 7) -> list[Order]:
            return []

    # Should not raise
    provider = CompleteProvider()
    assert provider is not None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_providers/test_base_abstract_methods.py -v
```

Expected: Tests fail because BaseProvider doesn't have these abstract methods yet

- [ ] **Step 3: Add abstract methods to BaseProvider class**

Add to the BaseProvider class, after list_open_orders method:

```python
# In BaseProvider class, add after list_open_orders:

@abstractmethod
def get_historical_bars(
    self,
    symbol: str,
    start_date: date,
    end_date: date,
    timeframe: str = "1Day"
) -> list[Bar]:
    """Get historical OHLCV bars for a symbol.

    Args:
        symbol: Trading symbol (e.g., "AAPL")
        start_date: Start date for historical data
        end_date: End date for historical data
        timeframe: Bar timeframe ("1Minute", "5Minute", "15Minute", "1Hour", "1Day")

    Returns:
        List of Bar objects with OHLCV data
    """
    pass


@abstractmethod
def get_order_history(self, days: int = 7) -> list[Order]:
    """Get order history for the last N days.

    Args:
        days: Number of days to look back

    Returns:
        List of Order objects
    """
    pass
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_providers/test_base_abstract_methods.py -v
```

Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/bot_trading/providers/base.py tests/test_providers/test_base_abstract_methods.py
git commit -m "feat: add get_historical_bars and get_order_history to BaseProvider

Add abstract methods for:
- Historical OHLCV bar data retrieval
- Order history retrieval

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 2: AlpacaProvider Implementation

This chunk implements the full Alpaca API integration.

### Task 2.1: Implement get_order_history in AlpacaProvider

**Files:**
- Modify: `src/bot_trading/providers/alpaca.py`
- Test: `tests/test_providers/test_alpaca_order_history.py`

**Note:** Alpaca API uses:
- Order.id for order ID
- Order.filled_at for fill time (not created_at)
- Order.qty as quantity (Decimal type)
- Order.filled_avg_price for average fill price

- [ ] **Step 1: Write the failing test**

```python
# tests/test_providers/test_alpaca_order_history.py
import os
from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from bot_trading.providers.alpaca import AlpacaProvider
from bot_trading.exceptions import APIError

# Mock credentials for testing
os.environ["ALPACA_API_KEY"] = "test_key"
os.environ["ALPACA_API_SECRET"] = "test_secret"
os.environ["ALPACA_BASE_URL"] = "https://paper-api.alpaca.markets"

def test_get_order_history_returns_list():
    """Should return list of orders from API."""
    # This test uses mocking - actual API call tests in integration tests
    from unittest.mock import Mock, patch

    with patch('bot_trading.providers.alpaca.TradingClient') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance

        # Mock order response
        mock_order = Mock()
        mock_order.id = "order_123"
        mock_order.symbol = "AAPL"
        mock_order.side = Mock(name="buy")
        mock_order.side.name = "BUY"
        mock_order.qty = Decimal("10")
        mock_order.filled_avg_price = Decimal("150.00")
        mock_order.status = Mock(name="filled")
        mock_order.status.name = "FILLED"
        mock_order.filled_at = datetime.now()

        mock_instance.get_orders.return_value = [mock_order]

        provider = AlpacaProvider()
        orders = provider.get_order_history(days=7)

        assert isinstance(orders, list)
        # Each order should be an Order dataclass
        for order in orders:
            assert hasattr(order, 'order_id')
            assert hasattr(order, 'symbol')
            assert hasattr(order, 'side')

def test_get_order_history_handles_api_error():
    """Should raise APIError when API call fails."""
    from unittest.mock import Mock, patch

    with patch('bot_trading.providers.alpaca.TradingClient') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.get_orders.side_effect = Exception("API Error")

        provider = AlpacaProvider()

        with pytest.raises(APIError, match="Failed to get order history"):
            provider.get_order_history(days=7)

def test_get_order_history_empty_result():
    """Should return empty list when no orders."""
    from unittest.mock import Mock, patch

    with patch('bot_trading.providers.alpaca.TradingClient') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.get_orders.return_value = []

        provider = AlpacaProvider()
        orders = provider.get_order_history(days=7)

        assert orders == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_providers/test_alpaca_order_history.py -v
```

Expected: Fails because method not implemented

- [ ] **Step 3: Implement get_order_history in AlpacaProvider**

Add to AlpacaProvider class:

```python
# In AlpacaProvider class, add the import at top:
from bot_trading.exceptions import APIError

# In AlpacaProvider class, add:

def get_order_history(self, days: int = 7) -> list[Order]:
    """Get order history for the last N days.

    Args:
        days: Number of days to look back (default: 7)

    Returns:
        List of Order objects

    Raises:
        APIError: If API call fails
    """
    try:
        from datetime import datetime, timedelta
        from alpaca.trading.requests import GetOrdersRequest

        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        # Use alpaca-trade-api to get orders
        request_params = GetOrdersRequest(
            status="all",
            after=start_time,
            until=end_time,
            limit=500
        )

        orders_data = self.client.get_orders(filter=request_params)

        orders = []
        for order_data in orders_data:
            # Convert API response to Order dataclass
            # Note: Order model expects 'created_at' but API gives 'filled_at'
            orders.append(Order(
                order_id=str(order_data.id),
                symbol=order_data.symbol,
                side=order_data.side.name.lower(),
                quantity=Decimal(str(order_data.qty)) if order_data.qty else Decimal("0"),
                price=Decimal(str(order_data.filled_avg_price)) if order_data.filled_avg_price else None,
                status=order_data.status.name.lower(),
                created_at=order_data.filled_at or order_data.created_at
            ))

        return orders

    except APIError:
        raise
    except Exception as e:
        raise APIError(f"Failed to get order history: {e}")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_providers/test_alpaca_order_history.py -v
```

Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/bot_trading/providers/alpaca.py tests/test_providers/test_alpaca_order_history.py
git commit -m "feat: implement get_order_history in AlpacaProvider

Add order history retrieval using alpaca-trade-api:
- Fetch orders for last N days
- Convert API response to Order dataclass
- Handle API errors with APIError exception
- Map API fields to existing Order model

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 2.2: Implement get_historical_bars in AlpacaProvider

**Files:**
- Modify: `src/bot_trading/providers/alpaca.py`
- Test: `tests/test_providers/test_alpaca_historical_bars.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_providers/test_alpaca_historical_bars.py
import os
from datetime import date, datetime
from decimal import Decimal
import pytest
from bot_trading.providers.alpaca import AlpacaProvider
from bot_trading.providers.base import Bar
from bot_trading.exceptions import APIError, InsufficientDataError

os.environ["ALPACA_API_KEY"] = "test_key"
os.environ["ALPACA_API_SECRET"] = "test_secret"
os.environ["ALPACA_BASE_URL"] = "https://paper-api.alpaca.markets"

def test_get_historical_bars_returns_bar_objects():
    """Should return list of Bar objects with OHLCV data."""
    from unittest.mock import Mock, patch

    with patch('bot_trading.providers.alpaca.StockHistoricalDataClient') as mock_data_client:
        mock_instance = Mock()
        mock_data_client.return_value = mock_instance

        # Mock bars response
        mock_bar = Mock()
        mock_bar.symbol = "AAPL"
        mock_bar.timestamp = datetime(2025, 3, 14, 9, 30)
        mock_bar.open = 150.0
        mock_bar.high = 151.0
        mock_bar.low = 149.5
        mock_bar.close = 150.5
        mock_bar.volume = 10000

        mock_bars_data = Mock()
        mock_bars_data.data = {"AAPL": [mock_bar]}
        mock_instance.get_stock_bars.return_value = mock_bars_data

        provider = AlpacaProvider()
        bars = provider.get_historical_bars(
            symbol="AAPL",
            start_date=date(2025, 3, 1),
            end_date=date(2025, 3, 14),
            timeframe="1Day"
        )

        assert isinstance(bars, list)
        for bar in bars:
            assert isinstance(bar, Bar)
            assert bar.symbol == "AAPL"
            assert isinstance(bar.open, Decimal)
            assert isinstance(bar.high, Decimal)
            assert isinstance(bar.low, Decimal)
            assert isinstance(bar.close, Decimal)
            assert isinstance(bar.volume, int)

def test_get_historical_bars_empty_result():
    """Should return empty list when no data available."""
    from unittest.mock import Mock, patch

    with patch('bot_trading.providers.alpaca.StockHistoricalDataClient') as mock_data_client:
        mock_instance = Mock()
        mock_data_client.return_value = mock_instance

        mock_bars_data = Mock()
        mock_bars_data.data = {}
        mock_instance.get_stock_bars.return_value = mock_bars_data

        provider = AlpacaProvider()
        bars = provider.get_historical_bars(
            symbol="INVALID",
            start_date=date(2020, 1, 1),
            end_date=date(2020, 1, 5),
        )

        assert bars == []

def test_get_historical_bars_invalid_timeframe():
    """Should raise InvalidConfigError for invalid timeframe."""
    from bot_trading.exceptions import InvalidConfigError

    provider = AlpacaProvider()

    with pytest.raises(InvalidConfigError, match="Invalid timeframe"):
        provider.get_historical_bars(
            symbol="AAPL",
            start_date=date(2025, 3, 1),
            end_date=date(2025, 3, 5),
            timeframe="InvalidTimeframe"
        )

def test_get_historical_bars_handles_api_error():
    """Should raise APIError when API call fails."""
    from unittest.mock import Mock, patch

    with patch('bot_trading.providers.alpaca.StockHistoricalDataClient') as mock_data_client:
        mock_instance = Mock()
        mock_data_client.return_value = mock_instance
        mock_instance.get_stock_bars.side_effect = Exception("API Error")

        provider = AlpacaProvider()

        with pytest.raises(APIError, match="Failed to get historical bars"):
            provider.get_historical_bars(
                symbol="AAPL",
                start_date=date(2025, 3, 1),
                end_date=date(2025, 3, 5),
            )

def test_get_historical_bars_date_boundary():
    """Should handle start_date > end_date gracefully."""
    provider = AlpacaProvider()

    # API should handle this, but we should return empty or raise
    bars = provider.get_historical_bars(
        symbol="AAPL",
        start_date=date(2025, 3, 10),
        end_date=date(2025, 3, 1),  # End before start
    )

    # Should return empty list or let API handle it
    assert isinstance(bars, list)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_providers/test_alpaca_historical_bars.py -v
```

Expected: Fails because method not implemented

- [ ] **Step 3: Implement get_historical_bars**

Add to AlpacaProvider class, also add the imports at top:

```python
# At top of file, add:
from bot_trading.exceptions import APIError, InvalidConfigError

# In AlpacaProvider class, add:

def get_historical_bars(
    self,
    symbol: str,
    start_date: date,
    end_date: date,
    timeframe: str = "1Day"
) -> list[Bar]:
    """Get historical OHLCV bars for a symbol.

    Args:
        symbol: Trading symbol (e.g., "AAPL")
        start_date: Start date for historical data
        end_date: End date for historical data
        timeframe: Bar timeframe ("1Minute", "5Minute", "15Minute", "1Hour", "1Day")

    Returns:
        List of Bar objects with OHLCV data

    Raises:
        APIError: If API call fails
        InvalidConfigError: If timeframe is invalid
    """
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame

    try:
        # Map timeframe string to TimeFrame enum
        timeframe_map = {
            "1Minute": TimeFrame.Minute,
            "5Minute": TimeFrame.FiveMinute,
            "15Minute": TimeFrame.FifteenMinute,
            "1Hour": TimeFrame.Hour,
            "1Day": TimeFrame.Day,
        }

        if timeframe not in timeframe_map:
            raise InvalidConfigError(f"Invalid timeframe: {timeframe}. Valid options: {list(timeframe_map.keys())}")

        tf = timeframe_map[timeframe]

        # Reuse existing credentials to create data client
        data_client = StockHistoricalDataClient(
            api_key=self._api_key,
            secret_key=self._api_secret
        )

        # Request bars
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=tf,
            start=start_date,
            end=end_date
        )

        bars_data = data_client.get_stock_bars(request_params)

        if not bars_data or not hasattr(bars_data, 'data') or symbol not in bars_data.data:
            return []

        bars = []
        for bar_data in bars_data.data[symbol]:
            bars.append(Bar(
                symbol=symbol,
                timestamp=bar_data.timestamp,
                open=Decimal(str(bar_data.open)),
                high=Decimal(str(bar_data.high)),
                low=Decimal(str(bar_data.low)),
                close=Decimal(str(bar_data.close)),
                volume=int(bar_data.volume)
            ))

        return bars

    except InvalidConfigError:
        raise
    except APIError:
        raise
    except Exception as e:
        raise APIError(f"Failed to get historical bars: {e}")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_providers/test_alpaca_historical_bars.py -v
```

Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/bot_trading/providers/alpaca.py tests/test_providers/test_alpaca_historical_bars.py
git commit -m "feat: implement get_historical_bars in AlpacaProvider

Add historical OHLCV bar retrieval:
- Support multiple timeframes (1Min, 5Min, 15Min, 1Hour, 1Day)
- Convert API response to Bar dataclass
- Handle empty results gracefully
- Use Decimal for price precision
- Reuse existing credentials for data client

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 3: MockProvider for Testing

This chunk creates a mock provider for testing without API calls.

### Task 3.1: Create MockProvider

**Files:**
- Create: `src/bot_trading/providers/mock.py`
- Test: `tests/test_providers/test_mock.py`

**Note:** Existing models use Decimal for quantity.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_providers/test_mock.py
from datetime import date, datetime, timedelta
from decimal import Decimal
from bot_trading.providers.mock import MockProvider
from bot_trading.providers.base import Bar, Account, Position, Order

def test_mock_provider_initialization():
    """MockProvider should initialize with default values."""
    provider = MockProvider()

    assert provider is not None
    assert provider.balance == Decimal("100000")

def test_mock_provider_get_account():
    """Should return Account with current balance."""
    provider = MockProvider()
    account = provider.get_account()

    assert isinstance(account, Account)
    assert account.cash == Decimal("100000")
    assert account.buying_power == Decimal("100000")

def test_mock_provider_get_positions_empty():
    """Should return empty list initially."""
    provider = MockProvider()
    positions = provider.get_positions()

    assert positions == []

def test_mock_provider_get_latest_price():
    """Should return price for known symbols."""
    provider = MockProvider()

    price = provider.get_latest_price("AAPL")
    assert price == Decimal("150.00")

    price = provider.get_latest_price("TSLA")
    assert price == Decimal("250.00")

def test_mock_provider_get_historical_bars():
    """Should return generated bar data."""
    provider = MockProvider()
    bars = provider.get_historical_bars(
        symbol="AAPL",
        start_date=date(2025, 3, 1),
        end_date=date(2025, 3, 5)
    )

    assert len(bars) > 0
    for bar in bars:
        assert isinstance(bar, Bar)
        assert bar.symbol == "AAPL"

def test_mock_provider_get_order_history():
    """Should return empty order history initially."""
    provider = MockProvider()
    orders = provider.get_order_history(days=7)

    assert orders == []

def test_mock_provider_state_persistence():
    """Should maintain state between submit_order and get_positions."""
    provider = MockProvider()

    # Submit a buy order
    order = provider.submit_order("AAPL", "buy", Decimal("10"))

    # Check position is updated
    positions = provider.get_positions()
    assert len(positions) == 1
    assert positions[0].symbol == "AAPL"
    assert positions[0].quantity == Decimal("10")

def test_mock_provider_decimal_precision():
    """Should maintain Decimal precision for prices."""
    provider = MockProvider()

    price = provider.get_latest_price("AAPL")
    assert isinstance(price, Decimal)
    assert price.as_tuple().exponent >= -2  # At least 2 decimal places
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_providers/test_mock.py -v
```

Expected: `ModuleNotFoundError: No module named 'bot_trading.providers.mock'`

- [ ] **Step 3: Create MockProvider**

```python
# src/bot_trading/providers/mock.py
"""Mock provider for testing without API calls."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from random import Random
from typing import Optional

from bot_trading.providers.base import (
    BaseProvider,
    Account,
    Position,
    Order,
    Bar,
)


class MockProvider(BaseProvider):
    """Mock provider for testing and development.

    Provides realistic mock data without requiring API credentials.
    Note: Skips weekends but does not account for exchange holidays.
    """

    # Default mock prices
    DEFAULT_PRICES = {
        "AAPL": Decimal("150.00"),
        "TSLA": Decimal("250.00"),
        "MSFT": Decimal("380.00"),
        "GOOGL": Decimal("140.00"),
        "AMZN": Decimal("180.00"),
    }

    def __init__(
        self,
        balance: Decimal = Decimal("100000"),
        prices: Optional[dict[str, Decimal]] = None
    ):
        """Initialize MockProvider.

        Args:
            balance: Starting account balance
            prices: Custom price map (uses DEFAULT_PRICES if None)
        """
        self.balance = balance
        self._prices = prices or self.DEFAULT_PRICES
        self._positions: dict[str, Decimal] = {}
        self._orders: list[Order] = []
        self._rng = Random(42)  # Fixed seed for reproducibility

    def get_account(self) -> Account:
        """Get current account information."""
        total_value = self.balance
        for symbol, quantity in self._positions.items():
            price = self._prices.get(symbol, Decimal("100"))
            total_value += price * quantity

        return Account(
            equity=total_value,
            cash=self.balance,
            portfolio_value=total_value,
            buying_power=self.balance
        )

    def get_positions(self) -> list[Position]:
        """Get current positions."""
        positions = []
        for symbol, quantity in self._positions.items():
            if quantity > 0:
                price = self._prices.get(symbol, Decimal("100"))
                positions.append(Position(
                    symbol=symbol,
                    quantity=quantity,
                    avg_entry_price=price,
                    current_price=price,
                    market_value=price * quantity
                ))
        return positions

    def get_latest_price(self, symbol: str) -> Decimal:
        """Get latest price for a symbol."""
        if symbol not in self._prices:
            # Generate random price for unknown symbols
            self._prices[symbol] = Decimal(str(100 + self._rng.random() * 100))
        return self._prices[symbol]

    def get_historical_bars(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        timeframe: str = "1Day"
    ) -> list[Bar]:
        """Get historical OHLCV bars.

        Note: Skips weekends (Mon-Fri only) but does not account for holidays.
        """
        bars = []
        current_date = start_date
        base_price = float(self.get_latest_price(symbol))

        while current_date <= end_date:
            # Skip weekends (weekday() < 5 means Mon-Fri)
            if current_date.weekday() < 5:
                # Generate realistic price movement
                day_offset = (current_date - start_date).days
                daily_change = (self._rng.random() - 0.5) * 0.02  # ±1% daily
                day_price = base_price * (1 + daily_change * day_offset * 0.1)

                open_price = day_price * (1 + (self._rng.random() - 0.5) * 0.01)
                high_price = max(open_price, day_price) * (1 + self._rng.random() * 0.005)
                low_price = min(open_price, day_price) * (1 - self._rng.random() * 0.005)
                close_price = day_price
                volume = int(self._rng.random() * 1000000 + 500000)

                bars.append(Bar(
                    symbol=symbol,
                    timestamp=datetime.combine(current_date, datetime.min.time()),
                    open=Decimal(f"{open_price:.2f}"),
                    high=Decimal(f"{high_price:.2f}"),
                    low=Decimal(f"{low_price:.2f}"),
                    close=Decimal(f"{close_price:.2f}"),
                    volume=volume
                ))

            current_date += timedelta(days=1)

        return bars

    def get_order_history(self, days: int = 7) -> list[Order]:
        """Get order history."""
        cutoff = datetime.now() - timedelta(days=days)
        return [o for o in self._orders if o.created_at >= cutoff]

    def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        order_type: str = "market",
        price: Optional[Decimal] = None
    ) -> Order:
        """Submit a new order."""
        order = Order(
            order_id=f"mock-{len(self._orders) + 1}",
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            status="filled",
            created_at=datetime.now()
        )
        self._orders.append(order)

        # Update position
        if side == "buy":
            self._positions[symbol] = self._positions.get(symbol, Decimal("0")) + quantity
            self.balance -= self.get_latest_price(symbol) * quantity
        else:
            self._positions[symbol] = self._positions.get(symbol, Decimal("0")) - quantity
            self.balance += self.get_latest_price(symbol) * quantity

        return order

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order (mock - always returns True)."""
        return True

    def list_open_orders(self) -> list[Order]:
        """List open orders (mock - returns empty list)."""
        return []
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_providers/test_mock.py -v
```

Expected: All 9 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/bot_trading/providers/mock.py tests/test_providers/test_mock.py
git commit -m "feat: add MockProvider for testing

Create mock provider for development/testing:
- Realistic mock data without API calls
- Configurable balance and prices
- Generates historical bars with price variation
- Tracks positions and orders locally
- Fixed random seed for reproducibility
- Uses Decimal for all quantities
- Note: Skips weekends but not holidays

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Chunk 4: Integration Tests and Documentation

### Task 4.1: Create Integration Tests

**Files:**
- Create: `tests/integration/test_alpaca_integration.py`

- [ ] **Step 1: Write integration test**

```python
# tests/integration/test_alpaca_integration.py
"""Integration tests for AlpacaProvider.

These tests require valid API credentials and will be skipped
in CI/CD unless credentials are available.
"""

import os
import pytest
from datetime import date, datetime
from decimal import Decimal

from bot_trading.providers.alpaca import AlpacaProvider
from bot_trading.exceptions import APIError


@pytest.mark.skipif(
    not all([
        os.getenv("ALPACA_API_KEY"),
        os.getenv("ALPACA_API_SECRET"),
    ]),
    reason="Alpaca credentials not available"
)
def test_alpaca_real_connection():
    """Test real connection to Alpaca Paper Trading API."""
    provider = AlpacaProvider()

    # Should not raise
    account = provider.get_account()
    assert account is not None
    assert account.cash >= 0


@pytest.mark.skipif(
    not all([
        os.getenv("ALPACA_API_KEY"),
        os.getenv("ALPACA_API_SECRET"),
    ]),
    reason="Alpaca credentials not available"
)
def test_alpaca_get_real_historical_data():
    """Test fetching real historical data."""
    provider = AlpacaProvider()

    bars = provider.get_historical_bars(
        symbol="AAPL",
        start_date=date(2025, 3, 1),
        end_date=date(2025, 3, 5),
        timeframe="1Day"
    )

    # Should have data for these trading days
    assert len(bars) > 0
    assert bars[0].symbol == "AAPL"
    assert bars[0].close > 0


@pytest.mark.skipif(
    not all([
        os.getenv("ALPACA_API_KEY"),
        os.getenv("ALPACA_API_SECRET"),
    ]),
    reason="Alpaca credentials not available"
)
def test_alpaca_paper_url_only(monkeypatch):
    """Should only connect to paper trading URL."""
    # Use monkeypatch for safer env var handling
    monkeypatch.setenv("ALPACA_BASE_URL", "https://api.alpaca.markets")

    with pytest.raises(ValueError, match="Refusing to connect"):
        AlpacaProvider()
```

- [ ] **Step 2: Run test to verify it passes**

```bash
pytest tests/integration/test_alpaca_integration.py -v
```

Expected: Tests are skipped unless credentials available

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_alpaca_integration.py
git commit -m "test: add Alpaca integration tests

Add integration tests for AlpacaProvider:
- Real API connection test
- Historical data fetch test
- Paper trading URL validation
- Tests skipped without credentials
- Use pytest monkeypatch for env var handling

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 4.2: Update pyproject.toml Dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Update dependencies**

Edit pyproject.toml:

```toml
[project]
name = "bot-trading"
version = "0.2.0"
requires-python = ">=3.11"
dependencies = [
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0",
    "requests>=2.31.0",
    "alpaca-trade-api>=3.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]

analysis = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
]
```

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "chore: update dependencies for Phase 0

Update version to 0.2.0
Add analysis optional dependencies for future phases

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

### Task 4.3: Run All Tests

- [ ] **Step 1: Run full test suite**

```bash
pytest tests/ -v --cov=bot_trading --cov-report=html
```

Expected: All tests pass with coverage > 80%

- [ ] **Step 2: Run linting**

```bash
ruff check src/ tests/
ruff format src/ tests/
```

Expected: No linting errors

- [ ] **Step 3: Commit any fixes**

```bash
git add .
git commit -m "chore: fix linting issues and improve test coverage"
```

---

## Completion Checklist

After completing all tasks:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage > 80%: `pytest --cov=bot_trading --cov-report=html`
- [ ] No linting errors: `ruff check src/ tests/`
- [ ] Code formatted: `ruff format src/ tests/`
- [ ] Git tag created: `v0.1.0-scaffold`

---

## Phase 0 Summary

**Files Created:**
- `src/bot_trading/exceptions.py` - Custom exception types
- `src/bot_trading/providers/mock.py` - Mock provider for testing
- `tests/test_exceptions.py` - Exception tests
- `tests/test_providers/test_base_models.py` - Data model tests
- `tests/test_providers/test_base_abstract_methods.py` - Interface tests
- `tests/test_providers/test_alpaca_order_history.py` - Order history tests
- `tests/test_providers/test_alpaca_historical_bars.py` - Historical bars tests
- `tests/test_providers/test_mock.py` - Mock provider tests
- `tests/integration/test_alpaca_integration.py` - Integration tests

**Files Modified:**
- `src/bot_trading/providers/base.py` - Added Bar, EquityPoint, new abstract methods
- `src/bot_trading/providers/alpaca.py` - Implemented get_order_history, get_historical_bars
- `pyproject.toml` - Updated version to 0.2.0

**Key Decisions:**
- Use Decimal for all price/quantity fields (consistent with existing code)
- Match existing Order model (order_id, created_at)
- Reuse credentials for data client (avoid duplicate connections)
- MockProvider skips weekends but not holidays (documented limitation)

**Next Phase:** Phase 1 will build on this foundation to add technical indicators and strategy management.

---

## Rollback Instructions

If any task fails critically:

```bash
# Reset to scaffold baseline
git reset --hard v0.1.0-scaffold

# Or reset to last working commit
git reset --hard HEAD~1
```

Then review the failure, fix the plan, and restart.
