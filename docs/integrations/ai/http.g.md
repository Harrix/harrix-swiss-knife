---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `http.py`

## 🔧 Function `post_bytes`

```python
def post_bytes(url: str, body: bytes, headers: dict[str, str], *, timeout_sec: int, proxy_url: str | None = None, should_cancel: Callable[[], bool] | None = None, on_connection: Callable[[http.client.HTTPConnection], None] | None = None) -> str
```

POST raw body and return response text; raise AiApiError on failure.

<details>
<summary>Code:</summary>

```python
def post_bytes(
    url: str,
    body: bytes,
    headers: dict[str, str],
    *,
    timeout_sec: int,
    proxy_url: str | None = None,
    should_cancel: Callable[[], bool] | None = None,
    on_connection: Callable[[http.client.HTTPConnection], None] | None = None,
) -> str:
    if should_cancel is not None or on_connection is not None:
        return _post_cancellable(
            url,
            body,
            headers,
            timeout_sec=timeout_sec,
            proxy_url=proxy_url,
            should_cancel=should_cancel,
            on_connection=on_connection,
        )

    request = Request(  # noqa: S310
        url,
        data=body,
        method="POST",
        headers=headers,
    )
    opener = build_https_opener(proxy_url)
    try:
        with opener.open(request, timeout=timeout_sec) as response:
            return response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        http_error = f"HTTP {exc.code}: {detail}"
        raise AiApiError(http_error) from exc
    except URLError as exc:
        raise AiApiError(format_urlerror_message(exc, proxy_url=proxy_url)) from exc
```

</details>
