"""Custom exceptions for the Trading Analysis Tool."""


class TradingAnalysisError(Exception):
    """Base exception for trading analysis tool."""

    pass


class APIError(TradingAnalysisError):
    """Raised when API call fails."""

    pass


class InsufficientDataError(TradingAnalysisError):
    """Raised when not enough data for analysis."""

    pass


class StrategyNotFoundError(TradingAnalysisError):
    """Raised when requested strategy is not found."""

    pass


class RiskLimitExceededError(TradingAnalysisError):
    """Raised when position exceeds risk limits."""

    pass


class InvalidConfigError(TradingAnalysisError):
    """Raised when strategy configuration is invalid."""

    pass
