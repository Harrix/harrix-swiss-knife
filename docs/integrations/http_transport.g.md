---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `http_transport.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_https_opener`](#-function-build_https_opener)
- [🔧 Function `format_urlerror_message`](#-function-format_urlerror_message)
- [🔧 Function `https_ssl_context`](#-function-https_ssl_context)
- [🔧 Function `resolve_proxy_url`](#-function-resolve_proxy_url)
- [🔧 Function `_proxy_diagnostic`](#-function-_proxy_diagnostic)

</details>

## 🔧 Function `build_https_opener`

```python
def build_https_opener(proxy_url: str | None = None) -> OpenerDirector
```

Return urllib opener with certifi SSL and optional HTTP(S) proxy.

<details>
<summary>Code:</summary>

```python
def build_https_opener(proxy_url: str | None = None) -> OpenerDirector:
    ctx = https_ssl_context()
    handlers: list[BaseHandler] = [HTTPSHandler(context=ctx)]
    if proxy_url:
        proxy_map = {"http": proxy_url, "https": proxy_url}
        handlers.insert(0, ProxyHandler(proxy_map))
    return build_opener(*handlers)
```

</details>

## 🔧 Function `format_urlerror_message`

```python
def format_urlerror_message(exc: URLError) -> str
```

Format URLError with optional hints for common school/corporate network issues.

<details>
<summary>Code:</summary>

```python
def format_urlerror_message(exc: URLError, *, proxy_url: str | None = None) -> str:
    reason_str = str(exc.reason)
    message = f"Network error: {reason_str}"
    upper = reason_str.upper()
    if "WRONG_VERSION_NUMBER" in upper or "wrong version number" in reason_str.lower():
        message += _WRONG_VERSION_HINT
        message += _proxy_diagnostic(proxy_url)
    elif "CERTIFICATE_VERIFY_FAILED" in upper:
        message += _CERT_VERIFY_HINT
    return message
```

</details>

## 🔧 Function `https_ssl_context`

```python
def https_ssl_context() -> ssl.SSLContext
```

Build SSL context with certifi CA bundle and optional SSL_CERT_FILE.

<details>
<summary>Code:</summary>

```python
def https_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context(cafile=certifi.where())
    ssl_cert_file = os.environ.get("SSL_CERT_FILE")
    if ssl_cert_file and Path(ssl_cert_file).is_file():
        ctx.load_verify_locations(cafile=ssl_cert_file)
    return ctx
```

</details>

## 🔧 Function `resolve_proxy_url`

```python
def resolve_proxy_url() -> str | None
```

Resolve proxy URL: config, Qt system proxy, env, then urllib getproxies.

<details>
<summary>Code:</summary>

```python
def resolve_proxy_url(
    *,
    config_proxy: str | None = None,
    qt_proxy_url: str | None = None,
) -> str | None:
    if config_proxy and config_proxy.strip():
        return config_proxy.strip()
    if qt_proxy_url and qt_proxy_url.strip():
        return qt_proxy_url.strip()
    for key in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    proxies = getproxies()
    return proxies.get("https") or proxies.get("http")
```

</details>

## 🔧 Function `_proxy_diagnostic`

```python
def _proxy_diagnostic(proxy_url: str | None) -> str
```

Return a short proxy diagnostic without exposing credentials.

<details>
<summary>Code:</summary>

```python
def _proxy_diagnostic(proxy_url: str | None) -> str:
    if not proxy_url:
        return "\n\nProxy diagnostic: no proxy was detected for this request."

    parts = urlsplit(proxy_url)
    host = parts.hostname or ""
    port = f":{parts.port}" if parts.port else ""
    netloc = f"{host}{port}" if host else parts.netloc
    masked = urlunsplit((parts.scheme, netloc, "", "", ""))
    return f"\n\nProxy diagnostic: using proxy {masked}."
```

</details>
