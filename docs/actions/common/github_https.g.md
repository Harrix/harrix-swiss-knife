---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `github_https.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `GITHUB_USER_AGENT`](#-constant-github_user_agent)
- [📎 Constant `ALLOWED_HTTPS_SCHEMES`](#-constant-allowed_https_schemes)
- [🔧 Function `github_api_headers`](#-function-github_api_headers)
- [🔧 Function `validate_https_url`](#-function-validate_https_url)

</details>

## 📎 Constant `GITHUB_USER_AGENT`

```python
GITHUB_USER_AGENT = 'harrix-swiss-knife'
```

_No docstring provided._

## 📎 Constant `ALLOWED_HTTPS_SCHEMES`

```python
ALLOWED_HTTPS_SCHEMES = frozenset({'https'})
```

_No docstring provided._

## 🔧 Function `github_api_headers`

```python
def github_api_headers() -> dict[str, str]
```

Return GitHub API headers, with optional `GITHUB_TOKEN` authorization.

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

Raise `ValueError` when `url` is not an allowed HTTPS URL.

<details>
<summary>Code:</summary>

```python
def validate_https_url(url: str) -> None:
    if urlparse(url).scheme not in ALLOWED_HTTPS_SCHEMES:
        msg = f"URL scheme must be one of {sorted(ALLOWED_HTTPS_SCHEMES)}"
        raise ValueError(msg)
```

</details>
