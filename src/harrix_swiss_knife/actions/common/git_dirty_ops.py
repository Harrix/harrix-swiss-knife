"""Dirty-repo file lists, selective commit, and non-blocking GitHub Desktop open."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from harrix_swiss_knife.actions.common.git_cmd import git_porcelain, git_run

_PORCELAIN_MIN_LEN = 4
_QUOTED_MIN_LEN = 2


@dataclass(frozen=True, slots=True)
class ChangedFile:
    """One path from `git status --porcelain`."""

    path: str
    status: str


@dataclass(frozen=True, slots=True)
class DirtyRepoStatus:
    """Current dirty state for one repository."""

    path: Path
    files: tuple[ChangedFile, ...]

    @property
    def changed_count(self) -> int:
        """Number of changed paths."""
        return len(self.files)

    @property
    def is_dirty(self) -> bool:
        """Return whether the repo still has uncommitted changes."""
        return bool(self.files)


def commit_selected_paths(repo: Path, paths: list[str], subject: str) -> tuple[bool, str]:
    """Stage `paths` and create a commit with `subject`. Return `(ok, detail)`."""
    repo = repo.resolve()
    cleaned = [path.replace("\\", "/").strip() for path in paths if path.strip()]
    subject = " ".join(subject.strip().splitlines()).strip()
    if not cleaned:
        return False, "No files selected"
    if not subject:
        return False, "Empty commit message"

    add_p = git_run(repo, "add", "--", *cleaned)
    if add_p.returncode != 0:
        return False, (add_p.stderr or add_p.stdout or "git add failed").strip()

    commit_p = git_run(repo, "commit", "-m", subject)
    if commit_p.returncode != 0:
        return False, (commit_p.stderr or commit_p.stdout or "git commit failed").strip()
    return True, subject


def list_changed_files(repo: Path) -> list[ChangedFile]:
    """Parse `git status --porcelain` into changed files.

    Do not `str.strip()` the whole status: an unstaged change starts with a space
    (`M path`), and stripping it drops the first character of the path.

    """
    porcelain = git_porcelain(repo)
    if not porcelain.strip():
        return []
    return parse_porcelain_files(porcelain)


def open_github_desktop_nonblocking(repo: Path) -> tuple[bool, str]:
    """Open `repo` in GitHub Desktop without waiting for the app to exit."""
    repo = repo.resolve()
    if not repo.is_dir():
        return False, f"Folder not found: {repo}"

    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        url = "x-github-client://openLocalRepo/" + quote(str(repo).replace("\\", "/"))
        exe = Path(local) / "GitHubDesktop" / "GitHubDesktop.exe"
        bat = Path(local) / "GitHubDesktop" / "bin" / "github.bat"
        try:
            os.startfile(url)  # noqa: S606
        except OSError:
            pass
        else:
            return True, url
        if bat.is_file():
            subprocess.Popen(
                ["cmd", "/c", "start", "", str(bat), str(repo)],  # noqa: S607
                cwd=str(repo),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True, str(bat)
        if exe.is_file():
            subprocess.Popen(
                [str(exe), str(repo)],
                cwd=str(repo),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True, str(exe)

    github_cli = shutil.which("github")
    if github_cli:
        subprocess.Popen(
            [github_cli, str(repo)],
            cwd=str(repo),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True, github_cli

    return False, "GitHub Desktop not found (install it or add `github` to PATH)"


def parse_porcelain_files(porcelain: str) -> list[ChangedFile]:
    """Parse porcelain status lines into `ChangedFile` rows."""
    files: list[ChangedFile] = []
    for raw in porcelain.splitlines():
        line = raw.rstrip("\n")
        if len(line) < _PORCELAIN_MIN_LEN:
            continue
        status = line[:2]
        rest = line[3:]
        if len(rest) >= _QUOTED_MIN_LEN and rest[0] == '"' and rest[-1] == '"':
            rest = rest[1:-1]
        path = rest.split(" -> ", 1)[1].strip() if " -> " in rest else rest.strip()
        if path:
            files.append(ChangedFile(path=path.replace("\\", "/"), status=status))
    return files


def refresh_repo_statuses(repos: list[Path], *, prefer_first: Path | None = None) -> list[DirtyRepoStatus]:
    """Re-status known dirty repos; return only those still dirty.

    Checks `prefer_first` before the rest when it is in `repos`.

    """
    ordered: list[Path] = []
    seen: set[Path] = set()
    if prefer_first is not None:
        preferred = prefer_first.resolve()
        for repo in repos:
            if repo.resolve() == preferred:
                ordered.append(preferred)
                seen.add(preferred)
                break
    for repo in repos:
        resolved = repo.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        ordered.append(resolved)

    dirty: list[DirtyRepoStatus] = []
    for repo in ordered:
        files = tuple(list_changed_files(repo))
        if files:
            dirty.append(DirtyRepoStatus(path=repo, files=files))
    return dirty
