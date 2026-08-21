"""Locate the `uv` executable and refresh process PATH (Windows-aware)."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    import winreg
else:  # pragma: no cover
    winreg = None  # type: ignore[assignment]


def find_uv_exe() -> Path | None:
    """Locate the `uv` executable on PATH or common install locations.

    Installer and standalone installs often put `uv` in `~/.local/bin`. Tray apps
    launched from Explorer shortcuts may not see an updated user PATH, so this
    also checks well-known directories.

    """
    which = shutil.which("uv")
    if which:
        return Path(which)

    home = Path.home()
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    candidates = [
        home / ".local" / "bin" / ("uv.exe" if sys.platform == "win32" else "uv"),
        local / "Programs" / "uv" / "uv.exe",
        local / "Microsoft" / "WinGet" / "Links" / "uv.exe",
        local / "Microsoft" / "WindowsApps" / "uv.exe",
        _program_files() / "uv" / "uv.exe",
        _program_files_x86() / "uv" / "uv.exe",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def refresh_path() -> None:
    r"""Refresh process PATH from the environment and Windows registry.

    Expands `%VAR%` segments from registry values so entries like
    `%USERPROFILE%\.local\bin` resolve for `shutil.which` / subprocess.

    """
    machine = os.environ.get("Path", "")  # noqa: SIM112
    user = ""
    if winreg is not None:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                user, _ = winreg.QueryValueEx(key, "Path")
        except OSError:
            user = os.environ.get("Path", "")  # noqa: SIM112
    else:
        user = os.environ.get("Path", "")  # noqa: SIM112
    parts = [p for p in (machine, user) if p]
    if winreg is not None:
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            ) as key:
                machine_reg, _ = winreg.QueryValueEx(key, "Path")
                parts = [machine_reg, user]
        except OSError:
            pass
    combined = ";".join(parts)
    if sys.platform == "win32":
        combined = os.path.expandvars(combined)
    os.environ["Path"] = combined  # noqa: SIM112


def _program_files() -> Path:
    return Path(
        os.environ.get("PROGRAMFILES") or os.environ.get("ProgramFiles") or r"C:\Program Files"  # noqa: SIM112
    )


def _program_files_x86() -> Path:
    return Path(
        os.environ.get("PROGRAMFILES(X86)")
        or os.environ.get("ProgramFiles(x86)")  # noqa: SIM112
        or r"C:\Program Files (x86)"
    )
