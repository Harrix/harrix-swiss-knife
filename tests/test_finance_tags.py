"""Tests for finance tags: text parsing, several tags per transaction, and old-database migration."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QApplication, QLineEdit, QListWidget, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager
from harrix_swiss_knife.apps.finance.delegates.tag_delegate import TagDelegate
from harrix_swiss_knife.apps.finance.tags import format_tag_text, parse_tag_text

RECOVER_SQL = Path(__file__).resolve().parents[1] / "src" / "harrix_swiss_knife" / "apps" / "finance" / "recover.sql"
RUB_ID = 1


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_parse_and_format_tag_text() -> None:
    assert parse_tag_text("  trip, food, trip ,  ") == ["trip", "food"]
    assert parse_tag_text("Trip, trip") == ["Trip"]
    assert format_tag_text(["food", "Trip", "food"]) == "food, Trip"


def test_tag_delegate_writes_checked_and_typed_tags(qapp: QApplication) -> None:
    assert qapp is not None
    model = QStandardItemModel(1, 1)
    model.setData(model.index(0, 0), "gift")
    delegate = TagDelegate(None, tags_provider=lambda: ["gift", "trip"])
    parent = QWidget()
    index = model.index(0, 0)
    editor = delegate.createEditor(parent, QStyleOptionViewItem(), index)
    delegate.setEditorData(editor, index)
    tag_list = editor.findChild(QListWidget)
    assert tag_list is not None
    for row in range(tag_list.count()):
        item = tag_list.item(row)
        assert item is not None
        if item.text() == "trip":
            item.setCheckState(Qt.CheckState.Checked)
    field = editor.findChild(QLineEdit)
    assert field is not None
    field.setText("cafe")
    delegate.setModelData(editor, model, index)
    assert model.data(index) == "cafe, gift, trip"
    editor.close()
    parent.close()


@pytest.fixture
def finance_db(tmp_path: Path, qapp: QApplication) -> Iterator[DatabaseManager]:
    assert qapp is not None
    db_path = tmp_path / "finance.db"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(RECOVER_SQL))
    db = DatabaseManager(str(db_path))
    yield db
    db.close()


def _category_id(db: DatabaseManager, name: str) -> int:
    rows = db.get_rows("SELECT _id FROM categories WHERE name = :name", {"name": name})
    assert rows
    return int(rows[0][0])


def test_transaction_can_keep_several_tags(finance_db: DatabaseManager) -> None:
    category_id = _category_id(finance_db, "Food")
    assert finance_db.add_transaction(12.0, "Lunch", category_id, RUB_ID, "2024-05-01", "trip, food")
    assert finance_db.add_transaction(8.0, "Coffee", category_id, RUB_ID, "2024-05-02", "trip")

    stored = finance_db.get_rows("SELECT _id, tag FROM transactions WHERE description = 'Lunch'")
    assert stored[0][1] == "food, trip"
    lunch_id = int(stored[0][0])
    lunch_ids = {int(row[0]) for row in finance_db.get_transactions_for_tag("food")}
    trip_ids = {int(row[0]) for row in finance_db.get_transactions_for_tag("Trip")}
    assert lunch_id in lunch_ids
    assert lunch_id in trip_ids
    assert finance_db.get_distinct_transaction_tags() == ["food", "trip"]

    assert finance_db.remove_transaction_tag(lunch_id, "food")
    assert finance_db.get_rows("SELECT tag FROM transactions WHERE _id = :id", {"id": lunch_id})[0][0] == "trip"
    assert finance_db.get_transactions_for_tag("food") == []
    totals = finance_db.get_tag_expense_totals_by_currency("trip")
    assert totals
    assert totals[0][1] == "RUB"
    assert totals[0][3] == 2000


def test_legacy_tag_column_is_copied_when_database_opens(tmp_path: Path, qapp: QApplication) -> None:
    assert qapp is not None
    db_path = tmp_path / "legacy.db"
    assert DatabaseManager.create_database_from_sql(str(db_path), str(RECOVER_SQL))
    db = DatabaseManager(str(db_path))
    category_id = _category_id(db, "Transport")
    assert db.add_transaction(30.0, "Taxi", category_id, RUB_ID, "2024-06-01", "legacy")
    assert db.execute_simple_query("DROP TABLE transaction_tags")
    assert db.execute_simple_query("DROP TABLE tags")
    db.close()

    reopened = DatabaseManager(str(db_path))
    assert reopened.get_distinct_transaction_tags() == ["legacy"]
    assert int(reopened.get_rows("SELECT COUNT(*) FROM transaction_tags")[0][0]) == 1
    assert reopened.get_rows("SELECT tag FROM transactions WHERE description = 'Taxi'")[0][0] == "legacy"
    reopened.close()

    again = DatabaseManager(str(db_path))
    assert int(again.get_rows("SELECT COUNT(*) FROM transaction_tags")[0][0]) == 1
    again.close()
