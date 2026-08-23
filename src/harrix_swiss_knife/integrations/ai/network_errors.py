"""User-facing AI network error messages."""

from __future__ import annotations

from urllib.parse import urlsplit

BOTHUB_UNREACHABLE_MSG = (
    "Cannot connect to BotHub. This is usually caused by a VPN "
    "or an unstable internet connection. Please disable the VPN and try again."
)

_CONNECT_TIMEOUT_ERRNOS = frozenset(
    {
        60,  # ETIMEDOUT on macOS
        110,  # ETIMEDOUT on Linux
        10060,  # WSAETIMEDOUT on Windows
    }
)
_CONNECT_TIMEOUT_MARKERS = (
    "10060",
    "did not properly respond after a period of time",
    "connected host has failed to respond",
    "timed out",
    "timeout",
    "etimedout",
)


def exception_is_connect_timeout(exc: BaseException) -> bool:
    """Return whether `exc` is a connection timeout or stalled handshake."""
    if isinstance(exc, TimeoutError):
        return True
    errno = getattr(exc, "winerror", None)
    if errno is None:
        errno = getattr(exc, "errno", None)
    if errno in _CONNECT_TIMEOUT_ERRNOS:
        return True
    reason = getattr(exc, "reason", None)
    if isinstance(reason, BaseException) and reason is not exc:
        return exception_is_connect_timeout(reason)
    return is_connect_timeout_message(str(exc))


def is_bothub_host(url_or_host: str) -> bool:
    """Return whether `url_or_host` points at bothub.chat or bothub.ru."""
    raw = url_or_host.strip()
    if not raw:
        return False
    host = urlsplit(raw).hostname if "://" in raw else raw
    host = (host or raw).lower().rstrip(".")
    return host in {"bothub.chat", "bothub.ru"} or host.endswith((".bothub.chat", ".bothub.ru"))


def is_connect_timeout_message(text: str) -> bool:
    """Return whether an error string is a connect/read timeout."""
    lower = text.lower()
    return any(marker in lower for marker in _CONNECT_TIMEOUT_MARKERS)


def remap_bothub_network_error(
    message: str,
    *,
    url: str | None = None,
    provider: str | None = None,
    exc: BaseException | None = None,
) -> str:
    """Replace a BotHub connect-timeout with a VPN/internet hint.

    Args:

    - `message` (`str`): Existing error text.
    - `url` (`str | None`): Request URL, when known.
    - `provider` (`str | None`): Active router ID (`bothub` or `bothub.ru`).
    - `exc` (`BaseException | None`): Original exception, when available.

    Returns:

    - `str`: Friendly BotHub message, or the original `message`.

    """
    if not _is_bothub_context(url=url, provider=provider):
        return message
    if exc is not None and exception_is_connect_timeout(exc):
        return BOTHUB_UNREACHABLE_MSG
    if is_connect_timeout_message(message):
        return BOTHUB_UNREACHABLE_MSG
    return message


def _is_bothub_context(*, url: str | None, provider: str | None) -> bool:
    if url and is_bothub_host(url):
        return True
    return provider in {"bothub", "bothub.ru"}
