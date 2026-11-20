"""Low-level Git subprocess helpers (no `actions.files` imports)."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def git_porcelain(repo: Path) -> str:
    """Return `git status --porcelain` output for `repo`."""
    proc = git_run(repo, "status", "--porcelain")
    return proc.stdout if proc.returncode == 0 else ""


def git_run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run a Git command in `cwd` and return the completed process."""
    return subprocess.run(
        ["git", *args],  # noqa: S607
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
