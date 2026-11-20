"""Dirty-repo file lists, selective commit, and non-blocking GitHub Desktop open."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from harrix_swiss_knife.actions.common.git_cmd import git_porcelain, git_run
from harrix_swiss_knife.actions.common.github_https import (
    GITHUB_USER_AGENT,
    github_api_headers,
    validate_https_url,
)
from harrix_swiss_knife.config_model import load_app_config
from harrix_swiss_knife.integrations.http_transport import https_ssl_context

_PORCELAIN_MIN_LEN = 4
_QUOTED_MIN_LEN = 2
_GITHUB_VISIBILITY_TIMEOUT_S = 8
_HTTP_OK = 200
_HTTP_UNAUTHORIZED = 401
_HTTP_FORBIDDEN = 403
_HTTP_NOT_FOUND = 404
_GITHUB_SLUG = re.compile(
    r"^(?:https://(?:www\.)?github\.com/|git@github\.com:|ssh://git@github\.com/)"
    r"(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)
_visibility_cache: dict[str, str] = {}


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


@dataclass(frozen=True, slots=True)
class RepoAccess:
    """Local-only checkout, or a remote with optional GitHub visibility."""

    kind: str
    remote_url: str = ""
    github_slug: str = ""

    def summary(self, path: Path) -> str:
        """Return a tooltip: path, then local / remote / public / private."""
        lines = [str(path)]
        if self.kind == "local":
            lines.append("Local repository, no remote")
        elif self.kind == "public":
            lines.append(f"Public GitHub repository {self.github_slug}")
        elif self.kind == "private":
            lines.append(f"Private GitHub repository {self.github_slug}")
        elif self.github_slug:
            lines.append(f"GitHub repository {self.github_slug}")
        else:
            lines.append(f"Remote: {self.remote_url}")
        return "\n".join(lines)


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


def configured_git_roots() -> list[Path]:
    """Return unique `paths_git_roots` from the current app config."""
    loaded = load_app_config()
    raw = loaded.get("paths_git_roots") if isinstance(loaded, dict) else None
    if not isinstance(raw, list):
        return []
    roots: list[Path] = []
    seen: set[Path] = set()
    for item in raw:
        text = str(item or "").strip()
        if not text:
            continue
        path = Path(text).expanduser()
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved in seen:
            continue
        seen.add(resolved)
        roots.append(resolved)
    return roots


def github_repo_visibility(owner: str, repo: str) -> str:
    """Return `public`, `private`, or `unknown` for a GitHub repository.

    Uses the configured GitHub token when one is present. A 404 is treated as
    private: without a token GitHub hides private repositories the same way.
    Successful answers are cached for this process.

    """
    key = f"{owner}/{repo}".casefold()
    cached = _visibility_cache.get(key)
    if cached is not None:
        return cached
    result = _fetch_github_visibility(owner, repo)
    if result != "unknown":
        _visibility_cache[key] = result
    return result


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
    """Open `repo` in GitHub Desktop without waiting for the app to exit.

    The process is detached from this console. `os.startfile` would let GitHub
    Desktop inherit it and print Chromium logs into the app terminal.

    """
    repo = repo.resolve()
    if not repo.is_dir():
        return False, f"Folder not found: {repo}"

    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        url = "x-github-client://openLocalRepo/" + quote(str(repo).replace("\\", "/"))
        exe = Path(local) / "GitHubDesktop" / "GitHubDesktop.exe"
        bat = Path(local) / "GitHubDesktop" / "bin" / "github.bat"
        try:
            _spawn_detached(["cmd", "/c", "start", "", url], cwd=repo)
        except OSError:
            pass
        else:
            return True, url
        if bat.is_file():
            _spawn_detached(["cmd", "/c", "start", "", str(bat), str(repo)], cwd=repo)
            return True, str(bat)
        if exe.is_file():
            _spawn_detached([str(exe), str(repo)], cwd=repo)
            return True, str(exe)

    github_cli = shutil.which("github")
    if github_cli:
        _spawn_detached([github_cli, str(repo)], cwd=repo)
        return True, github_cli

    return False, "GitHub Desktop not found (install it or add `github` to PATH)"


def parse_github_slug(remote_url: str) -> tuple[str, str] | None:
    """Return `(owner, repo)` when `remote_url` points at GitHub.com."""
    match = _GITHUB_SLUG.match(remote_url.strip())
    if match is None:
        return None
    return match.group("owner"), match.group("repo")


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


def read_repo_access(repo: Path) -> RepoAccess:
    """Classify `repo` from its remote. Visibility is used only when already cached."""
    remote_url = _origin_remote_url(repo)
    slug = parse_github_slug(remote_url)
    visibility = _visibility_cache.get(f"{slug[0]}/{slug[1]}".casefold()) if slug is not None else None
    return repo_access_from_remote(remote_url, visibility=visibility)


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


def repo_access_from_remote(remote_url: str, *, visibility: str | None = None) -> RepoAccess:
    """Build a `RepoAccess` from a remote URL and an optional visibility."""
    text = remote_url.strip()
    if not text:
        return RepoAccess(kind="local")
    slug = parse_github_slug(text)
    slug_text = f"{slug[0]}/{slug[1]}" if slug is not None else ""
    if visibility == "public":
        return RepoAccess(kind="public", remote_url=text, github_slug=slug_text)
    if visibility == "private":
        return RepoAccess(kind="private", remote_url=text, github_slug=slug_text)
    return RepoAccess(kind="remote", remote_url=text, github_slug=slug_text)


def scan_dirty_repos(roots: list[Path]) -> list[DirtyRepoStatus]:
    """Find dirty Git repos under `roots` (the root itself, or its immediate children)."""
    repos: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for repo in _find_git_repos(root):
            resolved = repo.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            repos.append(resolved)

    dirty: list[DirtyRepoStatus] = []
    for repo in sorted(repos, key=lambda path: str(path).casefold()):
        files = tuple(list_changed_files(repo))
        if files:
            dirty.append(DirtyRepoStatus(path=repo, files=files))
    return dirty


def visibility_from_github_payload(payload: object, *, status: int) -> str:
    """Map a GitHub repository API result to `public`, `private`, or `unknown`."""
    if status == _HTTP_NOT_FOUND:
        return "private"
    if status != _HTTP_OK or not isinstance(payload, dict):
        return "unknown"
    visibility = payload.get("visibility")
    private = payload.get("private")
    if visibility == "public" or private is False:
        return "public"
    if visibility in {"private", "internal"} or private is True:
        return "private"
    return "unknown"


def _anonymous_github_headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "User-Agent": GITHUB_USER_AGENT,
    }


def _fetch_github_visibility(owner: str, repo: str) -> str:
    status, payload = _github_repo_payload(owner, repo, headers=github_api_headers(config=load_app_config()))
    if status in {_HTTP_UNAUTHORIZED, _HTTP_FORBIDDEN}:
        # A rejected token must not hide a public repository. Ask again without it.
        status, payload = _github_repo_payload(owner, repo, headers=_anonymous_github_headers())
    if status == 0:
        return "unknown"
    return visibility_from_github_payload(payload, status=status)


def _find_git_repos(root: Path) -> list[Path]:
    """Return `root` when it is a repo, otherwise its immediate child repos."""
    root = root.resolve()
    if not root.is_dir():
        return []
    if _is_git_repo(root):
        return [root]
    try:
        children = sorted(root.iterdir(), key=lambda path: path.name.lower())
    except OSError:
        return []
    return [child for child in children if child.is_dir() and not child.name.startswith(".") and _is_git_repo(child)]


def _github_repo_payload(owner: str, repo: str, *, headers: dict[str, str]) -> tuple[int, object]:
    url = f"https://api.github.com/repos/{quote(owner, safe='')}/{quote(repo, safe='')}"
    try:
        validate_https_url(url)
        request = Request(url, headers=headers)
        with urlopen(request, timeout=_GITHUB_VISIBILITY_TIMEOUT_S, context=https_ssl_context()) as response:  # noqa: S310
            payload = json.loads(response.read().decode())
            status = int(getattr(response, "status", _HTTP_OK))
    except HTTPError as exc:
        status = exc.code
        exc.close()
        return status, None
    except (OSError, URLError, ValueError, json.JSONDecodeError):
        return 0, None
    return status, payload


def _is_git_repo(path: Path) -> bool:
    """Return whether `path` is a Git work tree rooted at `path`."""
    if not (path / ".git").exists():
        return False
    proc = git_run(path, "rev-parse", "--is-inside-work-tree")
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def _origin_remote_url(repo: Path) -> str:
    """Return the origin URL, or the first remote URL, or an empty string."""
    origin = git_run(repo, "remote", "get-url", "origin")
    if origin.returncode == 0 and origin.stdout.strip():
        return origin.stdout.strip()
    names = git_run(repo, "remote")
    if names.returncode != 0:
        return ""
    for name in names.stdout.splitlines():
        remote = name.strip()
        if not remote:
            continue
        url = git_run(repo, "remote", "get-url", remote)
        if url.returncode == 0 and url.stdout.strip():
            return url.stdout.strip()
    return ""


def _spawn_detached(command: list[str], *, cwd: Path) -> None:
    """Start `command` and return immediately, without this process's console."""
    kwargs: dict[str, Any] = {
        "cwd": str(cwd),
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(command, **kwargs)
