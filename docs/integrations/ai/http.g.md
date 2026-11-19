---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `http.py`

## 🔧 Function `post_bytes`

```python
def post_bytes(url: str, body: bytes, headers: dict[str, str], *, timeout_sec: int = DEFAULT_READ_TIMEOUT_SEC, connect_timeout_sec: int = DEFAULT_CONNECT_TIMEOUT_SEC, proxy_url: str | None = None, should_cancel: Callable[[], bool] | None = None, on_connection: Callable[[http.client.HTTPConnection], None] | None = None) -> str
```

POST raw body and return response text; raise AiApiError on failure.

`connect_timeout_sec` limits TCP/TLS setup; `timeout_sec` limits reading the
response body after the connection is open.

<details>
<summary>Code:</summary>

```python
def post_bytes(
    url: str,
    body: bytes,
    headers: dict[str, str],
    *,
    timeout_sec: int = DEFAULT_READ_TIMEOUT_SEC,
    connect_timeout_sec: int = DEFAULT_CONNECT_TIMEOUT_SEC,
    proxy_url: str | None = None,
    should_cancel: Callable[[], bool] | None = None,
    on_connection: Callable[[http.client.HTTPConnection], None] | None = None,
) -> str:
    if should_cancel and should_cancel():
        _raise_request_cancelled()

    parts = urlsplit(url)
    host = parts.hostname
    if host is None:
        msg = f"Invalid URL: {url}"
        raise AiApiError(msg)

    default_port = 443 if parts.scheme == "https" else 80
    port = parts.port or default_port
    path = parts.path or "/"
    if parts.query:
        path = f"{path}?{parts.query}"

    conn: http.client.HTTPConnection
    try:
        conn = _open_connection(
            host=host,
            port=port,
            scheme=parts.scheme,
            proxy_url=proxy_url,
            connect_timeout_sec=connect_timeout_sec,
        )
    except (TimeoutError, OSError, URLError) as exc:
        if should_cancel and should_cancel():
            raise RequestCancelledError from exc
        message = remap_bothub_network_error(
            format_urlerror_message(exc, proxy_url=proxy_url) if isinstance(exc, URLError) else f"Network error: {exc}",
            url=url,
            exc=exc,
        )
        raise AiApiError(message) from exc

    if on_connection is not None:
        on_connection(conn)

    _set_socket_timeout(conn, timeout_sec)

    response: http.client.HTTPResponse | None = None
    raw_bytes = b""
    try:
        conn.request("POST", path, body, headers)
        if should_cancel and should_cancel():
            _raise_request_cancelled()
        response = conn.getresponse()
        raw_bytes = _read_response_bytes(conn, response, should_cancel=should_cancel)
    except RequestCancelledError:
        raise
    except (TimeoutError, OSError) as exc:
        if should_cancel and should_cancel():
            raise RequestCancelledError from exc
        network_error = remap_bothub_network_error(
            f"Network error: {exc}",
            url=url,
            exc=exc,
        )
        raise AiApiError(network_error) from exc
    finally:
        conn.close()

    if response is None:
        no_response = "No response from server"
        raise AiApiError(no_response)
    if response.status >= 400:  # noqa: PLR2004
        detail = raw_bytes.decode("utf-8", errors="replace")
        http_error = f"HTTP {response.status}: {detail}"
        raise AiApiError(http_error)

    return raw_bytes.decode("utf-8")
```

</details>
