"""Install-root path resolution (mirrors PowerShell helpers)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from harrix_swiss_knife.installer.constants import REPO_NAMES

if sys.platform == "win32":
    import winreg
else:  # pragma: no cover
    winreg = None  # type: ignore[assignment]

_REPO_ROOT_PARENT_DEPTH = 4

# Windows rejects file paths longer than this unless long-path support is on.
MAX_WINDOWS_PATH = 259
# Deepest relative path seen inside a synced `.venv` (torch license tree, PySide6 qml objects).
DEEPEST_VENV_RELATIVE = 200
_LONG_PATHS_KEY = r"SYSTEM\CurrentControlSet\Control\FileSystem"
_LONG_PATHS_VALUE = "LongPathsEnabled"

# Preferred bundle parent: C:\harrix-swiss-knife\{harrix-swiss-knife,harrix-pylib,harrix-pyssg}
_FALLBACK_CREATE_PARENT = Path(r"C:\harrix-swiss-knife")


def default_install_root_parent() -> Path:
    r"""Prefer existing GitHub folders, else create `C:\harrix-swiss-knife`.

    Order:

    1. `D:\GitHub`, `C:\GitHub`, `Documents\GitHub` when already present
    2. Create `C:\harrix-swiss-knife` (admin installer)
    3. Fall back to `%USERPROFILE%\harrix-swiss-knife`

    """
    for candidate in _preferred_parent_candidates():
        if candidate.is_dir():
            return candidate.resolve()
    try:
        _FALLBACK_CREATE_PARENT.mkdir(parents=True, exist_ok=True)
        return _FALLBACK_CREATE_PARENT.resolve()
    except OSError:
        bundle = Path.home() / "harrix-swiss-knife"
        bundle.mkdir(parents=True, exist_ok=True)
        return bundle.resolve()


def enable_long_paths() -> bool:
    """Turn on system-wide long-path support. Needs admin rights; returns whether it worked."""
    if winreg is None:
        return False
    try:
        with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, _LONG_PATHS_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, _LONG_PATHS_VALUE, 0, winreg.REG_DWORD, 1)
    except OSError:
        return False
    return True


def is_under_program_files(path: Path) -> bool:
    """Return whether `path` is under Program Files (not recommended for this app)."""
    program_files = (
        os.environ.get("PROGRAMFILES") or os.environ.get("ProgramFiles") or r"C:\Program Files"  # noqa: SIM112
    )
    return str(path.resolve()).lower().startswith(program_files.lower())


def long_paths_enabled() -> bool:
    """Return whether Windows accepts paths longer than `MAX_WINDOWS_PATH`."""
    if winreg is None:
        return True
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _LONG_PATHS_KEY) as key:
            value, _ = winreg.QueryValueEx(key, _LONG_PATHS_VALUE)
    except OSError:
        return False
    try:
        return bool(int(value))
    except (TypeError, ValueError):
        return False


def normalize_install_root(selected: Path) -> Path:
    r"""Accept a parent for the three repos; do not nest under an extra `GitHub`.

    Kept as-is when the leaf is `GitHub` or `harrix-swiss-knife` (including
    `C:\harrix-swiss-knife` on the system drive). Otherwise append `GitHub` only
    for generic drive roots such as `D:\` so sibling repos still share a folder.

    """
    p = selected.resolve()
    leaf = p.name.lower()
    if leaf in {"github", "harrix-swiss-knife"}:
        p.mkdir(parents=True, exist_ok=True)
        return p
    # Bare drive root like `D:\` → `D:\GitHub`
    if len(p.parts) <= 1:
        gh = p / "GitHub"
        gh.mkdir(parents=True, exist_ok=True)
        return gh.resolve()
    # Any other explicit folder is used as the install parent as chosen.
    p.mkdir(parents=True, exist_ok=True)
    return p


def venv_path_headroom(install_root: Path) -> int:
    """Characters left for files inside a repo `.venv` when installing into `install_root`.

    Compare the result with `DEEPEST_VENV_RELATIVE` to see whether `uv sync` can
    write every packaged file without long-path support.

    """
    longest_repo = max(len(name) for name in REPO_NAMES)
    return MAX_WINDOWS_PATH - len(str(install_root).rstrip("\\/")) - 1 - longest_repo


def _preferred_parent_candidates() -> list[Path]:
    """Return preferred install parents in priority order (existing dirs only)."""
    docs = Path.home() / "Documents" / "GitHub"
    return [
        Path(r"D:\GitHub"),
        Path(r"C:\GitHub"),
        docs,
        Path(r"C:\harrix-swiss-knife"),
    ]


# Back-compat alias used by older tests.
_github_parent_candidates = _preferred_parent_candidates
