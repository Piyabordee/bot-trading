# Phase 2: AI Integration & Data Pipeline Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build AI-powered trading risk analysis system that ingests market data, generates analysis via Claude API, outputs structured config for Python to validate and process.

**Architecture:**
```
Provider → Data Pipeline → AI Client → Config Validator → Risk Engine
   ↓           ↓              ↓              ↓              ↓
Market      Transform      Claude API      Pydantic     Risk Scores
 Data      to Prompt       Analysis        Schema       + Advice
```

**Tech Stack:** Python 3.11+, Anthropic SDK, Pydantic v2, pytest

**Prerequisites:** Phase 0 complete (data models, providers, risk limits)

---

## File Structure

| File | Purpose |
|------|---------|
| `src/bot_trading/data/models.py` | Extend data models for AI context |
| `src/bot_trading/data/pipeline.py` | Fetch and transform market data for AI |
| `src/bot_trading/ai/client.py` | Claude API wrapper with retry logic |
| `src/bot_trading/ai/prompts.py` | Prompt templates for AI analysis |
| `src/bot_trading/ai/schema.py` | AI output config schema (Pydantic) |
| `src/bot_trading/ai/validator.py` | Validate AI-generated configs |
| `src/bot_trading/risk/scoring.py` | Risk scoring algorithm |
| `src/bot_trading/config/schema.py` | Unified config schema v1 |
| `tests/data/test_pipeline.py` | Data pipeline tests |
| `tests/ai/test_client.py` | AI client tests (with mock) |
| `tests/ai/test_schema.py` | Config schema validation tests |
| `tests/risk/test_scoring.py` | Risk scoring tests |
| `config/ai_analysis_config.yaml` | Example AI-generated config |

---

## Chunk 1: Data Pipeline Foundation

### Task 1: Create Data Models for AI Context

**Files:**
- Create: `src/bot_trading/data/models.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/data/test_models.py
import pytest
from datetime import datetime, date
from decimal import Decimal
from bot_trading.data.models import MarketContext, SymbolAnalysis


def test_market_context_creation():
    """Test MarketContext dataclass creation."""
    context = MarketContext(
        date=date(2026, 3, 14),
        account_equity=Decimal("10000"),
        cash=Decimal("5000"),
        positions={},
        symbols=["AAPL", "MSFT"],
    )
    assert context.date == date(2026, 3, 14)
    assert context.account_equity == Decimal("10000")
    assert context.symbols == ["AAPL", "MSFT"]


def test_symbol_analysis_creation():
    """Test SymbolAnalysis dataclass creation."""
    analysis = SymbolAnalysis(
        symbol="AAPL",
        current_price=Decimal("175.50"),
        sma_20=Decimal("170.00"),
        rsi_14=65.5,
        volume_avg=50000000,
    )
    assert analysis.symbol == "AAPL"
    assert analysis.current_price == Decimal("175.50")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/data/test_models.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'bot_trading.data.models'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/bot_trading/data/models.py
"""Data models for AI market context and analysis."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class SymbolAnalysis:
    """Analysis data for a single symbol.

    Contains technical indicators and metrics computed from
    historical price data for AI consumption.
    """

    symbol: str
    current_price: Decimal
    sma_20: Decimal | None = None  # Simple Moving Average 20-day
    ema_12: Decimal | None = None  # Exponential Moving Average 12-day
    rsi_14: float | None = None  # Relative Strength Index 14-period
    macd: Decimal | None = None  # MACD line
    macd_signal: Decimal | None = None  # MACD signal line
    volume_avg: int | None = None  # Average volume
    price_change_pct: float | None = None  # Price change % over period
    volatility: float | None = None  # Historical volatility


@dataclass
class MarketContext:
    """Market context bundle for AI analysis.

    Aggregates account state, positions, and symbol analysis
    into a single structure for prompt generation.
    """

    date: date
    account_equity: Decimal
    cash: Decimal
    buying_power: Decimal
    positions: dict[str, Decimal]  # symbol -> quantity
    symbols: list[str]  # Symbols to analyze
    symbol_data: dict[str, SymbolAnalysis]  # symbol -> analysis
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/data/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/data/test_models.py src/bot_trading/data/models.py
git commit -m "feat(phase2): add AI context data models"
```

---

### Task 2: Implement Data Pipeline

**Files:**
- Create: `src/bot_trading/data/pipeline.py`
- Test: `tests/data/test_pipeline.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/data/test_pipeline.py
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from bot_trading.data.pipeline import DataPipeline
from bot_trading.providers.mock import MockProvider


@pytest.fixture
def mock_provider():
    """Create mock provider with test data."""
    provider = MockProvider()
    # Mock will be pre-configured with test data
    return provider


def test_pipeline_fetches_historical_data(mock_provider):
    """Test pipeline fetches historical bars for symbols."""
    pipeline = DataPipeline(provider=mock_provider)

    end_date = date(2026, 3, 14)
    start_date = end_date - timedelta(days=30)

    bars = pipeline.fetch_historical_bars(
        symbols=["AAPL"],
        start_date=start_date,
        end_date=end_date,
    )

    assert "AAPL" in bars
    assert len(bars["AAPL"]) > 0


def test_pipeline_calculates_sma(mock_provider):
    """Test SMA calculation from historical bars."""
    from bot_trading.providers.base import Bar

    pipeline = DataPipeline(provider=mock_provider)

    bars = [
        Bar(symbol="AAPL", timestamp=datetime.now(), open=Decimal("100"), high=Decimal("105"),
            low=Decimal("95"), close=Decimal(s), volume=1000)
        for s in [100, 102, 104, 103, 105, 107, 106, 108, 110, 109,
                  111, 113, 112, 114, 116, 115, 117, 119, 118, 120]
    ]

    sma = pipeline.calculate_sma(bars, period=20)
    assert sma == pytest.approx(Decimal("110.5"))


def test_pipeline_creates_market_context(mock_provider):
    """Test creating complete market context."""
    pipeline = DataPipeline(provider=mock_provider)

    context = pipeline.create_market_context(
        symbols=["AAPL", "MSFT"],
        lookback_days=20,
    )

    assert context.date is not None
    assert context.account_equity > 0
    assert "AAPL" in context.symbol_data
    assert context.symbol_data["AAPL"].current_price > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/data/test_pipeline.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'bot_trading.data.pipeline'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/bot_trading/data/pipeline.py
"""Data pipeline for fetching and transforming market data.

Fetches historical data from providers, calculates technical indicators,
and bundles everything into AI-friendly context objects.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from bot_trading.data.models import MarketContext, SymbolAnalysis
from bot_trading.providers.base import Bar

if TYPE_CHECKING:
    from bot_trading.providers.base import BaseProvider


class DataPipeline:
    """Pipeline for fetching and transforming market data.

    Orchestrates data fetching from providers and computes
    technical indicators for AI analysis.
    """

    def __init__(self, provider: "BaseProvider") -> None:
        """Initialize pipeline with a data provider.

        Args:
            provider: BaseProvider instance (Mock, Alpaca, etc.)
        """
        self.provider = provider

    def fetch_historical_bars(
        self,
        symbols: list[str],
        start_date: date,
        end_date: date,
        timeframe: str = "1Day",
    ) -> dict[str, list[Bar]]:
        """Fetch historical bars for multiple symbols.

        Args:
            symbols: List of symbols to fetch
            start_date: Start date
            end_date: End date
            timeframe: Bar timeframe

        Returns:
            Dictionary mapping symbol to list of bars
        """
        result = {}
        for symbol in symbols:
            bars = self.provider.get_historical_bars(symbol, start_date, end_date, timeframe)
            result[symbol] = bars
        return result

    def calculate_sma(self, bars: list[Bar], period: int) -> Decimal | None:
        """Calculate Simple Moving Average.

        Args:
            bars: List of historical bars
            period: SMA period

        Returns:
            SMA value or None if insufficient data
        """
        if len(bars) < period:
            return None

        recent_bars = bars[-period:]
        total = sum(b.close for b in recent_bars)
        return total / Decimal(period)

    def calculate_rsi(self, bars: list[Bar], period: int = 14) -> float | None:
        """Calculate Relative Strength Index.

        Args:
            bars: List of historical bars
            period: RSI period

        Returns:
            RSI value (0-100) or None if insufficient data
        """
        if len(bars) < period + 1:
            return None

        # Calculate price changes
        gains = []
        losses = []

        for i in range(len(bars) - 1, len(bars) - period - 1, -1):
            change = float(bars[i].close - bars[i-1].close)
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_volatility(self, bars: list[Bar], period: int = 20) -> float | None:
        """Calculate historical volatility (standard deviation of returns).

        Args:
            bars: List of historical bars
            period: Lookback period

        Returns:
            Volatility as float or None if insufficient data
        """
        if len(bars) < period + 1:
            return None

        recent_bars = bars[-period-1:]
        returns = []

        for i in range(1, len(recent_bars)):
            prev_close = float(recent_bars[i-1].close)
            curr_close = float(recent_bars[i].close)
            if prev_close > 0:
                returns.append((curr_close - prev_close) / prev_close)

        if not returns:
            return None

        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        return variance ** 0.5

    def create_symbol_analysis(
        self,
        symbol: str,
        bars: list[Bar],
        lookback_days: int = 20,
    ) -> SymbolAnalysis:
        """Create SymbolAnalysis from historical bars.

        Args:
            symbol: Trading symbol
            bars: Historical bars
            lookback_days: Days to look back for indicators

        Returns:
            SymbolAnalysis with computed indicators
        """
        latest_bar = bars[-1] if bars else None

        if not latest_bar:
            raise ValueError(f"No bars available for {symbol}")

        # Calculate indicators
        sma_20 = self.calculate_sma(bars, 20)
        rsi_14 = self.calculate_rsi(bars, 14)
        volatility = self.calculate_volatility(bars)

        # Calculate price change
        price_change_pct = None
        if len(bars) >= lookback_days:
            old_price = float(bars[-lookback_days].close)
            new_price = float(latest_bar.close)
            if old_price > 0:
                price_change_pct = ((new_price - old_price) / old_price) * 100

        # Calculate average volume
        volume_avg = None
        if len(bars) >= 20:
            volume_avg = sum(b.volume for b in bars[-20:]) // 20

        return SymbolAnalysis(
            symbol=symbol,
            current_price=latest_bar.close,
            sma_20=sma_20,
            rsi_14=rsi_14,
            volume_avg=volume_avg,
            price_change_pct=price_change_pct,
            volatility=volatility,
        )

    def create_market_context(
        self,
        symbols: list[str],
        lookback_days: int = 20,
    ) -> MarketContext:
        """Create complete market context for AI analysis.

        Args:
            symbols: Symbols to analyze
            lookback_days: Historical lookback period

        Returns:
            MarketContext with all data bundled
        """
        # Fetch account info
        account = self.provider.get_account()

        # Fetch positions
        positions = self.provider.get_positions()
        position_dict = {p.symbol: p.quantity for p in positions}

        # Fetch historical data
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days + 50)  # Buffer for indicators

        all_bars = self.fetch_historical_bars(symbols, start_date, end_date)

        # Create symbol analysis
        symbol_data = {}
        for symbol in symbols:
            if symbol in all_bars and all_bars[symbol]:
                symbol_data[symbol] = self.create_symbol_analysis(
                    symbol, all_bars[symbol], lookback_days
                )

        # Get latest prices
        latest_prices = {}
        for symbol in symbols:
            latest_prices[symbol] = self.provider.get_latest_price(symbol)

        return MarketContext(
            date=end_date,
            account_equity=account.equity,
            cash=account.cash,
            buying_power=account.buying_power,
            positions=position_dict,
            symbols=symbols,
            symbol_data=symbol_data,
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/data/test_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/data/test_pipeline.py src/bot_trading/data/pipeline.py
git commit -m "feat(phase2): add data pipeline with technical indicators"
```

---

## Chunk 2: AI Client Integration

### Task 3: Create AI Client with Retry Logic

**Files:**
- Create: `src/bot_trading/ai/client.py`
- Test: `tests/ai/test_client.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/ai/test_client.py
import pytest
from unittest.mock import Mock, patch
from bot_trading.ai.client import AIClient, AIServiceError


def test_client_initialization():
    """Test AI client initialization."""
    client = AIClient(api_key="test-key")
    assert client.api_key == "test-key"
    assert client.model == "claude-3-5-sonnet-20241022"


def test_client_throws_without_api_key():
    """Test client requires API key."""
    with pytest.raises(ValueError, match="API key is required"):
        AIClient(api_key="")


@patch("bot_trading.ai.client.anthropic.Anthropic")
def test_generate_analysis_success(mock_anthropic):
    """Test successful analysis generation."""
    mock_response = Mock()
    mock_response.content = [Mock(text="```json\n{\"risk_score\": 5}\n```")]

    mock_client = Mock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    client = AIClient(api_key="test-key")
    result = client.generate_analysis(
        prompt="Analyze AAPL",
        max_tokens=1000,
    )

    assert result == "{\"risk_score\": 5}"
    mock_client.messages.create.assert_called_once()


@patch("bot_trading.ai.client.anthropic.Anthropic")
def test_retry_on_transient_error(mock_anthropic):
    """Test retry logic on transient errors."""
    mock_client = Mock()
    mock_client.messages.create.side_effect = [
        Exception("Rate limit"),  # First call fails
        Mock(content=[Mock(text="Success")]),  # Second succeeds
    ]
    mock_anthropic.return_value = mock_client

    client = AIClient(api_key="test-key", max_retries=2)
    result = client.generate_analysis(prompt="Test")

    assert result == "Success"
    assert mock_client.messages.create.call_count == 2


@patch("bot_trading.ai.client.anthropic.Anthropic")
def test_fails_after_max_retries(mock_anthropic):
    """Test failure after max retries exceeded."""
    mock_client = Mock()
    mock_client.messages.create.side_effect = Exception("Persistent error")
    mock_anthropic.return_value = mock_client

    client = AIClient(api_key="test-key", max_retries=2)

    with pytest.raises(AIServiceError, match="Failed after 2 retries"):
        client.generate_analysis(prompt="Test")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/ai/test_client.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'bot_trading.ai.client'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/bot_trading/ai/client.py
"""AI client for Claude API integration.

Handles communication with Anthropic's Claude API with
retry logic and error handling.
"""

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore

if TYPE_CHECKING:
    pass


class AIServiceError(Exception):
    """Exception raised when AI service fails."""

    def __init__(self, message: str, original_exception: Exception | None = None):
        self.message = message
        self.original_exception = original_exception
        super().__init__(message)


@dataclass
class AIClientConfig:
    """Configuration for AI client."""

    api_key: str
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.3  # Lower for more deterministic analysis
    max_retries: int = 3
    retry_delay: float = 1.0  # Seconds between retries


class AIClient:
    """Client for Anthropic Claude API.

    Provides a simple interface for generating trading analysis
    with built-in retry logic and error handling.
    """

    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        """Initialize AI client.

        Args:
            api_key: Anthropic API key
            model: Claude model to use
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries (seconds)

        Raises:
            ValueError: If api_key is empty
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key is required")

        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        if anthropic is None:
            raise ImportError("anthropic package is required. Install with: pip install anthropic")

        self._client = anthropic.Anthropic(api_key=api_key)

    def generate_analysis(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> str:
        """Generate trading analysis using Claude.

        Args:
            prompt: Analysis prompt with market context
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)

        Returns:
            AI-generated analysis text

        Raises:
            AIServiceError: If all retry attempts fail
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )

                # Extract text from response
                if response.content and len(response.content) > 0:
                    return response.content[0].text

                raise AIServiceError("Empty response from AI service")

            except Exception as e:
                last_exception = e

                # Check if error is transient (worth retrying)
                if self._is_transient_error(e) and attempt < self.max_retries:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue

                # Non-transient error or max retries exceeded
                break

        raise AIServiceError(
            f"Failed after {self.max_retries} retries",
            original_exception=last_exception,
        )

    def generate_json_analysis(
        self,
        prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        """Generate JSON-structured analysis.

        Convenience method that wraps the prompt with
        instructions for JSON output.

        Args:
            prompt: Analysis prompt
            max_tokens: Maximum tokens in response

        Returns:
            JSON string from AI
        """
        json_prompt = f"""{prompt}

IMPORTANT: Respond ONLY with valid JSON. Do not include any text
outside the JSON structure. Your response must be parseable by
json.loads().

Example format:
{{
  "analysis": "...",
  "recommendation": "...",
  "risk_score": 5
}}
"""
        return self.generate_analysis(json_prompt, max_tokens=max_tokens)

    def _is_transient_error(self, error: Exception) -> bool:
        """Check if error is transient (worth retrying).

        Args:
            error: Exception to check

        Returns:
            True if error might be transient
        """
        error_str = str(error).lower()

        # Rate limiting errors
        if "rate" in error_str or "429" in error_str:
            return True

        # Timeout errors
        if "timeout" in error_str or "timed out" in error_str:
            return True

        # Connection errors
        if "connection" in error_str or "network" in error_str:
            return True

        # Server errors (5xx)
        if "500" in error_str or "502" in error_str or "503" in error_str:
            return True

        return False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/ai/test_client.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/ai/test_client.py src/bot_trading/ai/client.py
git commit -m "feat(phase2): add AI client with retry logic"
```

---

### Task 4: Create Prompt Templates

**Files:**
- Create: `src/bot_trading/ai/prompts.py`
- Test: `tests/ai/test_prompts.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/ai/test_prompts.py
import pytest
from datetime import date
from decimal import Decimal
from bot_trading.ai.prompts import PromptBuilder
from bot_trading.data.models import MarketContext, SymbolAnalysis


@pytest.fixture
def sample_context():
    """Create sample market context for testing."""
    return MarketContext(
        date=date(2026, 3, 14),
        account_equity=Decimal("10000"),
        cash=Decimal("5000"),
        buying_power=Decimal("10000"),
        positions={"AAPL": Decimal("10")},
        symbols=["AAPL"],
        symbol_data={
            "AAPL": SymbolAnalysis(
                symbol="AAPL",
                current_price=Decimal("175.50"),
                sma_20=Decimal("170.00"),
                rsi_14=65.5,
                volume_avg=50000000,
                price_change_pct=5.2,
                volatility=0.02,
            )
        }
    }


def test_prompt_builder_creates_basic_prompt(sample_context):
    """Test basic prompt creation."""
    builder = PromptBuilder()
    prompt = builder.build_analysis_prompt(sample_context)

    assert "AAPL" in prompt
    assert "175.50" in prompt
    assert "65.5" in prompt
    assert "10000" in prompt


def test_prompt_builder_includes_risk_instructions(sample_context):
    """Test prompt includes risk management instructions."""
    builder = PromptBuilder()
    prompt = builder.build_analysis_prompt(sample_context)

    assert "risk" in prompt.lower()
    assert "10%" in prompt  # Default risk limit


def test_prompt_builder_custom_risk_limit(sample_context):
    """Test custom risk limit in prompt."""
    builder = PromptBuilder(max_position_risk_pct=0.05)
    prompt = builder.build_analysis_prompt(sample_context)

    assert "5%" in prompt
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/ai/test_prompts.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'bot_trading.ai.prompts'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/bot_trading/ai/prompts.py
"""Prompt templates for AI trading analysis.

Builds structured prompts that include market context,
account state, and clear instructions for AI analysis.
"""

from dataclasses import dataclass
from decimal import Decimal

from bot_trading.data.models import MarketContext


@dataclass
class PromptBuilderConfig:
    """Configuration for prompt building."""

    max_position_risk_pct: float = 0.10  # 10% default
    max_portfolio_exposure: float = 0.20
    include_technical_indicators: bool = True
    include_positions: bool = True
    temperature: float = 0.3


class PromptBuilder:
    """Build prompts for AI trading analysis.

    Creates structured, consistent prompts that include
    all necessary context for AI to generate trading analysis.
    """

    def __init__(
        self,
        max_position_risk_pct: float = 0.10,
        max_portfolio_exposure: float = 0.20,
    ) -> None:
        """Initialize prompt builder.

        Args:
            max_position_risk_pct: Max risk per position (decimal, e.g., 0.10 = 10%)
            max_portfolio_exposure: Max total portfolio exposure
        """
        self.max_position_risk_pct = max_position_risk_pct
        self.max_portfolio_exposure = max_portfolio_exposure

    def build_analysis_prompt(self, context: MarketContext) -> str:
        """Build complete analysis prompt from market context.

        Args:
            context: MarketContext with all market data

        Returns:
            Formatted prompt string for AI
        """
        sections = [
            self._build_system_instructions(),
            self._build_account_section(context),
            self._build_positions_section(context),
            self._build_market_data_section(context),
            self._build_output_format_section(),
        ]

        return "\n\n".join(filter(None, sections))

    def _build_system_instructions(self) -> str:
        """Build system instructions for AI."""
        return """# Trading Risk Analysis Request

You are a conservative trading risk analyst. Your role is to:
1. Analyze market data and identify potential risks
2. Provide clear, actionable recommendations
3. NEVER recommend risking more than {risk_pct}% of portfolio per trade
4. Explain your reasoning in simple terms
5. Highlight warning signs and red flags

Important:
- Focus on RISK MANAGEMENT, not profit maximization
- If conditions are unclear, recommend waiting/holding
- Always consider worst-case scenarios
- Be conservative with risk estimates""".format(
            risk_pct=int(self.max_position_risk_pct * 100)
        )

    def _build_account_section(self, context: MarketContext) -> str:
        """Build account information section."""
        return """## Account Information

- Date: {date}
- Portfolio Value: ${equity:,.2f}
- Cash Available: ${cash:,.2f}
- Buying Power: ${buying_power:,.2f}""".format(
            date=context.date,
            equity=float(context.account_equity),
            cash=float(context.cash),
            buying_power=float(context.buying_power),
        )

    def _build_positions_section(self, context: MarketContext) -> str:
        """Build current positions section."""
        if not context.positions:
            return "## Current Positions\n\nNo open positions."

        position_lines = []
        for symbol, qty in context.positions.items():
            position_lines.append(f"- {symbol}: {qty} shares")

        return "## Current Positions\n\n" + "\n".join(position_lines)

    def _build_market_data_section(self, context: MarketContext) -> str:
        """Build market data section with symbols."""
        lines = ["## Market Data"]

        for symbol in context.symbols:
            if symbol not in context.symbol_data:
                continue

            analysis = context.symbol_data[symbol]
            symbol_lines = [
                f"\n### {symbol}",
                f"- Current Price: ${float(analysis.current_price):.2f}",
            ]

            if analysis.sma_20 is not None:
                diff_pct = ((float(analysis.current_price) - float(analysis.sma_20)) /
                           float(analysis.sma_20) * 100)
                symbol_lines.append(f"- 20-day SMA: ${float(analysis.sma_20):.2f} ({diff_pct:+.1f}%)")

            if analysis.rsi_14 is not None:
                rsi_status = "Neutral"
                if analysis.rsi_14 > 70:
                    rsi_status = "Overbought"
                elif analysis.rsi_14 < 30:
                    rsi_status = "Oversold"
                symbol_lines.append(f"- RSI(14): {analysis.rsi_14:.1f} ({rsi_status})")

            if analysis.price_change_pct is not None:
                symbol_lines.append(f"- {20}-day Change: {analysis.price_change_pct:+.1f}%")

            if analysis.volatility is not None:
                symbol_lines.append(f"- Volatility: {analysis.volatility:.4f}")

            if analysis.volume_avg is not None:
                symbol_lines.append(f"- Avg Volume: {analysis.volume_avg:,}")

            lines.extend(symbol_lines)

        return "\n".join(lines)

    def _build_output_format_section(self) -> str:
        """Build output format instructions."""
        return """## Required Output Format

Provide your analysis as JSON with this exact structure:

```json
{
  "overall_sentiment": "bullish|bearish|neutral",
  "symbols": {
    "AAPL": {
      "action": "BUY|SELL|HOLD",
      "confidence": 0.0-1.0,
      "risk_score": 1-10,
      "reasoning": "Brief explanation",
      "entry_price": null or number,
      "stop_loss": null or number,
      "target_price": null or number,
      "position_size_pct": 0.0-1.0,
      "warning": null or "risk warning"
    }
  },
  "portfolio_risk": {
    "current_exposure": 0.0-1.0,
    "recommended_max_exposure": 0.0-1.0,
    "risk_factors": ["list of concerns"]
  }
}
```

Risk Score Guide:
- 1-2: Very Low Risk - Safe to proceed
- 3-4: Low Risk - Proceed with caution
- 5-6: Medium Risk - Be conservative
- 7-8: High Risk - Consider reducing size
- 9-10: Very High Risk - Avoid or wait

Respond ONLY with valid JSON. No text outside the JSON structure."""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/ai/test_prompts.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/ai/test_prompts.py src/bot_trading/ai/prompts.py
git commit -m "feat(phase2): add prompt builder for AI analysis"
```

---

## Chunk 3: Config Schema & Validation

### Task 5: Create AI Output Config Schema

**Files:**
- Create: `src/bot_trading/ai/schema.py`
- Test: `tests/ai/test_schema.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/ai/test_schema.py
import pytest
import json
from pydantic import ValidationError
from bot_trading.ai.schema import (
    AIAnalysisResult,
    SymbolRecommendation,
    PortfolioRisk,
)


def test_valid_minimal_schema():
    """Test minimal valid schema validation."""
    data = {
        "overall_sentiment": "neutral",
        "symbols": {},
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": [],
        }
    }

    result = AIAnalysisResult.model_validate(data)
    assert result.overall_sentiment == "neutral"


def test_valid_full_schema():
    """Test full valid schema with all fields."""
    data = {
        "overall_sentiment": "bullish",
        "symbols": {
            "AAPL": {
                "action": "BUY",
                "confidence": 0.75,
                "risk_score": 4,
                "reasoning": "Strong momentum with reasonable valuation",
                "entry_price": 175.50,
                "stop_loss": 170.00,
                "target_price": 185.00,
                "position_size_pct": 0.08,
            }
        },
        "portfolio_risk": {
            "current_exposure": 0.15,
            "recommended_max_exposure": 0.2,
            "risk_factors": ["Market near all-time highs"],
        }
    }

    result = AIAnalysisResult.model_validate(data)
    assert result.symbols["AAPL"].action == "BUY"
    assert result.symbols["AAPL"].confidence == 0.75


def test_invalid_action():
    """Test validation rejects invalid action."""
    data = {
        "overall_sentiment": "neutral",
        "symbols": {
            "AAPL": {
                "action": "INVALID_ACTION",
                "confidence": 0.5,
                "risk_score": 5,
                "reasoning": "test",
            }
        },
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": [],
        }
    }

    with pytest.raises(ValidationError):
        AIAnalysisResult.model_validate(data)


def test_risk_score_range():
    """Test risk score must be 1-10."""
    data = {
        "overall_sentiment": "neutral",
        "symbols": {
            "AAPL": {
                "action": "HOLD",
                "confidence": 0.5,
                "risk_score": 15,  # Invalid!
                "reasoning": "test",
            }
        },
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": [],
        }
    }

    with pytest.raises(ValidationError):
        AIAnalysisResult.model_validate(data)


def test_json_roundtrip():
    """Test JSON serialization/deserialization."""
    original = AIAnalysisResult(
        overall_sentiment="bearish",
        symbols={
            "MSFT": {
                "action": "SELL",
                "confidence": 0.6,
                "risk_score": 6,
                "reasoning": "Technical breakdown",
                "position_size_pct": 0.0,
            }
        },
        portfolio_risk=PortfolioRisk(
            current_exposure=0.1,
            recommended_max_exposure=0.15,
            risk_factors=["Increasing volatility"],
        ),
    )

    # Serialize
    json_str = original.model_dump_json()

    # Deserialize
    restored = AIAnalysisResult.model_validate_json(json_str)

    assert restored.overall_sentiment == "bearish"
    assert restored.symbols["MSFT"].action == "SELL"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/ai/test_schema.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'bot_trading.ai.schema'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/bot_trading/ai/schema.py
"""AI output config schema using Pydantic.

Defines the schema for AI-generated trading analysis configs.
Must be both AI-friendly (simple structure) and Python-readable
(strict validation, clear errors).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Literal

try:
    from pydantic import BaseModel, Field, field_validator
except ImportError:
    # Fallback for environments without pydantic
    BaseModel = object  # type: ignore
    Field = lambda **kwargs: None  # type: ignore
    field_validator = lambda *args: lambda f: f  # type: ignore


class TradingAction(str, Enum):
    """Valid trading actions."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Sentiment(str, Enum):
    """Overall market sentiment."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class SymbolRecommendation(BaseModel):
    """AI recommendation for a single symbol.

    Contains action, confidence, risk score, and optional
    price levels for position management.
    """

    action: TradingAction
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence level 0-1")
    risk_score: int = Field(ge=1, le=10, description="Risk score 1-10")
    reasoning: str = Field(min_length=1, description="Explanation for recommendation")
    entry_price: float | None = Field(None, ge=0, description="Suggested entry price")
    stop_loss: float | None = Field(None, ge=0, description="Suggested stop loss")
    target_price: float | None = Field(None, ge=0, description="Price target")
    position_size_pct: float = Field(
        ge=0.0,
        le=1.0,
        description="Position size as % of portfolio"
    )
    warning: str | None = Field(None, description="Risk warning if applicable")

    @field_validator("position_size_pct")
    @classmethod
    def position_size_not_zero_when_buying(cls, v: float, info) -> float:
        """Ensure position size > 0 when action is BUY."""
        if info.data.get("action") == TradingAction.BUY and v == 0:
            raise ValueError("position_size_pct must be > 0 for BUY orders")
        return v

    @field_validator("entry_price", "stop_loss", "target_price")
    @classmethod
    def prices_consistent(cls, v: float | None, info) -> float | None:
        """Validate price relationships."""
        if v is None:
            return v

        action = info.data.get("action")
        entry = info.data.get("entry_price")
        stop = info.data.get("stop_loss")

        if action == TradingAction.BUY and entry and stop:
            if stop >= entry:
                raise ValueError("stop_loss must be below entry_price for BUY")

        return v


class PortfolioRisk(BaseModel):
    """Portfolio-level risk assessment."""

    current_exposure: float = Field(ge=0.0, le=1.0, description="Current portfolio exposure")
    recommended_max_exposure: float = Field(
        ge=0.0,
        le=1.0,
        description="Recommended max exposure"
    )
    risk_factors: list[str] = Field(default_factory=list, description="List of risk concerns")


class AIAnalysisResult(BaseModel):
    """Complete AI analysis result.

    This is the core output schema that AI must generate.
    It's designed to be simple enough for AI to get right,
    but structured enough for Python to validate strictly.
    """

    overall_sentiment: Sentiment
    symbols: dict[str, SymbolRecommendation] = Field(
        default_factory=dict,
        description="Symbol-specific recommendations"
    )
    portfolio_risk: PortfolioRisk

    @field_validator("overall_sentiment", mode="before")
    @classmethod
    def normalize_sentiment(cls, v: str) -> str:
        """Normalize sentiment to lowercase."""
        if isinstance(v, str):
            return v.lower()
        return v

    def get_recommendation(self, symbol: str) -> SymbolRecommendation | None:
        """Get recommendation for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            SymbolRecommendation or None if not found
        """
        return self.symbols.get(symbol)

    def is_high_risk(self, symbol: str) -> bool:
        """Check if symbol recommendation is high risk (score >= 7).

        Args:
            symbol: Trading symbol

        Returns:
            True if risk score >= 7
        """
        rec = self.get_recommendation(symbol)
        return rec is not None and rec.risk_score >= 7


# Type alias for convenience
AIConfig = AIAnalysisResult
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/ai/test_schema.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/ai/test_schema.py src/bot_trading/ai/schema.py
git commit -m "feat(phase2): add AI output config schema with Pydantic"
```

---

### Task 6: Create Config Validator

**Files:**
- Create: `src/bot_trading/ai/validator.py`
- Test: `tests/ai/test_validator.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/ai/test_validator.py
import pytest
from bot_trading.ai.validator import ConfigValidator, ValidationError
from bot_trading.ai.schema import AIAnalysisResult


def test_validate_valid_json():
    """Test validation of valid JSON string."""
    json_str = '''{
        "overall_sentiment": "neutral",
        "symbols": {},
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": []
        }
    }'''

    validator = ConfigValidator()
    result = validator.validate_json(json_str)

    assert isinstance(result, AIAnalysisResult)
    assert result.overall_sentiment == "neutral"


def test_validate_invalid_json():
    """Test validation of invalid JSON."""
    json_str = '{"invalid": json}'

    validator = ConfigValidator()

    with pytest.raises(ValidationError, match="Invalid JSON"):
        validator.validate_json(json_str)


def test_validate_invalid_schema():
    """Test validation of JSON with invalid schema."""
    json_str = '''{
        "overall_sentiment": "invalid",
        "symbols": {},
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": []
        }
    }'''

    validator = ConfigValidator()

    with pytest.raises(ValidationError):
        validator.validate_json(json_str)


def test_validate_extracts_json_from_markdown():
    """Test validator extracts JSON from markdown code blocks."""
    markdown = """Here's my analysis:

```json
{
    "overall_sentiment": "bullish",
    "symbols": {},
    "portfolio_risk": {
        "current_exposure": 0.0,
        "recommended_max_exposure": 0.2,
        "risk_factors": []
    }
}
```

That's my recommendation!"""

    validator = ConfigValidator()
    result = validator.validate_json(markdown)

    assert result.overall_sentiment == "bullish"


def test_validate_with_custom_limits():
    """Test validation with custom risk limits."""
    json_str = '''{
        "overall_sentiment": "neutral",
        "symbols": {
            "AAPL": {
                "action": "BUY",
                "confidence": 0.8,
                "risk_score": 5,
                "reasoning": "test",
                "position_size_pct": 0.15
            }
        },
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": []
        }
    }'''

    validator = ConfigValidator(max_position_risk_pct=0.10)

    with pytest.raises(ValidationError, match="exceeds maximum"):
        validator.validate_json(json_str)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/ai/test_validator.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'bot_trading.ai.validator'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/bot_trading/ai/validator.py
"""Validate AI-generated configs.

Ensures AI outputs conform to schema and risk limits.
Provides clear error messages for debugging.
"""

import json
import re
from dataclasses import dataclass

from bot_trading.ai.schema import AIAnalysisResult, SymbolRecommendation


class ValidationError(Exception):
    """Config validation error with details."""

    def __init__(self, message: str, path: str = "", original_error: Exception | None = None):
        self.message = message
        self.path = path
        self.original_error = original_error

        full_message = message
        if path:
            full_message = f"{path}: {message}"
        super().__init__(full_message)


@dataclass
class ValidationConfig:
    """Configuration for validation."""

    max_position_risk_pct: float = 0.10
    max_portfolio_exposure: float = 0.20
    allow_unknown_fields: bool = False


class ConfigValidator:
    """Validate AI-generated trading configs.

    Features:
    - Extracts JSON from markdown code blocks
    - Validates schema with Pydantic
    - Enforces risk limits
    - Clear error messages
    """

    JSON_BLOCK_PATTERN = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)
    INLINE_JSON_PATTERN = re.compile(r"\{.*\}", re.DOTALL)

    def __init__(
        self,
        max_position_risk_pct: float = 0.10,
        max_portfolio_exposure: float = 0.20,
    ) -> None:
        """Initialize validator.

        Args:
            max_position_risk_pct: Max % risk per position
            max_portfolio_exposure: Max portfolio exposure
        """
        self.config = ValidationConfig(
            max_position_risk_pct=max_position_risk_pct,
            max_portfolio_exposure=max_portfolio_exposure,
        )

    def validate_json(self, json_str: str) -> AIAnalysisResult:
        """Validate JSON string and return config.

        Args:
            json_str: JSON string (may be in markdown)

        Returns:
            Validated AIAnalysisResult

        Raises:
            ValidationError: If validation fails
        """
        # Extract JSON from markdown if needed
        json_content = self._extract_json(json_str)

        # Parse JSON
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            raise ValidationError(
                f"Invalid JSON: {e.msg}",
                original_error=e,
            )

        # Validate schema
        try:
            config = AIAnalysisResult.model_validate(data)
        except Exception as e:
            raise ValidationError(
                f"Schema validation failed: {str(e)}",
                original_error=e,
            )

        # Validate risk limits
        self._validate_risk_limits(config)

        return config

    def _extract_json(self, text: str) -> str:
        """Extract JSON from text, handling markdown blocks.

        Args:
            text: Text that may contain JSON

        Returns:
            Extracted JSON string

        Raises:
            ValidationError: If JSON cannot be extracted
        """
        # Try markdown code block first
        match = self.JSON_BLOCK_PATTERN.search(text)
        if match:
            return match.group(1).strip()

        # Try to find JSON object
        match = self.INLINE_JSON_PATTERN.search(text)
        if match:
            return match.group(0).strip()

        # Assume entire text is JSON
        return text.strip()

    def _validate_risk_limits(self, config: AIAnalysisResult) -> None:
        """Validate config against risk limits.

        Args:
            config: Parsed AIAnalysisResult

        Raises:
            ValidationError: If limits exceeded
        """
        # Check portfolio risk
        if config.portfolio_risk.recommended_max_exposure > self.config.max_portfolio_exposure:
            raise ValidationError(
                f"Recommended exposure {config.portfolio_risk.recommended_max_exposure:.1%} "
                f"exceeds maximum {self.config.max_portfolio_exposure:.1%}",
                path="portfolio_risk.recommended_max_exposure",
            )

        # Check individual symbol risks
        for symbol, rec in config.symbols.items():
            if rec.position_size_pct > self.config.max_position_risk_pct:
                raise ValidationError(
                    f"Position size {rec.position_size_pct:.1%} for {symbol} "
                    f"exceeds maximum {self.config.max_position_risk_pct:.1%}",
                    path=f"symbols.{symbol}.position_size_pct",
                )

    def validate_and_get_warnings(self, json_str: str) -> tuple[AIAnalysisResult, list[str]]:
        """Validate with warnings instead of exceptions for some issues.

        Args:
            json_str: JSON string

        Returns:
            Tuple of (config, warnings)
        """
        warnings = []

        try:
            config = self.validate_json(json_str)
        except ValidationError as e:
            return None, [str(e)]

        # Check for high-risk recommendations
        for symbol, rec in config.symbols.items():
            if rec.risk_score >= 7:
                warnings.append(f"{symbol}: High risk score ({rec.risk_score}/10)")

            if rec.warning:
                warnings.append(f"{symbol}: {rec.warning}")

        return config, warnings
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/ai/test_validator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/ai/test_validator.py src/bot_trading/ai/validator.py
git commit -m "feat(phase2): add config validator with risk limit checks"
```

---

## Chunk 4: Risk Scoring & Integration

### Task 7: Create Risk Scoring Algorithm

**Files:**
- Create: `src/bot_trading/risk/scoring.py`
- Test: `tests/risk/test_scoring.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/risk/test_scoring.py
import pytest
from decimal import Decimal
from bot_trading.risk.scoring import RiskScorer, RiskFactors
from bot_trading.ai.schema import AIAnalysisResult, SymbolRecommendation, PortfolioRisk


@pytest.fixture
def sample_analysis():
    """Create sample AI analysis for testing."""
    return AIAnalysisResult(
        overall_sentiment="neutral",
        symbols={
            "AAPL": SymbolRecommendation(
                action="BUY",
                confidence=0.75,
                risk_score=5,
                reasoning="Test",
                position_size_pct=0.08,
                entry_price=175.0,
                stop_loss=170.0,
                target_price=185.0,
            )
        },
        portfolio_risk=PortfolioRisk(
            current_exposure=0.1,
            recommended_max_exposure=0.2,
            risk_factors=[],
        ),
    )


def test_risk_sorer_creates_factors(sample_analysis):
    """Test risk scorer extracts risk factors."""
    scorer = RiskScorer()
    factors = scorer.analyze_risk_factors(sample_analysis)

    assert factors.symbol == "AAPL"
    assert factors.ai_risk_score == 5
    assert factors.confidence == 0.75


def test_risk_sorer_calculates_position_size(sample_analysis):
    """Test position size calculation based on risk."""
    scorer = RiskScorer(portfolio_value=Decimal("10000"))

    size = scorer.calculate_position_size(
        analysis=sample_analysis,
        symbol="AAPL",
        risk_per_trade_pct=0.02,  # 2% risk
    )

    # With $175 entry and $5 stop loss distance:
    # 2% of $10k = $200 risk
    # $200 / $5 = 40 shares max
    assert size > 0
    assert size <= 100


def test_risk_sorer_adjusts_for_high_risk():
    """Test size reduction for high-risk symbols."""
    high_risk_analysis = AIAnalysisResult(
        overall_sentiment="neutral",
        symbols={
            "TSLA": SymbolRecommendation(
                action="BUY",
                confidence=0.5,
                risk_score=8,  # High risk!
                reasoning="Test",
                position_size_pct=0.05,
            )
        },
        portfolio_risk=PortfolioRisk(
            current_exposure=0.0,
            recommended_max_exposure=0.2,
            risk_factors=["High volatility"],
        ),
    )

    scorer = RiskScorer(portfolio_value=Decimal("10000"))

    # High risk should reduce position
    factors = scorer.analyze_risk_factors(high_risk_analysis)
    assert factors.risk_multiplier < 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/risk/test_scoring.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'bot_trading.risk.scoring'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/bot_trading/risk/scoring.py
"""Risk scoring algorithm.

Combines AI analysis with technical indicators to calculate
position sizes and risk adjustments.
"""

from dataclasses import dataclass
from decimal import Decimal

from bot_trading.ai.schema import AIAnalysisResult


@dataclass
class RiskFactors:
    """Risk factors for a trading decision."""

    symbol: str
    ai_risk_score: int  # 1-10 from AI
    confidence: float  # 0-1 from AI
    volatility: float | None = None  # Historical volatility
    distance_from_avg: float | None = None  # % distance from SMA
    rsi: float | None = None  # RSI value
    risk_multiplier: float = 1.0  # Size adjustment factor


class RiskScorer:
    """Calculate position sizes based on AI analysis and risk.

    Combines AI recommendations with technical risk metrics
    to determine safe position sizes.
    """

    def __init__(
        self,
        portfolio_value: Decimal = Decimal("10000"),
        max_risk_per_trade_pct: float = 0.02,  # 2% default
    ) -> None:
        """Initialize risk scorer.

        Args:
            portfolio_value: Total portfolio value
            max_risk_per_trade_pct: Max % of portfolio to risk per trade
        """
        self.portfolio_value = portfolio_value
        self.max_risk_per_trade_pct = max_risk_per_trade_pct

    def analyze_risk_factors(
        self,
        analysis: AIAnalysisResult,
        symbol: str | None = None,
    ) -> RiskFactors:
        """Extract risk factors from AI analysis.

        Args:
            analysis: AI analysis result
            symbol: Symbol to analyze (uses first if None)

        Returns:
            RiskFactors object
        """
        # Get symbol recommendation
        if symbol is None:
            if not analysis.symbols:
                raise ValueError("No symbols in analysis")
            symbol = next(iter(analysis.symbols.keys()))

        rec = analysis.symbols.get(symbol)
        if rec is None:
            raise ValueError(f"No recommendation for {symbol}")

        # Calculate risk multiplier based on AI score
        risk_multiplier = self._calculate_risk_multiplier(rec.risk_score)

        return RiskFactors(
            symbol=symbol,
            ai_risk_score=rec.risk_score,
            confidence=rec.confidence,
            risk_multiplier=risk_multiplier,
        )

    def calculate_position_size(
        self,
        analysis: AIAnalysisResult,
        symbol: str,
        entry_price: Decimal,
        stop_loss: Decimal,
        risk_per_trade_pct: float | None = None,
    ) -> int:
        """Calculate safe position size based on risk.

        Uses the standard formula:
        Position Size = (Portfolio * Risk%) / (Entry - Stop)

        Args:
            analysis: AI analysis result
            symbol: Trading symbol
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_per_trade_pct: Risk % per trade (uses default if None)

        Returns:
            Maximum safe position size in shares
        """
        if risk_per_trade_pct is None:
            risk_per_trade_pct = self.max_risk_per_trade_pct

        # Get risk factors
        factors = self.analyze_risk_factors(analysis, symbol)

        # Calculate dollar risk
        dollar_risk = float(self.portfolio_value) * risk_per_trade_pct

        # Apply risk multiplier
        dollar_risk *= factors.risk_multiplier

        # Calculate stop distance
        stop_distance = abs(float(entry_price) - float(stop_loss))

        if stop_distance == 0:
            return 0

        # Calculate position size
        shares = int(dollar_risk / stop_distance)

        return max(0, shares)

    def _calculate_risk_multiplier(self, ai_risk_score: int) -> float:
        """Calculate size multiplier based on AI risk score.

        Higher risk = smaller position.

        Args:
            ai_risk_score: AI risk score (1-10)

        Returns:
            Multiplier (0.1 to 1.0)
        """
        # Risk score to multiplier mapping
        # 1-2: 100% (very safe)
        # 3-4: 90%
        # 5-6: 75%
        # 7-8: 50%
        # 9-10: 25% (very risky)
        multipliers = {
            1: 1.0,
            2: 1.0,
            3: 0.9,
            4: 0.9,
            5: 0.75,
            6: 0.75,
            7: 0.5,
            8: 0.5,
            9: 0.25,
            10: 0.25,
        }

        return multipliers.get(ai_risk_score, 0.5)

    def get_recommendation_summary(
        self,
        analysis: AIAnalysisResult,
        symbol: str,
    ) -> str:
        """Get human-readable risk summary.

        Args:
            analysis: AI analysis result
            symbol: Trading symbol

        Returns:
            Formatted summary string
        """
        rec = analysis.symbols.get(symbol)
        if rec is None:
            return f"No recommendation for {symbol}"

        factors = self.analyze_risk_factors(analysis, symbol)

        lines = [
            f"Symbol: {symbol}",
            f"Action: {rec.action}",
            f"AI Risk Score: {rec.risk_score}/10",
            f"Confidence: {rec.confidence:.0%}",
            f"Risk Adjustment: {factors.risk_multiplier:.0%} of normal size",
        ]

        if rec.entry_price and rec.stop_loss:
            risk_per_share = abs(rec.entry_price - rec.stop_loss)
            lines.append(f"Risk per Share: ${risk_per_share:.2f}")

        if rec.warning:
            lines.append(f"WARNING: {rec.warning}")

        return "\n".join(lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/risk/test_scoring.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/risk/test_scoring.py src/bot_trading/risk/scoring.py
git commit -m "feat(phase2): add risk scoring algorithm"
```

---

### Task 8: Create End-to-End Integration

**Files:**
- Create: `src/bot_trading/ai/analyzer.py`
- Test: `tests/ai/test_analyzer.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/ai/test_analyzer.py
import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from bot_trading.ai.analyzer import TradingAnalyzer
from bot_trading.providers.mock import MockProvider


def test_analyzer_initialization():
    """Test analyzer initialization."""
    provider = MockProvider()
    analyzer = TradingAnalyzer(provider=provider)

    assert analyzer.provider is not None
    assert analyzer.pipeline is not None


@patch("bot_trading.ai.analyzer.AIClient")
def test_analyzer_full_analysis(mock_ai_client):
    """Test end-to-end analysis flow."""
    # Mock AI response
    mock_ai_client.return_value.generate_analysis.return_value = '''{
        "overall_sentiment": "neutral",
        "symbols": {
            "AAPL": {
                "action": "HOLD",
                "confidence": 0.6,
                "risk_score": 5,
                "reasoning": "Waiting for better entry",
                "position_size_pct": 0.0
            }
        },
        "portfolio_risk": {
            "current_exposure": 0.0,
            "recommended_max_exposure": 0.2,
            "risk_factors": []
        }
    }'''

    provider = MockProvider()
    analyzer = TradingAnalyzer(provider=provider, api_key="test-key")

    result = analyzer.analyze(symbols=["AAPL"])

    assert result is not None
    assert result.overall_sentiment == "neutral"
    assert result.symbols["AAPL"].action == "HOLD"


def test_analyzer_includes_risk_summary():
    """Test analyzer provides risk summary."""
    provider = MockProvider()

    with patch("bot_trading.ai.analyzer.AIClient") as mock_ai:
        mock_ai.return_value.generate_analysis.return_value = '''{
            "overall_sentiment": "neutral",
            "symbols": {},
            "portfolio_risk": {
                "current_exposure": 0.0,
                "recommended_max_exposure": 0.2,
                "risk_factors": []
            }
        }'''

        analyzer = TradingAnalyzer(provider=provider, api_key="test-key")
        summary = analyzer.analyze_with_risk_summary(symbols=["AAPL"])

        assert "Symbol:" in summary or "No symbols" in summary
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/ai/test_analyzer.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'bot_trading.ai.analyzer'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/bot_trading/ai/analyzer.py
"""End-to-end trading analysis orchestrator.

Coordinates data pipeline, AI client, and risk scoring
to provide complete trading analysis.
"""

from dataclasses import dataclass

from bot_trading.ai.client import AIClient
from bot_trading.ai.prompts import PromptBuilder
from bot_trading.ai.schema import AIAnalysisResult
from bot_trading.ai.validator import ConfigValidator
from bot_trading.data.pipeline import DataPipeline
from bot_trading.risk.scoring import RiskScorer


@dataclass
class AnalyzerConfig:
    """Configuration for TradingAnalyzer."""

    ai_api_key: str
    max_position_risk_pct: float = 0.10
    max_portfolio_exposure: float = 0.20
    lookback_days: int = 20


class TradingAnalyzer:
    """End-to-end trading analysis.

    Flow:
    1. Fetch market data via DataPipeline
    2. Build prompt via PromptBuilder
    3. Get AI analysis via AIClient
    4. Validate via ConfigValidator
    5. Calculate position sizes via RiskScorer
    """

    def __init__(
        self,
        provider,  # BaseProvider
        api_key: str,
        max_position_risk_pct: float = 0.10,
        lookback_days: int = 20,
    ) -> None:
        """Initialize analyzer.

        Args:
            provider: BaseProvider instance
            api_key: Anthropic API key
            max_position_risk_pct: Max risk per position
            lookback_days: Historical lookback period
        """
        self.provider = provider
        self.pipeline = DataPipeline(provider)
        self.prompt_builder = PromptBuilder(max_position_risk_pct=max_position_risk_pct)
        self.ai_client = AIClient(api_key=api_key)
        self.validator = ConfigValidator(max_position_risk_pct=max_position_risk_pct)
        self.risk_scorer = RiskScorer()
        self.lookback_days = lookback_days

    def analyze(
        self,
        symbols: list[str],
    ) -> AIAnalysisResult:
        """Run complete trading analysis.

        Args:
            symbols: Symbols to analyze

        Returns:
            Validated AIAnalysisResult

        Raises:
            AIServiceError: If AI call fails
            ValidationError: If config validation fails
        """
        # Step 1: Fetch and prepare data
        context = self.pipeline.create_market_context(
            symbols=symbols,
            lookback_days=self.lookback_days,
        )

        # Step 2: Build prompt
        prompt = self.prompt_builder.build_analysis_prompt(context)

        # Step 3: Get AI analysis
        ai_response = self.ai_client.generate_json_analysis(prompt)

        # Step 4: Validate
        result = self.validator.validate_json(ai_response)

        return result

    def analyze_with_risk_summary(
        self,
        symbols: list[str],
    ) -> str:
        """Analyze and return human-readable summary.

        Args:
            symbols: Symbols to analyze

        Returns:
            Formatted summary string
        """
        result = self.analyze(symbols)

        lines = [
            f"=== Trading Analysis Report ===",
            f"Overall Sentiment: {result.overall_sentiment.value.upper()}",
            "",
        ]

        # Portfolio risk
        lines.extend([
            "Portfolio Risk:",
            f"  Current Exposure: {result.portfolio_risk.current_exposure:.1%}",
            f"  Recommended Max: {result.portfolio_risk.recommended_max_exposure:.1%}",
        ])

        if result.portfolio_risk.risk_factors:
            lines.append("  Risk Factors:")
            for factor in result.portfolio_risk.risk_factors:
                lines.append(f"    - {factor}")

        lines.append("")

        # Symbol recommendations
        for symbol, rec in result.symbols.items():
            summary = self.risk_scorer.get_recommendation_summary(result, symbol)
            lines.extend(["", f"=== {symbol} ===", summary])

        return "\n".join(lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/ai/test_analyzer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/ai/test_analyzer.py src/bot_trading/ai/analyzer.py
git commit -m "feat(phase2): add end-to-end trading analyzer"
```

---

## Chunk 5: CLI Interface & Documentation

### Task 9: Create CLI Entry Point

**Files:**
- Create: `src/bot_trading/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli.py
import pytest
from unittest.mock import Mock, patch
from bot_trading.cli import main


@patch("bot_trading.cli.TradingAnalyzer")
@patch("bot_trading.cli.MockProvider")
def test_cli_runs_analysis(mock_provider, mock_analyzer, capsys):
    """Test CLI runs analysis and outputs results."""
    # Mock analyzer
    mock_result = Mock()
    mock_result.overall_sentiment.value = "neutral"
    mock_result.symbols = {}
    mock_result.portfolio_risk.current_exposure = 0.0
    mock_result.portfolio_risk.recommended_max_exposure = 0.2
    mock_result.portfolio_risk.risk_factors = []

    mock_analyzer.return_value.analyze_with_risk_summary.return_value = "Test Analysis"

    # Run CLI
    try:
        main(["--symbols", "AAPL,MSFT"])
    except SystemExit:
        pass  # CLI may exit

    captured = capsys.readouterr()
    assert "Analysis" in captured.out or "Test Analysis" in captured.out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL (may not exist yet)

- [ ] **Step 3: Write minimal implementation**

```python
# src/bot_trading/cli.py
"""CLI entry point for trading analysis.

Usage:
    python -m bot_trading.cli --symbols AAPL,MSFT
"""

import os
import sys

from bot_trading.ai.analyzer import TradingAnalyzer
from bot_trading.providers.mock import MockProvider


def main(argv: list[str] | None = None) -> int:
    """Run trading analysis CLI.

    Args:
        argv: Command line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="AI-powered trading risk analysis",
    )
    parser.add_argument(
        "--symbols",
        type=str,
        required=True,
        help="Comma-separated list of symbols to analyze",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("ANTHROPIC_API_KEY"),
        help="Anthropic API key (default: ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--max-risk",
        type=float,
        default=0.10,
        help="Max position risk as decimal (default: 0.10)",
    )

    args = parser.parse_args(argv)

    if not args.api_key:
        print("Error: ANTHROPIC_API_KEY environment variable or --api-key argument required")
        return 1

    symbols = [s.strip().upper() for s in args.symbols.split(",")]

    try:
        # Initialize
        provider = MockProvider()
        analyzer = TradingAnalyzer(
            provider=provider,
            api_key=args.api_key,
            max_position_risk_pct=args.max_risk,
        )

        # Run analysis
        print(f"Analyzing: {', '.join(symbols)}")
        print("")

        summary = analyzer.analyze_with_risk_summary(symbols=symbols)

        print(summary)
        print("")
        print("=== Analysis Complete ===")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_cli.py src/bot_trading/cli.py
git commit -m "feat(phase2): add CLI entry point for trading analysis"
```

---

### Task 10: Update Documentation and Example Config

**Files:**
- Modify: `README.md`
- Modify: `.env.example`
- Create: `config/ai_analysis_config.yaml`
- Create: `docs/ai-integration-guide.md`

- [ ] **Step 1: Update README with Phase 2 info**

Add to README.md after "Development Status" table:

```markdown
## Phase 2: AI Integration (Current)

Phase 2 adds AI-powered risk analysis:

- Data Pipeline: Fetch market data and calculate technical indicators
- AI Client: Claude API integration with retry logic
- Config Schema: Structured output format (AI-friendly, Python-readable)
- Risk Scoring: Position sizing based on AI analysis

### Quick Start (Phase 2)

```bash
# Set up Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"

# Run analysis
python -m bot_trading.cli --symbols AAPL,MSFT
```

See [AI Integration Guide](docs/ai-integration-guide.md) for details.
```

- [ ] **Step 2: Update .env.example**

Add to `.env.example`:

```bash
# Anthropic API for AI Analysis
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

- [ ] **Step 3: Create example AI output config**

```yaml
# config/ai_analysis_config.yaml
# Example AI-generated analysis output

# This file demonstrates the expected output format from AI
# Actual configs will be generated by the AI based on market data

overall_sentiment: "neutral"

symbols:
  AAPL:
    action: "HOLD"
    confidence: 0.65
    risk_score: 5
    reasoning: "Price near resistance, waiting for pullback"
    position_size_pct: 0.0
    entry_price: null
    stop_loss: null
    target_price: null

portfolio_risk:
  current_exposure: 0.0
  recommended_max_exposure: 0.2
  risk_factors: []
```

- [ ] **Step 4: Create AI integration guide**

```markdown
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
```

- [ ] **Step 5: Run final verification**

```bash
# Run all tests
pytest tests/ -v

# Check linting
ruff check src/ tests/

# Verify CLI help works
python -m bot_trading.cli --help
```

- [ ] **Step 6: Final commit**

```bash
git add README.md .env.example config/ai_analysis_config.yaml docs/ai-integration-guide.md
git commit -m "docs(phase2): add AI integration documentation and examples"
```

---

## Execution Summary

After completing all tasks:

1. **Data Pipeline**: Fetch and transform market data
2. **AI Client**: Claude API integration with retry
3. **Prompt Builder**: Structured prompts for consistent AI output
4. **Config Schema**: Pydantic validation of AI outputs
5. **Config Validator**: Risk limit enforcement
6. **Risk Scoring**: Position size calculation
7. **Analyzer**: End-to-end orchestration
8. **CLI**: Command-line interface

**Files Created:** 14 new files
**Files Modified:** 2 files (README.md, .env.example)
**Total Tests:** ~50 new tests

**Next Steps (Phase 3):**
- Live trading integration
- Dashboard UI
- Alert system
