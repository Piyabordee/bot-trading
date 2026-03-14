# AI Trading Risk Analyzer

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-157%20passing-success.svg)](tests/)

AI-powered trading risk analyzer with a desktop GUI for manual trading execution.

## Overview

This project analyzes trading risk from historical and real-time market data.
It outputs structured configurations that Python can validate and process.

**Core Flow:**
```
Data Sources → AI Analysis → Config Output → Risk Engine
```

**Key Features:**
- Desktop GUI (PyQt6) for manual trading
- Standardized config schema (AI-friendly, Python-readable)
- Robust validation with clear error messages
- Modular architecture for testing and extension
- Paper trading support for strategy validation
- Real-time portfolio tracking and notifications

## Quick Start

### GUI Application (Phase 3)

```bash
# Install GUI dependencies
pip install -e ".[gui,dev]"

# Launch GUI (paper mode - default)
python -m bot_trading.cli gui

# Or use the direct entry point
bot-trading-gui
```

### CLI Analysis (Phase 2)

```bash
# Install
pip install -e ".[dev]"

# Set up Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"

# Run analysis
python -m bot_trading.cli analyze --symbols AAPL,MSFT
```

## Development Status

| Phase | Status | Components |
|-------|--------|------------|
| Phase 0 | ✅ Complete | Data models, Provider interface, Risk limits |
| Phase 1 | ✅ Complete | Config schema, Risk scoring algorithm, Validation |
| Phase 2 | ✅ Complete | AI integration, Data pipeline, Risk analysis, CLI |
| Phase 3 | ✅ Complete | **Live Trading GUI, Portfolio tracking, Signal execution** |

**Latest: Phase 3 adds a PyQt6 desktop GUI with:**
- Manual signal entry and execution
- Real-time portfolio display
- Paper/Real trading mode toggle
- Desktop notifications
- Trade history persistence

## Architecture

The system consists of seven main modules:

| Module | Purpose |
|--------|---------|
| `core/` | **State management, persistence, notifications** |
| `controllers/` | **App coordination, trading operations, settings** |
| `gui/` | **PyQt6 desktop interface** |
| `config/` | Configuration schema and validation |
| `risk/` | Risk scoring and limit enforcement |
| `providers/` | Broker adapters (Alpaca, Mock) |
| `execution/` | Order execution logic |

## GUI Features (Phase 3)

### Main Window
- **Account Summary**: Real-time equity, cash, and P&L display
- **Trading Mode Indicator**: Paper (green) / Real (red) with warnings
- **Tabbed Interface**: Portfolio, Signals, Orders, Charts, Risk, Market Data
- **Status Bar**: Mode indicator, refresh button

### Portfolio Panel
- **Positions Table**: Symbol, quantity, avg price, current price, market value
- **Auto-refresh**: Updates when portfolio data changes

### Signals Panel
- **Manual Entry**: Form to add trading signals
- **Pending Signals**: Table with execute buttons
- **Validation**: Pre-trade checks before execution

### Settings Dialog
- **API Keys**: Secure storage for broker credentials
- **Trading Mode**: Paper/Real toggle with confirmation
- **Risk Limits**: Configure max position size and exposure

## Usage

### Running the GUI

```bash
# Launch in paper trading mode (default, safe)
python -m bot_trading.cli gui

# Launch in real trading mode (requires API keys)
python -m bot_trading.cli gui --mode real
```

### Using the GUI

1. **Add a Signal:**
   - Enter symbol (e.g., AAPL)
   - Select action (buy/sell)
   - Enter quantity and optional price
   - Click "Add to List"

2. **Execute a Signal:**
   - Click the ▶ button next to a pending signal
   - Review the execution result

3. **View Portfolio:**
   - Switch to the Portfolio tab
   - See real-time positions and P&L

4. **Change Settings:**
   - Tools → Settings
   - Configure API keys and trading mode

### Running Tests

```bash
# All tests
pytest tests/ -v

# GUI tests only
pytest tests/gui/ -v

# With coverage
pytest tests/ --cov=bot_trading --cov-report=html
```

### Code Quality

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Project Structure

```
bot-trading/
├── src/bot_trading/
│   ├── core/            # StateManager, DataStore, NotificationManager
│   ├── controllers/     # AppController, TradingController, SettingsController
│   ├── gui/             # PyQt6 desktop interface
│   │   ├── main_window.py
│   │   ├── panels/       # Portfolio, Signals, Orders, etc.
│   │   └── dialogs/      # Settings, Execute Trade
│   ├── providers/       # Broker adapters (Base, Alpaca, Mock)
│   ├── strategy/        # Trading strategies
│   ├── execution/       # Order execution
│   ├── risk/            # Risk limits & checks
│   └── data/            # Data models
├── tests/               # Test suite (157+ passing)
├── config/              # Sample configurations
├── data/                # Runtime data (state, history, signals)
└── pyproject.toml       # Project dependencies
```

## Configuration

### Trading Modes

| Mode | Description | Safety |
|------|-------------|--------|
| **Paper** | Simulated trading, no real money | Default, safe for testing |
| **Real** | Live trading with real money | Requires explicit confirmation |

### Environment Variables

```bash
# For GUI settings persistence
DATA_DIR="./data"  # Runtime data directory

# For AI analysis (Phase 2)
ANTHROPIC_API_KEY="your-key-here"

# For real trading (optional)
ALPACA_API_KEY="your-alpaca-key"
ALPACA_API_SECRET="your-alpaca-secret"
```

## Safety Features

1. **Paper Mode Default**: Always starts in paper trading mode
2. **Real Mode Confirmation**: Requires explicit checkbox to enable real trading
3. **Pre-Trade Checks**: Validates funds, positions, and risk limits
4. **Desktop Notifications**: Alerts for all trade executions
5. **Trade History**: All trades logged to CSV with timestamps

## Contributing

Contributions are welcome. Please:
1. Run tests before submitting
2. Follow the existing code style
3. Add tests for new features
4. Update documentation as needed

## License

MIT License

## Disclaimer

This software is a risk analysis tool. Trading decisions are your responsibility.
**Paper trading mode** is recommended for testing. **Real trading mode** uses actual money.
Never trade with money you cannot afford to lose.
