---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `git_cmd.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `git_porcelain`](#-function-git_porcelain)
- [🔧 Function `git_run`](#-function-git_run)

</details>

## 🔧 Function `git_porcelain`

```python
def git_porcelain(repo: Path) -> str
```

Return `git status --porcelain` output for `repo`.

<details>
<summary>Code:</summary>

```python
def git_porcelain(repo: Path) -> str:
    proc = git_run(repo, "status", "--porcelain")
    return proc.stdout if proc.returncode == 0 else ""
```

</details>

## 🔧 Function `git_run`

```python
def git_run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]
```

Run a Git command in `cwd` and return the completed process.

<details>
<summary>Code:</summary>

```python
def git_run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],  # noqa: S607
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
```

</details>
