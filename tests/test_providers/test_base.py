"""Tests for base provider interface."""
import pytest
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
