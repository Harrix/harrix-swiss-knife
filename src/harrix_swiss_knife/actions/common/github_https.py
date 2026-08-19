"""Shared GitHub HTTPS helpers for development actions."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from harrix_swiss_knife.paths import get_project_root

GITHUB_USER_AGENT = "harrix-swiss-knife"
ALLOWED_HTTPS_SCHEMES = frozenset({"https"})
_GITHUB_DOWNLOAD_HOST_SUFFIXES = (
    "github.com",
    "githubusercontent.com",
)


def github_api_headers(
    *,
    config: dict[str, Any] | None = None,
    project_root: Path | None = None,
    user_agent: str | None = None,
) -> dict[str, str]:
    """Return GitHub API headers, with optional Bearer authorization."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": user_agent or GITHUB_USER_AGENT,
    }
    token = resolve_github_token(config=config, project_root=project_root)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_download_headers(
    url: str,
    *,
    config: dict[str, Any] | None = None,
    project_root: Path | None = None,
    user_agent: str | None = None,
) -> dict[str, str]:
    """Return download headers; Authorization only for GitHub-hosted URLs."""
    headers: dict[str, str] = {"User-Agent": user_agent or GITHUB_USER_AGENT}
    if not is_github_hosted_url(url):
        return headers
    token = resolve_github_token(config=config, project_root=project_root)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def is_github_hosted_url(url: str) -> bool:
    """Return whether `url` is on GitHub.com or *.githubusercontent.com."""
    host = (urlparse(url).hostname or "").lower()
    if not host:
        return False
    return any(host == suffix or host.endswith(f".{suffix}") for suffix in _GITHUB_DOWNLOAD_HOST_SUFFIXES)


def resolve_github_token(
    *,
    config: dict[str, Any] | None = None,
    project_root: Path | None = None,
) -> str:
    """Return a usable GitHub token, or empty string when none is configured.

    Resolution order:

    1. `GITHUB_TOKEN` environment variable
    2. `github_token` from config (after snippet expansion)
    3. First line of `api-keys/github-token.txt` under the project root

    Empty values and placeholders starting with `paste-your-` are ignored.

    """
    env_token = _normalize_token(os.environ.get("GITHUB_TOKEN", ""))
    if env_token:
        return env_token

    if config is not None:
        cfg_token = _normalize_token(str(config.get("github_token") or ""))
        if cfg_token:
            return cfg_token

    root = project_root if project_root is not None else get_project_root()
    return _read_token_file(Path(root) / "api-keys" / "github-token.txt")


def validate_https_url(url: str) -> None:
    """Raise `ValueError` when `url` is not an allowed HTTPS URL."""
    if urlparse(url).scheme not in ALLOWED_HTTPS_SCHEMES:
        msg = f"URL scheme must be one of {sorted(ALLOWED_HTTPS_SCHEMES)}"
        raise ValueError(msg)


def _normalize_token(raw: str) -> str:
    token = raw.strip()
    # Example api-keys/*.example.txt placeholders start with this prefix.
    if not token or token.startswith("paste-your-"):
        return ""
    return token


def _read_token_file(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    first_line = text.splitlines()[0] if text else ""
    return _normalize_token(first_line)
