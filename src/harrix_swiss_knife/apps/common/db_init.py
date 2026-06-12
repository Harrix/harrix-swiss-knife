"""Shared database initialisation for tracker applications."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

from PySide6.QtWidgets import QFileDialog

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.qt_database_manager_base import QtSqliteDatabaseManagerBase

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import QWidget

TDbManager = TypeVar("TDbManager", bound=QtSqliteDatabaseManagerBase)


def init_tracker_database(
    parent: QWidget,
    configured_path: Path,
    app_name: str,
    recover_sql_path: Path,
    db_manager_class: type[TDbManager],
    *,
    has_required_tables: Callable[[TDbManager], bool],
    missing_table_label: str,
    on_opened: Callable[[TDbManager], None] | None = None,
) -> TDbManager:
    """Open tracker SQLite database from config, creating from recover.sql if needed.

    Args:

    - `parent` (`QWidget`): Parent widget for dialogs.
    - `configured_path` (`Path`): Database path from application config.
    - `app_name` (`str`): Application name for path fallback resolution.
    - `recover_sql_path` (`Path`): Path to ``recover.sql`` schema file.
    - `db_manager_class` (`type[TDbManager]`): Database manager class to instantiate.
    - `has_required_tables` (`Callable[[TDbManager], bool]`): Returns True when the
      opened database contains the required schema.
    - `missing_table_label` (`str`): Human-readable table name(s) for log messages.
    - `on_opened` (`Callable[[TDbManager], None] | None`): Optional callback invoked
      after a database manager is successfully opened. Defaults to `None`.

    Returns:

    - `TDbManager`: Open database manager instance.

    Raises:

    - `RuntimeError`: When the user cancels database selection or opening fails.

    """
    filename = db_manager_class.resolve_db_path_with_fallback(configured_path, app_name)

    if filename.exists():
        try:
            temp_db_manager = db_manager_class(str(filename))
            if has_required_tables(temp_db_manager):
                print(f"Database opened successfully: {filename}")
                if on_opened is not None:
                    on_opened(temp_db_manager)
                return temp_db_manager
            print(f"Database exists but {missing_table_label} missing at {filename}")
            temp_db_manager.close()
        except Exception as e:
            print(f"Failed to open existing database: {e}")

    if recover_sql_path.exists():
        print(f"Database not found or missing {missing_table_label} at {filename}")
        print(f"Attempting to create database from {recover_sql_path}")
        if db_manager_class.create_database_from_sql(str(filename), str(recover_sql_path)):
            print("Database created successfully from recover.sql")
        else:
            message_box.warning(
                parent,
                "Database Creation Failed",
                f"Failed to create database from {recover_sql_path}\nPlease select an existing database file.",
            )
    else:
        message_box.information(
            parent,
            "Database Not Found",
            f"Database file not found: {filename}\n"
            f"recover.sql file not found: {recover_sql_path}\n"
            "Please select an existing database file.",
        )

    if not filename.exists():
        filename_str, _ = QFileDialog.getOpenFileName(
            parent,
            "Open Database",
            str(filename.parent),
            "SQLite Database (*.db)",
        )
        if not filename_str:
            message_box.critical(parent, "Error", "No database selected")
            msg = "No database selected"
            raise RuntimeError(msg)
        filename = Path(filename_str)

    try:
        db_manager = db_manager_class(str(filename))
        print(f"Database opened successfully: {filename}")
    except (OSError, RuntimeError, ConnectionError) as exc:
        message_box.critical(parent, "Error", f"Failed to open database: {exc}")
        raise

    if on_opened is not None:
        on_opened(db_manager)
    return db_manager
