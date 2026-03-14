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

        # Create client (will raise ImportError if anthropic not available)
        if anthropic is None:
            raise ImportError("anthropic package is required. Install with: pip install anthropic")

        self._client = anthropic.Anthropic(api_key=api_key)

    @classmethod
    def for_testing(cls, client) -> "AIClient":
        """Create an AIClient with a mocked client for testing.

        Args:
            client: A mock anthropic client

        Returns:
            AIClient instance with the mocked client
        """
        instance = cls.__new__(cls)
        instance.api_key = "test-key"
        instance.model = cls.DEFAULT_MODEL
        instance.max_retries = 3
        instance.retry_delay = 1.0
        instance._client = client
        return instance

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
