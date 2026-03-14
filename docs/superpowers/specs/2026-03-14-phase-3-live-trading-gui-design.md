# Phase 3: Live Trading with Desktop GUI - Design Specification

**Date:** 2026-03-14
**Status:** Approved for Implementation
**Version:** 1.0

---

## Overview

Phase 3 adds a desktop GUI application for manual trading execution with paper/real mode toggle. Users manually enter trading signals and execute them through a polished interface with risk checks, order management, and performance tracking.

### Key Requirements

- **Manual signal entry** - No AI API; users enter their own trading signals
- **Desktop GUI** - PyQt6 with professional interface
- **Paper/Real toggle** - Safe testing before live trading
- **Manual execution** - User must approve each trade
- **On-demand** - No continuous running; user initiates actions
- **JSON/CSV storage** - Simple file-based persistence
- **Flexible providers** - Works with any provider implementing `BaseProvider`

---

## Architecture

### Overall Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Phase 3 Application                       │
├─────────────────────────────────────────────────────────────┤
│  VIEW (GUI)              CONTROLLER           MODEL (Core)   │
│  ┌─────────────┐        ┌─────────────┐    ┌─────────────┐  │
│  │ MainWindow  │◄───────│AppController│◄───│TradingEngine│  │
│  │ Panels:     │───────►│             │───►│             │  │
│  │ - Portfolio │        │Trading      │    │StateManager │  │
│  │ - Signal In│        │Controller   │    │DataStore    │  │
│  │ - Orders    │        │Settings     │    │Notification │  │
│  │ - Charts    │        │Controller   │    │Manager      │  │
│  │ - Risk      │        └─────────────┘    └─────────────┘  │
│  │ - Market    │                                          │
│  └─────────────┘                ▲                           │
│         │                       │                           │
│         └──────── Qt Signals/Slots ────────────────────────┘
│                                                               │
│  Existing Phase 0-2 Modules                                  │
│  - Providers, Risk, Config, Execution                       │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Single-threaded GUI** - All UI updates on main thread
2. **Signal-driven updates** - Qt signals/slots for reactive state changes
3. **Manual execution** - User must approve every trade
4. **Paper-first** - Default to paper mode; real mode requires explicit activation
5. **Fail-safe** - Risk checks before every execution

---

## Component Breakdown

### VIEW Layer (`src/bot_trading/gui/`)

```
gui/
├── __init__.py
├── main_window.py          # Main application window (QMainWindow)
├── panels/
│   ├── __init__.py
│   ├── portfolio.py        # Positions, account value, P&L table
│   ├── signals.py          # Manual signal entry + list (was analysis)
│   ├── orders.py           # Order history with status
│   ├── charts.py           # Performance charts (pyqtgraph)
│   ├── risk.py             # Risk metrics, limit usage display
│   └── market.py           # Market data, symbol watchlist
├── dialogs/
│   ├── __init__.py
│   ├── execute_trade.py    # Trade confirmation dialog
│   └── settings.py         # Settings (API keys, paper/real mode)
├── widgets/
│   ├── __init__.py
│   ├── signal_card.py      # Signal display widget
│   └── notification_tray.py # System tray integration
└── resources/
    └── icons/              # UI icons (paper mode, real mode, etc.)
```

### CONTROLLER Layer (`src/bot_trading/controllers/`)

```
controllers/
├── __init__.py
├── app_controller.py       # Root controller, initializes subsystems
├── trading_controller.py   # Trading operations (signals, execution)
└── settings_controller.py  # Configuration management
```

### MODEL Layer (`src/bot_trading/core/`)

```
core/
├── __init__.py
├── trading_engine.py       # Main trading engine wrapper
├── state_manager.py        # Application state with Qt signals
├── data_store.py           # JSON/CSV persistence
└── notification_manager.py # Desktop notifications
```

---

## Data Models

### ManualSignal

```python
@dataclass
class ManualSignal:
    """Manually entered trading signal."""
    symbol: str
    action: Literal["buy", "sell", "hold"]
    quantity: Decimal
    price: Decimal | None = None  # None = market price
    risk_score: int = 5  # 1-10
    reason: str = ""
    source: str = "manual"
    created_at: datetime = field(default_factory=datetime.now)

    def to_execution_signal(self) -> Signal:
        """Convert to strategy.Signal for execution."""
        return Signal(
            symbol=self.symbol,
            action=self.action,
            confidence=1.0,  # Manual = full confidence
            quantity=self.quantity,
            reason=self.reason
        )
```

---

## GUI Layout

### Main Window

```
┌─────────────────────────────────────────────────────────────────┐
│  AI Trading Risk Analyzer                    [Paper Mode] ●     │
├─────────────────────────────────────────────────────────────────┤
│  Menu: File | View | Tools | Help                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Account Summary                                          │  │
│  │  Equity: $52,340.50  |  Cash: $12,150.00  |  P&L: +2.3%  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Tabbed Panels (QTabWidget):                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │ │
│  │ │Portfolio │ │ Signals  │ │  Orders  │ │  Charts  │       │ │
│  │ │          │ │          │ │          │ │          │       │ │
│  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘       │ │
│  │ ┌──────────┐ ┌──────────┐                                 │ │
│  │ │   Risk   │ │  Market  │                                 │ │
│  │ └──────────┘ └──────────┘                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [Refresh Data]    [Settings]                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Signal Entry Panel

```
┌─────────────────────────────────────────────────────────┐
│  Signal Entry                                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Add New Signal:                                [Clear]  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Symbol:     [AAPL           ]                     │  │
│  │ Action:     [BUY ▼] (BUY/SELL/HOLD)              │  │
│  │ Quantity:   [100            ] shares              │  │
│  │ Price:      [$175.50        ] (optional)         │  │
│  │ Risk Score: [5  ▼] (1-10)                        │  │
│  │ Reason:     [Technical breakout...              ] │  │
│  │            [                                      ] │  │
│  │                                                  │  │
│  │            [  Add to List  ]  [  Cancel  ]      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Pending Signals:                                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Symbol │ Action │ Qty  │ Risk │ Reason       │Exec│ │
│  │──────────────────────────────────────────────────│ │
│  │ AAPL   │ BUY    │ 100  │ 5/10 │ Breakout    │[▶] │ │
│  │ NVDA   │ SELL   │ 25   │ 3/10 │ Take profit│[▶] │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Manual Trade Execution Flow

```
User
 │
 │ 1. Fill signal form, click "Add to List"
 ▼
SignalsPanel
 │
 │ 2. Validate, create ManualSignal
 ▼
StateManager
 │
 │ 3. Emit: signals_updated
 ▼
SignalsPanel (refresh)
 │
 │ 4. User clicks "[▶] Execute"
 ▼
TradingController.execute_signal()
 │
 │ 5. Pre-trade checks (risk, balance, market hours)
 ▼
ExecuteTradeDialog (show confirmation)
 │
 │ 6. User confirms
 ▼
TradingController
 │
 │ 7. Provider.submit_order()
 │    DataStore.record_trade()
 ▼
StateManager
 │
 │ 8. Emit: trade_executed, portfolio_updated
 ▼
All panels refresh, notification shown
```

---

## State Management

### StateManager Signals

| Signal | Emitted When | Consumers |
|--------|--------------|-----------|
| `state_changed` | Any state changes | MainWindow |
| `portfolio_updated` | Positions/account change | PortfolioPanel |
| `signals_updated` | Signal list changes | SignalsPanel |
| `orders_updated` | Order history changes | OrdersPanel |
| `trading_mode_changed` | Paper/Real toggle | All panels |

### File Structure

```
data/
├── state/
│   ├── current_state.json       # Latest application state
│   └── settings.json            # User settings, API keys
├── history/
│   ├── trades_2026_03_14.csv    # Trade log (one per day)
│   └── orders_2026_03_14.csv    # Order history
└── signals/
    └── pending_signals.json     # Unexecuted signals
```

---

## Error Handling

### Pre-Trade Safety Checks

1. **Trading mode validation** - Real mode requires valid API keys
2. **Risk limits** - Position size, portfolio exposure, daily loss
3. **Duplicate detection** - Block duplicate orders
4. **Market hours** - Real trading only when market open
5. **Buying power** - Sufficient funds for buy orders

### Error Display Hierarchy

1. **Inline** - Non-blocking warnings in panels
2. **Modal dialogs** - Blocking errors requiring acknowledgment
3. **Notifications** - Background events (order filled, etc.)

---

## Safety Features

### Paper/Real Mode

- **Default: Paper mode** - First launch always paper
- **Explicit activation** - Real mode requires:
  1. Valid API keys configured
  2. User types "ENABLE-REAL-TRADING" in settings
- **Visual indicator** - Mode shown in status bar (green=paper, red=real)
- **Confirmation dialogs** - Highlight mode prominently

### Risk Enforcement

All existing Phase 0-2 risk checks apply:
- Max position size per trade
- Max portfolio exposure
- Daily loss limit
- Duplicate order protection

---

## Testing Strategy

### Unit Tests

- Controllers with mocked providers
- StateManager signal emissions
- DataStore load/save operations
- GUI widget logic (qtbot)

### Integration Tests

- Full signal entry → execution flow
- Paper mode trading end-to-end
- State persistence across restarts

### Manual Checklist

- [ ] Paper trading executes correctly
- [ ] Risk limits enforced
- [ ] Mode toggle works
- [ ] Real mode requires API keys
- [ ] Order cancellation works
- [ ] Data persists after restart
- [ ] All panels update on state changes

---

## Dependencies

### New Dependencies

```toml
[project.optional-dependencies]
gui = [
    "PyQt6>=6.6.0",
    "pyqtgraph>=0.13.0",  # Charts
]
```

### Removed Dependencies

- `anthropic` - No AI API integration

---

## Implementation Notes

### Key Files to Create

1. `src/bot_trading/gui/main_window.py` - Entry point
2. `src/bot_trading/gui/panels/signals.py` - Manual signal entry
3. `src/bot_trading/controllers/trading_controller.py` - Execution logic
4. `src/bot_trading/core/state_manager.py` - Central state
5. `src/bot_trading/core/data_store.py` - Persistence

### Key Files to Modify

1. `src/bot_trading/execution/executor.py` - Implement actual order submission (remove TODO)
2. `src/bot_trading/cli.py` - Add GUI launch option

### Entry Point

```bash
# Launch GUI
python -m bot_trading.gui

# Or from CLI
python -m bot_trading.cli --gui
```

---

## Success Criteria

Phase 3 is complete when:

1. ✅ User can manually enter trading signals via GUI
2. ✅ Signals are validated and displayed in a list
3. ✅ User can execute signals with confirmation dialog
4. ✅ Orders are submitted to provider (paper or real)
5. ✅ Portfolio and order history update in real-time
6. ✅ Paper/Real mode toggle works with safety checks
7. ✅ Trade history persists to CSV
8. ✅ Application state survives restart
9. ✅ Desktop notifications work for key events

---

## Future Enhancements (Out of Scope)

- CSV import for bulk signal entry
- Signal presets/templates
- Real-time streaming price updates
- Backtesting integration
- Multiple provider support in single session
- Advanced charting (indicators, drawing tools)
