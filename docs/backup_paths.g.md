---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `backup_paths.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `backup_subdir`](#-function-backup_subdir)
- [🔧 Function `browser_bookmarks_backup_root`](#-function-browser_bookmarks_backup_root)
- [🔧 Function `cursor_backup_root`](#-function-cursor_backup_root)
- [🔧 Function `habits_backup_root`](#-function-habits_backup_root)
- [🔧 Function `musicbee_backup_root`](#-function-musicbee_backup_root)
- [🔧 Function `resolve_backup_dir`](#-function-resolve_backup_dir)
- [🔧 Function `save_commands_backup_root`](#-function-save_commands_backup_root)
- [🔧 Function `ticktick_backup_root`](#-function-ticktick_backup_root)

</details>

## 🔧 Function `backup_subdir`

```python
def backup_subdir(name: str, config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path
```

Return `{path_backups}/{name}`, creating it when missing.

<details>
<summary>Code:</summary>

```python
def backup_subdir(name: str, config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    path = resolve_backup_dir(config, config_path=config_path) / name
    path.mkdir(parents=True, exist_ok=True)
    return path
```

</details>

## 🔧 Function `browser_bookmarks_backup_root`

```python
def browser_bookmarks_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path
```

Return the folder for Chrome/Yandex Bookmarks backups.

<details>
<summary>Code:</summary>

```python
def browser_bookmarks_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    return backup_subdir(_SUBDIR_BROWSER_BOOKMARKS, config, config_path=config_path)
```

</details>

## 🔧 Function `cursor_backup_root`

```python
def cursor_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path
```

Return the folder for Cursor AI ZIP backups.

<details>
<summary>Code:</summary>

```python
def cursor_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    return backup_subdir(_SUBDIR_CURSOR, config, config_path=config_path)
```

</details>

## 🔧 Function `habits_backup_root`

```python
def habits_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path
```

Return the folder for Habits tracker backups.

<details>
<summary>Code:</summary>

```python
def habits_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    return backup_subdir(_SUBDIR_HABITS, config, config_path=config_path)
```

</details>

## 🔧 Function `musicbee_backup_root`

```python
def musicbee_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path
```

Return the shared backups root used by MusicBee (parent of `MusicBee/…`).

<details>
<summary>Code:</summary>

```python
def musicbee_backup_root(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    return resolve_backup_dir(config, config_path=config_path)
```

</details>

## 🔧 Function `resolve_backup_dir`

```python
def resolve_backup_dir(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path
```

Return the shared backups directory from config (see module docstring).

<details>
<summary>Code:</summary>

```python
def resolve_backup_dir(config: dict[str, Any] | None = None, *, config_path: str | None = None) -> Path:
    path_str = config_path or get_config_path_str()
    temp_value = _read_path_backups_from_file(_temp_config_path(path_str))
    if temp_value is not None:
        return temp_value

    file_value = _path_backups_from_mapping(_load_config(path_str))
    if file_value is not None:
        return file_value

    if config is not None:
        provided = _path_backups_from_mapping(config)
        if provided is not None:
            return provided

    return _default_local_backups_dir()
```

</details>

## 🔧 Function `save_commands_backup_root`

```python
def save_commands_backup_root(config: dict[str, Any] | None = None) -> Path
```

Return the folder for Save Commands `state.vscdb` backups.

<details>
<summary>Code:</summary>

```python
def save_commands_backup_root(config: dict[str, Any] | None = None) -> Path:
    return backup_subdir(_SUBDIR_SAVE_COMMANDS, config)
```

</details>

## 🔧 Function `ticktick_backup_root`

```python
def ticktick_backup_root(config: dict[str, Any] | None = None) -> Path
```

Return the folder for TickTick-only backups.

<details>
<summary>Code:</summary>

```python
def ticktick_backup_root(config: dict[str, Any] | None = None) -> Path:
    return backup_subdir(_SUBDIR_TICKTICK, config)
```

</details>
