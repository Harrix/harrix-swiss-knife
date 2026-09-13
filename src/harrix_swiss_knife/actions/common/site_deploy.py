"""Commit a generated static site and push it to a Git remote."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from harrix_swiss_knife.actions.common.subprocess_run import run_argv_output

if TYPE_CHECKING:
    from pathlib import Path

DEPLOY_BRANCH = "main"
DEPLOY_COMMIT_MESSAGE = "⬆️ Update generated site"
DEPLOY_REMOTE_NAME = "production"
_FALLBACK_GIT_EMAIL = "harrix-swiss-knife@local"
_FALLBACK_GIT_NAME = "Harrix Swiss Knife"
_GIT_PUSH_TIMEOUT = 600.0
_GIT_TIMEOUT = 120.0


def deploy_generated_site(
    html_folder: Path,
    *,
    remote_url: str | None = None,
    remote_name: str = DEPLOY_REMOTE_NAME,
    branch: str = DEPLOY_BRANCH,
    commit_message: str = DEPLOY_COMMIT_MESSAGE,
) -> tuple[bool, str]:
    """Commit generated HTML and push it to the production remote.

    Args:

    - `html_folder` (`Path`): Site output folder (Git work tree).
    - `remote_url` (`str | None`): URL for `remote_name`. Added or updated when set.
    - `remote_name` (`str`): Git remote name. Defaults to `production`.
    - `branch` (`str`): Branch to commit and push. Defaults to `main`.
    - `commit_message` (`str`): Commit subject when there are changes.

    Returns:

    - `tuple[bool, str]`: Success flag and combined log text.

    """
    folder = html_folder.expanduser().resolve()
    lines: list[str] = []
    remote = (remote_url or "").strip()

    if not folder.is_dir():
        return False, f"HTML output folder not found: {folder}"

    if not is_git_work_tree(folder):
        if not remote:
            return False, f"Not a Git repository: {folder}"
        if not _log_git(lines, folder, "init", "-b", branch):
            if not _log_git(lines, folder, "init"):
                return False, _join_log(lines)
            if not _log_git(lines, folder, "checkout", "-b", branch):
                return False, _join_log(lines)

    if remote:
        if not _ensure_remote(lines, folder, remote_name, remote):
            return False, _join_log(lines)
    else:
        ok, _current = _git(folder, "remote", "get-url", remote_name)
        if not ok:
            lines.append(f"No deploy remote `{remote_name}` configured.")
            return False, _join_log(lines)

    if not _log_git(lines, folder, "add", "-A"):
        return False, _join_log(lines)

    ok, porcelain = _git(folder, "status", "--porcelain")
    if not ok:
        lines.append(porcelain)
        return False, _join_log(lines)
    if not porcelain.strip():
        lines.append("No changes to commit.")
        return True, _join_log(lines)

    _ensure_git_identity(folder)
    if not _log_git(lines, folder, "-c", "commit.gpgsign=false", "commit", "-m", commit_message):
        return False, _join_log(lines)

    if not _log_git(lines, folder, "push", "-u", remote_name, branch, timeout=_GIT_PUSH_TIMEOUT):
        return False, _join_log(lines)
    lines.append(f"Pushed `{branch}` to `{remote_name}`.")
    return True, _join_log(lines)


def is_git_work_tree(path: Path) -> bool:
    """Return `True` when `path` is a Git working tree."""
    if not path.is_dir():
        return False
    ok, output = _git(path, "rev-parse", "--is-inside-work-tree", timeout=30.0)
    return ok and "true" in output.split()


def should_offer_deploy(html_folder: Path, deploy_remote: str | None) -> bool:
    """Return `True` when the action should ask to publish the generated site."""
    remote = (deploy_remote or "").strip()
    return bool(remote) or is_git_work_tree(html_folder)


def _ensure_git_identity(folder: Path) -> None:
    ok, _output = _git(folder, "config", "--get", "user.email")
    if ok:
        return
    _git(folder, "config", "user.email", _FALLBACK_GIT_EMAIL)
    _git(folder, "config", "user.name", _FALLBACK_GIT_NAME)


def _ensure_remote(lines: list[str], folder: Path, remote_name: str, remote_url: str) -> bool:
    ok, current = _git(folder, "remote", "get-url", remote_name)
    if ok:
        existing = current.strip().splitlines()[-1].strip() if current.strip() else ""
        if existing == remote_url:
            lines.append(f"Remote `{remote_name}` already points to {remote_url}")
            return True
        return _log_git(lines, folder, "remote", "set-url", remote_name, remote_url)
    return _log_git(lines, folder, "remote", "add", remote_name, remote_url)


def _git(folder: Path, *args: str, timeout: float = _GIT_TIMEOUT) -> tuple[bool, str]:
    code, output = run_argv_output(
        ["git", *args],
        cwd=folder,
        env=_git_env(),
        timeout=timeout,
    )
    return code == 0, output.strip()


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes"
    return env


def _join_log(parts: list[str]) -> str:
    return "\n".join(part.strip() for part in parts if part and part.strip())


def _log_git(lines: list[str], folder: Path, *args: str, timeout: float = _GIT_TIMEOUT) -> bool:
    ok, output = _git(folder, *args, timeout=timeout)
    label = " ".join(("git", *args))
    if output:
        lines.append(f"{label}\n{output}")
    else:
        lines.append(label)
    return ok
