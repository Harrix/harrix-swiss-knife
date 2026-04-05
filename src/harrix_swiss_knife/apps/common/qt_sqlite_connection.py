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


def qsqlite_temp_connection_name() -> str:
    """Return a unique name for short-lived bootstrap or migration connections."""
    return f"temp_db_{uuid.uuid4().hex[:8]}"


def qsqlite_thread_scoped_connection_name(prefix: str) -> str:
    """Return a unique Qt SQL connection name for the current thread."""
    thread_id = threading.current_thread().ident
    return f"{prefix}_{uuid.uuid4().hex[:8]}_{thread_id}"


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
