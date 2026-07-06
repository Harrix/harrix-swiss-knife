---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `http_download.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DownloadCancelledError`](#️-class-downloadcancellederror)
- [🔧 Function `download_https_to_path`](#-function-download_https_to_path)

</details>

## 🏛️ Class `DownloadCancelledError`

```python
class DownloadCancelledError(Exception)
```

Raised when a download is cancelled by the user.

<details>
<summary>Code:</summary>

```python
class DownloadCancelledError(Exception):
```

</details>

## 🔧 Function `download_https_to_path`

```python
def download_https_to_path(url: str, dest: Path) -> None
```

Download HTTPS URL to a local file with optional cancellation between chunks.

<details>
<summary>Code:</summary>

```python
def download_https_to_path(
    url: str,
    dest: Path,
    *,
    headers: dict[str, str] | None = None,
    timeout: int = 120,
    chunk_size: int = 256 * 1024,
    should_cancel: Callable[[], bool] | None = None,
) -> None:
    _validate_https_url(url)
    if should_cancel and should_cancel():
        raise DownloadCancelledError

    req = Request(url, headers=headers or {}, method="GET")  # noqa: S310
    with urlopen(req, timeout=timeout, context=https_ssl_context()) as resp, dest.open("wb") as out_file:  # noqa: S310
        while True:
            if should_cancel and should_cancel():
                raise DownloadCancelledError
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
```

</details>
