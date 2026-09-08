"""Read and write Save Commands globalState in VS Code `state.vscdb`."""

from __future__ import annotations

import json
import sqlite3
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.save_commands_sync.editors import EXTENSION_ID

if TYPE_CHECKING:
    from pathlib import Path

STATE_ITEM_KEY = EXTENSION_ID
_ITEM_TABLE = "ItemTable"


class SaveCommandsStorageError(OSError):
    """`state.vscdb` is missing, locked, or not a VS Code global-state database."""


def connect_state_db(path: Path, *, timeout_s: float = 30.0) -> sqlite3.Connection:
    """Open `state.vscdb` with a busy timeout."""
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


def copy_state_db(source: Path, dest: Path) -> Path:
    """Copy `source` (including WAL) into `dest` via the SQLite backup API."""
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


def dump_state_payload(commands: list[dict[str, Any]], folders: list[dict[str, Any]]) -> str:
    """Serialize global Save Commands memento the way the extension stores it."""
    return json.dumps(
        {"command_folders": folders, "commands": commands},
        ensure_ascii=False,
        separators=(",", ":"),
    )


def normalize_state(raw: Any) -> dict[str, list[dict[str, Any]]]:
    """Return `{commands, command_folders}` lists from a memento object or `None`."""
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


def read_save_commands_state(path: Path) -> dict[str, list[dict[str, Any]]]:
    """Load global Save Commands from `ItemTable`, or empty lists if the key is missing."""
    conn = connect_state_db(path)
    try:
        raw = _read_item_json(conn, STATE_ITEM_KEY)
    except sqlite3.Error as exc:
        msg = f"Cannot read Save Commands from {path}: {exc}"
        raise SaveCommandsStorageError(msg) from exc
    finally:
        conn.close()
    return normalize_state(raw)


def write_save_commands_state(
    path: Path,
    commands: list[dict[str, Any]],
    folders: list[dict[str, Any]],
) -> None:
    """Replace the Save Commands memento in `ItemTable` (creates the row if needed)."""
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


def _ensure_item_table(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (_ITEM_TABLE,),
    ).fetchone()
    if row is None:
        msg = f"{_ITEM_TABLE} is missing; not a VS Code globalStorage database"
        raise SaveCommandsStorageError(msg)


def _read_item_json(conn: sqlite3.Connection, key: str) -> Any:
    _ensure_item_table(conn)
    row = conn.execute("SELECT value FROM ItemTable WHERE key = ?", (key,)).fetchone()
    if row is None:
        return None
    value = row[0]
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        msg = f"Save Commands value for {key} is not valid JSON: {exc}"
        raise SaveCommandsStorageError(msg) from exc
