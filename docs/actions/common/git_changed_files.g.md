---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `git_changed_files.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `git_repo_root`](#-function-git_repo_root)
- [🔧 Function `list_changed_files_with_suffixes`](#-function-list_changed_files_with_suffixes)
- [🔧 Function `list_changed_markdown_files`](#-function-list_changed_markdown_files)
- [🔧 Function `list_changed_python_files`](#-function-list_changed_python_files)
- [🔧 Function `list_git_changed_files`](#-function-list_git_changed_files)

</details>

## 🔧 Function `git_repo_root`

```python
def git_repo_root(path: Path) -> Path | None
```

Return the Git toplevel for `path`, or `None` when not inside a work tree.

<details>
<summary>Code:</summary>

```python
def git_repo_root(path: Path) -> Path | None:
    path = path.resolve()
    proc = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],  # noqa: S607
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        return None
    root = proc.stdout.strip()
    if not root:
        return None
    return Path(root).resolve()
```

</details>

## 🔧 Function `list_changed_files_with_suffixes`

```python
def list_changed_files_with_suffixes(folder: Path, suffixes: set[str]) -> list[Path] | None
```

Return changed files under `folder` matching `suffixes`, or `None` outside Git.

`None` means the caller should fall back to processing the whole tree.
An empty list means no matching dirty files under `folder`.

<details>
<summary>Code:</summary>

```python
def list_changed_files_with_suffixes(folder: Path, suffixes: set[str]) -> list[Path] | None:
    folder = folder.resolve()
    root = git_repo_root(folder)
    if root is None:
        return None
    wanted = {suffix.casefold() if suffix.startswith(".") else f".{suffix.casefold()}" for suffix in suffixes}
    changed: list[Path] = []
    for path in list_git_changed_files(root):
        if path.suffix.casefold() not in wanted:
            continue
        try:
            path.relative_to(folder)
        except ValueError:
            continue
        changed.append(path)
    return sorted(changed, key=lambda item: str(item).casefold())
```

</details>

## 🔧 Function `list_changed_markdown_files`

```python
def list_changed_markdown_files(folder: Path) -> list[Path] | None
```

Return changed Markdown files under `folder`, or `None` when not a Git repo.

Includes `.md` and `.g.md` (any path whose suffix is `.md`).

<details>
<summary>Code:</summary>

```python
def list_changed_markdown_files(folder: Path) -> list[Path] | None:
    return list_changed_files_with_suffixes(folder, {".md"})
```

</details>

## 🔧 Function `list_changed_python_files`

```python
def list_changed_python_files(folder: Path) -> list[Path] | None
```

Return changed `.py` files under `folder`, or `None` when not a Git repo.

`None` means the caller should fall back to processing the whole tree.
An empty list means the repo is clean for Python under `folder`.

<details>
<summary>Code:</summary>

```python
def list_changed_python_files(folder: Path) -> list[Path] | None:
    return list_changed_files_with_suffixes(folder, {".py"})
```

</details>

## 🔧 Function `list_git_changed_files`

```python
def list_git_changed_files(repo: Path) -> list[Path]
```

Return absolute paths of changed, added, and untracked files under `repo`.

Uses `git status --porcelain` (including untracked files). Deleted paths are
omitted. Rename detection is disabled (`--no-renames`) for simpler parsing.

<details>
<summary>Code:</summary>

```python
def list_git_changed_files(repo: Path) -> list[Path]:
    repo = repo.resolve()
    argv = ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all", "--no-renames"]
    proc = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        return []

    paths: list[Path] = []
    seen: set[Path] = set()
    for raw_line in proc.stdout.splitlines():
        line = raw_line.rstrip("\r")
        if len(line) < _PORCELAIN_MIN_LEN:
            continue
        rel = _porcelain_path(line)
        if not rel:
            continue
        absolute = (repo / rel).resolve()
        if not absolute.is_file():
            continue
        if absolute in seen:
            continue
        seen.add(absolute)
        paths.append(absolute)
    return paths
```

</details>
