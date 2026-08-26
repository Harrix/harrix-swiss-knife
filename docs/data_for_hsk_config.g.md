---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `data_for_hsk_config.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_config_updates`](#-function-build_config_updates)
- [🔧 Function `is_config_placeholder_path`](#-function-is_config_placeholder_path)
- [🔧 Function `is_path_parent_creatable`](#-function-is_path_parent_creatable)

</details>

## 🔧 Function `build_config_updates`

```python
def build_config_updates(data_root: Path, notes_folders: tuple[str, ...] | list[str]) -> dict[str, Any]
```

Return `config.json` fields for `data_root` and its Notes subfolders.

<details>
<summary>Code:</summary>

```python
def build_config_updates(data_root: Path, notes_folders: tuple[str, ...] | list[str]) -> dict[str, Any]:
    data_root = data_root.expanduser().resolve()
    databases_dir = data_root / "databases"
    notes_parent = data_root / _NOTES_DIR_NAME
    folder_paths = {name: notes_parent / name for name in notes_folders}

    updates: dict[str, Any] = {
        "data_for_hsk_root": data_root.as_posix(),
        "data_for_hsk_notes_folders": list(notes_folders),
        "data_for_hsk_setup_done": True,
        "sqlite_finance": (databases_dir / "finance.db").as_posix(),
        "sqlite_fitness": (databases_dir / "fitness.db").as_posix(),
        "sqlite_habits": (databases_dir / "habits.db").as_posix(),
        "sqlite_food": (databases_dir / "food.db").as_posix(),
        "sqlite_snippets": (databases_dir / "snippets.db").as_posix(),
    }

    for folder_name, keys in _NOTE_FOLDER_SINGLE_KEYS.items():
        if folder_name not in folder_paths:
            continue
        path_posix = folder_paths[folder_name].as_posix()
        for key in keys:
            updates[key] = path_posix

    all_note_paths = [folder_paths[name].as_posix() for name in notes_folders if name in folder_paths]
    updates["paths_notes"] = all_note_paths
    updates["paths_git"] = [*all_note_paths, databases_dir.as_posix()]
    summary_names = [name for name in ("Notes", "Notes-Diaries") if name in folder_paths]
    updates["paths_notes_for_summaries"] = [folder_paths[name].as_posix() for name in summary_names]

    return updates
```

</details>

## 🔧 Function `is_config_placeholder_path`

```python
def is_config_placeholder_path(value: object) -> bool
```

Return whether `value` is empty or contains a `<YOUR_…>` placeholder.

<details>
<summary>Code:</summary>

```python
def is_config_placeholder_path(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return True
    return bool(_PLACEHOLDER_RE.search(value))
```

</details>

## 🔧 Function `is_path_parent_creatable`

```python
def is_path_parent_creatable(path: Path | str) -> bool
```

Return whether an ancestor of `path` exists as a directory.

Used to skip `mkdir` on missing drives (for example `D:\` on a machine
that has no `D:`).

<details>
<summary>Code:</summary>

```python
def is_path_parent_creatable(path: Path | str) -> bool:
    current = Path(path).expanduser()
    parent = current.parent
    for ancestor in [parent, *parent.parents]:
        try:
            if ancestor.exists():
                return ancestor.is_dir()
        except OSError:
            return False
    return False
```

</details>
