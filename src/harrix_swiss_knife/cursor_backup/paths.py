"""Resolve Cursor profile and project `.cursor` locations."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from harrix_swiss_knife.browser_bookmarks.paths import is_process_running

_CURSOR_PROCESS = "Cursor.exe" if sys.platform == "win32" else "Cursor"
_WIN_FILE_URI_DRIVE_MIN_LEN = 3
_SKIP_DOT_CURSOR_NAMES = frozenset(
    {
        "extensions",  # packed as its own part
        "browser-logs",
        "ai-tracking",
    }
)


def cursor_app_data_dir() -> Path:
    """Return `%APPDATA%/Cursor` (or the OS equivalent)."""
    return _roaming_app_data() / "Cursor"


def cursor_dot_dir() -> Path:
    """Return `~/.cursor`."""
    return Path.home() / ".cursor"


def cursor_running() -> bool:
    """Return whether the Cursor process appears to be running."""
    if sys.platform == "win32":
        return is_process_running(_CURSOR_PROCESS)
    return bool(is_process_running(_CURSOR_PROCESS)) or bool(is_process_running("cursor"))


def cursor_user_dir() -> Path:
    """Return the Cursor `User` profile directory (settings, chats, workspaceStorage)."""
    return cursor_app_data_dir() / "User"


def discover_project_cursor_dirs(workspace_storage: Path | None = None) -> list[Path]:
    """Return unique project `.cursor` folders from `workspaceStorage` `workspace.json` files."""
    root = workspace_storage if workspace_storage is not None else cursor_user_dir() / "workspaceStorage"
    if not root.is_dir():
        return []
    found: list[Path] = []
    seen: set[Path] = set()
    try:
        children = sorted(root.iterdir(), key=lambda path: path.name.casefold())
    except OSError:
        return []
    for entry in children:
        if not entry.is_dir():
            continue
        meta = entry / "workspace.json"
        project = _project_path_from_workspace_json(meta)
        if project is None:
            continue
        cursor_dir = project / ".cursor"
        try:
            resolved = cursor_dir.resolve()
        except OSError:
            continue
        if resolved in seen or not cursor_dir.is_dir():
            continue
        seen.add(resolved)
        found.append(cursor_dir)
    return found


def iter_dot_cursor_entries() -> list[Path]:
    """Return top-level paths under `~/.cursor` for the home `.cursor` backup part.

    Skips `extensions` (separate backup part) and noisy log/tracking folders.

    """
    root = cursor_dot_dir()
    if not root.is_dir():
        return []
    try:
        children = sorted(root.iterdir(), key=lambda path: path.name.casefold())
    except OSError:
        return []
    return [child for child in children if child.name not in _SKIP_DOT_CURSOR_NAMES]


def json_safe(value: Any) -> Any:
    """Return a JSON-serializable mirror of simple values (for manifests)."""
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    return value


def _path_from_file_uri(uri: str) -> Path | None:
    if uri.startswith("file:"):
        parsed = urlparse(uri)
        path_text = unquote(parsed.path or "")
        if (
            sys.platform == "win32"
            and path_text.startswith("/")
            and len(path_text) >= _WIN_FILE_URI_DRIVE_MIN_LEN
            and path_text[2] == ":"
        ):
            path_text = path_text[1:]
        elif sys.platform == "win32" and parsed.netloc:
            path_text = f"//{parsed.netloc}{path_text}"
        return Path(path_text) if path_text else None
    try:
        return Path(uri)
    except (OSError, TypeError, ValueError):
        return None


def _project_path_from_workspace_json(meta: Path) -> Path | None:
    if not meta.is_file():
        return None
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    folder = data.get("folder")
    if isinstance(folder, str) and folder.strip():
        return _path_from_file_uri(folder.strip())
    workspace = data.get("workspace")
    if isinstance(workspace, str) and workspace.strip():
        # Multi-root `.code-workspace` file — use its parent as the project root.
        workspace_file = _path_from_file_uri(workspace.strip())
        return workspace_file.parent if workspace_file is not None else None
    return None


def _roaming_app_data() -> Path:
    """Return the OS roaming/config directory (same idea as VS Code-family editors)."""
    if sys.platform == "win32":
        roaming = os.environ.get("APPDATA")
        if roaming:
            return Path(roaming)
        return Path.home() / "AppData" / "Roaming"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    return Path(xdg) if xdg else Path.home() / ".config"
