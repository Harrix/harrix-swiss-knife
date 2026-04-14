"""Shared Qt SQL query execution for app DatabaseManager classes."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtSql import QSqlQuery

logger = logging.getLogger(__name__)


def execute_qt_sql_query(
    *,
    ensure_connection: Callable[[], bool],
    create_query: Callable[[], QSqlQuery],
    query_text: str,
    params: dict[str, Any] | None = None,
) -> QSqlQuery | None:
    """Prepare and execute `query_text` with optional bound `params`.

    Args:

    - `ensure_connection`: Return whether the database connection is usable.
    - `create_query`: Build a `QSqlQuery` bound to the open connection.
    - `query_text`: Parametrised SQL statement.
    - `params`: Values for named placeholders. Defaults to `None`.

    Returns:

    - `QSqlQuery | None`: The executed query when successful, otherwise `None`.

    """
    if not ensure_connection():
        logger.error("Database connection is not available for query execution")
        return None

    try:
        query = create_query()
        if not query.prepare(query_text):
            error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown prepare error"
            logger.error("Failed to prepare Qt SQL query: %s", error_msg)
            return None

        if params:
            for key, value in params.items():
                query.bindValue(f":{key}", value)

        if not query.exec():
            error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown execution error"
            logger.error("Failed to execute Qt SQL query: %s", error_msg)
            return None

    except Exception as e:
        logger.exception("Exception during Qt SQL query execution: %s", e)
        return None

    else:
        return query


def execute_qt_sql_simple(
    *,
    ensure_connection: Callable[[], bool],
    create_query: Callable[[], QSqlQuery],
    query_text: str,
    params: dict[str, Any] | None = None,
) -> bool:
    """Execute INSERT/UPDATE/DELETE and return success; clear query on success.

    Args:

    - `ensure_connection`: Return whether the database connection is usable.
    - `create_query`: Build a `QSqlQuery` bound to the open connection.
    - `query_text`: Parametrised SQL statement.
    - `params`: Values for named placeholders. Defaults to `None`.

    Returns:

    - `bool`: `True` if successful, `False` otherwise.

    """
    if not ensure_connection():
        logger.error("Database connection is not available for query execution")
        return False

    try:
        query = create_query()
        if not query.prepare(query_text):
            error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown prepare error"
            logger.error("Failed to prepare Qt SQL query: %s", error_msg)
            return False

        if params:
            for key, value in params.items():
                query.bindValue(f":{key}", value)

        success = query.exec()
        if not success:
            error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown execution error"
            logger.error("Failed to execute Qt SQL query: %s", error_msg)
            return False

    except Exception as e:
        logger.exception("Exception during Qt SQL query execution: %s", e)
        return False

    else:
        query.clear()
        return True
