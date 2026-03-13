# Paper Trading Bot

A **safe, paper-trading-only demo bot** for validating strategy logic, risk controls, and execution flow.

> **⚠️ IMPORTANT:** This bot is for paper trading DEMONSTRATION only. No live trading. No real money.

## Features

- **Paper trading only** - Live trading paths are disabled by default
- **Provider abstraction** - Easy to swap brokers (Alpaca Paper Trading primary)
- **Risk management** - Built-in limits for position size, portfolio exposure, and daily loss
- **Duplicate protection** - Prevents accidental duplicate orders
- **Modular design** - Clean separation of strategy, execution, risk, and data modules

## Prerequisites

- Python 3.11+
- pip or uv for package management

## Quick Start

1. **Clone and install dependencies:**

```bash
git clone <your-repo>
cd bot-trading
make install
```

2. **Configure environment:**

```bash
cp .env.example .env
# Edit .env with your Alpaca Paper Trading credentials
```

Get your free paper trading credentials from: https://alpaca.markets/paper

3. **Run tests:**

```bash
make test
```

4. **Run the bot (paper mode):**

```bash
make run
```

## Project Structure

```
bot-trading/
├── src/bot_trading/
│   ├── config.py          # Configuration loading (PAPER default)
│   ├── providers/         # Broker adapters
│   │   ├── base.py        # Abstract interface
│   │   └── alpaca.py      # Alpaca Paper Trading
│   ├── strategy/          # Trading strategies
│   ├── execution/         # Order execution
│   ├── risk/              # Risk management
│   └── data/              # Data fetching
├── config/                # Configuration files
├── tests/                 # Test suite
├── main.py               # Entry point
└── Makefile              # Common commands
```

## Available Commands

```bash
make help       # Show all available commands
make install    # Install dependencies
make test       # Run tests
make lint       # Run linting
make format     # Format code
make run        # Run bot in paper mode
make clean      # Clean generated files
```

## Safety Features

- ✅ PAPER mode is the default and only supported mode
- ✅ Provider validation (refuses non-paper URLs)
- ✅ Risk limit enforcement before every order
- ✅ Duplicate order detection
- ✅ No secrets in repository
- ✅ Comprehensive test coverage

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `TRADING_MODE` | Trading mode (paper only) | `paper` |
| `ALPACA_API_KEY` | Alpaca API key | *required* |
| `ALPACA_API_SECRET` | Alpaca API secret | *required* |
| `ALPACA_BASE_URL` | Alpaca base URL | `https://paper-api.alpaca.markets` |
| `MAX_POSITION_SIZE` | Max position per trade | `1000` |
| `MAX_PORTFOLIO_EXPOSURE` | Max portfolio exposure | `0.2` |
| `DAILY_LOSS_LIMIT` | Daily loss limit | `500` |

## Testing

The project follows TDD principles. Run tests frequently:

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_config.py -v

# Run with coverage
make test-cov
```

## Roadmap

- [ ] Complete Alpaca API integration
- [ ] Add sample trading strategies
- [ ] Implement backtesting module
- [ ] Add historical data fetching
- [ ] Create strategy performance metrics

## License

MIT License - see LICENSE file for details

## Disclaimer

This software is for educational and demonstration purposes only. Paper trading does not guarantee similar results in live trading. Never trade with money you cannot afford to lose.
