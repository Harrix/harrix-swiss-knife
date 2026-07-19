r"""Project path helpers (CWD-independent).

The application frequently needs paths relative to the repository root (e.g. config files).
These helpers centralize path construction to avoid repeating string literals like
`config/config.json` and to make behavior independent of the current working directory.

Action output logs normally live under `<project>/temp/action_output`. If the project root is
not writable (for example a clone under `Program Files`), logs go to a per-user folder
(`%LOCALAPPDATA%\\HarrixSwissKnife\\action_output` on Windows). Override with env
`HSK_ACTION_OUTPUT_DIR`.
"""

from __future__ import annotations

import contextlib
import os
import re
import shutil
import sys
import uuid
from functools import lru_cache
from pathlib import Path

import harrix_pylib as h

# Keep at most this many newest `*.txt` files under `action_output` (see `prune_action_output_dir`).
DEFAULT_MAX_ACTION_OUTPUT_FILES = 80

# Max files offered when browsing recent action logs in the UI.
DEFAULT_RECENT_ACTION_OUTPUT_LIST_LIMIT = 50

# Max length for the class-name portion of an action output filename stem.
_MAX_ACTION_CLASS_STEM_LEN = 80

# Subdirectories under `temp/` that are kept (contents cleared) by `clear_temp_folder`.
TEMP_RESERVED_DIR_NAMES = frozenset({"images", "optimized_images"})


def clear_directory_contents(directory: Path) -> None:
    """Remove all files and subdirectories inside `directory`; the directory itself remains."""
    if not directory.is_dir():
        return
    for child in list(directory.iterdir()):
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
        else:
            with contextlib.suppress(OSError):
                child.unlink()


def clear_temp_folder(temp_dir: Path | None = None) -> list[str]:
    """Clear project `temp/`: empty `images` and `optimized_images`; remove everything else.

    Creates `temp/` and reserved subdirectories when missing. Returns human-readable log lines.
    """
    root = temp_dir if temp_dir is not None else get_project_root() / "temp"
    root.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    for child in list(root.iterdir()):
        if child.name in TEMP_RESERVED_DIR_NAMES:
            if child.is_dir():
                clear_directory_contents(child)
                lines.append(f"Folder `{child}` is clean.")
            else:
                with contextlib.suppress(OSError):
                    child.unlink()
                lines.append(f"Removed `{child}` (reserved name was not a directory).")
            continue
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
            lines.append(f"Removed folder `{child}`.")
        else:
            with contextlib.suppress(OSError):
                child.unlink()
            lines.append(f"Removed file `{child}`.")

    for name in sorted(TEMP_RESERVED_DIR_NAMES):
        reserved = root / name
        if not reserved.is_dir():
            reserved.mkdir(parents=True, exist_ok=True)
            lines.append(f"Created folder `{reserved}`.")

    if not lines:
        lines.append(f"Folder `{root}` is already clean.")
    return lines


@lru_cache(maxsize=1)
def get_action_output_dir() -> Path:
    """Return directory for per-run action log files (under project `temp/` when writable).

    Uses environment variable `HSK_ACTION_OUTPUT_DIR` when set. Otherwise prefers
    `<project>/temp/action_output` if the project `temp` directory can be created and
    written to; falls back to a per-user data directory when the tree is read-only.

    Result is cached for the process lifetime (startup builds many menu actions).
    """
    override = os.environ.get("HSK_ACTION_OUTPUT_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()

    root = get_project_root()
    project_temp = root / "temp"
    if _can_use_project_temp_dir(project_temp):
        return project_temp / "action_output"
    return _default_user_action_output_dir()


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
    """Return up to `limit` newest `*.txt` paths under the action output dir (newest first).

    Excludes `pending.txt` (placeholder name before a run assigns a real path).
    When `non_empty_only` is `True`, only files with size greater than zero bytes are included.
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
    """Return a new unique path `{ClassName}_{uuid12}.txt` under `output_dir`."""
    stem = _sanitize_action_class_stem(class_name)
    suffix = uuid.uuid4().hex[:12]
    return output_dir / f"{stem}_{suffix}.txt"


def prune_action_output_dir(
    directory: Path | None = None,
    *,
    max_files: int = DEFAULT_MAX_ACTION_OUTPUT_FILES,
) -> None:
    """Delete oldest `*.txt` files in the action output dir, keeping `max_files` newest by mtime."""
    root = directory if directory is not None else get_action_output_dir()
    if not root.is_dir():
        return
    paths = sorted(root.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in paths[max_files:]:
        with contextlib.suppress(OSError):
            path.unlink()


def _can_use_project_temp_dir(temp_dir: Path) -> bool:
    """Return `True` if `temp_dir` can be created and is writable (probe file)."""
    try:
        temp_dir.mkdir(parents=True, exist_ok=True)
        probe = temp_dir / ".hsk_write_probe"
        probe.write_text("", encoding="utf8")
        probe.unlink()
    except OSError:
        return False
    else:
        return True


def _default_user_action_output_dir() -> Path:
    """Writable per-user location when the repo tree cannot host `temp/action_output`."""
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        if not local:
            local = str(Path.home() / "AppData" / "Local")
        return Path(local) / "HarrixSwissKnife" / "action_output"
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    return base / "harrix-swiss-knife" / "action_output"


def _sanitize_action_class_stem(class_name: str) -> str:
    """Return a filesystem-safe stem fragment from an action class name."""
    s = re.sub(r"[^A-Za-z0-9_-]+", "_", class_name).strip("_")
    if not s:
        s = "Action"
    return s[:_MAX_ACTION_CLASS_STEM_LEN]
