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
- [🔧 Function `commit_selected_paths`](#-function-commit_selected_paths)
- [🔧 Function `list_changed_files`](#-function-list_changed_files)
- [🔧 Function `open_github_desktop_nonblocking`](#-function-open_github_desktop_nonblocking)
- [🔧 Function `parse_porcelain_files`](#-function-parse_porcelain_files)
- [🔧 Function `refresh_repo_statuses`](#-function-refresh_repo_statuses)

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

## 🔧 Function `list_changed_files`

```python
def list_changed_files(repo: Path) -> list[ChangedFile]
```

Parse `git status --porcelain` into changed files.

<details>
<summary>Code:</summary>

```python
def list_changed_files(repo: Path) -> list[ChangedFile]:
    porcelain = git_porcelain(repo).strip()
    if not porcelain:
        return []
    return parse_porcelain_files(porcelain)
```

</details>

## 🔧 Function `open_github_desktop_nonblocking`

```python
def open_github_desktop_nonblocking(repo: Path) -> tuple[bool, str]
```

Open `repo` in GitHub Desktop without waiting for the app to exit.

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
