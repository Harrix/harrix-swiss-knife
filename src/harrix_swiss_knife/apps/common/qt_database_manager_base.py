"""Shared base class for Qt-based SQLite database managers.

This module centralises the connection lifecycle and common query helpers used
across app-specific `DatabaseManager` implementations.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator

from PySide6.QtCore import QTimer
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from harrix_swiss_knife.apps.common.qt_sql_runner import execute_qt_sql_query, execute_qt_sql_simple
from harrix_swiss_knife.apps.common.qt_sqlite_connection import (
    open_thread_scoped_qsqlite,
    qsqlite_temp_connection_name,
    reconnect_thread_scoped_qsqlite,
    try_add_open_qsqlite,
)

logger = logging.getLogger(__name__)


class DatabaseConnectionUnavailableError(ConnectionError):
    """Database connection is not available."""

    def __init__(self) -> None:
        """Create exception with standard message."""
        super().__init__("❌ Database connection is not available")


class QtSqliteDatabaseManagerBase:
    """Base class that manages a thread-scoped Qt SQLite connection."""

    db: QSqlDatabase | None
    connection_name: str

    _db_filename: str
    _connection_prefix: str
    _db_closed: bool

    def __init__(self, *, prefix: str, db_filename: str) -> None:
        """Create manager bound to `db_filename` for the current thread."""
        self._connection_prefix = prefix
        self._db_filename = db_filename
        self.connection_name, self.db = open_thread_scoped_qsqlite(prefix, db_filename)
        self._db_closed = False

    def close(self) -> None:
        """Close the database connection and remove it from Qt registry."""
        if self._db_closed:
            return
        self._db_closed = True
        connection_name = self.connection_name
        db = getattr(self, "db", None)
        if db is not None and db.isValid():
            db.close()
        self.db = None
        QTimer.singleShot(0, lambda n=connection_name: QSqlDatabase.removeDatabase(n))

    @staticmethod
    def create_database_from_sql(db_filename: str, sql_file_path: str) -> bool:
        """Create a new database from an SQL file."""
        try:
            db_path = Path(db_filename)
            db_path.parent.mkdir(parents=True, exist_ok=True)

            sql_path = Path(sql_file_path)
            if not sql_path.exists():
                logger.error("SQL file not found: %s", sql_file_path)
                return False

            sql_content = sql_path.read_text(encoding="utf-8")

            temp_connection_name = qsqlite_temp_connection_name()
            temp_db, open_err = try_add_open_qsqlite(temp_connection_name, db_filename)
            if open_err is not None or temp_db is None:
                logger.error("Failed to create database: %s", open_err or "Unknown error")
                return False

            try:
                query = QSqlQuery(temp_db)
                statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
                for statement in statements:
                    if not query.exec(statement):
                        error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown error"
                        logger.error("Failed to execute SQL statement: %s", error_msg)
                        return False

                logger.info("Database created successfully: %s", db_filename)
                return True
            finally:
                temp_db.close()
                QSqlDatabase.removeDatabase(temp_connection_name)
        except Exception as e:
            logger.exception("Error creating database from SQL file: %s", e)
            return False

    def execute_query(self, query_text: str, params: dict[str, Any] | None = None) -> QSqlQuery | None:
        """Prepare and execute `query_text` with optional bound `params`."""
        return execute_qt_sql_query(
            ensure_connection=self._ensure_connection,
            create_query=self._create_query,
            query_text=query_text,
            params=params,
        )

    def execute_simple_query(self, query_text: str, params: dict[str, Any] | None = None) -> bool:
        """Execute INSERT/UPDATE/DELETE and return success status."""
        return execute_qt_sql_simple(
            ensure_connection=self._ensure_connection,
            create_query=self._create_query,
            query_text=query_text,
            params=params,
        )

    def get_rows(self, query_text: str, params: dict[str, Any] | None = None) -> list[list[Any]]:
        """Execute `query_text` and fetch the full result set."""
        query = self.execute_query(query_text, params)
        if query:
            result = self.rows_from_query(query)
            query.clear()
            return result
        return []

    def is_database_open(self) -> bool:
        """Return whether Qt connection is open and valid."""
        return hasattr(self, "db") and self.db is not None and self.db.isValid() and self.db.isOpen()

    def rows_from_query(self, query: QSqlQuery) -> list[list[Any]]:
        """Convert the full result set in `query` into a list of rows."""
        result: list[list[Any]] = []
        while query.next():
            row = [query.value(i) for i in range(query.record().count())]
            result.append(row)
        return result

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        if not self.is_database_open():
            return False
        query = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name",
            {"table_name": table_name},
        )
        return bool(query and query.next())

    def _create_query(self) -> QSqlQuery:
        if not self._ensure_connection() or self.db is None:
            raise DatabaseConnectionUnavailableError
        return QSqlQuery(self.db)

    def _ensure_connection(self) -> bool:
        if not hasattr(self, "db") or self.db is None or not self.db.isValid():
            logger.warning("Database object is invalid, attempting to reconnect")
            try:
                self._reconnect()
                return self.db is not None and self.db.isOpen()
            except Exception as e:
                logger.exception("Failed to reconnect to database: %s", e)
                return False

        if self.db is None or not self.db.isOpen():
            logger.warning("Database connection is closed, attempting to reopen")
            if self.db is None or not self.db.open():
                error_msg = self.db.lastError().text() if self.db and self.db.lastError().isValid() else "Unknown error"
                logger.error("Failed to reopen database: %s", error_msg)
                try:
                    self._reconnect()
                    return self.db is not None and self.db.isOpen()
                except Exception as e:
                    logger.exception("Failed to reconnect to database: %s", e)
                    return False

        return True

    def _iter_query(self, query: QSqlQuery | None) -> Iterator[QSqlQuery]:
        if query is None:
            return
        while query.next():
            yield query

    def _reconnect(self) -> None:
        self.connection_name, self.db = reconnect_thread_scoped_qsqlite(
            connection_name=self.connection_name,
            db=self.db,
            prefix=self._connection_prefix,
            db_filename=self._db_filename,
        )
        self._db_closed = False
