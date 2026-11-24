---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `git_dirty_ops.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ChangedFile`](#%EF%B8%8F-class-changedfile)
- [🏛️ Class `CommitDaySummary`](#%EF%B8%8F-class-commitdaysummary)
- [🏛️ Class `DayCommitCounts`](#%EF%B8%8F-class-daycommitcounts)
- [🏛️ Class `DirtyRepoStatus`](#%EF%B8%8F-class-dirtyrepostatus)
  - [⚙️ Method `changed_count (property)`](#%EF%B8%8F-method-changed_count-property)
  - [⚙️ Method `is_dirty (property)`](#%EF%B8%8F-method-is_dirty-property)
  - [⚙️ Method `list_label`](#%EF%B8%8F-method-list_label)
- [🏛️ Class `FoundGitRepo`](#%EF%B8%8F-class-foundgitrepo)
  - [⚙️ Method `needs_attention (property)`](#%EF%B8%8F-method-needs_attention-property)
- [🏛️ Class `GitRootAdd`](#%EF%B8%8F-class-gitrootadd)
- [🏛️ Class `RepoAccess`](#%EF%B8%8F-class-repoaccess)
  - [⚙️ Method `summary`](#%EF%B8%8F-method-summary)
- [🔧 Function `add_git_root`](#-function-add_git_root)
- [🔧 Function `attention_status`](#-function-attention_status)
- [🔧 Function `commit_selected_paths`](#-function-commit_selected_paths)
- [🔧 Function `configured_git_roots`](#-function-configured_git_roots)
- [🔧 Function `count_commits_by_day`](#-function-count_commits_by_day)
- [🔧 Function `count_recent_commits`](#-function-count_recent_commits)
- [🔧 Function `discard_changed_paths`](#-function-discard_changed_paths)
- [🔧 Function `discover_git_repos`](#-function-discover_git_repos)
- [🔧 Function `github_repo_visibility`](#-function-github_repo_visibility)
- [🔧 Function `list_changed_files`](#-function-list_changed_files)
- [🔧 Function `open_github_desktop_nonblocking`](#-function-open_github_desktop_nonblocking)
- [🔧 Function `parse_github_slug`](#-function-parse_github_slug)
- [🔧 Function `parse_porcelain_files`](#-function-parse_porcelain_files)
- [🔧 Function `push_current_branch`](#-function-push_current_branch)
- [🔧 Function `read_repo_access`](#-function-read_repo_access)
- [🔧 Function `refresh_repo_statuses`](#-function-refresh_repo_statuses)
- [🔧 Function `repo_access_from_remote`](#-function-repo_access_from_remote)
- [🔧 Function `scan_dirty_repos`](#-function-scan_dirty_repos)
- [🔧 Function `unpushed_commit_count`](#-function-unpushed_commit_count)
- [🔧 Function `visibility_from_github_payload`](#-function-visibility_from_github_payload)

</details>

## 🏛️ Class `ChangedFile`

```python
class ChangedFile
```

One path from `git status --porcelain`.

<details>
<summary>Code:</summary>

```python
class ChangedFile:

    path: str
    status: str
```

</details>

## 🏛️ Class `CommitDaySummary`

```python
class CommitDaySummary
```

Commit totals for the local today and yesterday.

<details>
<summary>Code:</summary>

```python
class CommitDaySummary:

    today: DayCommitCounts
    yesterday: DayCommitCounts
```

</details>

## 🏛️ Class `DayCommitCounts`

```python
class DayCommitCounts
```

How many commits were created on one local calendar day.

`total` includes every bucket. `public` and `private` are GitHub
repositories. `local` has no remote. `other` is any remaining remote.

<details>
<summary>Code:</summary>

```python
class DayCommitCounts:

    total: int = 0
    public: int = 0
    private: int = 0
    local: int = 0
    other: int = 0
```

</details>

## 🏛️ Class `DirtyRepoStatus`

```python
class DirtyRepoStatus
```

One repository that needs a commit, a push, or both.

`unpushed` is the number of commits on `HEAD` that are not on any
remote-tracking branch. It stays `0` for local repositories and for
anything that is not a public GitHub repository.

<details>
<summary>Code:</summary>

```python
class DirtyRepoStatus:

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
```

</details>

### ⚙️ Method `changed_count (property)`

```python
def changed_count(self) -> int
```

Number of changed paths.

<details>
<summary>Code:</summary>

```python
def changed_count(self) -> int:
        return len(self.files)
```

</details>

### ⚙️ Method `is_dirty (property)`

```python
def is_dirty(self) -> bool
```

Return whether the repo still has uncommitted changes.

<details>
<summary>Code:</summary>

```python
def is_dirty(self) -> bool:
        return bool(self.files)
```

</details>

### ⚙️ Method `list_label`

```python
def list_label(self) -> str
```

Return the repository row caption, including change and unpushed counts.

<details>
<summary>Code:</summary>

```python
def list_label(self) -> str:
        parts: list[str] = []
        if self.changed_count:
            parts.append(str(self.changed_count))
        if self.unpushed:
            parts.append(f"↑{self.unpushed}")
        if not parts:
            return self.path.name
        return f"{self.path.name}  ({', '.join(parts)})"
```

</details>

## 🏛️ Class `FoundGitRepo`

```python
class FoundGitRepo
```

One Git repository discovered under a folder added to `paths_git_roots`.

<details>
<summary>Code:</summary>

```python
class FoundGitRepo:

    path: Path
    status: DirtyRepoStatus | None = None

    @property
    def needs_attention(self) -> bool:
        """Return whether this repository belongs in the commit window."""
        return self.status is not None
```

</details>

### ⚙️ Method `needs_attention (property)`

```python
def needs_attention(self) -> bool
```

Return whether this repository belongs in the commit window.

<details>
<summary>Code:</summary>

```python
def needs_attention(self) -> bool:
        return self.status is not None
```

</details>

## 🏛️ Class `GitRootAdd`

```python
class GitRootAdd
```

Result of appending one folder to `paths_git_roots`.

<details>
<summary>Code:</summary>

```python
class GitRootAdd:

    path: Path
    added: bool
    message: str
```

</details>

## 🏛️ Class `RepoAccess`

```python
class RepoAccess
```

Local-only checkout, or a remote with optional GitHub visibility.

<details>
<summary>Code:</summary>

```python
class RepoAccess:

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
```

</details>

### ⚙️ Method `summary`

```python
def summary(self, path: Path) -> str
```

Return a tooltip: path, then local / remote / public / private.

<details>
<summary>Code:</summary>

```python
def summary(self, path: Path) -> str:
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
```

</details>

## 🔧 Function `add_git_root`

```python
def add_git_root(folder: Path, *, config_path: str | None = None) -> GitRootAdd
```

Append `folder` to `paths_git_roots` in `config.json`.

A folder that is already listed is left unchanged. The stored path uses
forward slashes, matching the existing config entries.

<details>
<summary>Code:</summary>

```python
def add_git_root(folder: Path, *, config_path: str | None = None) -> GitRootAdd:
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
```

</details>

## 🔧 Function `attention_status`

```python
def attention_status(repo: Path, *, resolve_visibility: bool = True) -> DirtyRepoStatus | None
```

Return a status when `repo` has uncommitted files or public unpushed commits.

Local repositories are judged only by the working tree. A clean public
GitHub repository is included when `HEAD` has commits that are not on a
remote-tracking branch. Private and unknown remotes are not listed for
push alone.

`resolve_visibility` asks GitHub when the cached visibility is missing.
Refresh on the UI thread should pass `False` and reuse the cache.

<details>
<summary>Code:</summary>

```python
def attention_status(repo: Path, *, resolve_visibility: bool = True) -> DirtyRepoStatus | None:
    repo = repo.resolve()
    files = tuple(list_changed_files(repo))
    access = read_repo_access(repo)
    unpushed = 0 if access.kind == "local" else unpushed_commit_count(repo)
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
```

</details>

## 🔧 Function `commit_selected_paths`

```python
def commit_selected_paths(repo: Path, paths: list[str], subject: str) -> tuple[bool, str]
```

Stage `paths` and create a commit with `subject`. Return `(ok, detail)`.

<details>
<summary>Code:</summary>

```python
def commit_selected_paths(repo: Path, paths: list[str], subject: str) -> tuple[bool, str]:
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
```

</details>

## 🔧 Function `configured_git_roots`

```python
def configured_git_roots() -> list[Path]
```

Return unique `paths_git_roots` from the current app config.

<details>
<summary>Code:</summary>

```python
def configured_git_roots() -> list[Path]:
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
```

</details>

## 🔧 Function `count_commits_by_day`

```python
def count_commits_by_day(roots: list[Path], start: date, end: date, *, scope: CommitScope = 'all') -> dict[date, int]
```

Sum commits per local calendar day under `roots` for `scope`.

Counts use the committer date of commits reachable from local branches.
Days with no commits are omitted. `cloud` keeps GitHub public and private
repositories and drops local checkouts.

<details>
<summary>Code:</summary>

```python
def count_commits_by_day(
    roots: list[Path],
    start: date,
    end: date,
    *,
    scope: CommitScope = "all",
) -> dict[date, int]:
    if end < start:
        return {}
    counts: dict[date, int] = {}
    since = _midnight_iso(start)
    until = _midnight_iso(end + timedelta(days=1))
    for repo in _unique_git_repos(roots):
        bucket = _commit_visibility_bucket(repo)
        if not _scope_includes(scope, bucket):
            continue
        proc = git_run(
            repo,
            "log",
            "--branches",
            f"--since={since}",
            f"--until={until}",
            "--pretty=format:%cI",
        )
        if proc.returncode != 0:
            continue
        for line in proc.stdout.splitlines():
            day = _local_calendar_date(line)
            if day is None or day < start or day > end:
                continue
            counts[day] = counts.get(day, 0) + 1
    return counts
```

</details>

## 🔧 Function `count_recent_commits`

```python
def count_recent_commits(roots: list[Path]) -> CommitDaySummary
```

Count commits created today and yesterday under `roots`.

Today and yesterday are local calendar days. The count uses the committer
date of commits reachable from local branches. Public and private are
GitHub repositories. A repository with no remote is local. Anything else
is other and still included in the total. GitHub is asked only for a
repository that has a commit in this window.

Args:

- `roots` (`list[Path]`): Folders from `paths_git_roots`. A folder that is
  itself a repository is counted alone; otherwise its immediate child
  repositories are counted.

<details>
<summary>Code:</summary>

```python
def count_recent_commits(roots: list[Path]) -> CommitDaySummary:
    yesterday, today = _recent_days()
    today_buckets = _empty_commit_buckets()
    yesterday_buckets = _empty_commit_buckets()
    for repo in _unique_git_repos(roots):
        today_count, yesterday_count = _commits_on_recent_days(repo, yesterday, today)
        if today_count == 0 and yesterday_count == 0:
            continue
        bucket = _commit_visibility_bucket(repo)
        today_buckets[bucket] += today_count
        yesterday_buckets[bucket] += yesterday_count
    return CommitDaySummary(
        today=_counts_from_buckets(today_buckets),
        yesterday=_counts_from_buckets(yesterday_buckets),
    )
```

</details>

## 🔧 Function `discard_changed_paths`

```python
def discard_changed_paths(repo: Path, paths: list[str]) -> tuple[bool, str]
```

Discard working-tree and index changes for `paths`. Return `(ok, detail)`.

Tracked paths are restored from `HEAD` (staged + worktree). Untracked paths
are removed with `git clean -fd`. Newly staged paths that are not in `HEAD`
are unstaged and deleted.

<details>
<summary>Code:</summary>

```python
def discard_changed_paths(repo: Path, paths: list[str]) -> tuple[bool, str]:
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
    return True, f"Discarded {discarded} {noun}"
```

</details>

## 🔧 Function `discover_git_repos`

```python
def discover_git_repos(root: Path) -> list[FoundGitRepo]
```

Return Git repositories under `root`, with status when they need attention.

When `root` itself is a repository, only that repository is returned.
Otherwise the immediate child repositories are returned.

<details>
<summary>Code:</summary>

```python
def discover_git_repos(root: Path) -> list[FoundGitRepo]:
    if not root.is_dir():
        return []
    found = [FoundGitRepo(path=repo.resolve(), status=attention_status(repo)) for repo in _find_git_repos(root)]
    found.sort(key=lambda item: str(item.path).casefold())
    return found
```

</details>

## 🔧 Function `github_repo_visibility`

```python
def github_repo_visibility(owner: str, repo: str) -> str
```

Return `public`, `private`, or `unknown` for a GitHub repository.

Uses the configured GitHub token when one is present. A 404 is treated as
private: without a token GitHub hides private repositories the same way.
Successful answers are cached for this process.

<details>
<summary>Code:</summary>

```python
def github_repo_visibility(owner: str, repo: str) -> str:
    key = f"{owner}/{repo}".casefold()
    cached = _visibility_cache.get(key)
    if cached is not None:
        return cached
    result = _fetch_github_visibility(owner, repo)
    if result != "unknown":
        _visibility_cache[key] = result
    return result
```

</details>

## 🔧 Function `list_changed_files`

```python
def list_changed_files(repo: Path) -> list[ChangedFile]
```

Parse `git status --porcelain` into changed files.

Do not `str.strip()` the whole status: an unstaged change starts with a space
(`M path`), and stripping it drops the first character of the path.

<details>
<summary>Code:</summary>

```python
def list_changed_files(repo: Path) -> list[ChangedFile]:
    porcelain = git_porcelain(repo)
    if not porcelain.strip():
        return []
    return parse_porcelain_files(porcelain)
```

</details>

## 🔧 Function `open_github_desktop_nonblocking`

```python
def open_github_desktop_nonblocking(repo: Path) -> tuple[bool, str]
```

Open `repo` in GitHub Desktop without waiting for the app to exit.

The process is detached from this console. `os.startfile` would let GitHub
Desktop inherit it and print Chromium logs into the app terminal.

<details>
<summary>Code:</summary>

```python
def open_github_desktop_nonblocking(repo: Path) -> tuple[bool, str]:
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
```

</details>

## 🔧 Function `parse_github_slug`

```python
def parse_github_slug(remote_url: str) -> tuple[str, str] | None
```

Return `(owner, repo)` when `remote_url` points at GitHub.com.

<details>
<summary>Code:</summary>

```python
def parse_github_slug(remote_url: str) -> tuple[str, str] | None:
    match = _GITHUB_SLUG.match(remote_url.strip())
    if match is None:
        return None
    return match.group("owner"), match.group("repo")
```

</details>

## 🔧 Function `parse_porcelain_files`

```python
def parse_porcelain_files(porcelain: str) -> list[ChangedFile]
```

Parse porcelain status lines into [`ChangedFile`](#%EF%B8%8F-class-changedfile) rows.

<details>
<summary>Code:</summary>

```python
def parse_porcelain_files(porcelain: str) -> list[ChangedFile]:
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
```

</details>

## 🔧 Function `push_current_branch`

```python
def push_current_branch(repo: Path) -> tuple[bool, str]
```

Push `HEAD` to its upstream, or to `origin` when no upstream is set.

<details>
<summary>Code:</summary>

```python
def push_current_branch(repo: Path) -> tuple[bool, str]:
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
    return True, _git_last_line(proc) or "Pushed"
```

</details>

## 🔧 Function `read_repo_access`

```python
def read_repo_access(repo: Path) -> RepoAccess
```

Classify `repo` from its remote. Visibility is used only when already cached.

<details>
<summary>Code:</summary>

```python
def read_repo_access(repo: Path) -> RepoAccess:
    remote_url = _origin_remote_url(repo)
    slug = parse_github_slug(remote_url)
    visibility = _visibility_cache.get(f"{slug[0]}/{slug[1]}".casefold()) if slug is not None else None
    return repo_access_from_remote(remote_url, visibility=visibility)
```

</details>

## 🔧 Function `refresh_repo_statuses`

```python
def refresh_repo_statuses(repos: list[Path], *, prefer_first: Path | None = None) -> list[DirtyRepoStatus]
```

Re-status known repos; keep those that still need a commit or a public push.

Checks `prefer_first` before the rest when it is in `repos`. Visibility is
read from the cache so this can run on a timer without calling GitHub.

<details>
<summary>Code:</summary>

```python
def refresh_repo_statuses(repos: list[Path], *, prefer_first: Path | None = None) -> list[DirtyRepoStatus]:
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
        status = attention_status(repo, resolve_visibility=False)
        if status is not None:
            dirty.append(status)
    return dirty
```

</details>

## 🔧 Function `repo_access_from_remote`

```python
def repo_access_from_remote(remote_url: str, *, visibility: str | None = None) -> RepoAccess
```

Build a [`RepoAccess`](#%EF%B8%8F-class-repoaccess) from a remote URL and an optional visibility.

<details>
<summary>Code:</summary>

```python
def repo_access_from_remote(remote_url: str, *, visibility: str | None = None) -> RepoAccess:
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
```

</details>

## 🔧 Function `scan_dirty_repos`

```python
def scan_dirty_repos(roots: list[Path]) -> list[DirtyRepoStatus]
```

Find repos under `roots` that need a commit or a public push.

A root is checked itself when it is a Git repository, otherwise its
immediate child repositories are checked. Local repositories are included
only when they have uncommitted files.

<details>
<summary>Code:</summary>

```python
def scan_dirty_repos(roots: list[Path]) -> list[DirtyRepoStatus]:
    dirty: list[DirtyRepoStatus] = []
    for repo in _unique_git_repos(roots):
        status = attention_status(repo)
        if status is not None:
            dirty.append(status)
    return dirty
```

</details>

## 🔧 Function `unpushed_commit_count`

```python
def unpushed_commit_count(repo: Path) -> int
```

Return how many commits on `HEAD` are missing from every remote-tracking ref.

A repository with no remote returns `0`. The count uses local remote-tracking
refs and does not contact the server.

<details>
<summary>Code:</summary>

```python
def unpushed_commit_count(repo: Path) -> int:
    names = git_run(repo, "remote")
    if names.returncode != 0 or not names.stdout.strip():
        return 0
    proc = git_run(repo, "rev-list", "--count", "HEAD", "--not", "--remotes")
    if proc.returncode != 0:
        return 0
    try:
        return max(0, int(proc.stdout.strip() or "0"))
    except ValueError:
        return 0
```

</details>

## 🔧 Function `visibility_from_github_payload`

```python
def visibility_from_github_payload(payload: object, *, status: int) -> str
```

Map a GitHub repository API result to `public`, `private`, or `unknown`.

<details>
<summary>Code:</summary>

```python
def visibility_from_github_payload(payload: object, *, status: int) -> str:
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
```

</details>
