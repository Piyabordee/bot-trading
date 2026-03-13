# Trading Analysis Tool - Design Document

**Date:** 2025-03-14
**Author:** Design Specification
**Status:** Revised v2 (after review)

---

## 1. Overview

### 1.1 Purpose

A manual-trigger trading analysis tool for users who:
- Work during the day and run analysis when coming home
- Find trading strategies from YouTube/Blog (cannot code)
- Want to see market data, positions, and signals before deciding
- Do NOT want auto-trading - manual decision only
- Want risk analysis with maximum 10% per trade

### 1.2 Key Requirements

| Requirement | Description |
|-------------|-------------|
| **Manual Trigger** | User runs `python main.py` when they want to analyze |
| **No Auto Trading** | Tool only analyzes and recommends - user decides |
| **Data Source** | Alpaca Paper Trading API (free, real data) |
| **Risk Limit** | Maximum 10% of portfolio per trade |
| **Output** | Console display + JSON file save |
| **Input** | User selects from pre-defined strategies with parameter config |

### 1.3 What This is NOT

- ❌ Auto-trading bot
- ❌ Scheduled execution
- ❌ Real-time monitoring system
- ❌ Production trading system

---

## 2. Architecture

### 2.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLI Interface (main.py)                    │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  1. Dashboard Display (Market + Positions + Orders)           │ │
│  │  2. Mode Selection Menu                                        │ │
│  │  3. Result Display (Console + File Save)                      │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Backtest     │   │   Signal      │   │   Calculator  │
│    Engine     │   │   Analyzer    │   │              │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────────┐
        │         Core Components                     │
        │  ┌───────────────────────────────────────┐  │
        │  │  AlpacaProvider (API Integration)     │  │
        │  │  - get_account()                      │  │
        │  │  - get_positions()                    │  │
        │  │  - get_latest_price()                 │  │
        │  │  - get_order_history()                │  │
        │  │  - get_historical_bars()              │  │
        │  └───────────────────────────────────────┘  │
        │  ┌───────────────────────────────────────┐  │
        │  │  StrategyManager                      │  │
        │  │  - List pre-defined strategies        │  │
        │  │  - Load strategy with config          │  │
        │  └───────────────────────────────────────┘  │
        │  ┌───────────────────────────────────────┐  │
        │  │  TechnicalIndicators                  │  │
        │  │  - RSI, SMA, EMA, MACD, Bollinger     │  │
        │  └───────────────────────────────────────┘  │
        │  ┌───────────────────────────────────────┐  │
        │  │  RiskCalculator                      │  │
        │  │  - Position sizing                    │  │
        │  │  - Risk calculation (max 10%)         │  │
        │  └───────────────────────────────────────┘  │
        └─────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Alpaca Paper    │
                    │  Trading API     │
                    └─────────────────┘
```

### 2.2 Data Flow

```
User Launch → Fetch Data → Display Dashboard → Select Mode
                                                    │
                                    ┌───────────────┼───────────────┐
                                    ▼               ▼               ▼
                              [Backtest]      [Signal]      [Calculator]
                                    │               │               │
                                    ▼               ▼               ▼
                            Historical     Current        What-if
                            Analysis       Analysis       Calculation
                                    │               │               │
                                    └───────────────┼───────────────┘
                                                    ▼
                                          Display Results
                                                    │
                                          Save to JSON
                                                    ▼
                                          User Decides
                                           (Manual)
```

---

## 3. Data Models

### 3.1 Enhanced BaseProvider Interface

**File:** `src/bot_trading/providers/base.py` (MODIFY)

**Add new data models:**

```python
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

@dataclass
class Bar:
    """OHLCV price bar."""
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
    returns_pct: Decimal  # Returns from start
```

**Add new abstract methods to BaseProvider:**

```python
class BaseProvider(ABC):
    # ... existing methods ...

    @abstractmethod
    def get_order_history(self, days: int = 7) -> list[Order]:
        """Get order history for the last N days."""
        pass

    @abstractmethod
    def get_historical_bars(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        timeframe: str = "1Day"
    ) -> list[Bar]:
        """Get historical OHLCV bars."""
        pass
```

### 3.2 Analysis Result Models

**File:** `src/bot_trading/analysis/models.py` (NEW)

```python
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import TypedDict

@dataclass
class BacktestResult:
    """Results from backtesting a strategy."""
    strategy_name: str
    symbol: str
    start_date: date
    end_date: date

    # Performance metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: Decimal  # 0.0 to 1.0

    total_return: Decimal  # Total profit/loss amount
    total_return_pct: Decimal  # Percentage return

    max_drawdown: Decimal
    max_drawdown_pct: Decimal

    sharpe_ratio: Decimal
    sortino_ratio: Decimal

    # Trade history
    trades: list[Trade]

    # Equity curve
    equity_curve: list[EquityPoint]


@dataclass
class AnalysisResult:
    """Results from current market analysis."""
    symbol: str
    timestamp: datetime

    # Signal
    signal: str  # "BUY", "SELL", "HOLD"
    confidence: Decimal  # 0.0 to 1.0
    reason: str

    # Price info
    current_price: Decimal
    target_price: Decimal | None
    stop_loss_price: Decimal | None

    # Risk
    position_size: int  # Recommended shares
    position_value: Decimal
    risk_amount: Decimal
    risk_pct_of_portfolio: Decimal  # 0.0 to 0.10 max

    # Indicators
    indicators: dict[str, Decimal]  # RSI, MA values, etc.


@dataclass
class RiskReport:
    """Report from position risk calculation."""
    symbol: str
    quantity: int
    entry_price: Decimal
    stop_loss_price: Decimal
    take_profit_price: Decimal

    # Position value
    position_value: Decimal

    # Risk analysis
    risk_per_share: Decimal
    total_risk: Decimal
    risk_pct_of_portfolio: Decimal

    # Recommendations
    max_shares_at_10pct: int
    recommended_quantity: int

    # Scenarios
    scenario_5pct_gain: Decimal
    scenario_5pct_loss: Decimal
    scenario_10pct_loss: Decimal


@dataclass
class Trade:
    """Single trade record."""
    entry_date: date
    exit_date: date | None  # None if still open
    action: str  # "BUY" or "SELL"
    entry_price: Decimal
    exit_price: Decimal | None
    quantity: int
    pnl: Decimal  # Profit/loss (closed) or unrealized (open)
    pnl_pct: Decimal
```

### 3.3 Exception Types

**File:** `src/bot_trading/exceptions.py` (NEW)

```python
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

---

## 4. Components

### 4.1 AlpacaProvider (Enhanced)

**File:** `src/bot_trading/providers/alpaca.py` (MODIFY)

**Purpose:** Connect to Alpaca Paper Trading API for real market data

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `get_account()` | `Account` | Current account balance, buying power |
| `get_positions()` | `list[Position]` | All current holdings |
| `get_latest_price(symbol)` | `Decimal` | Current market price |
| `get_order_history(days=7)` | `list[Order]` | Recent filled orders |
| `get_historical_bars(symbol, start, end, timeframe)` | `list[Bar]` | Historical OHLCV data |

**Dependencies:** Uses `alpaca-trade-api` (already in pyproject.toml)

**Safety:** `submit_order()` and `cancel_order()` raise `NotImplementedError`

### 4.2 StrategyManager

**File:** `src/bot_trading/strategy/manager.py` (NEW)

**Purpose:** Manage pre-defined trading strategies

**Simplified Approach:**
- Strategies are pre-defined Python classes
- Configuration via YAML/JSON files
- No markdown-to-Python conversion (too complex/risky)

**Strategy Config Format (YAML):**

```yaml
# docs/strategies/rsi_mean_reversion.yml
name: "RSI Mean Reversion"
description: "Buy when RSI < 30, sell when RSI > 70"
class_name: "RSIMeanReversionStrategy"

parameters:
  rsi_period: 14
  buy_threshold: 30
  sell_threshold: 70
  stop_loss_pct: 5
  take_profit_pct: 10
  max_position_pct: 10

indicators:
  - rsi
  - sma
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `list_strategies()` | `list[str]` | List available strategies |
| `load_strategy(name)` | `BaseStrategy` | Load strategy by name |
| `get_strategy_config(name)` | `dict` | Get strategy parameters |

### 4.3 TechnicalIndicators

**File:** `src/bot_trading/strategy/indicators.py` (NEW)

**Purpose:** Calculate technical indicators for strategy analysis

**All calculations use Decimal for precision:**

| Indicator | Parameters | Returns | Description |
|-----------|------------|---------|-------------|
| `rsi(prices, period)` | period: int | Decimal | Relative Strength Index |
| `sma(prices, period)` | period: int | Decimal | Simple Moving Average |
| `ema(prices, period)` | period: int | Decimal | Exponential Moving Average |
| `macd(prices, fast, slow, signal)` | fast, slow, signal: int | tuple | MACD line, signal, histogram |
| `bollinger_bands(prices, period, std_dev)` | period, std_dev: int | tuple | Upper, middle, lower bands |
| `atr(highs, lows, closes, period)` | period: int | Decimal | Average True Range |

### 4.4 BacktestEngine

**File:** `src/bot_trading/backtest/engine.py` (NEW)

**Purpose:** Run strategy on historical data

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `run_backtest(strategy, symbol, start, end)` | `BacktestResult` | Full backtest analysis |

**Backtesting Methodology:**

```
For each bar in historical data:
    1. Calculate indicators up to current bar
    2. Check strategy entry/exit conditions
    3. If entry signal and no position:
       - Calculate position size (max 10% of portfolio)
       - Record entry trade
    4. If exit signal and position open:
       - Record exit trade with P&L
    5. Track equity curve

Assumptions:
    - Market orders fill at next bar's open price
    - No slippage initially
    - No commission initially
    - Position sizing: Fixed % of portfolio per trade
```

### 4.5 SignalAnalyzer

**File:** `src/bot_trading/analysis/analyzer.py` (NEW)

**Purpose:** Analyze current market conditions and generate signals

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `analyze_current(strategy, symbol)` | `AnalysisResult` | Current signal analysis |

**Process:**
1. Fetch latest bars for indicator calculation
2. Calculate all required indicators
3. Evaluate strategy conditions
4. Generate BUY/SELL/HOLD signal
5. Calculate recommended position size
6. Assess risk

### 4.6 RiskCalculator

**File:** `src/bot_trading/analysis/calculator.py` (NEW)

**Purpose:** Calculate position risk for "what-if" scenarios

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `calculate_position_risk(symbol, quantity, entry_price, stop_loss_pct)` | `RiskReport` | Full risk analysis |
| `calculate_max_shares(portfolio_value, risk_pct, stop_loss_pct)` | `int` | Max shares at risk level |

**All values use Decimal for precision**

---

## 5. User Interface

### 5.1 Dashboard Display

```
╔═══════════════════════════════════════════════════════════════════╗
║              🤖 TRADING ANALYSIS BOT v1.0                        ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  📊 MARKET SNAPSHOT                     2025-03-14 18:30:15      ║
║  ─────────────────────────────────────────────────────────────  ║
║  AAPL:  $150.25  ▲ +1.2%    🟢 Strong Buy                        ║
║  TSLA:  $245.80  ▼ -0.5%    🟡 Hold                              ║
║  MSFT:  $380.50  ▲ +0.8%    🟢 Buy                               ║
║                                                                   ║
║  💼 YOUR PORTFOLIO                                                  ║
║  ─────────────────────────────────────────────────────────────  ║
║  Cash:          $98,500.00                                        ║
║  AAPL (10):     $1,502.50  (P/L: +$22.50  +1.5%)                 ║
║  Total Value:   $100,002.50                                       ║
║                                                                   ║
║  📜 RECENT ORDERS                                                  ║
║  ─────────────────────────────────────────────────────────────  ║
║  2025-03-10  BUY   AAPL  10  @ $148.00  →  Filled               ║
║  2025-03-08  SELL  TSLA  5   @ $250.00  →  Filled (+$400)        ║
║                                                                   ║
╠═══════════════════════════════════════════════════════════════════╣
║  🤖 What would you like to do?                                    ║
║                                                                   ║
║  [1] 📈 Run Strategy Backtest                                     ║
║  [2] 🎯 Check Current Signals                                     ║
║  [3] 🧮 Calculate Position Risk                                   ║
║  [4] 📋 Manage Strategies                                         ║
║  [5] 🚪 Exit                                                      ║
║                                                                   ║
║  Select: _                                                        ║
╚═══════════════════════════════════════════════════════════════════╝
```

**Market Snapshot Data Source:**
- Default symbols: AAPL, TSLA, MSFT (configurable in .env)
- Fetch from AlpacaProvider.get_latest_price()
- Optional: Add previous close for % change calculation

### 5.2 Backtest Result Display

```
╔═══════════════════════════════════════════════════════════════════╗
║  📈 BACKTEST RESULTS                                              ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  Strategy:    RSI Mean Reversion                                 ║
║  Symbol:      AAPL                                               ║
║  Period:      2025-02-14 to 2025-03-14 (30 days)                 ║
║                                                                   ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                   ║
║  Total Trades:           15                                      ║
║  Winning Trades:         9  (60%)                                ║
║  Losing Trades:          6  (40%)                                ║
║                                                                   ║
║  Total Return:           +$850.00                                ║
║  Total Return %:         +8.5%                                   ║
║                                                                   ║
║  Max Drawdown:           -$3,200.00                              ║
║  Max Drawdown %:         -3.2%                                   ║
║                                                                   ║
║  Sharpe Ratio:           1.2                                     ║
║  Sortino Ratio:          1.8                                     ║
║                                                                   ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                   ║
║  ✅ Results saved to: results/backtest_20250314_183000.json       ║
║                                                                   ║
║  [Enter] Continue  [V] View Trades  [Esc] Back to Menu           ║
╚═══════════════════════════════════════════════════════════════════╝
```

### 5.3 Signal Analysis Display

```
╔═══════════════════════════════════════════════════════════════════╗
║  🎯 SIGNAL ANALYSIS                                               ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  Strategy:    RSI Mean Reversion                                 ║
║  Symbol:      AAPL                                               ║
║  Timestamp:   2025-03-14 18:30:15                                ║
║                                                                   ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                   ║
║  SIGNAL:           🟢 BUY                                        ║
║  Confidence:       75%                                           ║
║                                                                   ║
║  Current Price:    $150.25                                        ║
║  Target Price:     $165.00 (+10%)                                ║
║  Stop Loss:        $142.50 (-5%)                                 ║
║                                                                   ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                   ║
║  Recommended Position:                                            ║
║  ─────────────────────────────────────────────────────────────  ║
║  Quantity:         10 shares                                     ║
║  Position Value:   $1,502.50                                     ║
║  Risk Amount:      $75.00 (if stop loss hit)                     ║
║  Risk % of Portfolio: 0.75% ✅ (within 10% limit)                 ║
║                                                                   ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                   ║
║  Indicators:                                                      ║
║  • RSI(14): 28.5 (oversold)                                      ║
║  • SMA(20): $148.50 (price above)                                ║
║  • Trend: Bullish                                                ║
║                                                                   ║
║  Reason:                                                           ║
║  RSI is below 30 (oversold) and price is above SMA(20),          ║
║  suggesting a mean reversion play.                               ║
║                                                                   ║
║  ✅ Results saved to: results/signal_20250314_183000.json         ║
║                                                                   ║
║  [Enter] Continue  [Esc] Back to Menu                            ║
╚════════════════════════════════════━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╝
```

### 5.4 Risk Calculator Display

```
╔═══════════════════════════════════════════════════════════════════╗
║  🧮 POSITION RISK CALCULATOR                                      ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  Enter symbol: AAPL                                               ║
║  Enter quantity: 20                                               ║
║  Enter entry price: 150.00                                        ║
║  Enter stop loss %: 5                                             ║
║                                                                   ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                   ║
║  POSITION SUMMARY                                                 ║
║  ─────────────────────────────────────────────────────────────  ║
║  Symbol:           AAPL                                           ║
║  Quantity:         20 shares                                     ║
║  Entry Price:      $150.00                                        ║
║  Position Value:   $3,000.00                                     ║
║                                                                   ║
║  RISK ANALYSIS                                                     ║
║  ─────────────────────────────────────────────────────────────  ║
║  Stop Loss Price:  $142.50                                       ║
║  Risk Per Share:  $7.50                                          ║
║  Total Risk:       $150.00                                       ║
║  Risk % of Portfolio: 1.5% ✅                                    ║
║                                                                   ║
║  RECOMMENDATIONS                                                  ║
║  ─────────────────────────────────────────────────────────────  ║
║  Max shares at 10% risk: 66 shares                                ║
║  Recommended quantity: 20 shares ✅                              ║
║                                                                   ║
║  SCENARIOS                                                         ║
║  ─────────────────────────────────────────────────────────────  ║
║  +5% gain:        +$150.00                                       ║
║  +10% gain:       +$300.00                                       ║
║  -5% loss:        -$150.00                                       ║
║  -10% loss:       -$300.00                                       ║
║                                                                   ║
║  ✅ Results saved to: results/risk_20250314_183000.json            ║
║                                                                   ║
║  [Enter] Continue  [Esc] Back to Menu                            ║
╚══════════════════════════━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╝
```

---

## 6. Error Handling

### 6.1 Error Categories

| Error Type | Exception | Message | Action |
|------------|-----------|---------|--------|
| **API Connection** | `APIError` | "Cannot connect to Alpaca API" | Check internet/credentials, offer retry |
| **Invalid Credentials** | `APIError` | "Invalid API credentials" | Check .env file |
| **No Data Found** | `InsufficientDataError` | "No data found for {symbol}" | Check symbol, suggest valid symbols |
| **Invalid Input** | `InvalidConfigError` | "Invalid input: {reason}" | Prompt for correct input |
| **Risk Too High** | `RiskLimitExceededError` | "Risk exceeds 10% of portfolio" | Suggest lower quantity |
| **Strategy Not Found** | `StrategyNotFoundError` | "Strategy not found: {name}" | List available strategies |
| **Insufficient Data** | `InsufficientDataError` | "Not enough data for backtest" | Suggest longer period |

### 6.2 Error Recovery Pattern

```python
from bot_trading.exceptions import (
    APIError,
    InsufficientDataError,
    StrategyNotFoundError,
    RiskLimitExceededError,
    InvalidConfigError,
)

def safe_execute(func):
    """Wrapper for safe execution with user-friendly errors."""
    try:
        return func()
    except APIError as e:
        logger.error(f"API Error: {e}")
        print(f"\n❌ Cannot connect to Alpaca API")
        print("Please check:")
        print("  1. Internet connection")
        print("  2. API credentials in .env file")
        return prompt_retry_or_exit()
    except InsufficientDataError as e:
        print(f"\n⚠️  {e}")
        print("Please select a longer time period")
        return prompt_new_period()
    except StrategyNotFoundError as e:
        print(f"\n❌ {e}")
        list_available_strategies()
        return prompt_retry_or_exit()
    except RiskLimitExceededError as e:
        print(f"\n⚠️  {e}")
        return suggest_lower_quantity()
```

---

## 7. Sample Strategies

### 7.1 RSI Mean Reversion

**File:** `src/bot_trading/strategy/strategies/rsi_mean_reversion.py`

```python
from decimal import Decimal
from bot_trading.strategy.base import BaseStrategy, Signal
from bot_trading.strategy.indicators import rsi, sma

class RSIMeanReversionStrategy(BaseStrategy):
    """Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought)."""

    def __init__(
        self,
        symbol: str,
        rsi_period: int = 14,
        buy_threshold: int = 30,
        sell_threshold: int = 70,
        stop_loss_pct: int = 5,
        take_profit_pct: int = 10,
    ):
        self.symbol = symbol
        self.rsi_period = rsi_period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    def generate_signals(self, bars: list[Bar]) -> list[Signal]:
        """Generate signals based on RSI mean reversion."""
        if len(bars) < self.rsi_period + 1:
            return []  # Not enough data

        # Calculate indicators
        closes = [bar.close for bar in bars]
        current_rsi = rsi(closes, self.rsi_period)
        sma_20 = sma(closes, 20)
        current_price = bars[-1].close

        signals = []

        # Buy signal: RSI oversold and price above SMA
        if current_rsi < self.buy_threshold and current_price > sma_20:
            signals.append(Signal(
                symbol=self.symbol,
                action="buy",
                confidence=Decimal("0.75"),
                reason=f"RSI({self.rsi_period}) is {current_rsi} (oversold), "
                       f"price above SMA(20)"
            ))

        # Sell signal: RSI overbought
        elif current_rsi > self.sell_threshold:
            signals.append(Signal(
                symbol=self.symbol,
                action="sell",
                confidence=Decimal("0.70"),
                reason=f"RSI({self.rsi_period}) is {current_rsi} (overbought)"
            ))

        return signals
```

**Config File:** `docs/strategies/rsi_mean_reversion.yml`

```yaml
name: "RSI Mean Reversion"
description: "Buy when RSI < 30, sell when RSI > 70"
class_name: "RSIMeanReversionStrategy"

parameters:
  rsi_period: 14
  buy_threshold: 30
  sell_threshold: 70
  stop_loss_pct: 5
  take_profit_pct: 10
```

### 7.2 SMA Crossover

**File:** `src/bot_trading/strategy/strategies/sma_crossover.py`

```python
class SMACrossoverStrategy(BaseStrategy):
    """Buy when SMA(50) crosses above SMA(200) (Golden Cross)."""

    def __init__(
        self,
        symbol: str,
        fast_period: int = 50,
        slow_period: int = 200,
    ):
        self.symbol = symbol
        self.fast_period = fast_period
        self.slow_period = slow_period

    def generate_signals(self, bars: list[Bar]) -> list[Signal]:
        """Generate signals based on SMA crossover."""
        if len(bars) < self.slow_period + 1:
            return []

        closes = [bar.close for bar in bars]
        fast_sma = sma(closes, self.fast_period)
        prev_fast_sma = sma(closes[:-1], self.fast_period)
        slow_sma = sma(closes, self.slow_period)
        prev_slow_sma = sma(closes[:-1], self.slow_period)

        signals = []

        # Golden Cross: Fast SMA crosses above Slow SMA
        if fast_sma > slow_sma and prev_fast_sma <= prev_slow_sma:
            signals.append(Signal(
                symbol=self.symbol,
                action="buy",
                confidence=Decimal("0.80"),
                reason=f"Golden Cross: SMA({self.fast_period}) crossed above SMA({self.slow_period})"
            ))

        # Death Cross: Fast SMA crosses below Slow SMA
        elif fast_sma < slow_sma and prev_fast_sma >= prev_slow_sma:
            signals.append(Signal(
                symbol=self.symbol,
                action="sell",
                confidence=Decimal("0.75"),
                reason=f"Death Cross: SMA({self.fast_period}) crossed below SMA({self.slow_period})"
            ))

        return signals
```

**Config File:** `docs/strategies/sma_crossover.yml`

```yaml
name: "SMA Crossover"
description: "Buy on Golden Cross (SMA50 > SMA200)"
class_name: "SMACrossoverStrategy"

parameters:
  fast_period: 50
  slow_period: 200
```

---

## 8. File Structure

```
bot-trading/
├── src/bot_trading/
│   ├── __init__.py
│   ├── config.py                              ✅ Existing
│   ├── exceptions.py                          🆕 New (custom exceptions)
│   │
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                            ⚠️  Modify (add Bar, EquityPoint, new methods)
│   │   ├── alpaca.py                          ⚠️  Modify (implement get_historical_bars, etc.)
│   │   └── mock.py                            ✅ Create (for testing)
│   │
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── base.py                            ✅ Existing
│   │   ├── manager.py                         🆕 New (load strategies)
│   │   ├── indicators.py                      🆕 New (RSI, MA, etc.)
│   │   └── strategies/
│   │       ├── __init__.py
│   │       ├── rsi_mean_reversion.py          🆕 New
│   │       └── sma_crossover.py               🆕 New
│   │
│   ├── analysis/                              🆁 New folder
│   │   ├── __init__.py
│   │   ├── models.py                          🆕 New (result dataclasses)
│   │   ├── analyzer.py                        🆕 New
│   │   └── calculator.py                      🆕 New
│   │
│   ├── backtest/                              🆁 New folder
│   │   ├── __init__.py
│   │   ├── engine.py                          🆕 New
│   │   └── result.py                          🆕 New (merge into models.py)
│   │
│   ├── execution/
│   │   └── executor.py                        ✅ Existing (not used in analysis mode)
│   │
│   ├── risk/
│   │   └── limits.py                          ✅ Existing
│   │
│   └── ui/                                    🆁 New folder
│       ├── __init__.py
│       ├── dashboard.py                       🆕 New
│       └── menus.py                           🆕 New
│
├── docs/strategies/                           🆁 New folder
│   ├── rsi_mean_reversion.yml                📝 Strategy config
│   └── sma_crossover.yml                      📝 Strategy config
│
├── results/                                   🆁 New folder
│   ├── .gitkeep
│   ├── backtest_YYYYMMDD_HHMMSS.json
│   └── signal_YYYYMMDD_HHMMSS.json
│
├── logs/                                      🆁 New folder
│   ├── .gitkeep
│   └── bot_YYYYMMDD.log
│
├── tests/
│   ├── test_analysis/
│   │   ├── __init__.py
│   │   ├── test_analyzer.py
│   │   └── test_calculator.py
│   ├── test_backtest/
│   │   ├── __init__.py
│   │   └── test_engine.py
│   ├── test_strategy/
│   │   ├── __init__.py
│   │   ├── test_manager.py
│   │   └── test_indicators.py
│   └── test_providers/
│       ├── __init__.py
│       ├── test_alpaca.py
│       └── test_mock.py
│
├── main.py                                    ⚠️  Rewrite (CLI interface)
├── .env                                       ✅ Existing
├── pyproject.toml                             ⚠️  Update dependencies
└── README.md                                  ⚠️  Update
```

---

## 9. Output File Formats

### 9.1 Backtest Result JSON

```json
{
  "type": "backtest",
  "timestamp": "2025-03-14T18:30:00",
  "strategy": "rsi_mean_reversion",
  "symbol": "AAPL",
  "period": {
    "start": "2025-02-14",
    "end": "2025-03-14",
    "days": 30
  },
  "results": {
    "total_trades": 15,
    "winning_trades": 9,
    "losing_trades": 6,
    "win_rate": "0.60",
    "total_return": "850.00",
    "total_return_pct": "8.5",
    "max_drawdown": "-3200.00",
    "max_drawdown_pct": "-3.2",
    "sharpe_ratio": "1.2",
    "sortino_ratio": "1.8"
  },
  "trades": [
    {
      "entry_date": "2025-02-15",
      "exit_date": "2025-02-18",
      "action": "BUY",
      "entry_price": "148.00",
      "exit_price": "152.00",
      "quantity": 10,
      "pnl": "40.00",
      "pnl_pct": "2.7"
    }
  ],
  "equity_curve": [
    {"timestamp": "2025-02-14T00:00:00", "value": "100000.00", "returns_pct": "0.0"},
    {"timestamp": "2025-02-15T00:00:00", "value": "100040.00", "returns_pct": "0.04"}
  ]
}
```

**Note:** All numeric values are strings representing Decimal values for precision.

### 9.2 Signal Analysis JSON

```json
{
  "type": "signal",
  "timestamp": "2025-03-14T18:30:00",
  "strategy": "rsi_mean_reversion",
  "symbol": "AAPL",
  "signal": "BUY",
  "confidence": "0.75",
  "current_price": "150.25",
  "target_price": "165.00",
  "stop_loss_price": "142.50",
  "recommended_quantity": 10,
  "position_value": "1502.50",
  "risk_amount": "75.00",
  "risk_pct_of_portfolio": "0.0075",
  "indicators": {
    "rsi_14": "28.5",
    "sma_20": "148.50",
    "sma_50": "147.00"
  },
  "reason": "RSI is below 30 (oversold) and price is above SMA(20)"
}
```

**Note:** `risk_pct_of_portfolio` is stored as decimal (0.0075 = 0.75%).

---

## 10. Implementation Phases

### Phase 0: Foundation API Work (Week 1-2)
**Prerequisite: Current codebase has all methods raising NotImplementedError**

- [ ] Update BaseProvider with new methods and data models
- [ ] Create exceptions module
- [ ] Implement AlpacaProvider fully:
  - [ ] get_historical_bars()
  - [ ] get_order_history()
  - [ ] Error handling
- [ ] Create MockProvider for testing
- [ ] Write comprehensive tests for providers

### Phase 1: Analysis Core (Week 3-4)
- [ ] Create TechnicalIndicators module
- [ ] Create StrategyManager
- [ ] Implement 2 sample strategies (RSI, SMA)
- [ ] Create analysis models
- [ ] Add tests for all above

### Phase 2: Analysis Engines (Week 5-6)
- [ ] Create BacktestEngine with methodology
- [ ] Create SignalAnalyzer
- [ ] Create RiskCalculator
- [ ] Add comprehensive tests
- [ ] Data caching for historical bars

### Phase 3: UI & CLI (Week 7-8)
- [ ] Create CLI interface with main menu
- [ ] Implement Dashboard display
- [ ] Add all mode interfaces
- [ ] Implement file saving
- [ ] Error handling and logging

### Phase 4: Polish & Testing (Week 9-10)
- [ ] End-to-end testing
- [ ] User workflow testing
- [ ] Documentation
- [ ] Performance optimization

**Total Timeline: 10 weeks (2.5 months)**

---

## 11. Testing Strategy

### Unit Tests
- [ ] Each indicator calculation
- [ ] Strategy loading and configuration
- [ ] Risk calculations
- [ ] Backtest logic
- [ ] All data model validations

### Integration Tests
- [ ] Alpaca API connection
- [ ] End-to-end backtest flow
- [ ] End-to-end signal analysis
- [ ] Error recovery flows

### Manual Testing
- [ ] User workflow testing
- [ ] UI/UX validation
- [ ] Error message clarity
- [ ] Performance with real data

---

## 12. Dependencies

**Update pyproject.toml:**

```toml
[project]
name = "bot-trading"
version = "0.2.0"
requires-python = ">=3.11"
dependencies = [
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0",  # For strategy configs
    "requests>=2.31.0",
    "alpaca-trade-api>=3.0.0",  # Existing, keep using this
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]

analysis = [
    "pandas>=2.0.0",  # For data manipulation
    "numpy>=1.24.0",  # For calculations
]
```

---

## 13. Data Caching Strategy

**Purpose:** Reduce API calls and speed up analysis

**Implementation:**
- Cache historical bars locally (pickle or JSON)
- Cache key: `{symbol}_{start_date}_{end_date}_{timeframe}`
- Cache duration: 1 day (market data changes daily)
- Invalidate on weekends

**File:** `src/bot_trading/data/cache.py`

---

## 14. Backtesting Methodology

### 14.1 Assumptions
- Market orders fill at next bar's open price
- No slippage (initially, can add later)
- No commission (initially, can add later)
- Position sizing: Fixed % of portfolio per trade
- Max position: 10% of portfolio

### 14.2 Process
```python
for each bar in historical_data:
    # Calculate indicators with data up to current bar
    indicators = calculate_all(bars[:current_index])

    # Check strategy
    signals = strategy.generate_signals(indicators)

    # Execute if signal and no position
    if signal == "BUY" and not position:
        shares = calculate_position_size(
            portfolio_value,
            max_risk_pct=0.10,
            stop_loss_pct=strategy.stop_loss
        )
        enter_position(symbol, shares, bar.next_open)
        position = Position(symbol, shares, entry_price)

    # Check exit if position open
    elif position and should_exit(position, indicators):
        close_position(position, bar.open)
        portfolio_value += position.pnl
```

---

## 15. Configuration

### 15.1 Environment Variables (.env)

```bash
# Trading Mode (ALWAYS paper)
TRADING_MODE=paper

# Alpaca Paper Trading Credentials
ALPACA_API_KEY=your_key_here
ALPACA_API_SECRET=your_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Risk Management Limits
MAX_POSITION_SIZE=1000
MAX_PORTFOLIO_EXPOSURE=0.2
DAILY_LOSS_LIMIT=500

# Dashboard Settings
WATCHLIST_SYMBOLS=AAPL,TSLA,MSFT,GOOGL,AMZN

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Cache Settings
CACHE_ENABLED=true
CACHE_DIR=cache/
```

### 15.2 User Configuration (~/.bot_trading/config.yml)

**Optional user-specific settings:**

```yaml
# User preferences
user:
  default_symbols:
    - AAPL
    - TSLA
  default_strategy: rsi_mean_reversion
  risk_tolerance: 0.10  # 10% max per trade
```

---

## 16. Security & Safety

### 16.1 Safety Features
- ✅ Paper trading ONLY (no live trading)
- ✅ submit_order() raises NotImplementedError
- ✅ Max 10% risk per trade enforced
- ✅ No secrets in git
- ✅ Input validation on all user inputs

### 16.2 API Security
- Credentials in .env only
- .env in .gitignore
- Validate paper URL only
- No hardcoded keys

### 16.3 Code Generation Safety
**DECISION:** NOT implementing markdown-to-Python conversion due to:
- Code injection risks
- High complexity
- Maintenance burden

**Alternative:** Pre-defined strategies with YAML config for parameters only

---

## 17. Future Enhancements (Out of Scope for MVP)

- Visual charts (matplotlib)
- Multiple timeframe analysis
- Portfolio optimization
- Machine learning strategies
- Real-time streaming data
- Web UI (Flask/FastAPI)
- Paper trading execution (manual trigger)
- More indicators (Ichimoku, Elliott Wave)
- Sentiment analysis integration

---

## 18. Revision History

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2025-03-14 | Initial design |
| v2 | 2025-03-14 | After review: Add Phase 0, fix data models, simplify strategy loading, add exceptions, standardize on Decimal, clarify timeline |

---

## 19. Approval

**Design Status:** ✅ Revised v2 - Ready for implementation planning

**Review Summary:**
- Addressed all critical issues from review
- Added Phase 0 for API foundation work
- Simplified strategy loading (pre-defined + YAML config)
- Added all missing data models
- Standardized on Decimal for all financial values
- Created exceptions module
- Clarified backtesting methodology
- Updated timeline to 10 weeks (realistic)

**Next Step:** Create detailed implementation plan with writing-plans skill
