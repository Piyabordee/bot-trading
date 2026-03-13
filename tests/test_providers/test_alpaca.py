"""Tests for Alpaca provider adapter."""

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
