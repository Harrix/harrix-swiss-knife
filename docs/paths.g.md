---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `paths.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `get_action_output_dir`](#-function-get_action_output_dir)
- [🔧 Function `get_config_path`](#-function-get_config_path)
- [🔧 Function `get_config_path_str`](#-function-get_config_path_str)
- [🔧 Function `get_project_root`](#-function-get_project_root)
- [🔧 Function `get_temp_config_path`](#-function-get_temp_config_path)
- [🔧 Function `get_temp_config_path_str`](#-function-get_temp_config_path_str)
- [🔧 Function `list_recent_action_output_files`](#-function-list_recent_action_output_files)
- [🔧 Function `new_action_output_file_path`](#-function-new_action_output_file_path)
- [🔧 Function `prune_action_output_dir`](#-function-prune_action_output_dir)
- [🔧 Function `_sanitize_action_class_stem`](#-function-_sanitize_action_class_stem)

</details>

## 🔧 Function `get_action_output_dir`

```python
def get_action_output_dir() -> Path
```

Return directory for per-run action log files (under project temp/).

<details>
<summary>Code:</summary>

```python
def get_action_output_dir() -> Path:
    return get_project_root() / "temp" / "action_output"
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

## 🔧 Function `_sanitize_action_class_stem`

```python
def _sanitize_action_class_stem(class_name: str) -> str
```

Return a filesystem-safe stem fragment from an action class name.

<details>
<summary>Code:</summary>

```python
def _sanitize_action_class_stem(class_name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_-]+", "_", class_name).strip("_")
    if not s:
        s = "Action"
    return s[:_MAX_ACTION_CLASS_STEM_LEN]
```

</details>
