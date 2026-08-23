---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `network_errors.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `exception_is_connect_timeout`](#-function-exception_is_connect_timeout)
- [🔧 Function `is_bothub_host`](#-function-is_bothub_host)
- [🔧 Function `is_connect_timeout_message`](#-function-is_connect_timeout_message)
- [🔧 Function `remap_bothub_network_error`](#-function-remap_bothub_network_error)

</details>

## 🔧 Function `exception_is_connect_timeout`

```python
def exception_is_connect_timeout(exc: BaseException) -> bool
```

Return whether `exc` is a connection timeout or stalled handshake.

<details>
<summary>Code:</summary>

```python
def exception_is_connect_timeout(exc: BaseException) -> bool:
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
```

</details>

## 🔧 Function `is_bothub_host`

```python
def is_bothub_host(url_or_host: str) -> bool
```

Return whether `url_or_host` points at bothub.chat or bothub.ru.

<details>
<summary>Code:</summary>

```python
def is_bothub_host(url_or_host: str) -> bool:
    raw = url_or_host.strip()
    if not raw:
        return False
    host = urlsplit(raw).hostname if "://" in raw else raw
    host = (host or raw).lower().rstrip(".")
    return host in {"bothub.chat", "bothub.ru"} or host.endswith((".bothub.chat", ".bothub.ru"))
```

</details>

## 🔧 Function `is_connect_timeout_message`

```python
def is_connect_timeout_message(text: str) -> bool
```

Return whether an error string is a connect/read timeout.

<details>
<summary>Code:</summary>

```python
def is_connect_timeout_message(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in _CONNECT_TIMEOUT_MARKERS)
```

</details>

## 🔧 Function `remap_bothub_network_error`

```python
def remap_bothub_network_error(message: str, *, url: str | None = None, provider: str | None = None, exc: BaseException | None = None) -> str
```

Replace a BotHub connect-timeout with a VPN/internet hint.

Args:

- `message` (`str`): Existing error text.
- `url` (`str | None`): Request URL, when known.
- `provider` (`str | None`): Active router ID (`bothub` or `bothub.ru`).
- `exc` (`BaseException | None`): Original exception, when available.

Returns:

- `str`: Friendly BotHub message, or the original `message`.

<details>
<summary>Code:</summary>

```python
def remap_bothub_network_error(
    message: str,
    *,
    url: str | None = None,
    provider: str | None = None,
    exc: BaseException | None = None,
) -> str:
    if not _is_bothub_context(url=url, provider=provider):
        return message
    if exc is not None and exception_is_connect_timeout(exc):
        return BOTHUB_UNREACHABLE_MSG
    if is_connect_timeout_message(message):
        return BOTHUB_UNREACHABLE_MSG
    return message
```

</details>
