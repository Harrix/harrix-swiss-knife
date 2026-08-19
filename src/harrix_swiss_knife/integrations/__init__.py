"""External service integrations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from harrix_swiss_knife.integrations.bothub_client import BotHubApiError, chat_completion, strip_markdown_fences

__all__ = ["BotHubApiError", "chat_completion", "strip_markdown_fences"]


def __getattr__(name: str) -> Any:
    """Load BotHub helpers lazily so installer HTTPS helpers stay isolated."""
    if name in {"BotHubApiError", "chat_completion", "strip_markdown_fences"}:
        from harrix_swiss_knife.integrations import bothub_client  # noqa: PLC0415

        return getattr(bothub_client, name)
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
