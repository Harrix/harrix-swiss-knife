"""Dirty-repo file lists, selective commit, and non-blocking GitHub Desktop open."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Literal
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import harrix_pylib as h

from harrix_swiss_knife.actions.common.git_cmd import git_porcelain, git_run
from harrix_swiss_knife.actions.common.github_https import (
    GITHUB_USER_AGENT,
    github_api_headers,
    validate_https_url,
)
from harrix_swiss_knife.config_model import load_app_config
from harrix_swiss_knife.integrations.http_transport import https_ssl_context
from harrix_swiss_knife.paths import get_config_path_str

_PORCELAIN_MIN_LEN = 4
_QUOTED_MIN_LEN = 2
_GITHUB_VISIBILITY_TIMEOUT_S = 8
_HTTP_OK = 200
_HTTP_UNAUTHORIZED = 401
_HTTP_FORBIDDEN = 403
_HTTP_NOT_FOUND = 404
_SCAN_WORKERS = 8
_GITHUB_SLUG = re.compile(
    r"^(?:https://(?:www\.)?github\.com/|git@github\.com:|ssh://git@github\.com/)"
    r"(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)
_visibility_cache: dict[str, str] = {}
_unpushed_cache: dict[str, int] = {}
_unpushed_cache_lock = threading.Lock()
_commit_day_cache: dict[str, RepoCommitDayCache] = {}
_commit_day_cache_lock = threading.Lock()

CommitScope = Literal["all", "private", "public", "cloud", "local"]
COMMIT_SCOPE_LABELS: tuple[tuple[CommitScope, str], ...] = (
    ("all", "All repositories"),
    ("private", "Private only"),
    ("public", "Public only"),
    ("cloud", "Cloud (public & private)"),
    ("local", "Local only"),
)


@dataclass(frozen=True, slots=True)
class ChangedFile:
    """One path from `git status --porcelain`."""

    path: str
    status: str


@dataclass(frozen=True, slots=True)
class CommitDaySummary:
    """Commit totals for the local today and yesterday."""

    today: DayCommitCounts
    yesterday: DayCommitCounts


@dataclass(frozen=True, slots=True)
class DayCommitCounts:
    """How many commits were created on one local calendar day.

    `total` includes every bucket. `public` and `private` are GitHub
    repositories. `local` has no remote. `other` is any remaining remote.

    """

    total: int = 0
    public: int = 0
    private: int = 0
    local: int = 0
    other: int = 0


@dataclass(frozen=True, slots=True)
class DirtyRepoStatus:
    """One repository that needs a commit, a push, or both.

    `unpushed` is the number of commits on `HEAD` that are not on any
    remote-tracking branch. It stays `0` for local repositories and for
    anything that is not a public GitHub repository.

    """

    path: Path
    files: tuple[ChangedFile, ...]
    unpushed: int = 0
    access_kind: str = ""

    @property
    def changed_count(self) -> int:
        """Number of changed paths."""
        return len(self.files)

    @property
    def is_dirty(self) -> bool:
        """Return whether the repo still has uncommitted changes."""
        return bool(self.files)

    def list_label(self) -> str:
        """Return the repository row caption, including change and unpushed counts."""
        parts: list[str] = []
        if self.changed_count:
            parts.append(str(self.changed_count))
        if self.unpushed:
            parts.append(f"↑{self.unpushed}")
        if not parts:
            return self.path.name
        return f"{self.path.name}  ({', '.join(parts)})"


@dataclass(frozen=True, slots=True)
class FoundGitRepo:
    """One Git repository discovered under a folder added to `paths_git_roots`."""

    path: Path
    status: DirtyRepoStatus | None = None

    @property
    def needs_attention(self) -> bool:
        """Return whether this repository belongs in the commit window."""
        return self.status is not None


@dataclass(frozen=True, slots=True)
class GitRootAdd:
    """Result of appending one folder to `paths_git_roots`."""

    path: Path
    added: bool
    message: str


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


@dataclass(frozen=True, slots=True)
class RepoCommitDayCache:
    """Cached per-day commit counts and visibility for one repository."""

    path: Path
    bucket: str
    counts: dict[date, int]


def add_git_root(folder: Path, *, config_path: str | None = None) -> GitRootAdd:
    """Append `folder` to `paths_git_roots` in `config.json`.

    A folder that is already listed is left unchanged. The stored path uses
    forward slashes, matching the existing config entries.

    """
    try:
        resolved = folder.expanduser().resolve()
    except OSError:
        resolved = folder
    if not resolved.is_dir():
        return GitRootAdd(path=resolved, added=False, message=f"Folder not found: {resolved}")

    path_str = config_path or get_config_path_str()
    loaded = load_app_config(path_str)
    raw = loaded.get("paths_git_roots") if isinstance(loaded, dict) else None
    items = [str(item).strip() for item in raw if str(item or "").strip()] if isinstance(raw, list) else []
    if any(_same_folder(Path(item), resolved) for item in items):
        return GitRootAdd(path=resolved, added=False, message="Already in `paths_git_roots`")

    items.append(resolved.as_posix())
    h.dev.config_update_value("paths_git_roots", items, path_str)
    return GitRootAdd(path=resolved, added=True, message=resolved.as_posix())


def attention_status(
    repo: Path,
    *,
    resolve_visibility: bool = True,
    fresh_unpushed: bool = False,
) -> DirtyRepoStatus | None:
    """Return a status when `repo` has uncommitted files or public unpushed commits.

    Local repositories are judged only by the working tree. A clean public
    GitHub repository is included when `HEAD` has commits that are not on a
    remote-tracking branch. Private and unknown remotes are not listed for
    push alone.

    `resolve_visibility` asks GitHub when the cached visibility is missing.
    Refresh on the UI thread should pass `False` and reuse the cache.
    Cached private repositories skip the unpushed `rev-list` entirely.

    """
    repo = repo.resolve()
    files = tuple(list_changed_files(repo))
    access = read_repo_access(repo)
    if access.kind in {"local", "private"}:
        unpushed = 0
    else:
        unpushed = unpushed_commit_count(repo, fresh=fresh_unpushed)
        if unpushed and access.kind == "remote" and access.github_slug and resolve_visibility:
            owner, _, name = access.github_slug.partition("/")
            if owner and name:
                access = repo_access_from_remote(
                    access.remote_url,
                    visibility=github_repo_visibility(owner, name),
                )
        if access.kind != "public":
            unpushed = 0
    if not files and unpushed <= 0:
        return None
    return DirtyRepoStatus(path=repo, files=files, unpushed=unpushed, access_kind=access.kind)


def clear_commit_day_cache() -> None:
    """Drop the in-memory per-repository commit-day cache."""
    with _commit_day_cache_lock:
        _commit_day_cache.clear()


def clear_unpushed_cache() -> None:
    """Drop the in-memory unpushed-commit count cache."""
    with _unpushed_cache_lock:
        _unpushed_cache.clear()


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
    invalidate_unpushed_cache(repo)
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


def count_commits_by_day(
    roots: list[Path],
    start: date,
    end: date,
    *,
    scope: CommitScope = "all",
    force_refresh: bool = False,
) -> dict[date, int]:
    """Sum commits per local calendar day under `roots` for `scope`.

    Counts use the committer date of commits reachable from local branches.
    Days with no commits are omitted. `cloud` keeps GitHub public and private
    repositories and drops local checkouts.

    Each repository is scanned once and cached. Later calls with a different
    `scope` or date window reuse that cache unless `force_refresh` is set.

    """
    if end < start:
        return {}
    ensure_commit_day_cache(roots, force=force_refresh)
    counts: dict[date, int] = {}
    for entry in _cached_repo_entries(roots):
        if not _scope_includes(scope, entry.bucket):
            continue
        for day, value in entry.counts.items():
            if day < start or day > end:
                continue
            counts[day] = counts.get(day, 0) + value
    return counts


def count_recent_commits(roots: list[Path]) -> CommitDaySummary:
    """Count commits created today and yesterday under `roots`.

    Today and yesterday are local calendar days. The count uses the committer
    date of commits reachable from local branches. Public and private are
    GitHub repositories. A repository with no remote is local. Anything else
    is other and still included in the total. GitHub is asked only for a
    repository that has a commit in this window.

    Args:

    - `roots` (`list[Path]`): Folders from `paths_git_roots`. A folder that is
      itself a repository is counted alone; otherwise its immediate child
      repositories are counted.

    """
    yesterday, today = _recent_days()
    today_buckets = _empty_commit_buckets()
    yesterday_buckets = _empty_commit_buckets()
    repos = list(_unique_git_repos(roots))
    if not repos:
        return CommitDaySummary(
            today=_counts_from_buckets(today_buckets),
            yesterday=_counts_from_buckets(yesterday_buckets),
        )

    def _one(repo: Path) -> tuple[int, int, str] | None:
        today_count, yesterday_count = _commits_on_recent_days(repo, yesterday, today)
        if today_count == 0 and yesterday_count == 0:
            return None
        return today_count, yesterday_count, _commit_visibility_bucket(repo)

    workers = min(_SCAN_WORKERS, len(repos))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for result in pool.map(_one, repos):
            if result is None:
                continue
            today_count, yesterday_count, bucket = result
            today_buckets[bucket] += today_count
            yesterday_buckets[bucket] += yesterday_count
    return CommitDaySummary(
        today=_counts_from_buckets(today_buckets),
        yesterday=_counts_from_buckets(yesterday_buckets),
    )


def discard_changed_paths(repo: Path, paths: list[str]) -> tuple[bool, str]:
    """Discard working-tree and index changes for `paths`. Return `(ok, detail)`.

    Tracked paths are restored from `HEAD` (staged + worktree). Untracked paths
    are removed with `git clean -fd`. Newly staged paths that are not in `HEAD`
    are unstaged and deleted.

    """
    repo = repo.resolve()
    cleaned = [path.replace("\\", "/").strip() for path in paths if path.strip()]
    if not cleaned:
        return False, "No files selected"

    status_map = {item.path: item.status for item in list_changed_files(repo)}
    tracked: list[str] = []
    untracked: list[str] = []
    for path in cleaned:
        status = status_map.get(path, "")
        if _is_untracked_status(status):
            untracked.append(path)
        else:
            tracked.append(path)

    discarded = 0
    for path in tracked:
        restore = git_run(
            repo,
            "restore",
            "--source=HEAD",
            "--staged",
            "--worktree",
            "--",
            path,
        )
        if restore.returncode != 0:
            # Newly staged paths are not in HEAD; unstage, then remove the file.
            reset = git_run(repo, "reset", "--", path)
            if reset.returncode != 0:
                return False, (reset.stderr or reset.stdout or f"git reset failed: {path}").strip()
            clean = git_run(repo, "clean", "-fd", "--", path)
            if clean.returncode != 0:
                return False, (clean.stderr or clean.stdout or f"git clean failed: {path}").strip()
        discarded += 1

    if untracked:
        clean = git_run(repo, "clean", "-fd", "--", *untracked)
        if clean.returncode != 0:
            return False, (clean.stderr or clean.stdout or "git clean failed").strip()
        discarded += len(untracked)

    noun = "path" if discarded == 1 else "paths"
    invalidate_unpushed_cache(repo)
    return True, f"Discarded {discarded} {noun}"


def discover_git_repos(root: Path) -> list[FoundGitRepo]:
    """Return Git repositories under `root`, with status when they need attention.

    When `root` itself is a repository, only that repository is returned.
    Otherwise the immediate child repositories are returned.

    """
    if not root.is_dir():
        return []
    found = [FoundGitRepo(path=repo.resolve(), status=attention_status(repo)) for repo in _find_git_repos(root)]
    found.sort(key=lambda item: str(item.path).casefold())
    return found


def ensure_commit_day_cache(roots: list[Path], *, force: bool = False) -> None:
    """Load (or refresh) per-repository commit-day caches under `roots`."""
    for repo in _unique_git_repos(roots):
        load_repo_commit_day_cache(repo, force=force)


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


def invalidate_unpushed_cache(repo: Path | None = None) -> None:
    """Drop cached unpushed counts for `repo`, or for every repository."""
    with _unpushed_cache_lock:
        if repo is None:
            _unpushed_cache.clear()
            return
        try:
            key = str(repo.resolve())
        except OSError:
            key = str(repo)
        _unpushed_cache.pop(key, None)


def list_changed_files(repo: Path) -> list[ChangedFile]:
    """Parse `git status --porcelain` into changed files.

    Do not `str.strip()` the whole status: an unstaged change starts with a space
    (`M path`), and stripping it drops the first character of the path.

    """
    porcelain = git_porcelain(repo)
    if not porcelain.strip():
        return []
    return parse_porcelain_files(porcelain)


def list_commit_years(
    roots: list[Path],
    *,
    scope: CommitScope = "all",
    force_refresh: bool = False,
) -> list[int]:
    """Return calendar years that have commits for `scope`, newest first."""
    ensure_commit_day_cache(roots, force=force_refresh)
    years: set[int] = set()
    for entry in _cached_repo_entries(roots):
        if not _scope_includes(scope, entry.bucket):
            continue
        years.update(day.year for day in entry.counts)
    return sorted(years, reverse=True)


def load_repo_commit_day_cache(repo: Path, *, force: bool = False) -> RepoCommitDayCache:
    """Return cached day counts for `repo`, scanning Git when missing or forced."""
    try:
        resolved = repo.resolve()
    except OSError:
        resolved = repo
    key = str(resolved)
    if not force:
        with _commit_day_cache_lock:
            cached = _commit_day_cache.get(key)
        if cached is not None:
            return cached

    bucket = _commit_visibility_bucket(resolved)
    counts: dict[date, int] = {}
    proc = git_run(resolved, "log", "--branches", "--pretty=format:%cI")
    if proc.returncode == 0:
        for line in proc.stdout.splitlines():
            day = _local_calendar_date(line)
            if day is None:
                continue
            counts[day] = counts.get(day, 0) + 1
    entry = RepoCommitDayCache(path=resolved, bucket=bucket, counts=counts)
    with _commit_day_cache_lock:
        _commit_day_cache[key] = entry
    return entry


def open_github_desktop_nonblocking(repo: Path) -> tuple[bool, str]:
    """Open `repo` in GitHub Desktop without waiting for the app to exit.

    Prefer the Desktop CLI (`github.bat` / `github`) with the repository path.
    The old `x-github-client://openLocalRepo/` protocol no longer switches the
    selected repository in current Desktop builds.

    The process is detached from this console. `os.startfile` would let GitHub
    Desktop inherit it and print Chromium logs into the app terminal.

    """
    repo = repo.resolve()
    if not repo.is_dir():
        return False, f"Folder not found: {repo}"

    path_arg = str(repo)
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        bat = Path(local) / "GitHubDesktop" / "bin" / "github.bat"
        exe = Path(local) / "GitHubDesktop" / "GitHubDesktop.exe"
        if bat.is_file():
            # `github.bat` forwards the path as a CLI open action.
            _spawn_detached(["cmd", "/c", str(bat), path_arg], cwd=repo)
            return True, str(bat)
        if exe.is_file():
            _spawn_detached([str(exe), path_arg], cwd=repo)
            return True, str(exe)

    github_cli = shutil.which("github")
    if github_cli:
        _spawn_detached([github_cli, path_arg], cwd=repo)
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


def push_current_branch(repo: Path) -> tuple[bool, str]:
    """Push `HEAD` to its upstream, or to `origin` when no upstream is set."""
    repo = repo.resolve()
    if not _origin_remote_url(repo):
        return False, "No remote"
    upstream = git_run(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    if upstream.returncode == 0 and upstream.stdout.strip():
        proc = git_run(repo, "push")
    else:
        proc = git_run(repo, "push", "-u", "origin", "HEAD")
    if proc.returncode != 0:
        return False, _git_last_line(proc) or "git push failed"
    invalidate_unpushed_cache(repo)
    return True, _git_last_line(proc) or "Pushed"


def read_repo_access(repo: Path) -> RepoAccess:
    """Classify `repo` from its remote. Visibility is used only when already cached."""
    remote_url = _origin_remote_url(repo)
    slug = parse_github_slug(remote_url)
    visibility = _visibility_cache.get(f"{slug[0]}/{slug[1]}".casefold()) if slug is not None else None
    return repo_access_from_remote(remote_url, visibility=visibility)


def refresh_repo_statuses(repos: list[Path], *, prefer_first: Path | None = None) -> list[DirtyRepoStatus]:
    """Re-status known repos; keep those that still need a commit or a public push.

    Checks `prefer_first` before the rest when it is in `repos`. Visibility is
    read from the cache so this can run on a timer without calling GitHub.
    Unpushed counts are refreshed in parallel and skip the process cache.

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

    if not ordered:
        return []

    def _one(repo: Path) -> DirtyRepoStatus | None:
        return attention_status(repo, resolve_visibility=False, fresh_unpushed=True)

    workers = min(_SCAN_WORKERS, len(ordered))
    by_path: dict[Path, DirtyRepoStatus] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_one, repo): repo for repo in ordered}
        for future in as_completed(futures):
            status = future.result()
            if status is not None:
                by_path[status.path] = status
    return [by_path[repo] for repo in ordered if repo in by_path]


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
    """Find repos under `roots` that need a commit or a public push.

    A root is checked itself when it is a Git repository, otherwise its
    immediate child repositories are checked. Local repositories are included
    only when they have uncommitted files. Repositories are checked in parallel.

    """
    repos = list(_unique_git_repos(roots))
    if not repos:
        return []

    def _one(repo: Path) -> DirtyRepoStatus | None:
        return attention_status(repo)

    workers = min(_SCAN_WORKERS, len(repos))
    by_path: dict[Path, DirtyRepoStatus] = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_one, repo): repo for repo in repos}
        for future in as_completed(futures):
            status = future.result()
            if status is not None:
                by_path[status.path] = status
    ordered: list[DirtyRepoStatus] = []
    for repo in repos:
        try:
            key = repo.resolve()
        except OSError:
            key = repo
        status = by_path.get(key)
        if status is not None:
            ordered.append(status)
    return ordered


def unpushed_commit_count(repo: Path, *, fresh: bool = False) -> int:
    """Return how many commits on `HEAD` are missing from every remote-tracking ref.

    A repository with no remote returns `0`. The count uses local remote-tracking
    refs and does not contact the server. Results are cached for this process
    unless `fresh` is set; commit/push/discard invalidate the entry.

    """
    try:
        key = str(repo.resolve())
    except OSError:
        key = str(repo)
    if not fresh:
        with _unpushed_cache_lock:
            cached = _unpushed_cache.get(key)
            if cached is not None:
                return cached
    names = git_run(repo, "remote")
    if names.returncode != 0 or not names.stdout.strip():
        count = 0
    else:
        proc = git_run(repo, "rev-list", "--count", "HEAD", "--not", "--remotes")
        if proc.returncode != 0:
            count = 0
        else:
            try:
                count = max(0, int(proc.stdout.strip() or "0"))
            except ValueError:
                count = 0
    with _unpushed_cache_lock:
        _unpushed_cache[key] = count
    return count


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


def _cached_repo_entries(roots: list[Path]) -> list[RepoCommitDayCache]:
    """Return cache entries for repositories under `roots` (skips unloaded ones)."""
    entries: list[RepoCommitDayCache] = []
    with _commit_day_cache_lock:
        for repo in _unique_git_repos(roots):
            try:
                key = str(repo.resolve())
            except OSError:
                key = str(repo)
            entry = _commit_day_cache.get(key)
            if entry is not None:
                entries.append(entry)
    return entries


def _commit_visibility_bucket(repo: Path) -> str:
    """Return `public`, `private`, `local`, or `other` for recent-commit totals."""
    access = read_repo_access(repo)
    if access.kind == "remote" and access.github_slug:
        owner, _, name = access.github_slug.partition("/")
        if owner and name:
            access = repo_access_from_remote(
                access.remote_url,
                visibility=github_repo_visibility(owner, name),
            )
    if access.kind in {"public", "private", "local"}:
        return access.kind
    return "other"


def _commits_on_recent_days(repo: Path, yesterday: date, today: date) -> tuple[int, int]:
    """Return `(today, yesterday)` commit counts for local branches in `repo`."""
    since = _midnight_iso(yesterday)
    until = _midnight_iso(today + timedelta(days=1))
    proc = git_run(
        repo,
        "log",
        "--branches",
        f"--since={since}",
        f"--until={until}",
        "--pretty=format:%cI",
    )
    if proc.returncode != 0:
        return 0, 0
    today_count = 0
    yesterday_count = 0
    for line in proc.stdout.splitlines():
        day = _local_calendar_date(line)
        if day == today:
            today_count += 1
        elif day == yesterday:
            yesterday_count += 1
    return today_count, yesterday_count


def _counts_from_buckets(buckets: dict[str, int]) -> DayCommitCounts:
    return DayCommitCounts(
        total=sum(buckets.values()),
        public=buckets["public"],
        private=buckets["private"],
        local=buckets["local"],
        other=buckets["other"],
    )


def _empty_commit_buckets() -> dict[str, int]:
    return {"public": 0, "private": 0, "local": 0, "other": 0}


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


def _git_last_line(proc: subprocess.CompletedProcess[str]) -> str:
    """Return the last non-empty line of Git stderr, or stdout."""
    text = proc.stderr or proc.stdout or ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[-1] if lines else ""


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


def _is_untracked_status(status: str) -> bool:
    """Return whether porcelain `status` is an untracked path (`??`)."""
    text = status.ljust(2)[:2]
    return text == "??" or text.strip() == "?"


def _local_calendar_date(text: str) -> date | None:
    raw = text.strip()
    if not raw:
        return None
    try:
        moment = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if moment.tzinfo is None:
        return moment.date()
    return moment.astimezone().date()


def _midnight_iso(day: date) -> str:
    """Return local midnight of `day` as an ISO timestamp Git can parse."""
    tz = datetime.now().astimezone().tzinfo
    return datetime(day.year, day.month, day.day, tzinfo=tz).isoformat(timespec="seconds")


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


def _recent_days() -> tuple[date, date]:
    """Return `(yesterday, today)` in the local calendar."""
    today = datetime.now().astimezone().date()
    return today - timedelta(days=1), today


def _same_folder(left: Path, right: Path) -> bool:
    """Return whether two paths name the same folder, ignoring slash style and case."""
    try:
        left_resolved = left.expanduser().resolve()
    except OSError:
        left_resolved = left
    try:
        right_resolved = right.expanduser().resolve()
    except OSError:
        right_resolved = right
    return os.path.normcase(str(left_resolved)) == os.path.normcase(str(right_resolved))


def _scope_includes(scope: CommitScope, bucket: str) -> bool:
    """Return whether a visibility `bucket` belongs in `scope`."""
    if scope == "all":
        return True
    if scope == "local":
        return bucket == "local"
    if scope == "public":
        return bucket == "public"
    if scope == "private":
        return bucket == "private"
    if scope == "cloud":
        return bucket in {"public", "private"}
    return True


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


def _unique_git_repos(roots: list[Path]) -> list[Path]:
    """Return each repository under `roots` once, ordered by path."""
    repos: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for repo in _find_git_repos(root):
            try:
                resolved = repo.resolve()
            except OSError:
                resolved = repo
            if resolved in seen:
                continue
            seen.add(resolved)
            repos.append(resolved)
    repos.sort(key=lambda path: str(path).casefold())
    return repos
