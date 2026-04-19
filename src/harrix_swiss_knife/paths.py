"""Project path helpers (CWD-independent).

The application frequently needs paths relative to the repository root (e.g. config files).
These helpers centralize path construction to avoid repeating string literals like
`config/config.json` and to make behavior independent of the current working directory.
"""

from __future__ import annotations

import contextlib
import re
import uuid
from pathlib import Path  # noqa: TC003

import harrix_pylib as h

# Keep at most this many newest ``*.txt`` files under ``action_output`` (see ``prune_action_output_dir``).
DEFAULT_MAX_ACTION_OUTPUT_FILES = 80

# Max files offered when browsing recent action logs in the UI.
DEFAULT_RECENT_ACTION_OUTPUT_LIST_LIMIT = 50

# Max length for the class-name portion of an action output filename stem.
_MAX_ACTION_CLASS_STEM_LEN = 80


def get_action_output_dir() -> Path:
    """Return directory for per-run action log files (under project temp/)."""
    return get_project_root() / "temp" / "action_output"


def get_config_path() -> Path:
    """Return absolute path to main config file."""
    return get_project_root() / "config" / "config.json"


def get_config_path_str() -> str:
    """Return config path as a string (for APIs expecting str)."""
    return str(get_config_path())


def get_project_root() -> Path:
    """Return project root directory as detected by harrix_pylib."""
    return h.dev.get_project_root()


def get_temp_config_path() -> Path:
    """Return absolute path to temp config file."""
    return get_project_root() / "config" / "config-temp.json"


def get_temp_config_path_str() -> str:
    """Return temp config path as a string (for APIs expecting str)."""
    return str(get_temp_config_path())


def list_recent_action_output_files(
    directory: Path | None = None,
    *,
    limit: int = DEFAULT_RECENT_ACTION_OUTPUT_LIST_LIMIT,
    non_empty_only: bool = False,
) -> list[Path]:
    """Return up to ``limit`` newest ``*.txt`` paths under the action output dir (newest first).

    Excludes ``pending.txt`` (placeholder name before a run assigns a real path).
    When ``non_empty_only`` is true, only files with size greater than zero bytes are included.
    """
    root = directory if directory is not None else get_action_output_dir()
    if not root.is_dir():
        return []
    paths = [p for p in root.glob("*.txt") if p.is_file() and p.name != "pending.txt"]
    paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    if non_empty_only:
        paths = [p for p in paths if p.stat().st_size > 0]
    return paths[:limit]


def new_action_output_file_path(output_dir: Path, class_name: str) -> Path:
    """Return a new unique path ``{ClassName}_{uuid12}.txt`` under ``output_dir``."""
    stem = _sanitize_action_class_stem(class_name)
    suffix = uuid.uuid4().hex[:12]
    return output_dir / f"{stem}_{suffix}.txt"


def prune_action_output_dir(
    directory: Path | None = None,
    *,
    max_files: int = DEFAULT_MAX_ACTION_OUTPUT_FILES,
) -> None:
    """Delete oldest ``*.txt`` files in the action output dir, keeping ``max_files`` newest by mtime."""
    root = directory if directory is not None else get_action_output_dir()
    if not root.is_dir():
        return
    paths = sorted(root.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in paths[max_files:]:
        with contextlib.suppress(OSError):
            path.unlink()


def _sanitize_action_class_stem(class_name: str) -> str:
    """Return a filesystem-safe stem fragment from an action class name."""
    s = re.sub(r"[^A-Za-z0-9_-]+", "_", class_name).strip("_")
    if not s:
        s = "Action"
    return s[:_MAX_ACTION_CLASS_STEM_LEN]
