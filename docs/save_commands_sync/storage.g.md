---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `storage.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `SaveCommandsStorageError`](#%EF%B8%8F-class-savecommandsstorageerror)
- [🔧 Function `connect_state_db`](#-function-connect_state_db)
- [🔧 Function `copy_state_db`](#-function-copy_state_db)
- [🔧 Function `dump_state_payload`](#-function-dump_state_payload)
- [🔧 Function `normalize_state`](#-function-normalize_state)
- [🔧 Function `read_save_commands_state`](#-function-read_save_commands_state)
- [🔧 Function `write_save_commands_state`](#-function-write_save_commands_state)

</details>

## 🏛️ Class `SaveCommandsStorageError`

```python
class SaveCommandsStorageError(OSError)
```

`state.vscdb` is missing, locked, or not a VS Code global-state database.

<details>
<summary>Code:</summary>

```python
class SaveCommandsStorageError(OSError):
```

</details>

## 🔧 Function `connect_state_db`

```python
def connect_state_db(path: Path, *, timeout_s: float = 30.0) -> sqlite3.Connection
```

Open `state.vscdb` with a busy timeout.

<details>
<summary>Code:</summary>

```python
def connect_state_db(path: Path, *, timeout_s: float = 30.0) -> sqlite3.Connection:
    if not path.is_file():
        msg = f"VS Code state database not found: {path}"
        raise SaveCommandsStorageError(msg)
    try:
        conn = sqlite3.connect(str(path), timeout=timeout_s)
    except sqlite3.Error as exc:
        msg = f"Cannot open VS Code state database {path}: {exc}"
        raise SaveCommandsStorageError(msg) from exc
    conn.execute(f"PRAGMA busy_timeout = {int(timeout_s * 1000)}")
    return conn
```

</details>

## 🔧 Function `copy_state_db`

```python
def copy_state_db(source: Path, dest: Path) -> Path
```

Copy `source` (including WAL) into `dest` via the SQLite backup API.

<details>
<summary>Code:</summary>

```python
def copy_state_db(source: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    src = connect_state_db(source)
    dst = sqlite3.connect(str(dest))
    try:
        src.backup(dst)
        dst.commit()
    except sqlite3.Error as exc:
        msg = f"Cannot backup VS Code state database {source}: {exc}"
        raise SaveCommandsStorageError(msg) from exc
    finally:
        dst.close()
        src.close()
    return dest
```

</details>

## 🔧 Function `dump_state_payload`

```python
def dump_state_payload(commands: list[dict[str, Any]], folders: list[dict[str, Any]]) -> str
```

Serialize global Save Commands memento the way the extension stores it.

<details>
<summary>Code:</summary>

```python
def dump_state_payload(commands: list[dict[str, Any]], folders: list[dict[str, Any]]) -> str:
    return json.dumps(
        {"command_folders": folders, "commands": commands},
        ensure_ascii=False,
        separators=(",", ":"),
    )
```

</details>

## 🔧 Function `normalize_state`

```python
def normalize_state(raw: Any) -> dict[str, list[dict[str, Any]]]
```

Return `{commands, command_folders}` lists from a memento object or `None`.

<details>
<summary>Code:</summary>

```python
def normalize_state(raw: Any) -> dict[str, list[dict[str, Any]]]:
    commands: list[dict[str, Any]] = []
    folders: list[dict[str, Any]] = []
    if isinstance(raw, dict):
        raw_commands = raw.get("commands")
        raw_folders = raw.get("command_folders")
        if isinstance(raw_commands, list):
            commands = [item for item in raw_commands if isinstance(item, dict)]
        if isinstance(raw_folders, list):
            folders = [item for item in raw_folders if isinstance(item, dict)]
    return {"commands": commands, "command_folders": folders}
```

</details>

## 🔧 Function `read_save_commands_state`

```python
def read_save_commands_state(path: Path) -> dict[str, list[dict[str, Any]]]
```

Load global Save Commands from `ItemTable`, or empty lists if the key is missing.

<details>
<summary>Code:</summary>

```python
def read_save_commands_state(path: Path) -> dict[str, list[dict[str, Any]]]:
    conn = connect_state_db(path)
    try:
        raw = _read_item_json(conn, STATE_ITEM_KEY)
    except sqlite3.Error as exc:
        msg = f"Cannot read Save Commands from {path}: {exc}"
        raise SaveCommandsStorageError(msg) from exc
    finally:
        conn.close()
    return normalize_state(raw)
```

</details>

## 🔧 Function `write_save_commands_state`

```python
def write_save_commands_state(path: Path, commands: list[dict[str, Any]], folders: list[dict[str, Any]]) -> None
```

Replace the Save Commands memento in `ItemTable` (creates the row if needed).

<details>
<summary>Code:</summary>

```python
def write_save_commands_state(
    path: Path,
    commands: list[dict[str, Any]],
    folders: list[dict[str, Any]],
) -> None:
    payload = dump_state_payload(commands, folders)
    conn = connect_state_db(path)
    try:
        _ensure_item_table(conn)
        conn.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", (STATE_ITEM_KEY, payload))
        conn.commit()
        with conn:
            conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
    except sqlite3.Error as exc:
        msg = f"Cannot write Save Commands to {path}: {exc}"
        raise SaveCommandsStorageError(msg) from exc
    finally:
        conn.close()
```

</details>
