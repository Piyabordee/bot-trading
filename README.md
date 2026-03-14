# AI Trading Risk Analyzer

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-passing-success.svg)](tests/)

One-click AI-powered risk analysis for trading decisions.

## Overview

This project analyzes trading risk from historical and real-time market data.
It outputs structured configurations that Python can validate and process.

**Core Flow:**
```
Data Sources → AI Analysis → Config Output → Risk Engine
```

**Key Features:**
- Standardized config schema (AI-friendly, Python-readable)
- Robust validation with clear error messages
- Modular architecture for testing and extension
- Paper trading support for strategy validation

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Configure
cp .env.example .env

# Run tests
pytest tests/ -v
```

See [Setup](#setup) for detailed configuration.

## Phase 2: AI Integration (Current)

Phase 2 adds AI-powered risk analysis:

- **Data Pipeline**: Fetch market data and calculate technical indicators
- **AI Client**: Claude API integration with retry logic
- **Config Schema**: Structured output format (AI-friendly, Python-readable)
- **Risk Scoring**: Position sizing based on AI analysis

### Quick Start (Phase 2)

```bash
# Install dependencies
pip install -e ".[dev]"

# Set up Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"

# Run analysis
python -m bot_trading.cli --symbols AAPL,MSFT
```

See [AI Integration Guide](docs/ai-integration-guide.md) for details.

## Development Status

| Phase | Status | Components |
|-------|--------|------------|
| Phase 0 | Complete | Data models, Provider interface, Risk limits, Tests (49 passed, 89% coverage) |
| Phase 1 | Complete | Config schema, Risk scoring algorithm, Validation module |
| Phase 2 | Complete | AI integration, Data pipeline, Risk analysis, CLI |
| Phase 3 | Planned | Live trading, Dashboard, Alerts |

## Architecture

The system consists of five main modules:

| Module | Purpose |
|--------|---------|
| `config/` | Configuration schema and validation (CORE) |
| `risk/` | Risk scoring and limit enforcement (CORE) |
| `providers/` | Broker adapters (Alpaca, Mock) |
| `strategy/` | Trading strategy interfaces |
| `execution/` | Order execution logic |

## Setup

### Requirements
- Python 3.11+
- pip or uv for package management

### Installation
```bash
git clone <your-repo>
cd bot-trading
pip install -e ".[dev]"
```

### Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Project Structure

```
bot-trading/
├── src/bot_trading/
│   ├── config.py        # Configuration loader
│   ├── exceptions.py    # Custom exceptions
│   ├── providers/       # Broker adapters (Base, Alpaca, Mock)
│   ├── strategy/        # Trading strategies
│   ├── execution/       # Order execution
│   ├── risk/            # Risk limits & checks
│   └── data/            # Data models
├── tests/               # Test suite (test_providers/, integration/)
├── config/              # Sample configurations
├── docs/                # Additional documentation
└── pyproject.toml       # Project dependencies
```

## Usage

### Running Tests
```bash
pytest tests/ -v
pytest tests/ --cov=bot_trading --cov-report=html
```

### Code Quality
```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `ALPACA_API_KEY` | Alpaca API key | *Required* |
| `ALPACA_API_SECRET` | Alpaca API secret | *Required* |
| `ALPACA_BASE_URL` | Alpaca base URL | `https://paper-api.alpaca.markets` |
| `MAX_POSITION_SIZE` | Max order size | `1000` |
| `MAX_PORTFOLIO_EXPOSURE` | Max exposure ratio | `0.2` |
| `DAILY_LOSS_LIMIT` | Daily loss limit | `500` |

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
Never trade with money you cannot afford to lose.
