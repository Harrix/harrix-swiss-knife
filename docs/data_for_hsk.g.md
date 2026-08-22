---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `data_for_hsk.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DataForHskSetupResult`](#%EF%B8%8F-class-dataforhsksetupresult)
- [🔧 Function `apply_data_for_hsk_to_config`](#-function-apply_data_for_hsk_to_config)
- [🔧 Function `create_data_for_hsk`](#-function-create_data_for_hsk)
- [🔧 Function `needs_data_for_hsk_setup`](#-function-needs_data_for_hsk_setup)
- [🔧 Function `read_notes_folder_names`](#-function-read_notes_folder_names)
- [🔧 Function `suggest_data_for_hsk_root`](#-function-suggest_data_for_hsk_root)

</details>

## 🏛️ Class `DataForHskSetupResult`

```python
class DataForHskSetupResult
```

Outcome of creating `data-for-hsk` on disk and updating config.

<details>
<summary>Code:</summary>

```python
class DataForHskSetupResult:

    data_root: Path
    databases_dir: Path
    notes_dir: Path
    note_folder_paths: tuple[Path, ...]
    created_databases: tuple[str, ...]
    git_repos_created: tuple[str, ...]
    config_updates: dict[str, Any]
```

</details>

## 🔧 Function `apply_data_for_hsk_to_config`

```python
def apply_data_for_hsk_to_config(data_root: Path, notes_folders: tuple[str, ...] | list[str] | None = None, *, init_databases: bool = True, init_git: bool = True, config_path: Path | None = None) -> DataForHskSetupResult
```

Create `data-for-hsk`, then merge path updates into `config.json`.

<details>
<summary>Code:</summary>

```python
def apply_data_for_hsk_to_config(
    data_root: Path,
    notes_folders: tuple[str, ...] | list[str] | None = None,
    *,
    init_databases: bool = True,
    init_git: bool = True,
    config_path: Path | None = None,
) -> DataForHskSetupResult:
    result = create_data_for_hsk(
        data_root,
        notes_folders,
        init_databases=init_databases,
        init_git=init_git,
    )
    path = config_path or get_config_path()
    data = _load_config_dict(path)
    data.update(result.config_updates)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
```

</details>

## 🔧 Function `create_data_for_hsk`

```python
def create_data_for_hsk(data_root: Path, notes_folders: tuple[str, ...] | list[str] | None = None, *, init_databases: bool = True, init_git: bool = True) -> DataForHskSetupResult
```

Create folder tree, optional SQLite DBs, and optional Git repos.

<details>
<summary>Code:</summary>

```python
def create_data_for_hsk(
    data_root: Path,
    notes_folders: tuple[str, ...] | list[str] | None = None,
    *,
    init_databases: bool = True,
    init_git: bool = True,
) -> DataForHskSetupResult:
    folders = tuple(notes_folders or DEFAULT_DATA_FOR_HSK_NOTES_FOLDERS)
    data_root = data_root.expanduser().resolve()
    databases_dir = data_root / "databases"
    notes_dir = data_root / "Notes"
    databases_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    note_folder_paths: list[Path] = []
    for name in folders:
        folder = notes_dir / name
        folder.mkdir(parents=True, exist_ok=True)
        note_folder_paths.append(folder)

    created_databases: list[str] = []
    if init_databases:
        for db_name, recover_sql in _TRACKER_DATABASES:
            db_path = databases_dir / db_name
            if db_path.is_file():
                continue
            if not recover_sql.is_file():
                logger.warning("recover.sql missing for %s: %s", db_name, recover_sql)
                continue
            if QtSqliteDatabaseManagerBase.create_database_from_sql(str(db_path), str(recover_sql)):
                created_databases.append(db_name)
            else:
                logger.warning("Failed to create database %s from %s", db_path, recover_sql)

    git_repos_created: list[str] = []
    if init_git:
        for db_name in TRACKER_DATABASE_NAMES:
            db_path = databases_dir / db_name
            if db_path.is_file() and ensure_sqlite_folder_git_repo(db_path):
                git_repos_created.append(str(databases_dir))
                break
        git_repos_created.extend(str(folder) for folder in note_folder_paths if ensure_folder_git_repo(folder))

    config_updates = build_config_updates(data_root, folders)
    return DataForHskSetupResult(
        data_root=data_root,
        databases_dir=databases_dir,
        notes_dir=notes_dir,
        note_folder_paths=tuple(note_folder_paths),
        created_databases=tuple(created_databases),
        git_repos_created=tuple(git_repos_created),
        config_updates=config_updates,
    )
```

</details>

## 🔧 Function `needs_data_for_hsk_setup`

```python
def needs_data_for_hsk_setup(config: dict[str, Any]) -> bool
```

Return whether the app should offer `data-for-hsk` setup.

<details>
<summary>Code:</summary>

```python
def needs_data_for_hsk_setup(config: dict[str, Any]) -> bool:
    if config.get("data_for_hsk_setup_done"):
        return False

    configured_db_paths = [
        Path(str(config[key])).expanduser()
        for key in SQLITE_CONFIG_KEYS
        if isinstance(config.get(key), str) and not is_config_placeholder_path(config[key])
    ]
    if len(configured_db_paths) == len(SQLITE_CONFIG_KEYS) and all(path.is_file() for path in configured_db_paths):
        return False

    root_value = config.get("data_for_hsk_root")
    if isinstance(root_value, str) and not is_config_placeholder_path(root_value):
        data_root = Path(root_value).expanduser()
        if data_root.is_dir():
            db_dir = data_root / "databases"
            if all((db_dir / name).is_file() for name in TRACKER_DATABASE_NAMES):
                return False

    for key in SQLITE_CONFIG_KEYS:
        value = config.get(key)
        if not isinstance(value, str) or is_config_placeholder_path(value):
            return True
        if "/data/databases/" in value.replace("\\", "/"):
            return True

    return True
```

</details>

## 🔧 Function `read_notes_folder_names`

```python
def read_notes_folder_names(config: dict[str, Any]) -> tuple[str, ...]
```

Return configured note folder names or the built-in default list.

<details>
<summary>Code:</summary>

```python
def read_notes_folder_names(config: dict[str, Any]) -> tuple[str, ...]:
    raw = config.get("data_for_hsk_notes_folders")
    if isinstance(raw, list):
        names = [str(item).strip() for item in raw if str(item).strip()]
        if names:
            return tuple(names)
    return DEFAULT_DATA_FOR_HSK_NOTES_FOLDERS
```

</details>

## 🔧 Function `suggest_data_for_hsk_root`

```python
def suggest_data_for_hsk_root(config: dict[str, Any] | None = None) -> Path
```

Suggest `…/data-for-hsk` next to the install stack (`path_github` or project parent).

<details>
<summary>Code:</summary>

```python
def suggest_data_for_hsk_root(config: dict[str, Any] | None = None) -> Path:
    cfg = config or {}
    github = cfg.get("path_github")
    if isinstance(github, str) and github.strip() and not is_config_placeholder_path(github):
        return Path(github).expanduser().resolve() / "data-for-hsk"
    return get_project_root().parent / "data-for-hsk"
```

</details>
