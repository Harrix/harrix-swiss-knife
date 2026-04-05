"""Shared Qt SQLite helpers: QSQLITE driver, connection naming, and open."""

from __future__ import annotations

import threading
import uuid

from PySide6.QtSql import QSqlDatabase


def add_open_qsqlite(
    connection_name: str,
    db_filename: str,
    *,
    failure_label: str = "Failed to open the database",
) -> QSqlDatabase:
    """Register QSQLITE, set the database file path, and open.

    Raises:
        ConnectionError: If the database cannot be opened. The connection is
            removed from Qt's registry before raising.

    """
    db = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    db.setDatabaseName(db_filename)
    if not db.open():
        detail = db.lastError().text() if db.lastError().isValid() else "Unknown database error"
        QSqlDatabase.removeDatabase(connection_name)
        msg = f"❌ {failure_label}: {detail}"
        raise ConnectionError(msg)
    return db


def close_and_remove_qsqlite(connection_name: str | None, db: QSqlDatabase | None) -> None:
    """Close `db` if it is open, then drop `connection_name` from Qt's registry."""
    if db is not None and db.isValid():
        db.close()
    if connection_name:
        QSqlDatabase.removeDatabase(connection_name)


def open_thread_scoped_qsqlite(
    prefix: str,
    db_filename: str,
    *,
    failure_label: str = "Failed to open the database",
) -> tuple[str, QSqlDatabase]:
    """Build a per-thread connection name, register QSQLITE, open, return `(name, db)`."""
    connection_name = qsqlite_thread_scoped_connection_name(prefix)
    database = add_open_qsqlite(connection_name, db_filename, failure_label=failure_label)
    return connection_name, database


def qsqlite_temp_connection_name() -> str:
    """Return a unique name for short-lived bootstrap or migration connections."""
    return f"temp_db_{uuid.uuid4().hex[:8]}"


def qsqlite_thread_scoped_connection_name(prefix: str) -> str:
    """Return a unique Qt SQL connection name for the current thread."""
    thread_id = threading.current_thread().ident
    return f"{prefix}_{uuid.uuid4().hex[:8]}_{thread_id}"


def reconnect_thread_scoped_qsqlite(
    *,
    connection_name: str | None,
    db: QSqlDatabase | None,
    prefix: str,
    db_filename: str,
    failure_label: str = "Failed to reconnect to database",
) -> tuple[str, QSqlDatabase]:
    """Close/remove the old Qt SQL connection and open a new thread-scoped SQLite connection."""
    close_and_remove_qsqlite(connection_name, db)
    return open_thread_scoped_qsqlite(prefix, db_filename, failure_label=failure_label)


def try_add_open_qsqlite(connection_name: str, db_filename: str) -> tuple[QSqlDatabase | None, str | None]:
    """Like `add_open_qsqlite` but return `(None, error_detail)` instead of raising.

    On failure, the connection is removed from Qt's registry.
    """
    db = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    db.setDatabaseName(db_filename)
    if not db.open():
        detail = db.lastError().text() if db.lastError().isValid() else "Unknown error"
        QSqlDatabase.removeDatabase(connection_name)
        return None, detail
    return db, None
