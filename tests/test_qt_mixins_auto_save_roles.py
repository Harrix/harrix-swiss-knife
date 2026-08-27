"""Tests that decoration-only model updates never trigger a row auto-save."""

from __future__ import annotations

from typing import Any

import pytest
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QIcon, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common.qt_mixins import AutoSaveMixin
from harrix_swiss_knife.apps.common.table_models import create_colored_table_proxy_model


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


class _Window(AutoSaveMixin):
    """Minimal auto-save host recording which rows were saved."""

    _SAFE_TABLES: frozenset[str] = frozenset({"exercises"})

    def __init__(self, proxy: Any) -> None:
        self.models = {"exercises": proxy}
        self.saved_rows: list[int] = []
        self._auto_save_handlers = {}
        self._auto_save_source_models = {}

    def _get_save_handlers(self) -> dict[str, Any]:
        return {"exercises": self._save_row}

    def _save_row(self, _model: QStandardItemModel, row: int, _row_id: str) -> None:
        self.saved_rows.append(row)

    def _validate_database_connection(self) -> bool:
        return True


def _build_window() -> tuple[_Window, QStandardItemModel]:
    proxy = create_colored_table_proxy_model(
        [["Push ups", "times", 1, Qt.GlobalColor.white]],
        ["Name", "Unit"],
        id_column=2,
    )
    source = proxy.sourceModel()
    assert isinstance(source, QStandardItemModel)
    return _Window(proxy), source


def test_decoration_change_does_not_auto_save(qapp: object) -> None:
    del qapp
    window, source = _build_window()
    index = source.index(0, 0)

    window._on_table_data_changed("exercises", index, index, [Qt.ItemDataRole.DecorationRole])

    assert window.saved_rows == []


def test_display_change_still_auto_saves(qapp: object) -> None:
    del qapp
    window, source = _build_window()
    index = source.index(0, 0)

    window._on_table_data_changed("exercises", index, index, [Qt.ItemDataRole.DisplayRole])

    assert window.saved_rows == [0]


def test_unspecified_roles_still_auto_save(qapp: object) -> None:
    del qapp
    window, source = _build_window()
    index = source.index(0, 0)

    window._on_table_data_changed("exercises", index, index, [])

    assert window.saved_rows == [0]


def test_set_icon_on_item_does_not_auto_save(qapp: object) -> None:
    del qapp
    window, source = _build_window()
    window._connect_table_auto_save_signal("exercises")

    item = source.item(0, 0)
    assert isinstance(item, QStandardItem)
    item.setIcon(QIcon())

    assert window.saved_rows == []


def test_set_text_on_item_auto_saves(qapp: object) -> None:
    del qapp
    window, source = _build_window()
    window._connect_table_auto_save_signal("exercises")

    item = source.item(0, 0)
    assert isinstance(item, QStandardItem)
    item.setText("Pull ups")

    assert window.saved_rows == [0]


def test_invalid_index_range_is_ignored(qapp: object) -> None:
    del qapp
    window, _source = _build_window()

    window._on_table_data_changed("weight", QModelIndex(), QModelIndex(), [Qt.ItemDataRole.DisplayRole])

    assert window.saved_rows == []
