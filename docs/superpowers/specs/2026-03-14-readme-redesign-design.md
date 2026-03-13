# README Redesign Design Document

**Date:** 2026-03-14
**Status:** Draft
**Version:** 2
**Author:** Claude (with user collaboration)

## Change Log
- **v2**: Fixed issues from spec review (LICENSE, test badge, project structure)
- **v1**: Initial design

## Overview

Redesign the project README.md to be more beautiful, universally accessible, and professional. The current README is primarily in Thai with heavy emoji usage, which limits international accessibility.

## Requirements

### Target Audience
- **Primary:** General open-source developers
- **Secondary:** Finance/Trading professionals (quants, algorithmic traders)
- **Approach:** Hybrid with progressive disclosure

### Language
- **100% English** for full international accessibility

### Style
- **Clean Minimal** — professional, minimal emojis, no visual clutter

## Design Approach

**Selected:** Option A — Linear Sections

**Rationale:**
- Simplest for maintainability
- Works natively on GitHub without HTML tricks
- Progressive disclosure via headers + table of contents
- Fits the Clean Minimal style requirement

## New README Structure

### Section 1: Header & Badges
```markdown
# AI Trading Risk Analyzer

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-passing-success.svg)](tests/)

One-click AI-powered risk analysis for trading decisions.
```

**Design Decisions:**
- Only 2 essential badges: Python version, Test status
- No LICENSE badge (LICENSE file to be created separately)
- No emoji in title
- Clear, concise tagline
- Test badge uses generic "passing" instead of specific count (avoids manual updates)

### Section 2: TL;DR Overview
```markdown
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
```

**Design Decisions:**
- Explains what and why in 3 sentences
- Simple ASCII diagram (one line, no boxes)
- 4 bullet-point features (not overwhelming)
- No emojis

### Section 3: Quick Start
```markdown
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
```

**Design Decisions:**
- Minimal commands to get started
- Links to detailed setup section
- No extensive explanations here

### Section 4: Development Status
```markdown
## Development Status

| Phase | Status | Components |
|-------|--------|------------|
| Phase 0 | Complete | Data models, Provider interface, Risk limits, Tests (49 passed, 89% coverage) |
| Phase 1 | In Progress | Config schema, Risk scoring algorithm, Validation module |
| Phase 2 | Planned | AI integration, Data pipeline |
| Phase 3 | Planned | Live trading, Dashboard, Alerts |
```

**Design Decisions:**
- Clean table format
- No status emojis (using text: "Complete", "In Progress", "Planned")
- Brief component descriptions
- Includes test statistics from Phase 0

### Section 5: Architecture (Brief)
```markdown
## Architecture

The system consists of five main modules:

| Module | Purpose |
|--------|---------|
| `config/` | Configuration schema and validation (CORE) |
| `risk/` | Risk scoring and limit enforcement (CORE) |
| `providers/` | Broker adapters (Alpaca, Mock) |
| `strategy/` | Trading strategy interfaces |
| `execution/` | Order execution logic |
```

**Design Decisions:**
- Simple table format
- Highlights CORE modules
- No ASCII art diagrams
- Links to actual code structure

### Section 6: Setup
```markdown
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
```

**Design Decisions:**
- Clear subsections
- Code blocks for commands
- Reference to .env.example

### Section 7: Project Structure
```markdown
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
```

**Design Decisions:**
- Minimal ASCII tree (no decorations)
- Shows actual structure: config.py as file, not directory
- One-line comments per directory/module

### Section 8: Usage & Commands
```markdown
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
```

### Section 9: Configuration
```markdown
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
```

### Section 10: Contributing
```markdown
## Contributing

Contributions are welcome. Please:
1. Run tests before submitting
2. Follow the existing code style
3. Add tests for new features
4. Update documentation as needed
```

### Section 11: License & Disclaimer
```markdown
## License

MIT License

## Disclaimer

This software is a risk analysis tool. Trading decisions are your responsibility.
Never trade with money you cannot afford to lose.
```

**Design Decisions:**
- No link to LICENSE file (to be created separately)
- Simple, clear disclaimer

## Design Principles Applied

1. **Minimal Emojis** — Only used sparingly if at all (none in main content)
2. **Clean Tables** — Used for structured data, no decorations
3. **Brief Sections** — Each section is concise, links to details where needed
4. **Progressive Disclosure** — Overview first, details later
5. **No Clutter** — Removed excessive ASCII art and visual noise
6. **Professional Tone** — Direct, clear, no informal language

## Pre-Implementation Checklist

Before implementing this redesign, complete these steps:

- [ ] Create LICENSE file (MIT)
- [ ] Archive current README as `README.th.md` (Thai version preservation)
- [ ] Update `pyproject.toml` description to: "AI Trading Risk Analyzer — One-click risk analysis for trading decisions"
- [ ] Verify test status for badge accuracy

## Files to Modify

- **Primary:** `README.md` — Complete rewrite
- **Secondary:** `AGENTS.md` — Update to reflect new README structure
- **Tertiary:** `pyproject.toml` — Consider updating description to match

## Success Criteria

- [ ] Pre-implementation checklist completed
- [ ] README is 100% English
- [ ] Minimal or no emoji usage
- [ ] Clean, professional appearance
- [ ] All essential information preserved
- [ ] Quick Start section works (tested commands)
- [ ] Links are valid and functional
- [ ] Project structure matches actual directory layout
- [ ] LICENSE file created and properly referenced
