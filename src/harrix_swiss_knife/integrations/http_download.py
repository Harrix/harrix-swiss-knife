"""Cancellable HTTPS download helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from harrix_swiss_knife.integrations.http_transport import https_ssl_context

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


class DownloadCancelledError(Exception):
    """Raised when a download is cancelled by the user."""


def download_https_to_path(
    url: str,
    dest: Path,
    *,
    headers: dict[str, str] | None = None,
    timeout: int = 120,
    chunk_size: int = 256 * 1024,
    should_cancel: Callable[[], bool] | None = None,
) -> None:
    """Download HTTPS URL to a local file with optional cancellation between chunks."""
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


def _validate_https_url(url: str) -> None:
    parts = urlparse(url)
    if parts.scheme != "https" or not parts.netloc:
        msg = f"Invalid HTTPS URL: {url}"
        raise ValueError(msg)
