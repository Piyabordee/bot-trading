# AGENTS.md

## Project
AI Trading Risk Analyzer — One-click risk analysis powered by AI.
Primary goal: analyze trading risk from historical + real-time data, output config for Python to process.

## Vision
```
Data Pipeline (user handles) → AI Analysis → Config Output → Python Risk Engine
```

**Ultimate Goal:** Use analysis results to make informed real-money trading decisions.

## Core Focus
- **Config System** — AI output format that Python can reliably read and validate
- **Risk Engine** — Algorithm to score and explain trading risk
- **Modular Design** — Easy to test, extend, and maintain

## Non-goals
- No live trading (yet) — current focus is analysis, not execution
- No automated money-making — this is a decision support tool
- No secrets committed to git

## Tech stack
- Python 3.11+
- Package manager: uv or pip
- Main modules:
  - config/ (★ CORE)
  - risk/ (★ CORE)
  - providers/ (data sources)
  - strategy/
  - execution/
  - tests/

## Config System Rules (★ IMPORTANT)
- Config must be **AI-friendly** — easy for LLMs to generate correctly
- Config must be **Python-readable** — strict validation, clear error messages
- Config schema must be **versioned** — backward compatibility when possible
- Invalid config = fail fast with clear explanation (not silent errors)

## Provider abstraction
Support provider adapters behind a common interface:
- get_account()
- get_positions()
- get_latest_price(symbol)
- submit_order(...)
- cancel_order(...)
- list_open_orders()
- get_historical_bars() — critical for risk analysis
- get_order_history() — for backtesting

Preferred first provider:
- Alpaca Paper Trading for US stocks (data source + testing)
Alternative:
- Binance Spot Testnet for crypto

## Risk rules
Always enforce:
- max position size per trade
- max portfolio exposure
- daily loss limit
- duplicate order protection
- explainable risk scores (not just numbers)

## Coding rules
- Keep functions small and testable
- Prefer typed Python
- Add docstrings for public functions
- Avoid hidden side effects
- Never hardcode API keys
- Use environment variables
- **Config validation is critical** — fail early, fail clear

## File conventions
- `.env.example` must exist
- `README.md` must explain the AI → Config → Python flow
- Store sample configs under `config/`
- Config schema should be documented clearly
- Put experiments under `notebooks/` or `research/`

## Testing
Before finishing any task:
1. Run unit tests
2. Run lint/format
3. **Validate config schema** — ensure AI can generate valid configs
4. Test config validation with edge cases

## Expected commands
- install dependencies
- run tests
- run lint
- validate config
- run risk analysis

## Safety
If a requested change could enable real trading, pause and ask for confirmation.
If credentials are missing, generate placeholders and update `.env.example` instead of inventing secrets.
If provider behavior is unclear, create an adapter stub with TODO notes rather than guessing.

**Config Safety:**
- Always validate config before processing
- Never process invalid/malformed config
- Log all config validation failures for debugging

## Collaboration
When making changes:
1. Explain planned file changes briefly
2. Make the smallest safe change first
3. Update README/AGENTS.md when goals change
4. Add tests for new behavior
5. Summarize what was changed and how to run it
