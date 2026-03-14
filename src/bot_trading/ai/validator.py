"""Validate AI-generated configs.

Ensures AI outputs conform to schema and risk limits.
Provides clear error messages for debugging.
"""

import json
import re

from bot_trading.ai.schema import AIAnalysisResult


class ValidationError(Exception):
    """Config validation error with details."""

    def __init__(self, message: str, path: str = "", original_error: Exception | None = None):
        self.message = message
        self.path = path
        self.original_exception = original_error

        full_message = message
        if path:
            full_message = f"{path}: {message}"
        super().__init__(full_message)


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
        self.max_position_risk_pct = max_position_risk_pct
        self.max_portfolio_exposure = max_portfolio_exposure

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
        if config.portfolio_risk.recommended_max_exposure > self.max_portfolio_exposure:
            raise ValidationError(
                f"Recommended exposure {config.portfolio_risk.recommended_max_exposure:.1%} "
                f"exceeds maximum {self.max_portfolio_exposure:.1%}",
                path="portfolio_risk.recommended_max_exposure",
            )

        # Check individual symbol risks
        for symbol, rec in config.symbols.items():
            if rec.position_size_pct > self.max_position_risk_pct:
                raise ValidationError(
                    f"Position size {rec.position_size_pct:.1%} for {symbol} "
                    f"exceeds maximum {self.max_position_risk_pct:.1%}",
                    path=f"symbols.{symbol}.position_size_pct",
                )

    def validate_and_get_warnings(self, json_str: str) -> tuple[AIAnalysisResult | None, list[str]]:
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
