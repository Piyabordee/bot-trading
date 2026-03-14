# AI Integration Guide

## Overview

Phase 2 integrates AI (Claude) for trading risk analysis. The system:

1. Fetches market data from your provider
2. Calculates technical indicators
3. Sends context to Claude API
4. Receives structured JSON analysis
5. Validates and processes recommendations

## Setup

### 1. Install Dependencies

```bash
pip install anthropic
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

Or add to `.env`:
```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Run Analysis

```bash
python -m bot_trading.cli --symbols AAPL,MSFT,GOOGL
```

## Output Format

AI returns JSON with:

- `overall_sentiment`: bullish/bearish/neutral
- `symbols`: Per-symbol recommendations
  - `action`: BUY/SELL/HOLD
  - `confidence`: 0-1
  - `risk_score`: 1-10
  - `position_size_pct`: 0-1
  - `entry_price`, `stop_loss`, `target_price`: Optional
- `portfolio_risk`: Portfolio-level risk assessment

## Risk Scoring

Risk scores map to position size adjustments:

| Score | Risk Level | Position Multiplier |
|-------|-----------|---------------------|
| 1-2   | Very Low  | 100%                |
| 3-4   | Low       | 90%                 |
| 5-6   | Medium    | 75%                 |
| 7-8   | High      | 50%                 |
| 9-10  | Very High | 25%                 |

## Architecture

```
Provider → Data Pipeline → AI Client → Config Validator → Risk Engine
   ↓           ↓              ↓              ↓              ↓
Market      Transform      Claude API      Pydantic     Risk Scores
 Data      to Prompt       Analysis        Schema       + Advice
```

## Components

### Data Pipeline (`src/bot_trading/data/pipeline.py`)
- Fetches historical bars from providers
- Calculates technical indicators (SMA, RSI, volatility)
- Creates `MarketContext` for AI consumption

### AI Client (`src/bot_trading/ai/client.py`)
- Wraps Anthropic Claude API
- Implements retry logic with exponential backoff
- Handles transient errors (rate limits, timeouts)

### Prompt Builder (`src/bot_trading/ai/prompts.py`)
- Builds structured prompts from market context
- Includes risk management instructions
- Specifies required JSON output format

### Config Schema (`src/bot_trading/ai/schema.py`)
- Pydantic models for AI output validation
- Enforces type constraints and value ranges
- Provides clear validation errors

### Config Validator (`src/bot_trading/ai/validator.py`)
- Extracts JSON from markdown responses
- Validates against schema
- Enforces risk limits

### Risk Scorer (`src/bot_trading/risk/scoring.py`)
- Calculates position sizes based on risk
- Adjusts size based on AI risk score
- Provides human-readable summaries

### Trading Analyzer (`src/bot_trading/ai/analyzer.py`)
- End-to-end orchestration
- Combines all components
- Provides CLI interface

## Testing

All components have comprehensive tests:

```bash
# Run all tests
pytest tests/ -v

# Run specific module tests
pytest tests/data/ -v      # Data pipeline tests
pytest tests/ai/ -v        # AI client, prompts, schema tests
pytest tests/risk/ -v      # Risk scoring tests

# Run with coverage
pytest tests/ --cov=bot_trading --cov-report=html
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API key | Yes |
| `ALPACA_API_KEY` | Alpaca API key (for live data) | No* |

*Optional for testing with MockProvider

### Risk Limits

Default limits can be customized:

```python
from bot_trading.ai.analyzer import TradingAnalyzer

analyzer = TradingAnalyzer(
    provider=provider,
    api_key="your-key",
    max_position_risk_pct=0.05,  # 5% per position
    lookback_days=30,             # 30-day lookback
)
```

## Example Output

```
=== Trading Analysis Report ===
Overall Sentiment: NEUTRAL

Portfolio Risk:
  Current Exposure: 0.0%
  Recommended Max: 20%

=== AAPL ===
Symbol: AAPL
Action: HOLD
AI Risk Score: 5/10
Confidence: 65%
Risk Adjustment: 75% of normal size

=== Analysis Complete ===
```

## Troubleshooting

### "API key is required"
Set `ANTHROPIC_API_KEY` environment variable or use `--api-key` argument.

### "Rate limit exceeded"
The AI client automatically retries with exponential backoff. Wait a moment and try again.

### "Schema validation failed"
Check that AI response matches expected format. See `config/ai_analysis_config.yaml` for example.

## Next Steps

- **Phase 3**: Add live trading integration
- **Phase 3**: Build dashboard UI
- **Phase 3**: Implement alert system
