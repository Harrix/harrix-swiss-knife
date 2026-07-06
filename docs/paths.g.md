---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `paths.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `clear_directory_contents`](#-function-clear_directory_contents)
- [🔧 Function `clear_temp_folder`](#-function-clear_temp_folder)
- [🔧 Function `get_action_output_dir`](#-function-get_action_output_dir)
- [🔧 Function `get_config_path`](#-function-get_config_path)
- [🔧 Function `get_config_path_str`](#-function-get_config_path_str)
- [🔧 Function `get_project_root`](#-function-get_project_root)
- [🔧 Function `get_temp_config_path`](#-function-get_temp_config_path)
- [🔧 Function `get_temp_config_path_str`](#-function-get_temp_config_path_str)
- [🔧 Function `list_recent_action_output_files`](#-function-list_recent_action_output_files)
- [🔧 Function `new_action_output_file_path`](#-function-new_action_output_file_path)
- [🔧 Function `prune_action_output_dir`](#-function-prune_action_output_dir)

</details>

## 🔧 Function `clear_directory_contents`

```python
def clear_directory_contents(directory: Path) -> None
```

Remove all files and subdirectories inside `directory`; the directory itself remains.

<details>
<summary>Code:</summary>

```python
def clear_directory_contents(directory: Path) -> None:
    if not directory.is_dir():
        return
    for child in list(directory.iterdir()):
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
        else:
            with contextlib.suppress(OSError):
                child.unlink()
```

</details>

## 🔧 Function `clear_temp_folder`

```python
def clear_temp_folder(temp_dir: Path | None = None) -> list[str]
```

Clear project `temp/`: empty `images` and `optimized_images`; remove everything else.

Creates `temp/` and reserved subdirectories when missing. Returns human-readable log lines.

<details>
<summary>Code:</summary>

```python
def clear_temp_folder(temp_dir: Path | None = None) -> list[str]:
    root = temp_dir if temp_dir is not None else get_project_root() / "temp"
    root.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    for child in list(root.iterdir()):
        if child.name in TEMP_RESERVED_DIR_NAMES:
            if child.is_dir():
                clear_directory_contents(child)
                lines.append(f"Folder `{child}` is clean.")
            else:
                with contextlib.suppress(OSError):
                    child.unlink()
                lines.append(f"Removed `{child}` (reserved name was not a directory).")
            continue
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
            lines.append(f"Removed folder `{child}`.")
        else:
            with contextlib.suppress(OSError):
                child.unlink()
            lines.append(f"Removed file `{child}`.")

    for name in sorted(TEMP_RESERVED_DIR_NAMES):
        reserved = root / name
        if not reserved.is_dir():
            reserved.mkdir(parents=True, exist_ok=True)
            lines.append(f"Created folder `{reserved}`.")

    if not lines:
        lines.append(f"Folder `{root}` is already clean.")
    return lines
```

</details>

## 🔧 Function `get_action_output_dir`

```python
def get_action_output_dir() -> Path
```

Return directory for per-run action log files (under project `temp/` when writable).

Uses environment variable `HSK_ACTION_OUTPUT_DIR` when set. Otherwise prefers
`<project>/temp/action_output` if the project `temp` directory can be created and
written to; falls back to a per-user data directory when the tree is read-only.

<details>
<summary>Code:</summary>

```python
def get_action_output_dir() -> Path:
    override = os.environ.get("HSK_ACTION_OUTPUT_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()

    root = get_project_root()
    project_temp = root / "temp"
    if _can_use_project_temp_dir(project_temp):
        return project_temp / "action_output"
    return _default_user_action_output_dir()
```

</details>

## 🔧 Function `get_config_path`

```python
def get_config_path() -> Path
```

Return absolute path to main config file.

<details>
<summary>Code:</summary>

```python
def get_config_path() -> Path:
    return get_project_root() / "config" / "config.json"
```

</details>

## 🔧 Function `get_config_path_str`

```python
def get_config_path_str() -> str
```

Return config path as a string (for APIs expecting str).

<details>
<summary>Code:</summary>

```python
def get_config_path_str() -> str:
    return str(get_config_path())
```

</details>

## 🔧 Function `get_project_root`

```python
def get_project_root() -> Path
```

Return project root directory as detected by harrix_pylib.

<details>
<summary>Code:</summary>

```python
def get_project_root() -> Path:
    return h.dev.get_project_root()
```

</details>

## 🔧 Function `get_temp_config_path`

```python
def get_temp_config_path() -> Path
```

Return absolute path to temp config file.

<details>
<summary>Code:</summary>

```python
def get_temp_config_path() -> Path:
    return get_project_root() / "config" / "config-temp.json"
```

</details>

## 🔧 Function `get_temp_config_path_str`

```python
def get_temp_config_path_str() -> str
```

Return temp config path as a string (for APIs expecting str).

<details>
<summary>Code:</summary>

```python
def get_temp_config_path_str() -> str:
    return str(get_temp_config_path())
```

</details>

## 🔧 Function `list_recent_action_output_files`

```python
def list_recent_action_output_files(directory: Path | None = None) -> list[Path]
```

Return up to `limit` newest `*.txt` paths under the action output dir (newest first).

Excludes `pending.txt` (placeholder name before a run assigns a real path).
When `non_empty_only` is true, only files with size greater than zero bytes are included.

<details>
<summary>Code:</summary>

```python
def list_recent_action_output_files(
    directory: Path | None = None,
    *,
    limit: int = DEFAULT_RECENT_ACTION_OUTPUT_LIST_LIMIT,
    non_empty_only: bool = False,
) -> list[Path]:
    root = directory if directory is not None else get_action_output_dir()
    if not root.is_dir():
        return []
    paths = [p for p in root.glob("*.txt") if p.is_file() and p.name != "pending.txt"]
    paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    if non_empty_only:
        paths = [p for p in paths if p.stat().st_size > 0]
    return paths[:limit]
```

</details>

## 🔧 Function `new_action_output_file_path`

```python
def new_action_output_file_path(output_dir: Path, class_name: str) -> Path
```

Return a new unique path `{ClassName}_{uuid12}.txt` under `output_dir`.

<details>
<summary>Code:</summary>

```python
def new_action_output_file_path(output_dir: Path, class_name: str) -> Path:
    stem = _sanitize_action_class_stem(class_name)
    suffix = uuid.uuid4().hex[:12]
    return output_dir / f"{stem}_{suffix}.txt"
```

</details>

## 🔧 Function `prune_action_output_dir`

```python
def prune_action_output_dir(directory: Path | None = None) -> None
```

Delete oldest `*.txt` files in the action output dir, keeping `max_files` newest by mtime.

<details>
<summary>Code:</summary>

```python
def prune_action_output_dir(
    directory: Path | None = None,
    *,
    max_files: int = DEFAULT_MAX_ACTION_OUTPUT_FILES,
) -> None:
    root = directory if directory is not None else get_action_output_dir()
    if not root.is_dir():
        return
    paths = sorted(root.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in paths[max_files:]:
        with contextlib.suppress(OSError):
            path.unlink()
```

</details>
