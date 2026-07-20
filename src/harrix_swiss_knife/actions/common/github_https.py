"""Shared GitHub HTTPS helpers for development actions."""

from __future__ import annotations

import os
from urllib.parse import urlparse

GITHUB_USER_AGENT = "harrix-swiss-knife"
ALLOWED_HTTPS_SCHEMES = frozenset({"https"})


def github_api_headers() -> dict[str, str]:
    """Return GitHub API headers, with optional `GITHUB_TOKEN` authorization."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": GITHUB_USER_AGENT,
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def validate_https_url(url: str) -> None:
    """Raise `ValueError` when `url` is not an allowed HTTPS URL."""
    if urlparse(url).scheme not in ALLOWED_HTTPS_SCHEMES:
        msg = f"URL scheme must be one of {sorted(ALLOWED_HTTPS_SCHEMES)}"
        raise ValueError(msg)
