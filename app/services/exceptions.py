class SmartAlphaError(Exception):
    """Base exception for SmartAlpha AI."""


class EmptyInputError(SmartAlphaError):
    """Raised when user input is empty."""


class InvalidTickerError(SmartAlphaError):
    """Raised when a ticker symbol cannot be resolved or is invalid."""


class DataUnavailableError(SmartAlphaError):
    """Raised when market data is unavailable (e.g., delisted stock)."""


class APIError(SmartAlphaError):
    """Raised when an external API returns an error."""


class NetworkError(SmartAlphaError):
    """Raised when a network request fails."""
