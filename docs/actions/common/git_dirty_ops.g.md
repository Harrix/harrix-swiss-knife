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
- [🏛️ Class `DirtyRepoStatus`](#%EF%B8%8F-class-dirtyrepostatus)
  - [⚙️ Method `changed_count (property)`](#%EF%B8%8F-method-changed_count-property)
  - [⚙️ Method `is_dirty (property)`](#%EF%B8%8F-method-is_dirty-property)
- [🏛️ Class `RepoAccess`](#%EF%B8%8F-class-repoaccess)
  - [⚙️ Method `summary`](#%EF%B8%8F-method-summary)
- [🔧 Function `commit_selected_paths`](#-function-commit_selected_paths)
- [🔧 Function `configured_git_roots`](#-function-configured_git_roots)
- [🔧 Function `github_repo_visibility`](#-function-github_repo_visibility)
- [🔧 Function `list_changed_files`](#-function-list_changed_files)
- [🔧 Function `open_github_desktop_nonblocking`](#-function-open_github_desktop_nonblocking)
- [🔧 Function `parse_github_slug`](#-function-parse_github_slug)
- [🔧 Function `parse_porcelain_files`](#-function-parse_porcelain_files)
- [🔧 Function `read_repo_access`](#-function-read_repo_access)
- [🔧 Function `refresh_repo_statuses`](#-function-refresh_repo_statuses)
- [🔧 Function `repo_access_from_remote`](#-function-repo_access_from_remote)
- [🔧 Function `scan_dirty_repos`](#-function-scan_dirty_repos)
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

## 🏛️ Class `DirtyRepoStatus`

```python
class DirtyRepoStatus
```

Current dirty state for one repository.

<details>
<summary>Code:</summary>

```python
class DirtyRepoStatus:

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

Re-status known dirty repos; return only those still dirty.

Checks `prefer_first` before the rest when it is in `repos`.

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
        files = tuple(list_changed_files(repo))
        if files:
            dirty.append(DirtyRepoStatus(path=repo, files=files))
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

Find dirty Git repos under `roots` (the root itself, or its immediate children).

<details>
<summary>Code:</summary>

```python
def scan_dirty_repos(roots: list[Path]) -> list[DirtyRepoStatus]:
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
