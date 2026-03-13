# Trading Analysis Tool - Design Document

**Date:** 2025-03-14
**Author:** Design Specification
**Status:** Approved

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
| **Output** | Console display + JSON file save + Visual (if possible) |
| **Input** | User pastes strategy from YouTube/Blog → tool converts to Python |

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
        │  │  - get_historical_data()              │  │
        │  └───────────────────────────────────────┘  │
        │  ┌───────────────────────────────────────┐  │
        │  │  StrategyLoader                       │  │
        │  │  - Load strategies from .md files     │  │
        │  │  - Parse and convert to Python        │  │
        │  └───────────────────────────────────────┘  │
        │  ┌───────────────────────────────────────┐  │
        │  │  TechnicalIndicators                  │  │
        │  │  - RSI, SMA, EMA, MACD, Bollinger     │  │
        │  └───────────────────────────────────────┘  │
        │  ┌───────────────────────────────────────┐  │
        │  │  RiskManager                          │  │
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

## 3. Components

### 3.1 AlpacaProvider (Enhanced)

**File:** `src/bot_trading/providers/alpaca.py`

**Purpose:** Connect to Alpaca Paper Trading API for real market data

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `get_account()` | `Account` | Current account balance, buying power |
| `get_positions()` | `list[Position]` | All current holdings |
| `get_latest_price(symbol)` | `Decimal` | Current market price |
| `get_order_history(days=7)` | `list[Order]` | Recent filled orders |
| `get_historical_data(symbol, start, end)` | `list[Bar]` | Historical OHLCV data |
| `get_bars(symbol, timeframe, limit)` | `list[Bar]` | Recent bars for indicators |

**Note:** `submit_order()` and `cancel_order()` will raise `NotImplementedError` to prevent accidental trading.

---

### 3.2 StrategyLoader

**File:** `src/bot_trading/strategy/loader.py`

**Purpose:** Load trading strategies from markdown files

**Strategy Format (.md):**

```markdown
# Strategy Name

## Description
Brief description of the strategy logic.

## Parameters
- param_name: value

## Indicators
- RSI(period=14)
- SMA(period=20)

## Entry Conditions
- RSI < 30 (buy)
- RSI > 70 (sell)

## Risk Management
- Stop Loss: 5%
- Take Profit: 10%
- Max Position: 10% of portfolio
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `load_strategy(name)` | `BaseStrategy` | Load strategy by name |
| `list_strategies()` | `list[str]` | List available strategies |
| `validate_strategy(doc)` | `bool` | Validate strategy format |

---

### 3.3 TechnicalIndicators

**File:** `src/bot_trading/strategy/indicators.py`

**Purpose:** Calculate technical indicators for strategy analysis

**Indicators:**

| Indicator | Parameters | Description |
|-----------|------------|-------------|
| RSI | period, prices | Relative Strength Index |
| SMA | period, prices | Simple Moving Average |
| EMA | period, prices | Exponential Moving Average |
| MACD | fast, slow, signal | Moving Average Convergence Divergence |
| Bollinger Bands | period, std_dev | Price bands |
| ATR | period | Average True Range |

---

### 3.4 BacktestEngine

**File:** `src/bot_trading/backtest/engine.py`

**Purpose:** Run strategy on historical data

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `run_backtest(strategy, symbol, start, end)` | `BacktestResult` | Full backtest analysis |

**BacktestResult:**

```python
@dataclass
class BacktestResult:
    strategy_name: str
    symbol: str
    start_date: date
    end_date: date

    # Performance metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float  # 0.0 to 1.0

    total_return: Decimal  # Total profit/loss
    total_return_pct: float  # Percentage

    max_drawdown: Decimal
    max_drawdown_pct: float

    sharpe_ratio: float
    sortino_ratio: float

    # Trade history
    trades: list[Trade]

    # Equity curve
    equity_curve: list[EquityPoint]
```

---

### 3.5 SignalAnalyzer

**File:** `src/bot_trading/analysis/analyzer.py`

**Purpose:** Analyze current market conditions and generate signals

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `analyze_current(strategy, symbol)` | `AnalysisResult` | Current signal analysis |

**AnalysisResult:**

```python
@dataclass
class AnalysisResult:
    symbol: str
    timestamp: datetime

    # Signal
    signal: str  # "BUY", "SELL", "HOLD"
    confidence: float  # 0.0 to 1.0
    reason: str

    # Price info
    current_price: Decimal
    target_price: Decimal | None
    stop_loss_price: Decimal | None

    # Risk
    position_size: int  # Recommended shares
    position_value: Decimal
    risk_amount: Decimal
    risk_pct_of_portfolio: float  # 0.0 to 0.10 max

    # Indicators
    indicators: dict[str, float]  # RSI, MA values, etc.
```

---

### 3.6 RiskCalculator

**File:** `src/bot_trading/analysis/calculator.py`

**Purpose:** Calculate position risk for "what-if" scenarios

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `calculate_position_risk(symbol, quantity, entry_price, stop_loss_pct)` | `RiskReport` | Full risk analysis |

**RiskReport:**

```python
@dataclass
class RiskReport:
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
    risk_pct_of_portfolio: float

    # Recommendations
    max_shares_at_10pct: int
    recommended_quantity: int

    # Scenarios
    scenario_5pct_gain: Decimal
    scenario_5pct_loss: Decimal
    scenario_10pct_loss: Decimal
```

---

### 3.7 CLI Interface (main.py)

**File:** `main.py`

**Purpose:** Main entry point with interactive menu

**Flow:**

1. Initialize AlpacaProvider
2. Fetch and display Dashboard
3. Show mode selection menu
4. Execute selected mode
5. Display results
6. Save to file
7. Return to menu or exit

---

## 4. User Interface

### 4.1 Dashboard Display

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

### 4.2 Backtest Result Display

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

### 4.3 Signal Analysis Display

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

### 4.4 Risk Calculator Display

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
╚════════════════════════════════━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╝
```

---

## 5. File Structure

```
bot-trading/
├── src/bot_trading/
│   ├── __init__.py
│   ├── config.py                              ✅ Existing
│   │
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                            ✅ Existing
│   │   ├── alpaca.py                          ⚠️  Enhance (add historical data)
│   │   └── mock.py                            ✅ Create (for testing)
│   │
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── base.py                            ✅ Existing
│   │   ├── loader.py                          ✅ Create (load .md files)
│   │   ├── indicators.py                      ✅ Create (RSI, MA, etc.)
│   │   └── strategies/
│   │       ├── __init__.py
│   │       ├── rsi_mean_reversion.py          ✅ Create
│   │       └── simple MovingAverage.py        ✅ Create
│   │
│   ├── analysis/                              🆁 New folder
│   │   ├── __init__.py
│   │   ├── analyzer.py                        ✅ Create
│   │   └── calculator.py                      ✅ Create
│   │
│   ├── backtest/                              🆁 New folder
│   │   ├── __init__.py
│   │   ├── engine.py                          ✅ Create
│   │   └── result.py                          ✅ Create
│   │
│   ├── data/                                  🆁 New folder
│   │   ├── __init__.py
│   │   └── fetcher.py                         ✅ Create
│   │
│   ├── execution/
│   │   └── executor.py                        ✅ Existing (not used in analysis mode)
│   │
│   ├── risk/
│   │   └── limits.py                          ✅ Existing
│   │
│   └── ui/                                    🆁 New folder
│       ├── __init__.py
│       ├── dashboard.py                       ✅ Create
│       └── menus.py                           ✅ Create
│
├── docs/strategies/                           🆁 New folder
│   ├── rsi-mean-reversion.md                 📝 Strategy definition
│   └── simple-moving-average.md              📝 Strategy definition
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
│   └── test_strategy/
│       ├── __init__.py
│       ├── test_loader.py
│       └── test_indicators.py
│
├── main.py                                    ⚠️  Rewrite (CLI interface)
├── .env                                       ✅ Existing
├── pyproject.toml                             ✅ Existing
└── README.md                                  ⚠️  Update
```

---

## 6. Error Handling

### 6.1 Error Categories

| Error Type | Message | Action |
|------------|---------|--------|
| **API Connection** | "❌ ไม่สามารถเชื่อมต่อ Alpaca API ได้" | Check internet/credentials, offer retry |
| **Invalid Credentials** | "❌ API Key หรือ Secret ไม่ถูกต้อง" | Check .env file |
| **No Data Found** | "⚠️  ไม่พบข้อมูลสำหรับ {symbol}" | Check symbol, suggest valid symbols |
| **Invalid Input** | "❌ Input ไม่ถูกต้อง: {reason}" | Prompt for correct input |
| **Risk Too High** | "⚠️  ความเสี่ยงเกิน 10% ของพอร์ต!" | Suggest lower quantity |
| **Strategy Not Found** | "❌ ไม่พบ strategy: {name}" | List available strategies |
| **Insufficient Data** | "⚠️  ข้อมูลไม่เพียงพอสำหรับ backtest" | Suggest longer period |

### 6.2 Error Recovery

```python
# All modes will have try-except with user-friendly recovery

try:
    result = execute_operation()
except AlpacaAPIError as e:
    logger.error(f"API Error: {e}")
    print("\n❌ เกิดข้อผิดพลาดในการเชื่อมต่อ API")
    print("กรุณาตรวจสอบ:")
    print("  1. Internet connection")
    print("  2. API credentials ในไฟล์ .env")
    choice = input("\nกด [Enter] เพื่อลองใหม่ หรือ [Q] เพื่อออก: ")
    if choice.upper() != 'Q':
        retry_operation()

except InsufficientDataError as e:
    print(f"\n⚠️  {e}")
    print("กรุณาเลือกช่วงเวลาที่ยาวขึ้น")
    prompt_for_new_period()

```

---

## 7. Sample Strategies

### 7.1 RSI Mean Reversion

**File:** `docs/strategies/rsi-mean-reversion.md`

```markdown
# RSI Mean Reversion Strategy

## Description
กลยุทธ์การกลับสู่ค่าเฉลี่ย (Mean Reversion) โดยใช้ RSI
- ซื้อเมื่อ RSI < 30 (oversold)
- ขายเมื่อ RSI > 70 (overbought)

## Parameters
- RSI Period: 14
- Buy Threshold: 30
- Sell Threshold: 70

## Entry Conditions
- Buy: RSI crosses below 30 AND price > SMA(20)
- Sell: RSI crosses above 70 OR price < SMA(20)

## Risk Management
- Stop Loss: 5%
- Take Profit: 10%
- Max Position: 10% of portfolio
```

### 7.2 Simple Moving Average Crossover

**File:** `docs/strategies/sma-crossover.md`

```markdown
# SMA Crossover Strategy

## Description
กลยุทธ์การตัดกันของเส้น SMA (Moving Average Crossover)
- ซื้อเมื่อ SMA(50) ตัด SMA(200) ขึ้น (Golden Cross)
- ขายเมื่อ SMA(50) ตัด SMA(200) ลง (Death Cross)

## Parameters
- Fast SMA: 50
- Slow SMA: 200

## Entry Conditions
- Buy: SMA(50) > SMA(200) AND previous SMA(50) <= previous SMA(200)
- Sell: SMA(50) < SMA(200)

## Risk Management
- Stop Loss: 8%
- Take Profit: 15%
- Max Position: 10% of portfolio
```

---

## 8. Output File Formats

### 8.1 Backtest Result JSON

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
    "win_rate": 0.60,
    "total_return": 850.00,
    "total_return_pct": 8.5,
    "max_drawdown": -3200.00,
    "max_drawdown_pct": -3.2,
    "sharpe_ratio": 1.2,
    "sortino_ratio": 1.8
  },
  "trades": [
    {
      "entry_date": "2025-02-15",
      "exit_date": "2025-02-18",
      "action": "BUY",
      "entry_price": 148.00,
      "exit_price": 152.00,
      "quantity": 10,
      "pnl": 40.00,
      "pnl_pct": 2.7
    }
  ],
  "equity_curve": [
    {"date": "2025-02-14", "value": 100000.00},
    {"date": "2025-02-15", "value": 100040.00}
  ]
}
```

### 8.2 Signal Analysis JSON

```json
{
  "type": "signal",
  "timestamp": "2025-03-14T18:30:00",
  "strategy": "rsi_mean_reversion",
  "symbol": "AAPL",
  "signal": "BUY",
  "confidence": 0.75,
  "current_price": 150.25,
  "target_price": 165.00,
  "stop_loss_price": 142.50,
  "recommended_quantity": 10,
  "position_value": 1502.50,
  "risk_amount": 75.00,
  "risk_pct_of_portfolio": 0.0075,
  "indicators": {
    "rsi_14": 28.5,
    "sma_20": 148.50,
    "sma_50": 147.00,
    "trend": "bullish"
  },
  "reason": "RSI is below 30 (oversold) and price is above SMA(20)"
}
```

---

## 9. Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Enhance AlpacaProvider with historical data
- [ ] Create TechnicalIndicators module
- [ ] Create StrategyLoader
- [ ] Implement 2 sample strategies

### Phase 2: Analysis Core (Week 2)
- [ ] Create BacktestEngine
- [ ] Create SignalAnalyzer
- [ ] Create RiskCalculator
- [ ] Add comprehensive tests

### Phase 3: UI & CLI (Week 3)
- [ ] Create CLI interface with main menu
- [ ] Implement Dashboard display
- [ ] Add all mode interfaces
- [ ] Implement file saving

### Phase 4: Polish (Week 4)
- [ ] Add error handling
- [ ] Add logging
- [ ] Add input validation
- [ ] Create documentation

---

## 10. Testing Strategy

### Unit Tests
- Each indicator calculation
- Strategy loading and parsing
- Risk calculations
- Backtest logic

### Integration Tests
- Alpaca API connection
- End-to-end backtest flow
- End-to-end signal analysis

### Manual Testing
- User workflow testing
- Error recovery testing
- UI/UX validation

---

## 11. Dependencies

**Add to pyproject.toml:**

```toml
[project.dependencies]
alpaca-py = "^0.1.0"
pandas = "^2.0.0"
requests = "^2.31.0"

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]
analysis = [
    "matplotlib>=3.7.0",  # For charts (optional)
    "numpy>=1.24.0",
]
```

---

## 12. Security & Safety

### Safety Features
- ✅ Paper trading ONLY (no live trading)
- ✅ submit_order() raises NotImplementedError
- ✅ Max 10% risk per trade enforced
- ✅ No secrets in git
- ✅ Input validation

### API Security
- Credentials in .env only
- .env in .gitignore
- Validate paper URL only

---

## 13. Future Enhancements (Out of Scope for MVP)

- Visual charts (matplotlib)
- Multiple timeframe analysis
- Portfolio optimization
- Machine learning strategies
- Real-time streaming data
- Web UI (Flask/FastAPI)

---

## 14. Approval

**Design Status:** ✅ Approved by user

**Ready for Implementation Planning:** Yes

**Next Step:** Create detailed implementation plan with writing-plans skill
