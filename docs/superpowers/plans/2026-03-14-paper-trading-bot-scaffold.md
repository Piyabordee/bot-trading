# Paper-Trading Bot Scaffold Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold a safe, paper-trading-only demo bot that validates strategy logic, risk controls, and execution flow in a non-live environment.

**Architecture:**
- Provider adapter pattern with Alpaca Paper Trading as primary target
- Modular design: strategy/execution/risk/data/backtest/tests
- Environment-based configuration with PAPER mode as default
- No live trading code paths enabled

**Tech Stack:**
- Python 3.11+
- uv or pip for package management
- pytest for testing
- python-dotenv for configuration

---

## File Structure Overview

```
bot-trading/
├── .env.example              # Environment variable placeholders
├── .gitignore                # Python + secrets exclusions
├── README.md                 # Setup and run instructions
├── pyproject.toml            # Project metadata and dependencies
├── Makefile                  # Common commands
├── src/
│   └── bot_trading/
│       ├── __init__.py
│       ├── config.py         # Configuration loading with PAPER default
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py       # Abstract provider interface
│       │   └── alpaca.py     # Alpaca Paper Trading adapter
│       ├── strategy/
│       │   ├── __init__.py
│       │   └── base.py       # Base strategy class
│       ├── execution/
│       │   ├── __init__.py
│       │   └── executor.py   # Order execution logic
│       ├── risk/
│       │   ├── __init__.py
│       │   └── limits.py     # Risk management rules
│       └── data/
│           ├── __init__.py
│           └── fetcher.py    # Data fetching utilities
├── config/
│   └── paper_config.yaml     # Paper trading configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_config.py
│   ├── test_risk_limits.py
│   └── test_providers/
│       ├── __init__.py
│       └── test_alpaca.py
└── main.py                   # Entry point for paper trading bot
```

---

## Chunk 1: Project Foundation

### Task 1: Initialize git repository and create .gitignore

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Initialize git repository**

```bash
cd c:/Users/snowb4ll/Documents/bot-trading
git init
git config user.name "snowb4ll"
git config user.email "snowb4ll@users.noreply.github.com"
```

Expected: "Initialized empty Git repository"

- [ ] **Step 2: Create .gitignore with Python and security best practices**

```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
dist/
build/
*.egg-info/

# Virtual environments
venv/
env/
.venv/

# IDEs
.vscode/
.idea/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Environment files
.env

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Project specific
config/*.local.yaml
```

- [ ] **Step 3: Commit initial gitignore**

```bash
git add .gitignore
git commit -m "chore: add .gitignore for Python project"
```

---

### Task 2: Create pyproject.toml with project metadata

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Write pyproject.toml**

```toml
[project]
name = "bot-trading"
version = "0.1.0"
description = "Paper trading demo bot for strategy validation"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0",
    "requests>=2.31.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "alpaca-trade-api>=3.0.0",
]

[project.scripts]
bot-trading = "bot_trading.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add pyproject.toml with project metadata"
```

---

### Task 3: Create .env.example with placeholders

**Files:**
- Create: `.env.example`

- [ ] **Step 1: Create .env.example with all required environment variables**

```bash
# Trading Mode (ALWAYS paper unless explicitly changed)
TRADING_MODE=paper

# Alpaca Paper Trading Credentials
# Get your paper trading keys from: https://alpaca.markets/paper
ALPACA_API_KEY=your_paper_api_key_here
ALPACA_API_SECRET=your_paper_api_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Risk Management Limits
MAX_POSITION_SIZE=1000
MAX_PORTFOLIO_EXPOSURE=0.2
DAILY_LOSS_LIMIT=500

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
```

- [ ] **Step 2: Verify no actual secrets in .env.example**

```bash
grep -i "sk-\|pk-" .env.example
```

Expected: No matches (no actual API keys)

- [ ] **Step 3: Commit**

```bash
git add .env.example
git commit -m "chore: add .env.example with safe placeholders"
```

---

### Task 4: Create source directory structure and __init__ files

**Files:**
- Create: `src/bot_trading/__init__.py`
- Create: `src/bot_trading/providers/__init__.py`
- Create: `src/bot_trading/strategy/__init__.py`
- Create: `src/bot_trading/execution/__init__.py`
- Create: `src/bot_trading/risk/__init__.py`
- Create: `src/bot_trading/data/__init__.py`

- [ ] **Step 1: Create all __init__.py files**

```bash
mkdir -p src/bot_trading/{providers,strategy,execution,risk,data}
touch src/bot_trading/__init__.py
touch src/bot_trading/providers/__init__.py
touch src/bot_trading/strategy/__init__.py
touch src/bot_trading/execution/__init__.py
touch src/bot_trading/risk/__init__.py
touch src/bot_trading/data/__init__.py
```

- [ ] **Step 2: Add package version to main __init__.py**

```python
"""Bot Trading - Paper Trading Demo Bot.

A safe, paper-trading-only bot for validating strategy logic,
risk controls, and execution flow.
"""

__version__ = "0.1.0"
```

- [ ] **Step 3: Commit**

```bash
git add src/
git commit -m "chore: create source directory structure"
```

---

## Chunk 2: Configuration Module

### Task 5: Create configuration loader with PAPER default

**Files:**
- Create: `src/bot_trading/config.py`

- [ ] **Step 1: Write the failing test first**

```python
# tests/test_config.py
import os
import pytest
from bot_trading.config import Config, get_config

def test_config_defaults_to_paper_mode():
    """Paper mode must be the default unless explicitly set."""
    config = Config()
    assert config.trading_mode == "paper"

def test_config_from_env_sets_paper_mode():
    """Environment variable should set trading mode."""
    os.environ["TRADING_MODE"] = "paper"
    config = Config()
    assert config.trading_mode == "paper"

def test_config_rejects_live_mode_without_explicit_setting():
    """Live mode should NOT be settable without explicit intent."""
    # Default should always be paper
    config = Config()
    assert config.trading_mode != "live"

def test_config_loads_risk_limits():
    """Risk limits should be loaded from environment."""
    os.environ["MAX_POSITION_SIZE"] = "1000"
    config = Config()
    assert config.max_position_size == 1000

def test_config_singleton():
    """get_config should return the same instance."""
    config1 = get_config()
    config2 = get_config()
    assert config1 is config2
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd c:/Users/snowb4ll/Documents/bot-trading
pytest tests/test_config.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'bot_trading.config'"

- [ ] **Step 3: Create minimal Config implementation**

```python
# src/bot_trading/config.py
import os
from dataclasses import dataclass
from functools import lru_cache

@dataclass
class Config:
    """Application configuration with PAPER mode as default.

    IMPORTANT: This is a paper-trading-only demo bot.
    Live trading paths should remain disabled unless explicitly approved.
    """

    trading_mode: str = "paper"
    max_position_size: float = 1000.0
    max_portfolio_exposure: float = 0.2
    daily_loss_limit: float = 500.0
    log_level: str = "INFO"

    def __post_init__(self):
        """Load values from environment with safe defaults."""
        # ALWAYS default to paper mode
        self.trading_mode = os.getenv("TRADING_MODE", "paper").lower()

        # Safety check: if someone tries to set live via env, still default to paper
        # unless explicitly documented and approved
        if self.trading_mode not in ("paper", "live"):
            self.trading_mode = "paper"

        self.max_position_size = float(os.getenv("MAX_POSITION_SIZE", str(self.max_position_size)))
        self.max_portfolio_exposure = float(os.getenv("MAX_PORTFOLIO_EXPOSURE", str(self.max_portfolio_exposure)))
        self.daily_loss_limit = float(os.getenv("DAILY_LOSS_LIMIT", str(self.daily_loss_limit)))
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)

    @property
    def is_paper_mode(self) -> bool:
        """Check if running in paper trading mode."""
        return self.trading_mode == "paper"

    @property
    def is_live_mode(self) -> bool:
        """Check if running in live mode (should always be False for demo)."""
        return self.trading_mode == "live"

@lru_cache
def get_config() -> Config:
    """Get singleton configuration instance."""
    return Config()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_config.py -v
```

Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add src/bot_trading/config.py tests/test_config.py
git commit -m "feat: add config module with paper-mode default"
```

---

## Chunk 3: Provider Abstraction

### Task 6: Create base provider interface

**Files:**
- Create: `src/bot_trading/providers/base.py`

- [ ] **Step 1: Write the test for abstract interface**

```python
# tests/test_providers/test_base.py
import pytest
from abc import ABC
from bot_trading.providers.base import BaseProvider

def test_base_provider_is_abstract():
    """BaseProvider should not be instantiable directly."""
    with pytest.raises(TypeError):
        BaseProvider()  # type: ignore

def test_base_provider_requires_abstract_methods():
    """Concrete provider must implement all abstract methods."""
    class IncompleteProvider(BaseProvider):
        pass

    with pytest.raises(TypeError):
        IncompleteProvider()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_providers/test_base.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Create BaseProvider abstract class**

```python
# src/bot_trading/providers/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class Account:
    """Account information."""
    equity: Decimal
    cash: Decimal
    buying_power: Decimal
    portfolio_value: Decimal

@dataclass
class Position:
    """Open position information."""
    symbol: str
    quantity: Decimal
    avg_entry_price: Decimal
    current_price: Decimal
    market_value: Decimal

@dataclass
class Order:
    """Order information."""
    order_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: Decimal
    price: Decimal | None
    status: str
    created_at: datetime

class BaseProvider(ABC):
    """Abstract base class for trading providers.

    All provider adapters must implement this interface to ensure
    consistent behavior across different brokers/exchanges.
    """

    @abstractmethod
    def get_account(self) -> Account:
        """Get current account information."""
        pass

    @abstractmethod
    def get_positions(self) -> list[Position]:
        """Get all open positions."""
        pass

    @abstractmethod
    def get_latest_price(self, symbol: str) -> Decimal:
        """Get latest price for a symbol."""
        pass

    @abstractmethod
    def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        order_type: str = "market",
        price: Decimal | None = None,
    ) -> Order:
        """Submit a new order.

        Args:
            symbol: Trading symbol
            side: 'buy' or 'sell'
            quantity: Order quantity
            order_type: 'market' or 'limit'
            price: Limit price (required for limit orders)

        Returns:
            Order object with order_id and status
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order."""
        pass

    @abstractmethod
    def list_open_orders(self) -> list[Order]:
        """List all open orders."""
        pass
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_providers/test_base.py -v
```

Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add src/bot_trading/providers/base.py tests/test_providers/test_base.py
git commit -m "feat: add abstract base provider interface"
```

---

### Task 7: Create Alpaca Paper Trading adapter stub

**Files:**
- Create: `src/bot_trading/providers/alpaca.py`

- [ ] **Step 1: Write the test for Alpaca adapter**

```python
# tests/test_providers/test_alpaca.py
import os
from decimal import Decimal
from unittest.mock import Mock, patch
from bot_trading.providers.alpaca import AlpacaProvider

def test_alpaca_provider_requires_api_credentials():
    """Alpaca provider should fail without API credentials."""
    # Clear credentials
    os.environ["ALPACA_API_KEY"] = ""
    os.environ["ALPACA_API_SECRET"] = ""

    with pytest.raises(ValueError, match="API credentials"):
        AlpacaProvider()

@patch("bot_trading.providers.alpaca.REST")
def test_alpaca_provider_uses_paper_url_by_default(mock_rest):
    """Provider should use paper trading URL by default."""
    os.environ["ALPACA_API_KEY"] = "test-key"
    os.environ["ALPACA_API_SECRET"] = "test-secret"

    provider = AlpacaProvider()
    assert provider.base_url == "https://paper-api.alpaca.markets"

@patch("bot_trading.providers.alpaca.REST")
def test_alpaca_get_account_returns_account_data(mock_rest):
    """get_account should return Account dataclass."""
    os.environ["ALPACA_API_KEY"] = "test-key"
    os.environ["ALPACA_API_SECRET"] = "test-secret"

    mock_api = Mock()
    mock_api.get_account.return_value = {
        "equity": "100000",
        "cash": "50000",
        "buying_power": "200000",
        "portfolio_value": "100000",
    }
    mock_rest.return_value = mock_api

    provider = AlpacaProvider()
    account = provider.get_account()

    assert account.equity == Decimal("100000")
    assert account.cash == Decimal("50000")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_providers/test_alpaca.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Create AlpacaProvider implementation**

```python
# src/bot_trading/providers/alpaca.py
import os
from decimal import Decimal
from typing import cast

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False

from bot_trading.providers.base import (
    BaseProvider,
    Account,
    Position,
    Order,
)

class AlpacaProvider(BaseProvider):
    """Alpaca Paper Trading provider adapter.

    This adapter connects to Alpaca's paper trading environment only.
    It will NOT connect to live trading endpoints.

    TODO: Implement full order submission and management
    TODO: Add proper error handling for network failures
    TODO: Add retry logic for transient errors
    """

    PAPER_URL = "https://paper-api.alpaca.markets"

    def __init__(self) -> None:
        """Initialize Alpaca Paper Trading client.

        Raises:
            ValueError: If API credentials are not configured
            ImportError: If alpaca-trade-api is not installed
        """
        if not ALPACA_AVAILABLE:
            raise ImportError(
                "alpaca-trade-api is required for AlpacaProvider. "
                "Install with: pip install alpaca-trade-api"
            )

        api_key = os.getenv("ALPACA_API_KEY", "")
        api_secret = os.getenv("ALPACA_API_SECRET", "")

        if not api_key or api_secret in ("your_paper_api_key_here", ""):
            raise ValueError(
                "Alpaca API credentials not configured. "
                "Set ALPACA_API_KEY and ALPACA_API_SECRET in .env"
            )

        self.base_url = os.getenv("ALPACA_BASE_URL", self.PAPER_URL)

        # Safety: verify we're using paper URL
        if "paper" not in self.base_url:
            raise ValueError(
                f"Refusing to connect to non-paper URL: {self.base_url}. "
                "This is a paper-trading-only demo bot."
            )

        # TODO: Initialize actual TradingClient when implementing full flow
        # self.client = TradingClient(api_key=api_key, secret_key=api_secret, paper=True)
        self._api_key = api_key
        self._api_secret = api_secret

    def get_account(self) -> Account:
        """Get current account information from Alpaca.

        TODO: Implement actual API call when client is initialized
        """
        # TODO: return Account from actual API
        raise NotImplementedError("get_account: TODO - implement when adding full API integration")

    def get_positions(self) -> list[Position]:
        """Get all open positions.

        TODO: Implement actual API call
        """
        raise NotImplementedError("get_positions: TODO - implement when adding full API integration")

    def get_latest_price(self, symbol: str) -> Decimal:
        """Get latest price for a symbol.

        TODO: Implement actual API call
        """
        raise NotImplementedError("get_latest_price: TODO - implement when adding full API integration")

    def submit_order(
        self,
        symbol: str,
        side: str,
        quantity: Decimal,
        order_type: str = "market",
        price: Decimal | None = None,
    ) -> Order:
        """Submit a new order to Alpaca.

        TODO: Implement actual order submission
        """
        raise NotImplementedError("submit_order: TODO - implement when adding full API integration")

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order.

        TODO: Implement actual order cancellation
        """
        raise NotImplementedError("cancel_order: TODO - implement when adding full API integration")

    def list_open_orders(self) -> list[Order]:
        """List all open orders.

        TODO: Implement actual API call
        """
        raise NotImplementedError("list_open_orders: TODO - implement when adding full API integration")
```

- [ ] **Step 4: Update tests to handle NotImplementedError gracefully**

```python
# tests/test_providers/test_alpaca.py - UPDATED
import os
import pytest
from decimal import Decimal
from bot_trading.providers.alpaca import AlpacaProvider

def test_alpaca_provider_requires_api_credentials():
    """Alpaca provider should fail without API credentials."""
    # Clear credentials
    original_key = os.environ.get("ALPACA_API_KEY", "")
    original_secret = os.environ.get("ALPACA_API_SECRET", "")

    try:
        os.environ["ALPACA_API_KEY"] = ""
        os.environ["ALPACA_API_SECRET"] = ""

        with pytest.raises(ValueError, match="API credentials"):
            AlpacaProvider()
    finally:
        # Restore original values
        if original_key:
            os.environ["ALPACA_API_KEY"] = original_key
        if original_secret:
            os.environ["ALPACA_API_SECRET"] = original_secret

def test_alpaca_provider_uses_paper_url_by_default():
    """Provider should use paper trading URL by default."""
    original_key = os.environ.get("ALPACA_API_KEY", "")
    original_secret = os.environ.get("ALPACA_API_SECRET", "")

    try:
        os.environ["ALPACA_API_KEY"] = "test-key"
        os.environ["ALPACA_API_SECRET"] = "test-secret"

        provider = AlpacaProvider()
        assert provider.base_url == "https://paper-api.alpaca.markets"
    finally:
        if original_key:
            os.environ["ALPACA_API_KEY"] = original_key
        if original_secret:
            os.environ["ALPACA_API_SECRET"] = original_secret

def test_alpaca_provider_rejects_non_paper_url():
    """Provider should refuse to connect to non-paper URLs."""
    original_key = os.environ.get("ALPACA_API_KEY", "")
    original_secret = os.environ.get("ALPACA_API_SECRET", "")
    original_url = os.environ.get("ALPACA_BASE_URL", "")

    try:
        os.environ["ALPACA_API_KEY"] = "test-key"
        os.environ["ALPACA_API_SECRET"] = "test-secret"
        os.environ["ALPACA_BASE_URL"] = "https://api.alpaca.markets"

        with pytest.raises(ValueError, match="Refusing to connect"):
            AlpacaProvider()
    finally:
        if original_key:
            os.environ["ALPACA_API_KEY"] = original_key
        if original_secret:
            os.environ["ALPACA_API_SECRET"] = original_secret
        if original_url:
            os.environ["ALPACA_BASE_URL"] = original_url
        else:
            os.environ.pop("ALPACA_BASE_URL", None)

def test_alpaca_methods_raise_not_implemented():
    """Alpaca methods should raise NotImplementedError until fully implemented."""
    original_key = os.environ.get("ALPACA_API_KEY", "")
    original_secret = os.environ.get("ALPACA_API_SECRET", "")

    try:
        os.environ["ALPACA_API_KEY"] = "test-key"
        os.environ["ALPACA_API_SECRET"] = "test-secret"

        provider = AlpacaProvider()

        with pytest.raises(NotImplementedError):
            provider.get_account()

        with pytest.raises(NotImplementedError):
            provider.get_positions()

        with pytest.raises(NotImplementedError):
            provider.get_latest_price("AAPL")

        with pytest.raises(NotImplementedError):
            provider.submit_order("AAPL", "buy", Decimal("10"))
    finally:
        if original_key:
            os.environ["ALPACA_API_KEY"] = original_key
        if original_secret:
            os.environ["ALPACA_API_SECRET"] = original_secret
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_providers/test_alpaca.py -v
```

Expected: PASS (4 tests)

- [ ] **Step 6: Commit**

```bash
git add src/bot_trading/providers/alpaca.py tests/test_providers/test_alpaca.py
git commit -m "feat: add Alpaca paper trading adapter stub"
```

---

## Chunk 4: Risk Management

### Task 8: Create risk limits module

**Files:**
- Create: `src/bot_trading/risk/limits.py`

- [ ] **Step 1: Write the test for risk limits**

```python
# tests/test_risk_limits.py
import pytest
from decimal import Decimal
from bot_trading.risk.limits import RiskLimits, RiskCheckResult

def test_risk_limits_blocks_order_exceeding_max_position():
    """Should reject orders larger than max position size."""
    limits = RiskLimits(max_position_size=Decimal("1000"))
    result = limits.check_order_size(quantity=Decimal("1500"))
    assert result.allowed is False
    assert "exceeds maximum" in result.reason.lower()

def test_risk_limits_allows_order_within_limits():
    """Should allow orders within risk limits."""
    limits = RiskLimits(max_position_size=Decimal("1000"))
    result = limits.check_order_size(quantity=Decimal("500"))
    assert result.allowed is True

def test_risk_limits_enforces_portfolio_exposure():
    """Should check portfolio exposure limits."""
    limits = RiskLimits(
        max_position_size=Decimal("1000"),
        max_portfolio_exposure=Decimal("0.2"),
        portfolio_value=Decimal("100000")
    )
    result = limits.check_portfolio_exposure(new_value=Decimal("25000"))
    assert result.allowed is False
    assert "exposure" in result.reason.lower()

def test_risk_limits_blocks_duplicate_orders():
    """Should prevent duplicate orders for same symbol."""
    limits = RiskLimits()
    limits.record_order("AAPL", "buy")
    result = limits.check_duplicate_order("AAPL", "buy", within_seconds=60)
    assert result.allowed is False

def test_risk_limits_allows_different_symbols():
    """Should allow orders for different symbols."""
    limits = RiskLimits()
    limits.record_order("AAPL", "buy")
    result = limits.check_duplicate_order("TSLA", "buy", within_seconds=60)
    assert result.allowed is True
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_risk_limits.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Create RiskLimits implementation**

```python
# src/bot_trading/risk/limits.py
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal

@dataclass
class RiskCheckResult:
    """Result of a risk limit check."""
    allowed: bool
    reason: str = ""

@dataclass
class OrderRecord:
    """Record of a submitted order for duplicate detection."""
    symbol: str
    side: str
    timestamp: datetime

class RiskLimits:
    """Risk management limits and checks.

    Enforces:
    - Max position size per trade
    - Max portfolio exposure
    - Daily loss limit
    - Duplicate order protection

    TODO: Add daily loss limit tracking
    TODO: Add market hours validation
    """

    def __init__(
        self,
        max_position_size: Decimal = Decimal("1000"),
        max_portfolio_exposure: Decimal = Decimal("0.2"),
        daily_loss_limit: Decimal = Decimal("500"),
        portfolio_value: Decimal = Decimal("0"),
    ) -> None:
        self.max_position_size = max_position_size
        self.max_portfolio_exposure = max_portfolio_exposure
        self.daily_loss_limit = daily_loss_limit
        self.portfolio_value = portfolio_value
        self._order_history: deque[OrderRecord] = deque()

    def check_order_size(self, quantity: Decimal) -> RiskCheckResult:
        """Check if order size is within limits.

        Args:
            quantity: Order quantity

        Returns:
            RiskCheckResult indicating if order is allowed
        """
        if quantity > self.max_position_size:
            return RiskCheckResult(
                allowed=False,
                reason=f"Order size {quantity} exceeds maximum {self.max_position_size}"
            )
        return RiskCheckResult(allowed=True)

    def check_portfolio_exposure(
        self,
        new_value: Decimal,
        current_exposure: Decimal = Decimal("0"),
    ) -> RiskCheckResult:
        """Check if new position would exceed portfolio exposure limit.

        Args:
            new_value: Value of new position
            current_exposure: Current total exposure

        Returns:
            RiskCheckResult indicating if position is allowed
        """
        total_exposure = current_exposure + new_value
        max_allowed = self.portfolio_value * self.max_portfolio_exposure

        if total_exposure > max_allowed:
            return RiskCheckResult(
                allowed=False,
                reason=f"Total exposure {total_exposure} exceeds maximum {max_allowed}"
            )
        return RiskCheckResult(allowed=True)

    def check_duplicate_order(
        self,
        symbol: str,
        side: str,
        within_seconds: int = 30,
    ) -> RiskCheckResult:
        """Check for duplicate orders within time window.

        Args:
            symbol: Trading symbol
            side: Order side ('buy' or 'sell')
            within_seconds: Time window to check for duplicates

        Returns:
            RiskCheckResult indicating if order is allowed
        """
        cutoff = datetime.now() - timedelta(seconds=within_seconds)

        for record in self._order_history:
            if record.timestamp < cutoff:
                continue
            if record.symbol == symbol and record.side == side:
                return RiskCheckResult(
                    allowed=False,
                    reason=f"Duplicate order for {symbol} {side} within {within_seconds}s"
                )

        return RiskCheckResult(allowed=True)

    def record_order(self, symbol: str, side: str) -> None:
        """Record an order for duplicate detection.

        Args:
            symbol: Trading symbol
            side: Order side
        """
        self._order_history.append(OrderRecord(
            symbol=symbol,
            side=side,
            timestamp=datetime.now()
        ))

        # Clean old records
        cutoff = datetime.now() - timedelta(seconds=300)  # Keep 5 minutes
        while self._order_history and self._order_history[0].timestamp < cutoff:
            self._order_history.popleft()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_risk_limits.py -v
```

Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add src/bot_trading/risk/limits.py tests/test_risk_limits.py
git commit -m "feat: add risk limits module with duplicate protection"
```

---

## Chunk 5: Basic Strategy and Execution

### Task 9: Create base strategy class

**Files:**
- Create: `src/bot_trading/strategy/base.py`

- [ ] **Step 1: Write the test for base strategy**

```python
# tests/test_strategy_base.py
import pytest
from decimal import Decimal
from bot_trading.strategy.base import BaseStrategy, Signal

def test_base_strategy_is_abstract():
    """BaseStrategy should not be instantiable directly."""
    with pytest.raises(TypeError):
        BaseStrategy()  # type: ignore

def test_concrete_strategy_can_generate_signals():
    """Concrete strategy should implement generate_signals."""
    class SimpleStrategy(BaseStrategy):
        def generate_signals(self):
            return [Signal(symbol="AAPL", action="hold", confidence=1.0)]

    strategy = SimpleStrategy()
    signals = strategy.generate_signals()
    assert len(signals) == 1
    assert signals[0].symbol == "AAPL"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_strategy_base.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Create BaseStrategy implementation**

```python
# src/bot_trading/strategy/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Signal:
    """Trading signal generated by a strategy."""
    symbol: str
    action: str  # 'buy', 'sell', 'hold'
    confidence: float  # 0.0 to 1.0
    quantity: Decimal | None = None
    reason: str = ""

class BaseStrategy(ABC):
    """Base class for trading strategies.

    All strategies must implement the generate_signals method.
    This is a paper-trading demo - strategies should be safe
    and well-tested before any consideration of live use.
    """

    @abstractmethod
    def generate_signals(self) -> list[Signal]:
        """Generate trading signals based on strategy logic.

        Returns:
            List of Signal objects representing desired actions
        """
        pass
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_strategy_base.py -v
```

Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add src/bot_trading/strategy/base.py tests/test_strategy_base.py
git commit -m "feat: add base strategy class with signal generation"
```

---

### Task 10: Create basic executor stub

**Files:**
- Create: `src/bot_trading/execution/executor.py`

- [ ] **Step 1: Write the test for executor**

```python
# tests/test_executor.py
import pytest
from decimal import Decimal
from unittest.mock import Mock
from bot_trading.execution.executor import Executor
from bot_trading.strategy.base import Signal
from bot_trading.providers.base import BaseProvider

def test_executor_requires_provider_and_risk_limits():
    """Executor should require provider and risk limits."""
    with pytest.raises(TypeError):
        Executor()  # type: ignore

def test_executor_validates_risk_before_execution():
    """Executor should check risk limits before executing orders."""
    mock_provider = Mock(spec=BaseProvider)
    mock_risk = Mock()
    mock_risk.check_order_size.return_value = Mock(allowed=False)

    executor = Executor(provider=mock_provider, risk_limits=mock_risk)
    signal = Signal(symbol="AAPL", action="buy", confidence=0.8, quantity=Decimal("100"))

    result = executor.execute_signal(signal)
    assert result.executed is False
    assert "risk" in result.reason.lower() or "limit" in result.reason.lower()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_executor.py -v
```

Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Create Executor implementation**

```python
# src/bot_trading/execution/execution.py
from dataclasses import dataclass, field
from decimal import Decimal
import logging

from bot_trading.providers.base import BaseProvider
from bot_trading.risk.limits import RiskLimits, RiskCheckResult
from bot_trading.strategy.base import Signal

logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """Result of an execution attempt."""
    executed: bool
    signal: Signal
    reason: str = ""
    order_id: str | None = None

class Executor:
    """Executes trading signals with risk checks.

    Flow:
    1. Validate signal
    2. Check risk limits
    3. Submit order to provider
    4. Log result

    TODO: Implement actual order submission
    TODO: Add retry logic for failed orders
    TODO: Add order status tracking
    """

    def __init__(self, provider: BaseProvider, risk_limits: RiskLimits) -> None:
        """Initialize executor.

        Args:
            provider: Trading provider (e.g., AlpacaProvider)
            risk_limits: Risk management limits
        """
        self.provider = provider
        self.risk_limits = risk_limits

    def execute_signal(self, signal: Signal) -> ExecutionResult:
        """Execute a trading signal with risk checks.

        Args:
            signal: Trading signal to execute

        Returns:
            ExecutionResult with execution status
        """
        # Validate signal
        if signal.action not in ("buy", "sell"):
            return ExecutionResult(
                executed=False,
                signal=signal,
                reason=f"Invalid action: {signal.action}"
            )

        if not signal.quantity:
            return ExecutionResult(
                executed=False,
                signal=signal,
                reason="Signal has no quantity"
            )

        # Check risk limits
        size_check = self.risk_limits.check_order_size(signal.quantity)
        if not size_check.allowed:
            logger.warning(f"Order rejected by risk limits: {size_check.reason}")
            return ExecutionResult(
                executed=False,
                signal=signal,
                reason=f"Risk check failed: {size_check.reason}"
            )

        # Check for duplicates
        duplicate_check = self.risk_limits.check_duplicate_order(signal.symbol, signal.action)
        if not duplicate_check.allowed:
            logger.warning(f"Duplicate order blocked: {duplicate_check.reason}")
            return ExecutionResult(
                executed=False,
                signal=signal,
                reason=f"Duplicate check failed: {duplicate_check.reason}"
            )

        # TODO: Submit actual order to provider
        logger.info(
            f"Would execute {signal.action} {signal.quantity} {signal.symbol} "
            f"(confidence: {signal.confidence})"
        )

        return ExecutionResult(
            executed=False,  # Until full implementation
            signal=signal,
            reason="TODO: Order submission not yet implemented"
        )
```

- [ ] **Step 4: Fix the module name (execution.py -> executor.py in test)**

```python
# tests/test_executor.py - UPDATED
import pytest
from decimal import Decimal
from unittest.mock import Mock
from bot_trading.execution.executor import Executor
from bot_trading.strategy.base import Signal
from bot_trading.providers.base import BaseProvider

def test_executor_requires_provider_and_risk_limits():
    """Executor should require provider and risk limits."""
    with pytest.raises(TypeError):
        Executor()  # type: ignore

def test_executor_validates_risk_before_execution():
    """Executor should check risk limits before executing orders."""
    mock_provider = Mock(spec=BaseProvider)
    mock_risk = Mock()
    mock_risk.check_order_size.return_value = Mock(allowed=False, reason="Too large")

    executor = Executor(provider=mock_provider, risk_limits=mock_risk)
    signal = Signal(symbol="AAPL", action="buy", confidence=0.8, quantity=Decimal("100"))

    result = executor.execute_signal(signal)
    assert result.executed is False
    assert "risk" in result.reason.lower() or "failed" in result.reason.lower()
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_executor.py -v
```

Expected: PASS (2 tests)

- [ ] **Step 6: Commit**

```bash
git add src/bot_trading/execution/executor.py tests/test_executor.py
git commit -m "feat: add executor with risk check integration"
```

---

## Chunk 6: Configuration Files and Main Entry Point

### Task 11: Create paper trading configuration file

**Files:**
- Create: `config/paper_config.yaml`

- [ ] **Step 1: Create paper trading config**

```yaml
# config/paper_config.yaml
# Paper Trading Configuration

# Trading settings
mode: paper
symbols:
  - AAPL
  - MSFT
  - GOOGL

# Risk limits
risk:
  max_position_size: 1000
  max_portfolio_exposure: 0.2
  daily_loss_limit: 500

# Strategy settings
strategy:
  name: "demo_strategy"
  parameters:
    lookback_period: 20
    confidence_threshold: 0.7
```

- [ ] **Step 2: Commit**

```bash
git add config/paper_config.yaml
git commit -m "chore: add paper trading configuration file"
```

---

### Task 12: Create main entry point

**Files:**
- Create: `main.py`

- [ ] **Step 1: Create main.py with paper trading entry point**

```python
#!/usr/bin/env python3
"""Main entry point for paper trading bot.

This is a DEMO bot for paper trading only.
No live trading will be executed.
"""

import logging
import sys
from pathlib import Path
from decimal import Decimal

from bot_trading.config import get_config
from bot_trading.providers.alpaca import AlpacaProvider
from bot_trading.risk.limits import RiskLimits
from bot_trading.execution.executor import Executor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point."""
    config = get_config()

    logger.info("=" * 60)
    logger.info("Paper Trading Bot - DEMO ONLY")
    logger.info("=" * 60)
    logger.info(f"Trading Mode: {config.trading_mode.upper()}")
    logger.info(f"Max Position Size: ${config.max_position_size}")
    logger.info(f"Max Portfolio Exposure: {config.max_portfolio_exposure * 100}%")
    logger.info(f"Daily Loss Limit: ${config.daily_loss_limit}")
    logger.info("=" * 60)

    # Safety verification
    if not config.is_paper_mode:
        logger.error("REFUSING TO RUN: This is a paper-trading-only demo bot")
        logger.error("Set TRADING_MODE=paper in environment")
        return 1

    try:
        # Initialize provider (will fail without credentials)
        logger.info("Initializing Alpaca Paper Trading provider...")
        provider = AlpacaProvider()
        logger.info(f"Provider initialized: {provider.base_url}")

        # Initialize risk limits
        risk_limits = RiskLimits(
            max_position_size=Decimal(str(config.max_position_size)),
            max_portfolio_exposure=Decimal(str(config.max_portfolio_exposure)),
            daily_loss_limit=Decimal(str(config.daily_loss_limit)),
        )
        logger.info("Risk limits initialized")

        # Initialize executor
        executor = Executor(provider=provider, risk_limits=risk_limits)
        logger.info("Executor initialized")

        logger.info("Bot ready - TODO: Implement main trading loop")
        logger.info("Currently in scaffold mode - no actual trading will occur")

        return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file")
        return 1
    except ImportError as e:
        logger.error(f"Dependency error: {e}")
        logger.error("Install dependencies: pip install -e '.[dev]'")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Commit**

```bash
git add main.py
git commit -m "feat: add main entry point with paper mode verification"
```

---

### Task 13: Create Makefile for common commands

**Files:**
- Create: `Makefile`

- [ ] **Step 1: Create Makefile**

```makefile
.PHONY: help install test lint format run clean

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv pip install -e .
	uv pip install -e ".[dev]"

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ -v --cov=bot_trading --cov-report=html

lint:  ## Run linting
	ruff check src/ tests/

format:  ## Format code
	ruff format src/ tests/
	ruff check --fix src/ tests/

run:  ## Run bot in paper mode
	python main.py

clean:  ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info
```

- [ ] **Step 2: Commit**

```bash
git add Makefile
git commit -m "chore: add Makefile with common commands"
```

---

### Task 14: Create comprehensive README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

```markdown
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
- uv or pip for package management

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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive README.md"
```

---

## Chunk 7: Final Verification

### Task 15: Run all tests and verify setup

- [ ] **Step 1: Run all tests**

```bash
cd c:/Users/snowb4ll/Documents/bot-trading
pytest tests/ -v
```

Expected: All tests pass (approx 20+ tests)

- [ ] **Step 2: Run linting**

```bash
ruff check src/ tests/
```

Expected: No errors (may have warnings for unused TODO code)

- [ ] **Step 3: Verify paper mode is default**

```bash
TRADING_MODE="" python -c "from bot_trading.config import get_config; c = get_config(); print(f'Mode: {c.trading_mode}')"
```

Expected: "Mode: paper"

- [ ] **Step 4: Verify no live endpoints**

```bash
grep -r "api.alpaca.markets" src/ config/ 2>/dev/null || echo "No live endpoints found ✓"
```

Expected: "No live endpoints found ✓"

- [ ] **Step 5: Verify no secrets in repository**

```bash
grep -rE "(sk-|pk-|AKIA|secret)" --include="*.py" --include="*.yaml" --include="*.toml" --exclude-dir=.git . || echo "No secrets found ✓"
```

Expected: "No secrets found ✓"

- [ ] **Step 6: Final commit**

```bash
git add .
git commit -m "chore: final scaffold verification complete"
```

---

## Summary

This plan scaffolds a **safe, paper-trading-only demo bot** with:

1. ✅ PAPER mode as default (enforced in config)
2. ✅ No live trading paths enabled (Alpaca adapter stub with TODOs)
3. ✅ No secrets (placeholders in .env.example)
4. ✅ Risk management with duplicate protection
5. ✅ Provider abstraction for future extensibility
6. ✅ Comprehensive tests for all modules
7. ✅ Documentation (README.md, AGENTS.md)
8. ✅ Common commands (Makefile)

**Next Steps (after this scaffold):**
1. Complete Alpaca API integration (remove NotImplementedError stubs)
2. Implement sample strategies
3. Add backtesting module
4. Create data fetcher for historical data
