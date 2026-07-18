"""Actions for Python development and code management."""

from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.development._github_https import (
    github_api_headers,
    validate_https_url,
)
from harrix_swiss_knife.integrations.http_download import DownloadCancelledError, download_https_to_path
from harrix_swiss_knife.integrations.http_transport import https_ssl_context


class OnDownloadOptimizeDependencies(ActionBase):
    """Download `ffmpeg.exe`, `avifenc.exe`, `avifdec.exe` from official GitHub releases.

    Fetches the latest Windows builds from AOMediaCodec/libavif and BtbN/FFmpeg-Builds,
    extracts the executables to the project root for use by image optimization actions.
    Requires Windows. HTTPS uses certifi for CA verification; optional GITHUB_TOKEN for API rate limits.
    Extra CA bundle: set SSL_CERT_FILE to a PEM file path (e.g. corporate root CA).
    """

    icon = "⬇️"
    title = "Download ffmpeg, avifenc, avifdec"

    # User-Agent for GitHub API (required)
    _GITHUB_UA = "Harrix-Swiss-Knife/1.0 (Python; urllib)"
    # Chunk size for streaming download
    _DOWNLOAD_CHUNK = 256 * 1024
    _HTTP_FORBIDDEN = 403
    _ALLOWED_URL_SCHEMES = ("https",)
    # Windows: WSAHOST_NOT_FOUND, WSATRY_AGAIN (name resolution / DNS)
    _WIN_DNS_ERRNOS = frozenset({11001, 11002})

    @ActionBase.handle_exceptions("download Optimize dependencies")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Download `ffmpeg.exe`, `avifenc.exe`, `avifdec.exe` from official GitHub releases."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows.")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title, cancellable=True)

    @ActionBase.handle_exceptions("download dependencies thread")
    def in_thread(self) -> str:
        """Run download and extract in a separate thread."""
        dest_dir = h.dev.get_project_root()
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            try:
                # --- libavif: avifenc.exe, avifdec.exe ---
                self.raise_if_work_cancelled()
                self.add_line("Fetching libavif latest release...")
                release = self._fetch_release_latest("AOMediaCodec", "libavif")
                self.raise_if_work_cancelled()
                url = self._get_asset_download_url(release, asset_name="windows-artifacts.zip")
                self.add_line("Downloading windows-artifacts.zip...")
                zip_path = tmp_path / "libavif.zip"
                self._download_to_path(url, zip_path)
                for exe_name in ("avifenc.exe", "avifdec.exe"):
                    self.raise_if_work_cancelled()
                    exe_path = self._extract_exe_from_zip(zip_path, dest_dir, exe_name)
                    if exe_path:
                        self.add_line(f"  Extracted {exe_name} -> {exe_path}")
                    else:
                        self.add_line(f"  Warning: {exe_name} not found in archive")
                # --- FFmpeg: ffmpeg.exe ---
                self.raise_if_work_cancelled()
                self.add_line("Fetching FFmpeg-Builds latest release...")
                release = self._fetch_release_latest("BtbN", "FFmpeg-Builds")
                self.raise_if_work_cancelled()
                try:
                    url = self._get_asset_download_url(release, asset_name="ffmpeg-master-latest-win64-gpl.zip")
                except ValueError:
                    url = self._get_asset_download_url(release, name_contains=("win64", "gpl", ".zip"))
                self.add_line("Downloading FFmpeg zip...")
                zip_path = tmp_path / "ffmpeg.zip"
                self._download_to_path(url, zip_path)
                self.raise_if_work_cancelled()
                exe_path = self._extract_exe_from_zip(zip_path, dest_dir, "ffmpeg.exe")
                if exe_path:
                    self.add_line(f"  Extracted ffmpeg.exe -> {exe_path}")
                else:
                    self.add_line("  Warning: ffmpeg.exe not found in archive")
            except DownloadCancelledError:
                self.add_line("❌ Download cancelled by user.")
            except HTTPError as e:
                self.add_line(f"HTTP error: {e.code} {e.reason}")
                if e.code == self._HTTP_FORBIDDEN:
                    self.add_line("If rate limited, set GITHUB_TOKEN environment variable.")
            except URLError as e:
                reason_str = str(e.reason)
                self.add_line(f"Network error: {reason_str}")
                if "CERTIFICATE_VERIFY_FAILED" in reason_str:
                    self.add_line(
                        "SSL hint: install Windows updates for root certificates, "
                        "or set SSL_CERT_FILE to a PEM bundle that includes your corporate CA."
                    )
                elif self._is_dns_or_unreachable_urlerror(e.reason, reason_str):
                    self.add_line(
                        "DNS/network hint: this PC could not resolve or reach GitHub (no internet, wrong DNS, "
                        "firewall, or proxy). Check the connection and that api.github.com opens in a browser. "
                        "Offline option: put windows-artifacts.zip and the FFmpeg win64-gpl zip under "
                        "install/dependencies/ and run the installer bundle step that extracts them "
                        "(see THIRD_PARTY_NOTICES.md)."
                    )
            except ValueError as e:
                self.add_line(f"Error: {e}")
            except OSError as e:
                self.add_line(f"IO/OS error: {e}")

        return "Done."

    @ActionBase.handle_exceptions("download dependencies thread completion")
    def thread_after(self, result: Any) -> None:
        """Show result in main thread."""
        self.show_toast("Download Optimize dependencies completed")
        self.add_line(result)
        self.show_result()

    def _download_to_path(self, url: str, dest: Path) -> None:
        """Download URL to dest path, following redirects. Raises on error."""
        download_https_to_path(
            url,
            dest,
            headers={"User-Agent": self._GITHUB_UA},
            timeout=120,
            chunk_size=self._DOWNLOAD_CHUNK,
            should_cancel=self.is_work_cancelled,
        )

    def _extract_exe_from_zip(
        self, zip_path: Path, dest_dir: Path, exe_name: str, archive_inner_path: str | None = None
    ) -> Path | None:
        """Extract a single exe from zip. If archive_inner_path given, use it; else find by exe name in namelist().

        Returns dest file path or None.
        """
        with zipfile.ZipFile(zip_path, "r") as zf:
            if archive_inner_path and archive_inner_path in zf.namelist():
                zf.extract(archive_inner_path, dest_dir)
                extracted = dest_dir / archive_inner_path
                if extracted != dest_dir / exe_name:
                    shutil.move(str(extracted), str(dest_dir / exe_name))
                return dest_dir / exe_name
            for name in zf.namelist():
                if name.replace("\\", "/").rstrip("/").endswith(exe_name):
                    zf.extract(name, dest_dir)
                    extracted = dest_dir / name
                    target = dest_dir / exe_name
                    if extracted.resolve() != target.resolve():
                        shutil.move(str(extracted), str(target))
                    # Remove empty parent dirs if any
                    for part in Path(name).parents:
                        if part != Path():
                            d = dest_dir / part
                            if d.exists() and d.is_dir() and not any(d.iterdir()):
                                d.rmdir()
                    return target
        return None

    def _fetch_release_latest(self, owner: str, repo: str) -> dict[str, Any]:
        """Fetch latest release info from GitHub API. Raises on error."""
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        validate_https_url(url)
        req = Request(url, headers=github_api_headers())  # noqa: S310
        with urlopen(req, timeout=30, context=https_ssl_context()) as resp:  # noqa: S310
            return json.loads(resp.read().decode())

    def _get_asset_download_url(
        self, release: dict[str, Any], asset_name: str | None = None, name_contains: tuple[str, ...] = ()
    ) -> str:
        """Get browser_download_url for an asset by exact name or by substrings. Raises if not found."""
        assets = release.get("assets") or []
        if asset_name:
            for a in assets:
                if a.get("name") == asset_name:
                    return a["browser_download_url"]
            msg = f"Asset '{asset_name}' not found in release"
            raise ValueError(msg)
        for a in assets:
            name = a.get("name") or ""
            if all(s in name for s in name_contains) and "shared" not in name.lower() and name.endswith(".zip"):
                return a["browser_download_url"]
        msg = f"No asset matching {name_contains} found in release"
        raise ValueError(msg)

    @staticmethod
    def _is_dns_or_unreachable_urlerror(reason: object, reason_str: str) -> bool:
        """Return whether the URLError likely indicates DNS failure or no route to GitHub."""
        needles = (
            "getaddrinfo",
            "Name or service not known",
            "nodename nor servname provided, or not known",
            "Temporary failure in name resolution",
        )
        if any(n in reason_str for n in needles):
            return True
        errno_val = getattr(reason, "errno", None) if isinstance(reason, OSError) else None
        return errno_val in OnDownloadOptimizeDependencies._WIN_DNS_ERRNOS
