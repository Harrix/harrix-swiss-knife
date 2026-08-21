"""Tests for Qt SQLite database creation from recover.sql files."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.qt_database_manager_base import QtSqliteDatabaseManagerBase

_FOOD_RECOVER = Path(__file__).resolve().parents[1] / "src" / "harrix_swiss_knife" / "apps" / "food" / "recover.sql"


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for Qt SQL drivers."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_strip_sql_line_comments_keeps_semicolon_inside_strings() -> None:
    text = QtSqliteDatabaseManagerBase._strip_sql_line_comments(
        "INSERT INTO t VALUES ('a;b'); -- trailing note; ignore\nCREATE TABLE x (id INTEGER); -- end\n"
    )
    assert "'a;b'" in text
    assert "trailing note" not in text
    assert "CREATE TABLE x" in text


def test_create_database_from_sql_skips_semicolon_in_comment(tmp_path: Path, qapp: QApplication) -> None:
    """A `;` inside a `--` comment must not break statement splitting."""
    del qapp
    sql_path = tmp_path / "recover.sql"
    sql_path.write_text(
        "-- Schema note: keep food_items; leave food_log empty\n"
        "CREATE TABLE food_items (id INTEGER PRIMARY KEY);\n"
        "CREATE TABLE food_log (id INTEGER PRIMARY KEY);\n",
        encoding="utf-8",
    )
    db_path = tmp_path / "food.db"
    assert QtSqliteDatabaseManagerBase.create_database_from_sql(str(db_path), str(sql_path))
    assert db_path.is_file()
    assert db_path.stat().st_size > 0


def test_create_food_database_from_recover_sql(tmp_path: Path, qapp: QApplication) -> None:
    """Full food recover.sql must create a non-empty database on a fresh install."""
    del qapp
    assert _FOOD_RECOVER.is_file()
    db_path = tmp_path / "food.db"
    assert QtSqliteDatabaseManagerBase.create_database_from_sql(str(db_path), str(_FOOD_RECOVER))
    assert db_path.stat().st_size > 0
