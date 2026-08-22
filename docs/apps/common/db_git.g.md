---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `db_git.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `ensure_folder_git_repo`](#-function-ensure_folder_git_repo)
- [🔧 Function `ensure_sqlite_folder_git_repo`](#-function-ensure_sqlite_folder_git_repo)
- [🔧 Function `sqlite_folder_git_commit_message`](#-function-sqlite_folder_git_commit_message)

</details>

## 🔧 Function `ensure_folder_git_repo`

```python
def ensure_folder_git_repo(folder: Path) -> bool
```

Create a Git repo in `folder` with an initial `.gitkeep` commit when `.git` is missing.

Args:

- `folder` (`Path`): Directory to initialize as a Git repository.

Returns:

- `bool`: `True` when a new repository was created and committed.

<details>
<summary>Code:</summary>

```python
def ensure_folder_git_repo(folder: Path) -> bool:
    resolved = Path(folder).expanduser().resolve()
    if not resolved.is_dir():
        resolved.mkdir(parents=True, exist_ok=True)
    if (resolved / ".git").exists():
        return False
    if shutil.which("git") is None:
        logger.warning("git is not on PATH; skipped repository for %s", resolved)
        return False

    gitkeep = resolved / ".gitkeep"
    if not gitkeep.is_file():
        gitkeep.write_text("", encoding="utf-8")

    code, output = run_argv_output(["git", "init"], cwd=resolved)
    if code != 0:
        logger.warning("git init failed in %s: %s", resolved, output)
        return False

    _ensure_git_identity(resolved)
    code, output = run_argv_output(["git", "add", "--", ".gitkeep"], cwd=resolved)
    if code != 0:
        logger.warning("git add failed for %s: %s", resolved, output)
        return False

    day = datetime.now(tz=UTC).astimezone().date()
    message = f"➕ Add .gitkeep ({day.isoformat()})"  # noqa: RUF001
    code, output = run_argv_output(["git", "commit", "-m", message], cwd=resolved)
    if code != 0:
        logger.warning("git commit failed in %s: %s", resolved, output)
        return False

    logger.info("Created git repository in %s (%s)", resolved, message)
    return True
```

</details>

## 🔧 Function `ensure_sqlite_folder_git_repo`

```python
def ensure_sqlite_folder_git_repo(db_path: Path) -> bool
```

Create a Git repo in the database folder and commit the SQLite file if needed.

When the folder already has `.git`, do nothing. Used both after creating a
database from `recover.sql` and when opening an existing file.

Args:

- `db_path` (`Path`): Path to the SQLite file.

Returns:

- `bool`: `True` when a new repository was created and the file was committed.

<details>
<summary>Code:</summary>

```python
def ensure_sqlite_folder_git_repo(db_path: Path) -> bool:
    resolved = Path(db_path).expanduser().resolve()
    if not resolved.is_file():
        return False
    folder = resolved.parent
    if not folder.is_dir() or (folder / ".git").exists():
        return False
    if shutil.which("git") is None:
        logger.warning("git is not on PATH; skipped repository for %s", folder)
        return False

    code, output = run_argv_output(["git", "init"], cwd=folder)
    if code != 0:
        logger.warning("git init failed in %s: %s", folder, output)
        return False

    _ensure_git_identity(folder)
    code, output = run_argv_output(["git", "add", "--", resolved.name], cwd=folder)
    if code != 0:
        logger.warning("git add failed for %s: %s", resolved, output)
        return False

    message = sqlite_folder_git_commit_message(resolved)
    code, output = run_argv_output(["git", "commit", "-m", message], cwd=folder)
    if code != 0:
        logger.warning("git commit failed in %s: %s", folder, output)
        return False

    logger.info("Created git repository in %s (%s)", folder, message)
    return True
```

</details>

## 🔧 Function `sqlite_folder_git_commit_message`

```python
def sqlite_folder_git_commit_message(db_path: Path, *, on: date | None = None) -> str
```

Return the initial commit subject for a tracker SQLite file.

Args:

- `db_path` (`Path`): Path to the SQLite file (only the filename is used).
- `on` (`date | None`): Date in the subject. Defaults to today.

Returns:

- `str`: Subject with Add prefix, filename, and ISO date.

<details>
<summary>Code:</summary>

```python
def sqlite_folder_git_commit_message(db_path: Path, *, on: date | None = None) -> str:
    day = on or datetime.now(tz=UTC).astimezone().date()
    return f"➕ Add {Path(db_path).name} ({day.isoformat()})"  # noqa: RUF001
```

</details>
