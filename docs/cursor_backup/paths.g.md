---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `paths.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `cursor_app_data_dir`](#-function-cursor_app_data_dir)
- [🔧 Function `cursor_dot_dir`](#-function-cursor_dot_dir)
- [🔧 Function `cursor_running`](#-function-cursor_running)
- [🔧 Function `cursor_user_dir`](#-function-cursor_user_dir)
- [🔧 Function `discover_project_cursor_dirs`](#-function-discover_project_cursor_dirs)
- [🔧 Function `find_cursor_exe`](#-function-find_cursor_exe)
- [🔧 Function `iter_dot_cursor_entries`](#-function-iter_dot_cursor_entries)
- [🔧 Function `json_safe`](#-function-json_safe)

</details>

## 🔧 Function `cursor_app_data_dir`

```python
def cursor_app_data_dir() -> Path
```

Return `%APPDATA%/Cursor` (or the OS equivalent).

<details>
<summary>Code:</summary>

```python
def cursor_app_data_dir() -> Path:
    return _roaming_app_data() / "Cursor"
```

</details>

## 🔧 Function `cursor_dot_dir`

```python
def cursor_dot_dir() -> Path
```

Return `~/.cursor`.

<details>
<summary>Code:</summary>

```python
def cursor_dot_dir() -> Path:
    return Path.home() / ".cursor"
```

</details>

## 🔧 Function `cursor_running`

```python
def cursor_running() -> bool
```

Return whether the Cursor process appears to be running.

<details>
<summary>Code:</summary>

```python
def cursor_running() -> bool:
    if sys.platform == "win32":
        return is_process_running(_CURSOR_PROCESS)
    return bool(is_process_running(_CURSOR_PROCESS)) or bool(is_process_running("cursor"))
```

</details>

## 🔧 Function `cursor_user_dir`

```python
def cursor_user_dir() -> Path
```

Return the Cursor `User` profile directory (settings, chats, workspaceStorage).

<details>
<summary>Code:</summary>

```python
def cursor_user_dir() -> Path:
    return cursor_app_data_dir() / "User"
```

</details>

## 🔧 Function `discover_project_cursor_dirs`

```python
def discover_project_cursor_dirs(workspace_storage: Path | None = None) -> list[Path]
```

Return unique project `.cursor` folders from `workspaceStorage` `workspace.json` files.

<details>
<summary>Code:</summary>

```python
def discover_project_cursor_dirs(workspace_storage: Path | None = None) -> list[Path]:
    root = workspace_storage if workspace_storage is not None else cursor_user_dir() / "workspaceStorage"
    if not root.is_dir():
        return []
    found: list[Path] = []
    seen: set[Path] = set()
    try:
        children = sorted(root.iterdir(), key=lambda path: path.name.casefold())
    except OSError:
        return []
    for entry in children:
        if not entry.is_dir():
            continue
        meta = entry / "workspace.json"
        project = _project_path_from_workspace_json(meta)
        if project is None:
            continue
        cursor_dir = project / ".cursor"
        try:
            resolved = cursor_dir.resolve()
        except OSError:
            continue
        if resolved in seen or not cursor_dir.is_dir():
            continue
        seen.add(resolved)
        found.append(cursor_dir)
    return found
```

</details>

## 🔧 Function `find_cursor_exe`

```python
def find_cursor_exe() -> Path | None
```

Return the Cursor GUI executable when it can be located on this machine.

<details>
<summary>Code:</summary>

```python
def find_cursor_exe() -> Path | None:
    if sys.platform != "win32":
        which = shutil.which("cursor")
        return Path(which) if which else None
    local = os.environ.get("LOCALAPPDATA", "")
    pf = os.environ.get("PROGRAMFILES") or os.environ.get("ProgramFiles") or ""  # noqa: SIM112
    pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
    candidates: list[Path] = []
    if local:
        candidates.append(Path(local) / "Programs" / "cursor" / "Cursor.exe")
    if pf:
        candidates.append(Path(pf) / "Cursor" / "Cursor.exe")
    if pfx86:
        candidates.append(Path(pfx86) / "Cursor" / "Cursor.exe")
    for path in candidates:
        if path.is_file():
            return path
    which = shutil.which("Cursor.exe") or shutil.which("cursor")
    return Path(which) if which else None
```

</details>

## 🔧 Function `iter_dot_cursor_entries`

```python
def iter_dot_cursor_entries() -> list[Path]
```

Return top-level paths under `~/.cursor` for the home `.cursor` backup part.

Skips `extensions` (separate backup part) and noisy log/tracking folders.

<details>
<summary>Code:</summary>

```python
def iter_dot_cursor_entries() -> list[Path]:
    root = cursor_dot_dir()
    if not root.is_dir():
        return []
    try:
        children = sorted(root.iterdir(), key=lambda path: path.name.casefold())
    except OSError:
        return []
    return [child for child in children if child.name not in _SKIP_DOT_CURSOR_NAMES]
```

</details>

## 🔧 Function `json_safe`

```python
def json_safe(value: Any) -> Any
```

Return a JSON-serializable mirror of simple values (for manifests).

<details>
<summary>Code:</summary>

```python
def json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    return value
```

</details>
