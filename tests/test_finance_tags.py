"""Tests for finance tags: text parsing, several tags per transaction, and old-database migration."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap, QStandardItemModel
from PySide6.QtWidgets import QApplication, QStyleOptionViewItem, QWidget

from harrix_swiss_knife.apps.finance.database_manager import DatabaseManager
from harrix_swiss_knife.apps.finance.delegates.tag_delegate import TagCheckListEditor, TagDelegate
from harrix_swiss_knife.apps.finance.tags import format_tag_text, parse_tag_text
from harrix_swiss_knife.fluent.widgets.button_base import FluentPushButton
from harrix_swiss_knife.fluent.widgets.buttons import FluentCheckBox, FluentPrimaryButton
from harrix_swiss_knife.fluent.widgets.input_base import FluentLineEdit

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
    boxes = editor.findChildren(FluentCheckBox)
    assert {box.text() for box in boxes} == {"gift", "trip"}
    for box in boxes:
        if box.text() == "trip":
            box.setChecked(True)
        if box.text() == "gift":
            assert box.isChecked()
    field = editor.findChild(FluentLineEdit)
    assert field is not None
    field.setText("cafe")
    delegate.setModelData(editor, model, index)
    assert model.data(index) == "cafe, gift, trip"
    editor.close()
    parent.close()


def test_tag_delegate_paints_chips_without_plain_text(qapp: QApplication) -> None:
    assert qapp is not None
    model = QStandardItemModel(1, 1)
    model.setData(model.index(0, 0), "trip, food")
    delegate = TagDelegate(None, tags=["trip", "food"])
    option = QStyleOptionViewItem()
    option.rect = option.rect.adjusted(0, 0, 200, 28)
    option.rect.setRect(0, 0, 200, 28)
    pixmap = QPixmap(200, 28)
    pixmap.fill(Qt.GlobalColor.white)
    painter = QPainter(pixmap)
    delegate.paint(painter, option, model.index(0, 0))
    painter.end()
    image = pixmap.toImage()
    assert any(
        image.pixelColor(x, y) != Qt.GlobalColor.white for y in range(image.height()) for x in range(image.width())
    )


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
    # "trip, food" is stored as links in first-seen parse order → trip then food by _id.
    assert finance_db.get_distinct_transaction_tags() == ["trip", "food"]

    assert finance_db.remove_transaction_tag(lunch_id, "food")
    assert finance_db.get_rows("SELECT tag FROM transactions WHERE _id = :id", {"id": lunch_id})[0][0] == "trip"
    assert finance_db.get_transactions_for_tag("food") == []
    totals = finance_db.get_tag_expense_totals_by_currency("trip")
    assert totals
    assert totals[0][1] == "RUB"
    assert totals[0][3] == 2000


def test_distinct_tags_follow_appearance_order_and_refresh(finance_db: DatabaseManager) -> None:
    """New tags from a later transaction appear at the end when the picker refreshes."""
    category_id = _category_id(finance_db, "Food")
    assert finance_db.add_transaction(5.0, "A", category_id, RUB_ID, "2024-05-01", "alpha")
    assert finance_db.get_distinct_transaction_tags() == ["alpha"]
    assert finance_db.add_transaction(6.0, "B", category_id, RUB_ID, "2024-05-02", "beta")
    assert finance_db.get_distinct_transaction_tags() == ["alpha", "beta"]
    assert finance_db.add_transaction(7.0, "C", category_id, RUB_ID, "2024-05-03", "alpha, gamma")
    assert finance_db.get_distinct_transaction_tags() == ["alpha", "beta", "gamma"]


def test_tag_checklist_has_ok_and_close_buttons(qapp: QApplication) -> None:
    """Tag picker exposes OK / Close so the window is not Enter-only."""
    assert qapp is not None
    parent = QWidget()
    editor = TagCheckListEditor(["gift", "trip"], ["gift"], parent)
    assert editor.findChild(FluentPrimaryButton) is not None
    assert any(button.text() == "Close" for button in editor.findChildren(FluentPushButton))
    accepted: list[bool] = []
    rejected: list[bool] = []
    editor.accepted.connect(lambda: accepted.append(True))
    editor.rejected.connect(lambda: rejected.append(True))
    ok = editor.findChild(FluentPrimaryButton)
    assert ok is not None
    ok.click()
    assert accepted == [True]
    close = next(button for button in editor.findChildren(FluentPushButton) if button.text() == "Close")
    close.click()
    assert rejected == [True]
    editor.close()
    parent.close()


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
