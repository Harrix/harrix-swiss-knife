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
- [🔧 Function `github_download_headers`](#-function-github_download_headers)
- [🔧 Function `is_github_hosted_url`](#-function-is_github_hosted_url)
- [🔧 Function `resolve_github_token`](#-function-resolve_github_token)
- [🔧 Function `validate_https_url`](#-function-validate_https_url)

</details>

## 🔧 Function `github_api_headers`

```python
def github_api_headers(*, config: dict[str, Any] | None = None, project_root: Path | None = None, user_agent: str | None = None) -> dict[str, str]
```

Return GitHub API headers, with optional Bearer authorization.

<details>
<summary>Code:</summary>

```python
def github_api_headers(
    *,
    config: dict[str, Any] | None = None,
    project_root: Path | None = None,
    user_agent: str | None = None,
) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": user_agent or GITHUB_USER_AGENT,
    }
    token = resolve_github_token(config=config, project_root=project_root)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers
```

</details>

## 🔧 Function `github_download_headers`

```python
def github_download_headers(url: str, *, config: dict[str, Any] | None = None, project_root: Path | None = None, user_agent: str | None = None) -> dict[str, str]
```

Return download headers; Authorization only for GitHub-hosted URLs.

<details>
<summary>Code:</summary>

```python
def github_download_headers(
    url: str,
    *,
    config: dict[str, Any] | None = None,
    project_root: Path | None = None,
    user_agent: str | None = None,
) -> dict[str, str]:
    headers: dict[str, str] = {"User-Agent": user_agent or GITHUB_USER_AGENT}
    if not is_github_hosted_url(url):
        return headers
    token = resolve_github_token(config=config, project_root=project_root)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers
```

</details>

## 🔧 Function `is_github_hosted_url`

```python
def is_github_hosted_url(url: str) -> bool
```

Return whether `url` is on GitHub.com or *.githubusercontent.com.

<details>
<summary>Code:</summary>

```python
def is_github_hosted_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    if not host:
        return False
    return any(host == suffix or host.endswith(f".{suffix}") for suffix in _GITHUB_DOWNLOAD_HOST_SUFFIXES)
```

</details>

## 🔧 Function `resolve_github_token`

```python
def resolve_github_token(*, config: dict[str, Any] | None = None, project_root: Path | None = None) -> str
```

Return a usable GitHub token, or empty string when none is configured.

Resolution order:

1. `GITHUB_TOKEN` environment variable
2. `github_token` from config (after snippet expansion)
3. First line of `api-keys/github-token.txt` under the project root

Empty values and placeholders starting with `paste-your-` are ignored.

<details>
<summary>Code:</summary>

```python
def resolve_github_token(
    *,
    config: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> str:
    env_token = _normalize_token(os.environ.get("GITHUB_TOKEN", ""))
    if env_token:
        return env_token

    if config is not None:
        cfg_token = _normalize_token(str(config.get("github_token") or ""))
        if cfg_token:
            return cfg_token

    root = project_root if project_root is not None else get_project_root()
    return _read_token_file(Path(root) / "api-keys" / "github-token.txt")
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
