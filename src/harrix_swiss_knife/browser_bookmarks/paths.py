"""Resolve Chromium Bookmarks paths, snapshot location, and running browsers."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

_CHROME_PROCESS = "chrome.exe"
_YANDEX_PROCESS = "browser.exe"


def backup_root() -> Path:
    """Directory for timestamped Bookmarks backups."""
    return harrix_swiss_knife_data_dir() / "browser_bookmarks_backups"


def default_chrome_bookmarks_path() -> Path:
    """Default Chrome `Bookmarks` file for the Default profile."""
    return local_app_data() / "Google" / "Chrome" / "User Data" / "Default" / "Bookmarks"


def default_yandex_bookmarks_path() -> Path:
    """Default Yandex Browser `Bookmarks` file for the Default profile."""
    return local_app_data() / "Yandex" / "YandexBrowser" / "User Data" / "Default" / "Bookmarks"


def harrix_swiss_knife_data_dir() -> Path:
    """Per-user data directory outside the Git repo."""
    if sys.platform == "win32":
        return local_app_data() / "HarrixSwissKnife"
    return local_app_data() / "harrix-swiss-knife"


def is_chrome_running() -> bool:
    """Return whether Google Chrome is running."""
    return is_process_running(_CHROME_PROCESS)


def is_process_running(image_name: str) -> bool:
    """Return whether a Windows process with `image_name` is running."""
    if sys.platform != "win32":
        return False
    tasklist = shutil.which("tasklist")
    if not tasklist:
        return False
    result = subprocess.run(
        [tasklist, "/FI", f"IMAGENAME eq {image_name}", "/NH"],
        capture_output=True,
        text=True,
        check=False,
    )
    return image_name.casefold() in (result.stdout or "").casefold()


def is_yandex_running() -> bool:
    """Return whether Yandex Browser (`browser.exe`) is running."""
    return is_process_running(_YANDEX_PROCESS)


def local_app_data() -> Path:
    """Return the Windows LocalAppData directory (or a home fallback)."""
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        if not local:
            local = str(Path.home() / "AppData" / "Local")
        return Path(local)
    xdg = os.environ.get("XDG_DATA_HOME")
    return Path(xdg) if xdg else Path.home() / ".local" / "share"


def running_browser_names() -> list[str]:
    """Return display names of browsers that are currently running."""
    names: list[str] = []
    if is_chrome_running():
        names.append("Google Chrome")
    if is_yandex_running():
        names.append("Yandex Browser")
    return names


def snapshot_path() -> Path:
    """Path to the sync snapshot JSON (never under the Git repo)."""
    return harrix_swiss_knife_data_dir() / "browser_bookmarks_sync.json"
