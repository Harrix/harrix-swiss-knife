"""Manual source-text edits clear English so the background translator runs again."""

from __future__ import annotations

from typing import Any

import pytest
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.finance.mixins import AutoSaveOperations as FinanceAutoSave
from harrix_swiss_knife.apps.food.food_log_calories import FOOD_LOG_COL_NAME_EN
from harrix_swiss_knife.apps.food.mixins import AutoSaveOperations as FoodAutoSave

_TX_COL_DESCRIPTION_EN = 1


@pytest.fixture
def qapp() -> QApplication:
    """Ensure a QApplication exists for Qt item models."""
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


class _FinanceDb:
    """Records transaction updates and the description already stored."""

    def __init__(self, description: str) -> None:
        self.description = description
        self.saved: dict[str, Any] | None = None

    def get_transaction_by_id(self, transaction_id: int) -> list[Any]:
        return [transaction_id, 1000, self.description, 1, 1, "2026-09-24", ""]

    def get_id(self, _table: str, _column: str, _name: str) -> int:
        return 1

    def get_currency_by_code(self, code: str) -> tuple[int, str, str]:
        return (1, code, "$")

    def update_transaction(
        self,
        transaction_id: int,
        amount: float,
        description: str,
        category_id: int,
        currency_id: int,
        date: str,
        tag: str = "",
        description_en: str = "",
    ) -> bool:
        self.saved = {
            "id": transaction_id,
            "amount": amount,
            "description": description,
            "category_id": category_id,
            "currency_id": currency_id,
            "date": date,
            "tag": tag,
            "description_en": description_en,
        }
        self.description = description
        return True


class _FinanceHost(FinanceAutoSave):
    def __init__(self, db: _FinanceDb) -> None:
        self.db_manager = db
        self.armed = 0
        self.error = ""

    def _arm_background_transaction_translate_timer(self) -> None:
        self.armed += 1

    def _is_valid_date(self, _date: str) -> bool:
        return True

    def _show_db_error(self, message: str) -> None:
        self.error = message

    def _show_validation_error(self, message: str) -> None:
        self.error = message


class _FoodDb:
    def __init__(self, name: str) -> None:
        self.name = name
        self.saved: dict[str, Any] | None = None

    def get_food_log_records_by_ids(self, record_ids: list[int]) -> list[list[Any]]:
        record_id = record_ids[0]
        return [[record_id, "2026-09-24", 100.0, 50.0, self.name, "Milk", 0]]

    def update_food_log_record(self, record_id: int, **kwargs: Any) -> bool:
        self.saved = {"id": record_id, **kwargs}
        self.name = str(kwargs.get("name") or "")
        return True


class _FoodHost(FoodAutoSave):
    def __init__(self, db: _FoodDb) -> None:
        self.db_manager = db
        self.armed = 0

    def _arm_background_food_translate_timer(self) -> None:
        self.armed += 1

    def _is_valid_date(self, _date: str) -> bool:
        return True


def _transaction_model(description: str, description_en: str, amount: str = "10.00") -> QStandardItemModel:
    model = QStandardItemModel(1, 7)
    values = [description, description_en, amount, "Food", "USD", "2026-09-24", ""]
    for column, value in enumerate(values):
        model.setItem(0, column, QStandardItem(value))
    return model


def _food_model(name: str, name_en: str) -> QStandardItemModel:
    model = QStandardItemModel(1, 7)
    values = [name, "", "100", "50", "2026-09-24", name_en, ""]
    for column, value in enumerate(values):
        model.setItem(0, column, QStandardItem(value))
    return model


def test_changed_transaction_description_clears_english(qapp: QApplication) -> None:
    del qapp
    db = _FinanceDb("Молоко")
    host = _FinanceHost(db)
    model = _transaction_model("Кефир", "Milk")
    signals: list[int] = []
    model.dataChanged.connect(lambda *_args: signals.append(1))

    host._save_transaction_data(model, 0, "7")

    assert host.error == ""
    assert db.saved is not None
    assert db.saved["description"] == "Кефир"
    assert db.saved["description_en"] == ""
    assert model.data(model.index(0, _TX_COL_DESCRIPTION_EN)) == ""
    assert host.armed == 1
    assert signals == []


def test_unchanged_transaction_description_keeps_english(qapp: QApplication) -> None:
    del qapp
    db = _FinanceDb("Молоко")
    host = _FinanceHost(db)
    model = _transaction_model("молоко", "Milk", amount="12.00")

    host._save_transaction_data(model, 0, "7")

    assert db.saved is not None
    assert db.saved["description_en"] == "Milk"
    assert model.data(model.index(0, _TX_COL_DESCRIPTION_EN)) == "Milk"
    assert host.armed == 0


def test_changed_food_name_clears_english(qapp: QApplication) -> None:
    del qapp
    db = _FoodDb("Молоко")
    host = _FoodHost(db)
    model = _food_model("Кефир", "Milk")
    signals: list[int] = []
    model.dataChanged.connect(lambda *_args: signals.append(1))

    host._save_food_log_data(model, 0, "4")

    assert db.saved is not None
    assert db.saved["name"] == "Кефир"
    assert db.saved["name_en"] is None
    assert model.data(model.index(0, FOOD_LOG_COL_NAME_EN)) == ""
    assert host.armed == 1
    assert signals == []


def test_same_food_name_keeps_english(qapp: QApplication) -> None:
    del qapp
    db = _FoodDb("Молоко")
    host = _FoodHost(db)
    model = _food_model("молоко", "Milk")

    host._save_food_log_data(model, 0, "4")

    assert db.saved is not None
    assert db.saved["name"] == "Молоко"
    assert db.saved["name_en"] == "Milk"
    assert host.armed == 0
