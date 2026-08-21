"""Ensure a Git repository next to a tracker SQLite database."""

from __future__ import annotations

import logging
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

from harrix_swiss_knife.actions.common.subprocess_run import run_argv_output

logger = logging.getLogger(__name__)

_FALLBACK_GIT_NAME = "Harrix Swiss Knife"
_FALLBACK_GIT_EMAIL = "harrix-swiss-knife@local"


def ensure_sqlite_folder_git_repo(db_path: Path) -> bool:
    """Create a Git repo in the database folder and commit the SQLite file if needed.

    When the folder already has `.git`, do nothing. Used both after creating a
    database from `recover.sql` and when opening an existing file.

    Args:

    - `db_path` (`Path`): Path to the SQLite file.

    Returns:

    - `bool`: `True` when a new repository was created and the file was committed.

    """
    resolved = Path(db_path).expanduser().resolve()
    if not resolved.is_file():
        return False
    folder = resolved.parent
    if not folder.is_dir() or (folder / ".git").exists():
        return False
    if shutil.which("git") is None:
        logger.warning("git is not on PATH; skipped repository for %s", folder)
        return False

    code, output = run_argv_output(["git", "init"], cwd=folder)
    if code != 0:
        logger.warning("git init failed in %s: %s", folder, output)
        return False

    _ensure_git_identity(folder)
    code, output = run_argv_output(["git", "add", "--", resolved.name], cwd=folder)
    if code != 0:
        logger.warning("git add failed for %s: %s", resolved, output)
        return False

    message = sqlite_folder_git_commit_message(resolved)
    code, output = run_argv_output(["git", "commit", "-m", message], cwd=folder)
    if code != 0:
        logger.warning("git commit failed in %s: %s", folder, output)
        return False

    logger.info("Created git repository in %s (%s)", folder, message)
    return True


def sqlite_folder_git_commit_message(db_path: Path, *, on: date | None = None) -> str:
    """Return the initial commit subject for a tracker SQLite file.

    Args:

    - `db_path` (`Path`): Path to the SQLite file (only the filename is used).
    - `on` (`date | None`): Date in the subject. Defaults to today.

    Returns:

    - `str`: Subject with Add prefix, filename, and ISO date.

    """
    day = on or datetime.now(tz=UTC).astimezone().date()
    return f"➕ Add {Path(db_path).name} ({day.isoformat()})"  # noqa: RUF001


def _ensure_git_identity(folder: Path) -> None:
    """Set local `user.name` / `user.email` when Git has no identity."""
    if not _git_config_value(folder, "user.name"):
        run_argv_output(["git", "config", "user.name", _FALLBACK_GIT_NAME], cwd=folder)
    if not _git_config_value(folder, "user.email"):
        run_argv_output(["git", "config", "user.email", _FALLBACK_GIT_EMAIL], cwd=folder)


def _git_config_value(folder: Path, key: str) -> str:
    """Return a Git config value from `folder`, or empty when unset."""
    code, output = run_argv_output(["git", "config", "--get", key], cwd=folder)
    return output.strip() if code == 0 else ""
