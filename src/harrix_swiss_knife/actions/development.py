"""Actions for Python development and code management."""

from __future__ import annotations

import contextlib
import copy
import json
import os
import shutil
import ssl
import subprocess
import sys
import time
import tomllib
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Literal, TypedDict, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import certifi
import harrix_pylib as h
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.desktop_shortcut import create_desktop_shortcut
from harrix_swiss_knife.paths import list_recent_action_output_files


class OnAboutDialog(ActionBase):
    """Show the about dialog with program information.

    This action displays a dialog window containing information about the application,
    including version, description, author, and license information.
    """

    icon = "ℹ️"  # noqa: RUF001
    title = "About"
    show_in_compact_mode = True

    @ActionBase.handle_exceptions("about dialog")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Show the about dialog with program information."""
        version = self._get_version_from_pyproject()

        about_info = self.dialogs.show_about_dialog(
            title="About",
            app_name="Harrix Swiss Knife",
            version=version,
            description=(
                "A multifunctional tool for developers.\n"
                "Includes a rich set of utilities for working with files, images,\n"
                "Python code, and more."
            ),
            author="Anton Sergienko (Harrix)",
            license_text="MIT License",
            github="https://github.com/harrix/harrix-swiss-knife",
        )

        if about_info:
            self.add_line("✅ The About window has been shown")
        else:
            self.add_line("❌ The About window has been canceled")

    def _get_version_from_pyproject(self) -> str:
        """Get version from pyproject.toml file.

        Returns:

        - `str`: Version string from `pyproject.toml`, or "Unknown" if not found.

        """
        try:
            pyproject_path = h.dev.get_project_root() / "pyproject.toml"
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "Unknown")
        except Exception as e:
            self.add_line(f"⚠️ Warning: Could not read version from pyproject.toml: {e}")
            return "Unknown"


class OnCreateDesktopShortcut(ActionBase):
    """Create or update a desktop shortcut to launch Harrix Swiss Knife.

    Uses the same target, arguments, working directory, and icon as
    ``New-DesktopShortcut`` in ``install/harrix-swiss-knife.ps1`` (``pythonw.exe``,
    ``main.py``, ``img/icon.ico`` or ``assets/app.ico``). Windows only.
    """

    icon = "🔗"
    title = "Create desktop shortcut"

    @ActionBase.handle_exceptions("creating desktop shortcut")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Create desktop shortcut for this project."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows.")
            self.show_result()
            return

        project_root = h.dev.get_project_root()
        pyw = project_root / ".venv" / "Scripts" / "pythonw.exe"
        main_py = project_root / "src" / "harrix_swiss_knife" / "main.py"

        if not pyw.is_file():
            self.add_line(f"❌ pythonw.exe not found: {pyw}")
            self.show_result()
            return
        if not main_py.is_file():
            self.add_line(f"❌ main.py not found: {main_py}")
            self.show_result()
            return

        try:
            lnk_path = create_desktop_shortcut(project_root)
        except OSError as e:
            self.add_line(f"❌ {e}")
            self.show_result()
            return

        self.add_line(f"✅ Desktop shortcut created: {lnk_path}")
        self.show_toast("Desktop shortcut created")
        self.show_result()


class OnDownloadOptimizeDependencies(ActionBase):
    """Download ffmpeg.exe, avifenc.exe, avifdec.exe from official GitHub releases.

    Fetches the latest Windows builds from AOMediaCodec/libavif and BtbN/FFmpeg-Builds,
    extracts the executables to the project root for use by Optimize (optimize.js).
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
        """Download ffmpeg.exe, avifenc.exe, avifdec.exe from official GitHub releases."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows.")
            self.show_result()
            return
        self.start_thread(self._in_thread, self._thread_after, self.title)

    def _download_to_path(self, url: str, dest: Path) -> None:
        """Download URL to dest path, following redirects. Raises on error."""
        self._validate_https_url(url)
        req = Request(url, headers={"User-Agent": self._GITHUB_UA})  # noqa: S310
        with urlopen(req, timeout=120, context=self._https_context()) as resp, dest.open("wb") as f:  # noqa: S310
            while True:
                chunk = resp.read(self._DOWNLOAD_CHUNK)
                if not chunk:
                    break
                f.write(chunk)

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
        self._validate_https_url(url)
        req = Request(url, headers=self._github_api_headers())  # noqa: S310
        with urlopen(req, timeout=30, context=self._https_context()) as resp:  # noqa: S310
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

    def _github_api_headers(self) -> dict[str, str]:
        """Build headers for GitHub API requests, optionally with token."""
        headers = {"Accept": "application/vnd.github+json", "User-Agent": self._GITHUB_UA}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _https_context(self) -> ssl.SSLContext:
        """SSL context for GitHub HTTPS: Mozilla CA bundle via certifi, plus optional SSL_CERT_FILE."""
        ctx = ssl.create_default_context(cafile=certifi.where())
        ssl_cert_file = os.environ.get("SSL_CERT_FILE")
        if ssl_cert_file and Path(ssl_cert_file).is_file():
            ctx.load_verify_locations(cafile=ssl_cert_file)
        return ctx

    @ActionBase.handle_exceptions("download dependencies thread")
    def _in_thread(self) -> str:
        """Run download and extract in a separate thread."""
        dest_dir = h.dev.get_project_root()
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            try:
                # --- libavif: avifenc.exe, avifdec.exe ---
                self.add_line("Fetching libavif latest release...")
                release = self._fetch_release_latest("AOMediaCodec", "libavif")
                url = self._get_asset_download_url(release, asset_name="windows-artifacts.zip")
                self.add_line("Downloading windows-artifacts.zip...")
                zip_path = tmp_path / "libavif.zip"
                self._download_to_path(url, zip_path)
                for exe_name in ("avifenc.exe", "avifdec.exe"):
                    exe_path = self._extract_exe_from_zip(zip_path, dest_dir, exe_name)
                    if exe_path:
                        self.add_line(f"  Extracted {exe_name} -> {exe_path}")
                    else:
                        self.add_line(f"  Warning: {exe_name} not found in archive")
                # --- FFmpeg: ffmpeg.exe ---
                self.add_line("Fetching FFmpeg-Builds latest release...")
                release = self._fetch_release_latest("BtbN", "FFmpeg-Builds")
                try:
                    url = self._get_asset_download_url(release, asset_name="ffmpeg-master-latest-win64-gpl.zip")
                except ValueError:
                    url = self._get_asset_download_url(release, name_contains=("win64", "gpl", ".zip"))
                self.add_line("Downloading FFmpeg zip...")
                zip_path = tmp_path / "ffmpeg.zip"
                self._download_to_path(url, zip_path)
                exe_path = self._extract_exe_from_zip(zip_path, dest_dir, "ffmpeg.exe")
                if exe_path:
                    self.add_line(f"  Extracted ffmpeg.exe -> {exe_path}")
                else:
                    self.add_line("  Warning: ffmpeg.exe not found in archive")
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

    @ActionBase.handle_exceptions("download dependencies thread completion")
    def _thread_after(self, result: Any) -> None:
        """Show result in main thread."""
        self.show_toast("Download Optimize dependencies completed")
        self.add_line(result)
        self.show_result()

    def _validate_https_url(self, url: str) -> None:
        """Raise ValueError if URL scheme is not in allowed list (https only)."""
        scheme = urlparse(url).scheme
        if scheme not in self._ALLOWED_URL_SCHEMES:
            msg = f"URL scheme must be one of {self._ALLOWED_URL_SCHEMES}"
            raise ValueError(msg)


class OnExit(ActionBase):
    """Exit the application.

    This action terminates the current Qt application instance,
    closing all windows and ending the program execution.
    """

    icon = "×"  # noqa: RUF001
    title = "Exit"
    show_in_compact_mode = True

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the OnExit action."""
        super().__init__(**kwargs)
        self.parent = kwargs.get("parent")

    @ActionBase.handle_exceptions("application exit")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Exit the application."""
        QApplication.quit()


class OnInstallHarrixNotesExplorerExtension(ActionBase):
    """Install or update the bundled Harrix Notes Explorer VS Code extension into local profiles.

    Shows a checkbox dialog listing all supported VS Code-family editors (stable order). Detected
    installs are selectable; missing installs appear as ``(not installed)`` and are disabled. Editors
    that already have ``harrix-notes-explorer`` are checked by default. Copies the
    ``vscode/harrix-notes-explorer`` tree into ``harrix-notes-explorer`` under each selected editor's
    ``extensions`` folder (no symlinks or elevation required for typical user profiles), then upserts
    an entry in that directory's ``extensions.json`` so current VS Code builds list the extension.
    """

    icon = "📦"
    title = "Update/Install Harrix Notes Explorer extension for VSCode"

    _HARRIX_NOTES_EXPLORER_EXT_ID = "local.harrix-notes-explorer"
    _HARRIX_NOTES_EXPLORER_EXT_UUID = "fbb16925-9395-59b6-ad7f-f25518ab2be8"

    _EDITOR_LABEL_VSCODE = "VS Code"
    _EDITOR_LABEL_INSIDERS = "VS Code Insiders"
    _EDITOR_LABEL_CURSOR = "Cursor"
    _EDITOR_LABEL_VSCODIUM = "VSCodium"
    _EDITOR_LABEL_WINDSURF = "Windsurf"
    _EDITOR_LABEL_ANTIGRAVITY = "Google Antigravity"
    _EDITOR_NOT_INSTALLED_SUFFIX = " (not installed)"
    _SUPPORTED_WIN32_EDITOR_LABELS: tuple[str, ...] = (
        _EDITOR_LABEL_VSCODE,
        _EDITOR_LABEL_INSIDERS,
        _EDITOR_LABEL_CURSOR,
        _EDITOR_LABEL_VSCODIUM,
        _EDITOR_LABEL_WINDSURF,
        _EDITOR_LABEL_ANTIGRAVITY,
    )

    @ActionBase.handle_exceptions("install Harrix Notes Explorer extension")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Copy extension files into each selected editor's extensions directory."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows.")
            self.show_result()
            return

        ext_dir = (h.dev.get_project_root() / "vscode" / "harrix-notes-explorer").resolve()
        if not ext_dir.is_dir():
            self.add_line(f"❌ Extension folder not found: {ext_dir}")
            self.show_result()
            return

        installed = set(self._discover_win32_editors())
        all_editors = self._all_supported_win32_editor_labels()
        choices = [self._editor_choice_label(e, installed=e in installed) for e in all_editors]
        disabled_choices = [self._editor_choice_label(e, installed=False) for e in all_editors if e not in installed]
        default_selected = [
            self._editor_choice_label(e, installed=True)
            for e in all_editors
            if e in installed and self._is_harrix_notes_explorer_installed(e)
        ]
        selected = self.dialogs.get_checkbox_selection(
            self.title,
            "Install or update Harrix Notes Explorer for which editors? "
            "Grayed items are not detected on this system. Unchecked editors are skipped.",
            choices,
            default_selected=default_selected,
            disabled_choices=disabled_choices,
        )
        if not selected:
            self.add_line("Canceled or no editors selected.")
            self.show_result()
            return

        selected_canonical = [self._canonical_editor_label(s) for s in selected]
        dest_pairs = self._dest_extension_roots(selected_canonical)
        if not dest_pairs:
            self.add_line("❌ No valid editor selection to install.")
            self.show_result()
            return

        ext_version = "0.0.1"
        try:
            with (ext_dir / "package.json").open(encoding="utf-8") as f:
                ext_version = str(json.load(f).get("version", ext_version))
        except (OSError, json.JSONDecodeError, TypeError):
            pass

        ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
        for label, ext_root in dest_pairs:
            dest = ext_root / "harrix-notes-explorer"
            try:
                ext_root.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    shutil.rmtree(dest, ignore_errors=False)
                shutil.copytree(ext_dir, dest, ignore=ignore)
            except OSError as e:
                self.add_line(f"❌ {label}: could not copy to {dest}: {e}")
                self.add_line("   Close that editor if files are locked, then try again.")
                continue
            merged, merge_err = self._merge_harrix_notes_explorer_extensions_json(ext_root, dest, ext_version)
            if merged:
                self.add_line(f"✅ {label}: installed to {dest} (extensions.json updated)")
            else:
                self.add_line(f"✅ {label}: installed to {dest}")
                self.add_line(
                    f"⚠️ {label}: could not update extensions.json ({merge_err}). "
                    "Try Command Palette → Developer: Install Extension from Location, then reload the window."
                )

        self.show_result()

    @classmethod
    def _all_supported_win32_editor_labels(cls) -> list[str]:
        """Return display labels for all supported VS Code-family editors (stable order)."""
        return list(cls._SUPPORTED_WIN32_EDITOR_LABELS)

    @staticmethod
    def _antigravity_installed_win32() -> bool:
        if shutil.which("antigravity"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "Antigravity" / "Antigravity.exe")
        if pf:
            candidates.append(Path(pf) / "Antigravity" / "Antigravity.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "Antigravity" / "Antigravity.exe")
        return any(p.is_file() for p in candidates)

    @classmethod
    def _canonical_editor_label(cls, display: str) -> str:
        """Strip ``(not installed)`` suffix from a dialog choice label."""
        suffix = cls._EDITOR_NOT_INSTALLED_SUFFIX
        if display.endswith(suffix):
            return display[: -len(suffix)]
        return display

    @staticmethod
    def _cursor_installed_win32() -> bool:
        if shutil.which("cursor"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "cursor" / "Cursor.exe")
        if pf:
            candidates.append(Path(pf) / "Cursor" / "Cursor.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "Cursor" / "Cursor.exe")
        return any(p.is_file() for p in candidates)

    @classmethod
    def _dest_extension_roots(cls, selected_labels: list[str]) -> list[tuple[str, Path]]:
        """Map selected editor labels to each editor's user ``extensions`` directory."""
        home = Path.home()
        mapping: dict[str, Path] = {
            cls._EDITOR_LABEL_VSCODE: home / ".vscode" / "extensions",
            cls._EDITOR_LABEL_INSIDERS: home / ".vscode-insiders" / "extensions",
            cls._EDITOR_LABEL_CURSOR: home / ".cursor" / "extensions",
            cls._EDITOR_LABEL_VSCODIUM: home / ".vscode-oss" / "extensions",
            cls._EDITOR_LABEL_WINDSURF: home / ".windsurf" / "extensions",
            cls._EDITOR_LABEL_ANTIGRAVITY: home / ".antigravity" / "extensions",
        }
        out: list[tuple[str, Path]] = []
        for label in selected_labels:
            root = mapping.get(label)
            if root is not None:
                out.append((label, root))
        return out

    @classmethod
    def _discover_win32_editors(cls) -> list[str]:
        """Return display labels for detected VS Code-family installs (stable order)."""
        found: list[str] = []
        if cls._vscode_stable_installed_win32():
            found.append(cls._EDITOR_LABEL_VSCODE)
        if cls._vscode_insiders_installed_win32():
            found.append(cls._EDITOR_LABEL_INSIDERS)
        if cls._cursor_installed_win32():
            found.append(cls._EDITOR_LABEL_CURSOR)
        if cls._vscodium_installed_win32():
            found.append(cls._EDITOR_LABEL_VSCODIUM)
        if cls._windsurf_installed_win32():
            found.append(cls._EDITOR_LABEL_WINDSURF)
        if cls._antigravity_installed_win32():
            found.append(cls._EDITOR_LABEL_ANTIGRAVITY)
        return found

    @staticmethod
    def _editor_choice_label(canonical: str, *, installed: bool) -> str:
        """Return dialog checkbox text for *canonical* editor name."""
        if installed:
            return canonical
        return f"{canonical}{OnInstallHarrixNotesExplorerExtension._EDITOR_NOT_INSTALLED_SUFFIX}"

    @classmethod
    def _is_harrix_notes_explorer_installed(cls, editor_label: str) -> bool:
        """Return whether ``harrix-notes-explorer`` is present with expected manifest under that editor."""
        pairs = cls._dest_extension_roots([editor_label])
        if not pairs:
            return False
        _, ext_root = pairs[0]
        pkg = ext_root / "harrix-notes-explorer" / "package.json"
        if not pkg.is_file():
            return False
        try:
            with pkg.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError, TypeError):
            return False
        if not isinstance(data, dict):
            return False
        return str(data.get("name", "")) == "harrix-notes-explorer" and str(data.get("publisher", "")) == "local"

    @classmethod
    def _merge_harrix_notes_explorer_extensions_json(cls, ext_root: Path, dest: Path, version: str) -> tuple[bool, str]:
        """Upsert ``local.harrix-notes-explorer`` in ``extensions.json`` under ``ext_root``."""
        json_path = ext_root / "extensions.json"
        data: list[Any]
        try:
            if json_path.is_file():
                loaded = json.loads(json_path.read_text(encoding="utf-8"))
                if not isinstance(loaded, list):
                    return False, "extensions.json root is not a JSON array"
                data = loaded
            else:
                data = []
        except json.JSONDecodeError as e:
            return False, f"invalid JSON ({e})"

        ext_id = cls._HARRIX_NOTES_EXPLORER_EXT_ID
        data = [x for x in data if not (isinstance(x, dict) and x.get("identifier", {}).get("id") == ext_id)]

        uri_path = cls._vscode_extensions_json_uri_path(dest)
        ts = int(time.time() * 1000)
        uuid_val = cls._HARRIX_NOTES_EXPLORER_EXT_UUID
        entry: dict[str, Any] = {
            "identifier": {"id": ext_id, "uuid": uuid_val},
            "version": version,
            "location": {"$mid": 1, "path": uri_path, "scheme": "file"},
            "relativeLocation": dest.name,
            "metadata": {
                "installedTimestamp": ts,
                "pinned": False,
                "source": "path",
                "id": uuid_val,
                "publisherDisplayName": "local",
                "targetPlatform": "undefined",
                "updated": False,
                "private": False,
                "isPreReleaseVersion": False,
                "hasPreReleaseVersion": False,
                "preRelease": False,
            },
        }
        data.append(entry)

        tmp_path = ext_root / f".extensions.json.{os.getpid()}.tmp"
        try:
            payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            tmp_path.write_text(payload, encoding="utf-8")
            tmp_path.replace(json_path)
        except OSError as e:
            with contextlib.suppress(OSError):
                tmp_path.unlink(missing_ok=True)
            return False, str(e)
        return True, ""

    @staticmethod
    def _vscode_extensions_json_uri_path(folder: Path) -> str:
        """Match VS Code ``extensions.json`` ``location.path`` shape (e.g. ``/c:/Users/...``)."""
        s = folder.resolve().as_posix()
        try:
            if s[1] == ":" and s[0].isalpha():
                return f"/{s[0].lower()}:{s[2:]}"
        except IndexError:
            pass
        return s if s.startswith("/") else f"/{s}"

    @staticmethod
    def _vscode_insiders_installed_win32() -> bool:
        if shutil.which("code-insiders"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "Microsoft VS Code Insiders" / "Code - Insiders.exe")
        if pf:
            candidates.append(Path(pf) / "Microsoft VS Code Insiders" / "Code - Insiders.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "Microsoft VS Code Insiders" / "Code - Insiders.exe")
        return any(p.is_file() for p in candidates)

    @staticmethod
    def _vscode_stable_installed_win32() -> bool:
        if shutil.which("code"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "Microsoft VS Code" / "Code.exe")
        if pf:
            candidates.append(Path(pf) / "Microsoft VS Code" / "Code.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "Microsoft VS Code" / "Code.exe")
        return any(p.is_file() for p in candidates)

    @staticmethod
    def _vscodium_installed_win32() -> bool:
        if shutil.which("codium"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "VSCodium" / "VSCodium.exe")
        if pf:
            candidates.append(Path(pf) / "VSCodium" / "VSCodium.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "VSCodium" / "VSCodium.exe")
        return any(p.is_file() for p in candidates)

    @staticmethod
    def _windsurf_installed_win32() -> bool:
        if shutil.which("windsurf"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.extend(
                [
                    Path(local) / "Programs" / "Windsurf" / "Windsurf.exe",
                    Path(local) / "Programs" / "windsurf" / "Windsurf.exe",
                ]
            )
        if pf:
            candidates.extend(
                [
                    Path(pf) / "Windsurf" / "Windsurf.exe",
                    Path(pf) / "windsurf" / "Windsurf.exe",
                ]
            )
        if pfx86:
            candidates.extend(
                [
                    Path(pfx86) / "Windsurf" / "Windsurf.exe",
                    Path(pfx86) / "windsurf" / "Windsurf.exe",
                ]
            )
        return any(p.is_file() for p in candidates)


class OnNodeUpdate(ActionBase):
    """Update Node.js to the latest version via winget.

    This action upgrades OpenJS.NodeJS using the Windows Package Manager (winget)
    command 'winget upgrade OpenJS.NodeJS'. Available only on Windows.
    """

    icon = "📥"
    title = "Update Node.js"

    @ActionBase.handle_exceptions("Node.js update")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Update Node.js to the latest version via winget."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows (winget).")
            self.show_result()
            return
        self.start_thread(self._in_thread, self._thread_after, self.title)

    @ActionBase.handle_exceptions("Node.js update thread")
    def _in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Avoid interactive agreement prompts (msstore) by pinning the "winget" source
        # and disabling interactivity.
        cmd = (
            "winget upgrade -e --id OpenJS.NodeJS.LTS --source winget "
            "--accept-package-agreements --accept-source-agreements --silent --disable-interactivity"
        )
        return h.dev.run_command(cmd)

    @ActionBase.handle_exceptions("Node.js update thread completion")
    def _thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Node.js update completed")
        self.add_line(result)
        self.show_result()


class OnNpmManagePackages(ActionBase):
    """Install or update configured NPM packages globally.

    This action manages NPM packages specified in the `config["npm_packages"]` list:

    1. Updates NPM itself to the latest version
    2. Installs/updates all configured packages (npm install will update if already exists)
    3. Runs global update to ensure all packages are at latest versions

    This ensures all configured packages are present and up-to-date in the system.
    """

    icon = "📦"
    title = "Update/Install global NPM packages"

    @ActionBase.handle_exceptions("NPM package management")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Install or update configured NPM packages globally."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("NPM operations thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Update NPM itself first
        self.add_line("Updating NPM...")
        result = h.dev.run_command("npm update npm -g")
        self.add_line(result)

        # Install/update all configured packages
        self.add_line("Installing/updating configured packages...")
        install_commands = "\n".join([f"npm i -g {package}" for package in self.config["npm_packages"]])
        result = h.dev.run_command(install_commands)
        self.add_line(result)

        # Run global update to ensure everything is up-to-date
        self.add_line("Running global update...")
        result = h.dev.run_command("npm update -g")
        self.add_line(result)

        return "NPM packages management completed"

    @ActionBase.handle_exceptions("NPM thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("NPM packages management completed")
        self.add_line(result)
        self.show_result()


class OnOpenConfigJson(ActionBase):
    """Open the application's configuration file.

    Opens ``config.json`` in the editor from ``editor``. If that command or path is
    missing, tries ``cursor``, ``code`` (VS Code), ``code-insiders`` in order, writes
    the first match back to ``config.json`` under ``editor``, then opens the file.
    If none are available on Windows, uses Notepad and persists ``editor`` as
    ``notepad``. On other platforms, opens the file with the default application when
    no editor is found.
    """

    icon = "⚙️"
    title = "Open config.json"

    @ActionBase.handle_exceptions("config file opening")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open the application's configuration file."""
        config_file = (h.dev.get_project_root() / self.config_path).resolve()
        editor_raw = str(self.config.get("editor") or "").strip()
        fallback_commands = ("cursor", "code", "code-insiders")

        chosen_key = editor_raw
        resolved: str | None = None

        if editor_raw:
            resolved = self._resolve_editor_executable(editor_raw)

        if resolved is None:
            for name in fallback_commands:
                found = shutil.which(name)
                if found:
                    chosen_key = name
                    resolved = found
                    break

        if resolved is None and sys.platform == "win32":
            found = shutil.which("notepad") or self._windows_notepad_exe()
            if found:
                chosen_key = "notepad"
                resolved = found

        if resolved is not None and chosen_key != editor_raw:
            h.dev.config_update_value("editor", chosen_key, self.config_path)
            self.config["editor"] = chosen_key
            self.add_line(f'Updated "editor" in config.json to: {chosen_key}')

        if resolved is not None:
            commands = f'"{resolved}" "{config_file}"'
            result = h.dev.run_command(commands)
            self.add_line(result)
            return

        if sys.platform == "win32":
            try:
                os.startfile(str(config_file))  # noqa: S606
            except OSError as e:
                self.add_line(f"❌ Could not open config.json: {e}")
            else:
                self.add_line(f"Opened with default app: {config_file}")
                return
        elif sys.platform == "darwin":
            result = h.dev.run_command(f'open "{config_file}"')
            if result:
                self.add_line(result)
            self.add_line(f"Opened with default app: {config_file}")
            return
        else:
            result = h.dev.run_command(f'xdg-open "{config_file}"')
            if result:
                self.add_line(result)
            self.add_line(f"Opened with default app: {config_file}")
            return

        self.add_line("❌ No editor available (configured editor missing; no cursor, code, code-insiders, or notepad).")
        self.add_line(f"Config path: {config_file}")

    def _editor_token_looks_like_path(self, editor: str) -> bool:
        min_windows_drive_len = 2
        return "/" in editor or "\\" in editor or (len(editor) >= min_windows_drive_len and editor[1] == ":")

    def _resolve_editor_executable(self, editor: str) -> str | None:
        """Return a filesystem path to *editor* if it can be launched, else ``None``."""
        editor = editor.strip()
        if not editor:
            return None
        if self._editor_token_looks_like_path(editor):
            try:
                candidate = Path(editor).expanduser().resolve()
            except OSError:
                return None
            return str(candidate) if candidate.is_file() else None
        return shutil.which(editor)

    def _windows_notepad_exe(self) -> str | None:
        system_root = os.environ.get("SYSTEMROOT") or r"C:\Windows"
        notepad = Path(system_root) / "System32" / "notepad.exe"
        return str(notepad) if notepad.is_file() else None


class OnUpdateHarrixSwissKnife(ActionBase):
    """Update Harrix stack repos from git or GitHub ZIP archives.

    For ``harrix-swiss-knife``, ``harrix-pylib``, and ``harrix-pyssg`` paths taken from
    ``paths_python_projects``: if ``.git`` exists, runs ``git pull --ff-only`` (optional
    commit when the tree is dirty). Without ``.git``, downloads the default branch ZIP
    from GitHub and replaces the tree. Swiss Knife keeps ``temp/`` and merges
    ``config/config.json`` with a checkbox dialog (default: keep local values).
    """

    icon = "⬆️"
    title = "Update Harrix Swiss Knife from GitHub"

    _PROJECT_NAMES = ("harrix-swiss-knife", "harrix-pylib", "harrix-pyssg")
    _GITHUB_UA = "Harrix-Swiss-Knife/1.0 (Python; urllib)"
    _ALLOWED_SCHEMES = ("https",)
    _GIT_DIRTY_COMMIT = "Commit all changes and pull"
    _GIT_DIRTY_SKIP = "Skip this repository"
    _GIT_DIRTY_CANCEL = "Cancel entire update"

    @ActionBase.handle_exceptions("update Harrix Swiss Knife stack")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Run updates for Harrix sibling repos (git pull or GitHub ZIP)."""
        steps = self._collect_steps_interactive()
        if steps is None:
            return
        if not steps:
            self.add_line("Nothing to update (no valid project paths).")
            self.show_result()
            return
        self.start_thread(lambda: self._worker_run(steps), self._worker_finished, self.title)

    @staticmethod
    def _build_swiss_config_merged(
        local: dict[str, Any] | None,
        incoming: dict[str, Any],
        keys_keep_local: set[str],
    ) -> dict[str, Any]:
        merged = copy.deepcopy(incoming)
        if local:
            for k, v in local.items():
                if k not in merged:
                    merged[k] = copy.deepcopy(v)
            for k in keys_keep_local:
                if k in local:
                    merged[k] = copy.deepcopy(local[k])
        return merged

    @staticmethod
    def _clear_directory_children(root: Path) -> None:
        if not root.is_dir():
            return
        for child in list(root.iterdir()):
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                with contextlib.suppress(OSError):
                    child.unlink()

    def _collect_steps_interactive(self) -> list[OnUpdateHarrixSwissKnife._UpdateStep] | None:
        raw = self.config.get("paths_python_projects")
        if not isinstance(raw, list):
            self.add_line('❌ config "paths_python_projects" must be a list.')
            return None

        by_name: dict[str, Path] = {}
        for entry in raw:
            p = Path(str(entry)).expanduser()
            name = p.name
            if name in self._PROJECT_NAMES and name not in by_name:
                try:
                    by_name[name] = p.resolve()
                except OSError:
                    self.add_line(f"⚠️ Could not resolve path: {entry}")

        ordered_paths = [by_name[n] for n in self._PROJECT_NAMES if n in by_name]
        if not ordered_paths:
            self.add_line(
                f'❌ None of {self._PROJECT_NAMES} found in "paths_python_projects". Add them in config.json.'
            )
            return None

        steps: list[OnUpdateHarrixSwissKnife._UpdateStep] = []
        for root in ordered_paths:
            if not root.is_dir():
                self.add_line(f"⚠️ Skip (not a directory): {root}")
                continue

            if (root / ".git").exists():
                dirty = self._git_porcelain(root).strip()
                commit_message: str | None = None
                if dirty:
                    choice = self.get_choice_from_list(
                        "Git: uncommitted changes",
                        f"{root.name}: the working tree has local changes. Choose an action:",
                        [self._GIT_DIRTY_COMMIT, self._GIT_DIRTY_SKIP, self._GIT_DIRTY_CANCEL],
                    )
                    if choice is None or choice == self._GIT_DIRTY_CANCEL:
                        self.add_line("❌ Update cancelled.")
                        self.show_result()
                        return None
                    if choice == self._GIT_DIRTY_SKIP:
                        steps.append(
                            {
                                "kind": "skip",
                                "path": root,
                                "commit_message": None,
                                "skip_reason": "Skipped (dirty tree)",
                            }
                        )
                        continue
                    msg = self.get_text_input(
                        "Commit message",
                        "Enter a commit message for all current changes (or cancel to skip this repo):",
                        default_value="🔧 Modify local changes before update",
                    )
                    if msg is None or not str(msg).strip():
                        self.add_line(f"⚠️ {root.name}: no commit message — skipped.")
                        steps.append(
                            {
                                "kind": "skip",
                                "path": root,
                                "commit_message": None,
                                "skip_reason": "Skipped (no commit message)",
                            }
                        )
                        continue
                    commit_message = str(msg).strip()

                steps.append(
                    {
                        "kind": "git_pull",
                        "path": root,
                        "commit_message": commit_message,
                        "skip_reason": None,
                    }
                )
            else:
                steps.append({"kind": "zip", "path": root, "commit_message": None, "skip_reason": None})

        return steps

    @staticmethod
    def _copy_tree_contents(src: Path, dest: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            target = dest / item.name
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)

    @staticmethod
    def _deep_equal_json(a: object, b: object) -> bool:
        if type(a) is not type(b):
            return False
        if isinstance(a, dict):
            b_dict = cast("dict[str, Any]", b)
            a_dict = cast("dict[str, Any]", a)
            if set(a_dict) != set(b_dict):
                return False
            return all(OnUpdateHarrixSwissKnife._deep_equal_json(a_dict[k], b_dict[k]) for k in a_dict)
        if isinstance(a, list):
            b_list = cast("list[Any]", b)
            a_list = cast("list[Any]", a)
            if len(a_list) != len(b_list):
                return False
            return all(OnUpdateHarrixSwissKnife._deep_equal_json(x, y) for x, y in zip(a_list, b_list, strict=True))
        return a == b

    def _download_https_to_path(self, url: str, dest: Path) -> None:
        self._validate_https_url(url)
        chunk = 256 * 1024
        req = Request(url, headers={"User-Agent": self._GITHUB_UA})  # noqa: S310
        with urlopen(req, timeout=300, context=self._https_context()) as resp, dest.open("wb") as f:  # noqa: S310
            while True:
                block = resp.read(chunk)
                if not block:
                    break
                f.write(block)

    def _fetch_github_default_branch(self, owner: str, repo: str) -> str:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        self._validate_https_url(url)
        req = Request(url, headers=self._github_api_headers())  # noqa: S310
        with urlopen(req, timeout=60, context=self._https_context()) as resp:  # noqa: S310
            data = json.loads(resp.read().decode())
        branch = data.get("default_branch")
        if not isinstance(branch, str) or not branch.strip():
            msg = "Missing default_branch in API response"
            raise ValueError(msg)
        return branch.strip()

    @staticmethod
    def _git_porcelain(repo: Path) -> str:
        p = OnUpdateHarrixSwissKnife._git_run(repo, "status", "--porcelain")
        return p.stdout if p.returncode == 0 else ""

    @staticmethod
    def _git_run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],  # noqa: S607
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    @staticmethod
    def _github_api_headers() -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": OnUpdateHarrixSwissKnife._GITHUB_UA,
        }
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    @staticmethod
    def _https_context() -> ssl.SSLContext:
        ctx = ssl.create_default_context(cafile=certifi.where())
        ssl_cert_file = os.environ.get("SSL_CERT_FILE")
        if ssl_cert_file and Path(ssl_cert_file).is_file():
            ctx.load_verify_locations(cafile=ssl_cert_file)
        return ctx

    @staticmethod
    def _load_json_dict(path: Path) -> tuple[dict[str, Any] | None, str | None]:
        if not path.is_file():
            return None, None
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            return None, str(e)
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            return None, str(e)
        if not isinstance(data, dict):
            return None, "Root JSON value must be an object"
        return cast("dict[str, Any]", data), None

    @staticmethod
    def _restore_config_dir_except_json(backup: Path, dest_config: Path) -> None:
        if not backup.is_dir():
            return
        for f in backup.rglob("*"):
            if not f.is_file():
                continue
            rel = f.relative_to(backup)
            if rel.as_posix() == "config.json":
                continue
            out = dest_config / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, out)

    @staticmethod
    def _top_level_keys_differing(local: dict[str, Any], incoming: dict[str, Any]) -> list[str]:
        out: list[str] = []
        for k, v_loc in local.items():
            if k not in incoming:
                continue
            if not OnUpdateHarrixSwissKnife._deep_equal_json(v_loc, incoming[k]):
                out.append(k)
        return sorted(out)

    @staticmethod
    def _validate_https_url(url: str) -> None:
        if urlparse(url).scheme not in OnUpdateHarrixSwissKnife._ALLOWED_SCHEMES:
            msg = f"URL scheme must be one of {OnUpdateHarrixSwissKnife._ALLOWED_SCHEMES}"
            raise ValueError(msg)

    @ActionBase.handle_exceptions("update Harrix Swiss Knife stack thread completion")
    def _worker_finished(self, merge_tasks: Any) -> None:
        if not isinstance(merge_tasks, list):
            merge_tasks = []

        for task in merge_tasks:
            if not isinstance(task, dict):
                continue
            cfg_path = task.get("config_path")
            if not isinstance(cfg_path, Path):
                continue
            err = task.get("error")
            if err:
                continue
            local_read_error = str(task.get("local_read_error") or "")
            if local_read_error:
                self.add_line(f"⚠️ {cfg_path}: skipping config merge ({local_read_error}).")
                continue
            local = task.get("local")
            incoming = task.get("incoming")
            if not isinstance(incoming, dict):
                continue

            if local is None:
                self._write_config_json_pretty(cfg_path, incoming)
                self.add_line(f"✅ Wrote {cfg_path.name} (no previous local JSON).")
                continue

            if not isinstance(local, dict):
                self.add_line(f"⚠️ {cfg_path}: skipping merge (unexpected local type).")
                continue

            local_dict = local
            diff_keys = self._top_level_keys_differing(local_dict, incoming)
            if not diff_keys:
                merged = self._build_swiss_config_merged(local_dict, incoming, set())
                self._write_config_json_pretty(cfg_path, merged)
                self.add_line(f"✅ Merged {cfg_path} (no conflicting top-level keys).")
                continue

            labels = [f"Keep current value: {k}" for k in diff_keys]
            selected = self.get_checkbox_selection(
                "config.json merge",
                "Checked keys keep your current value. Uncheck to take the value from the repository.",
                labels,
                default_selected=labels,
            )
            if selected is None:
                self.add_line(f"⚠️ {cfg_path}: merge dialog cancelled — left repository version on disk.")
                continue

            key_by_label = {f"Keep current value: {k}": k for k in diff_keys}
            keep_local_keys = {key_by_label[lab] for lab in selected if lab in key_by_label}
            merged = self._build_swiss_config_merged(local_dict, incoming, keep_local_keys)
            self._write_config_json_pretty(cfg_path, merged)
            self.add_line(f"✅ Merged {cfg_path} with your key selection.")

        self.show_toast("Harrix projects update finished")
        self.show_result()

    def _worker_git_pull(self, repo: Path, commit_message: str | None) -> list[OnUpdateHarrixSwissKnife._MergeTask]:
        tasks: list[OnUpdateHarrixSwissKnife._MergeTask] = []
        swiss = repo.name == "harrix-swiss-knife"
        cfg = repo / "config" / "config.json"
        local_data: dict[str, Any] | None = None
        local_read_error = ""
        if swiss:
            local_data, local_err = self._load_json_dict(cfg)
            if local_err:
                self.add_line(f"⚠️ {repo.name}: could not read local config.json: {local_err}")
                local_read_error = local_err

        if commit_message:
            self.add_line(f"🔵 {repo.name}: committing local changes…")
            add_p = self._git_run(repo, "add", "-A")
            if add_p.returncode != 0:
                self.add_line(f"❌ git add failed: {add_p.stderr.strip() or add_p.stdout}")
                return tasks
            commit_p = self._git_run(repo, "commit", "-m", commit_message)
            if commit_p.returncode != 0:
                self.add_line(f"❌ git commit failed: {commit_p.stderr.strip() or commit_p.stdout}")
                return tasks
            self.add_line(f"✅ {repo.name}: committed.")

        self.add_line(f"🔵 {repo.name}: git pull --ff-only…")
        pull_p = self._git_run(repo, "pull", "--ff-only")
        out = (pull_p.stdout + "\n" + pull_p.stderr).strip()
        if out:
            self.add_line(out)
        if pull_p.returncode != 0:
            self.add_line(f"❌ {repo.name}: git pull failed (exit {pull_p.returncode}).")
            return tasks
        self.add_line(f"✅ {repo.name}: pull completed.")

        if swiss:
            incoming, inc_err = self._load_json_dict(cfg)
            if inc_err:
                self.add_line(f"❌ {repo.name}: config.json after pull is invalid: {inc_err}")
                tasks.append(
                    {
                        "config_path": cfg,
                        "local": local_data,
                        "incoming": None,
                        "error": inc_err,
                        "local_read_error": local_read_error,
                    }
                )
            else:
                tasks.append(
                    {
                        "config_path": cfg,
                        "local": local_data,
                        "incoming": incoming,
                        "error": None,
                        "local_read_error": local_read_error,
                    }
                )
        return tasks

    def _worker_run(
        self, steps: list[OnUpdateHarrixSwissKnife._UpdateStep]
    ) -> list[OnUpdateHarrixSwissKnife._MergeTask]:
        owner = str(self.config.get("github_user") or "Harrix").strip() or "Harrix"
        merge_tasks: list[OnUpdateHarrixSwissKnife._MergeTask] = []

        for step in steps:
            path = step["path"]
            if step["kind"] == "skip":
                self.add_line(f"⏭️ {path.name}: {step.get('skip_reason') or 'skipped'}")
                continue
            if step["kind"] == "git_pull":
                merge_tasks.extend(self._worker_git_pull(path, step.get("commit_message")))
            elif step["kind"] == "zip":
                merge_tasks.extend(self._worker_zip_update(path, owner))

        return merge_tasks

    def _worker_zip_swiss_knife(
        self, dest: Path, src_root: Path, cfg: Path, tmp_path: Path
    ) -> list[OnUpdateHarrixSwissKnife._MergeTask]:
        tasks: list[OnUpdateHarrixSwissKnife._MergeTask] = []
        local_data, local_err = self._load_json_dict(cfg)
        if local_err:
            self.add_line(f"⚠️ harrix-swiss-knife: could not read local config.json: {local_err}")

        temp_bak = tmp_path / "temp_bak"
        cfg_bak = tmp_path / "config_bak"
        temp_dir = dest / "temp"
        config_dir = dest / "config"

        if temp_dir.is_dir():
            shutil.copytree(temp_dir, temp_bak, dirs_exist_ok=True)
        if config_dir.is_dir():
            shutil.copytree(config_dir, cfg_bak, dirs_exist_ok=True)

        self.add_line("🔵 harrix-swiss-knife: replacing directory contents (ZIP)…")
        self._clear_directory_children(dest)
        self._copy_tree_contents(src_root, dest)

        if temp_bak.is_dir():
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            shutil.copytree(temp_bak, temp_dir, dirs_exist_ok=True)
            self.add_line("✅ Restored temp/ from backup.")

        if cfg_bak.is_dir():
            config_dir.mkdir(parents=True, exist_ok=True)
            self._restore_config_dir_except_json(cfg_bak, config_dir)
            self.add_line("✅ Restored config/* from backup (except config.json).")

        incoming, inc_err = self._load_json_dict(cfg)
        local_read_error = local_err or ""
        if inc_err:
            self.add_line(f"❌ harrix-swiss-knife: config.json invalid after ZIP: {inc_err}")
            tasks.append(
                {
                    "config_path": cfg,
                    "local": local_data,
                    "incoming": None,
                    "error": inc_err,
                    "local_read_error": local_read_error,
                }
            )
        else:
            tasks.append(
                {
                    "config_path": cfg,
                    "local": local_data,
                    "incoming": incoming,
                    "error": None,
                    "local_read_error": local_read_error,
                }
            )

        self.add_line("✅ harrix-swiss-knife: tree updated from ZIP.")
        return tasks

    def _worker_zip_update(self, dest: Path, owner: str) -> list[OnUpdateHarrixSwissKnife._MergeTask]:
        tasks: list[OnUpdateHarrixSwissKnife._MergeTask] = []
        repo_name = dest.name
        cfg = dest / "config" / "config.json"

        try:
            branch = self._fetch_github_default_branch(owner, repo_name)
        except (OSError, ValueError, URLError, HTTPError, json.JSONDecodeError) as e:
            self.add_line(f"❌ {repo_name}: could not resolve default branch: {e}")
            return tasks

        zip_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/{branch}.zip"
        self.add_line(f"⬇️ {repo_name}: downloading {zip_url} …")

        try:
            with TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                zip_path = tmp_path / f"{repo_name}.zip"
                self._download_https_to_path(zip_url, zip_path)
                extract_root = tmp_path / "extracted"
                extract_root.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(extract_root)
                members = [p for p in extract_root.iterdir() if p.name]
                if len(members) != 1 or not members[0].is_dir():
                    self.add_line(f"❌ {repo_name}: unexpected ZIP layout.")
                    return tasks
                src_root = members[0]

                if repo_name == "harrix-swiss-knife":
                    tasks.extend(self._worker_zip_swiss_knife(dest, src_root, cfg, tmp_path))
                else:
                    self.add_line(f"🔵 {repo_name}: replacing directory contents…")
                    self._clear_directory_children(dest)
                    self._copy_tree_contents(src_root, dest)
                    self.add_line(f"✅ {repo_name}: updated from ZIP.")
        except (OSError, ValueError, URLError, HTTPError) as e:
            self.add_line(f"❌ {repo_name}: ZIP update failed: {e}")

        return tasks

    @staticmethod
    def _write_config_json_pretty(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        path.write_text(text, encoding="utf-8")

    class _UpdateStep(TypedDict):
        kind: Literal["git_pull", "zip", "skip"]
        path: Path
        commit_message: str | None
        skip_reason: str | None

    class _MergeTask(TypedDict):
        config_path: Path
        local: dict[str, Any] | None
        incoming: dict[str, Any] | None
        error: str | None
        local_read_error: str


class OnUvUpdate(ActionBase):
    """Update uv package manager to its latest version.

    Tries ``uv self update`` (standalone uv only), then on Windows ``winget upgrade`` /
    ``winget install`` for ``astral-sh.uv``, then ``python -m pip install --upgrade uv``
    (prefers ``python.exe`` over ``pythonw.exe`` when the GUI launcher has no pip).
    """

    icon = "📥"
    title = "Update uv"

    _UV_SELF_UPDATE_BLOCKED = (
        "Self-update is only available for uv binaries installed via the standalone installation scripts"
    )

    @ActionBase.handle_exceptions("uv update")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Update uv package manager to its latest version."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("uv update thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        result = h.dev.run_command("uv self update")
        blocks: list[str] = [f"=== uv self update ===\n{result}"]

        if not isinstance(result, str) or self._UV_SELF_UPDATE_BLOCKED not in result:
            return result

        if sys.platform == "win32" and shutil.which("winget"):
            upgrade = (
                "winget upgrade -e --id astral-sh.uv --source winget "
                "--accept-package-agreements --accept-source-agreements --silent"
            )
            winget_out = h.dev.run_command(upgrade)
            blocks.append(f"\n=== winget upgrade (astral-sh.uv) ===\n{winget_out}")
            if "no installed package" in winget_out.lower():
                install = (
                    "winget install -e --id astral-sh.uv --source winget "
                    "--accept-package-agreements --accept-source-agreements --silent"
                )
                blocks.append(f"\n=== winget install (astral-sh.uv) ===\n{h.dev.run_command(install)}")

        pip_sections = [
            f"--- {py_exe} ---\n{self._pip_install_upgrade_uv_log(py_exe)}"
            for py_exe in self._python_candidates_for_pip()
        ]
        blocks.append("\n=== pip (venv / current interpreters) ===\n" + "\n\n".join(pip_sections))

        blocks.append(
            "\n=== If uv is still not updated ===\n"
            "Install the standalone binary: https://docs.astral.sh/uv/getting-started/installation/\n"
            "Or run: powershell -NoProfile -ExecutionPolicy Bypass -Command "
            "'irm https://astral.sh/uv/install.ps1 | iex'"
        )
        return "\n".join(blocks)

    @ActionBase.handle_exceptions("uv update thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("UV update steps finished (see output)")
        self.add_line(result)
        self.show_result()

    def _pip_install_upgrade_uv_log(self, py_exe: Path) -> str:
        """Run pip upgrade for uv; bootstrap pip with ensurepip when missing."""
        quoted = f'"{py_exe}"'
        pip_cmd = f"{quoted} -m pip install --upgrade uv"
        lines = [pip_cmd]
        pip_out = h.dev.run_command(pip_cmd)
        lines.append(pip_out)
        if "No module named pip" in pip_out:
            ensure_cmd = f"{quoted} -m ensurepip --upgrade"
            lines.append(ensure_cmd)
            lines.append(h.dev.run_command(ensure_cmd))
            lines.append(pip_cmd)
            lines.append(h.dev.run_command(pip_cmd))
        return "\n".join(lines)

    @staticmethod
    def _python_candidates_for_pip() -> list[Path]:
        """Return interpreter paths to try for ``python -m pip`` (GUI apps often run as pythonw.exe)."""
        exe = Path(sys.executable).resolve()
        candidates: list[Path] = []
        if exe.name.lower() == "pythonw.exe":
            console = exe.with_name("python.exe")
            if console.is_file():
                candidates.append(console)
        candidates.append(exe)
        seen: set[Path] = set()
        unique: list[Path] = []
        for p in candidates:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        return unique


class OnViewRecentActionLogs(ActionBase):
    """Browse and open text logs from recent action runs (``temp/action_output``)."""

    icon = "📋"
    title = "View recent action logs"

    @ActionBase.handle_exceptions("view recent action logs")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open split-view browser: file list and live preview; sync main window when selection changes."""
        paths = list_recent_action_output_files(non_empty_only=True)
        if not paths:
            self.add_line("No action log files found in temp/action_output.")
            self.show_result()
            return

        entries: list[tuple[Path, str]] = []
        for path in paths:
            stat = path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime, tz=UTC).astimezone().strftime("%Y-%m-%d %H:%M:%S")
            entries.append((path, f"{mtime} · {self._format_byte_size(stat.st_size)}"))

        def sync_main_window(path: Path) -> None:
            if self._output_bus is not None:
                self._output_bus.set_active_output(path)

        self.dialogs.show_action_output_log_browser(entries, on_file_selected=sync_main_window)

    def _format_byte_size(self, num_bytes: int) -> str:
        """Return a short human-readable size for file listings."""
        bytes_per_kib = 1024
        if num_bytes < bytes_per_kib:
            return f"{num_bytes} B"
        return f"{num_bytes / bytes_per_kib:.1f} KiB"
