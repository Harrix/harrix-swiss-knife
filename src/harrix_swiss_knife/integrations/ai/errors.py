"""AI provider errors."""

from __future__ import annotations


class AiApiError(RuntimeError):
    """Raised when an AI provider returns an error or the response cannot be parsed."""


class RequestCancelledError(AiApiError):
    """Raised when an in-flight AI request is cancelled by the user."""
