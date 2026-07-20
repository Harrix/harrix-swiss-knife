---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `github_https.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `github_api_headers`](#-function-github_api_headers)
- [🔧 Function `validate_https_url`](#-function-validate_https_url)

</details>

## 🔧 Function `github_api_headers`

```python
def github_api_headers() -> dict[str, str]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def github_api_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": GITHUB_USER_AGENT,
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers
```

</details>

## 🔧 Function `validate_https_url`

```python
def validate_https_url(url: str) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def validate_https_url(url: str) -> None:
    if urlparse(url).scheme not in ALLOWED_HTTPS_SCHEMES:
        msg = f"URL scheme must be one of {sorted(ALLOWED_HTTPS_SCHEMES)}"
        raise ValueError(msg)
```

</details>
