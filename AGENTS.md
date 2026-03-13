# AGENTS.md

## Project
This repository is a demo trading bot for paper trading only.
Primary goal: validate strategy logic, risk controls, and execution flow in a safe non-live environment.

## Non-goals
- No live trading
- No real money movement
- No production deployment without explicit approval
- No secrets committed to git

## Tech stack
- Python 3.11+
- Package manager: uv or pip
- Main modules:
  - strategy/
  - execution/
  - risk/
  - data/
  - backtest/
  - tests/

## Trading mode rules
- Default mode must be PAPER
- Live trading code paths must stay disabled unless explicitly requested
- Use provider sandbox/testnet credentials only
- Separate paper config and live config

## Provider abstraction
Support provider adapters behind a common interface:
- get_account()
- get_positions()
- get_latest_price(symbol)
- submit_order(...)
- cancel_order(...)
- list_open_orders()

Preferred first provider:
- Alpaca Paper Trading for US stocks
Alternative:
- Binance Spot Testnet for crypto

## Risk rules
Always enforce:
- max position size per trade
- max portfolio exposure
- daily loss limit
- duplicate order protection
- market hours / tradable symbol validation where applicable

## Coding rules
- Keep functions small and testable
- Prefer typed Python
- Add docstrings for public functions
- Avoid hidden side effects
- Never hardcode API keys
- Use environment variables
- Log every order attempt and result

## File conventions
- `.env.example` must exist
- `README.md` must explain setup and run steps
- `Makefile` or task runner should include common commands
- Store sample configs under `config/`
- Put experiments under `notebooks/` or `research/`

## Testing
Before finishing any task:
1. Run unit tests
2. Run lint/format
3. Validate no live endpoint is used
4. Verify paper mode remains default

## Expected commands
- install dependencies
- run tests
- run lint
- run bot in paper mode
- run backtest

## Safety
If a requested change could enable real trading, pause and ask for confirmation.
If credentials are missing, generate placeholders and update `.env.example` instead of inventing secrets.
If provider behavior is unclear, create an adapter stub with TODO notes rather than guessing.

## Collaboration
When making changes:
1. Explain planned file changes briefly
2. Make the smallest safe change first
3. Update README when setup changes
4. Add tests for new behavior
5. Summarize what was changed and how to run it
