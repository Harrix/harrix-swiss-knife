"""Qt table model helpers shared across apps."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtGui import QBrush, QStandardItem, QStandardItemModel

if TYPE_CHECKING:
    from collections.abc import Sequence


def create_colored_table_proxy_model(
    data: Sequence[Sequence[object]],
    headers: list[str],
    *,
    id_column: int = -2,
    color_column: int = -1,
) -> QSortFilterProxyModel:
    """Create a colored proxy model with ID and color columns excluded from display.

    By default the ID is at index ``-2`` and the color at ``-1`` (last column).
    """
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(headers)

    for row_idx, row in enumerate(data):
        row_list = list(row)
        row_color = row_list[color_column]
        row_id = row_list[id_column]

        display_indices = [i for i in range(len(row_list)) if i not in {id_column, color_column}]
        items = []
        for col_idx in display_indices:
            value = row_list[col_idx]
            item = QStandardItem(str(value) if value is not None else "")
            item.setBackground(QBrush(row_color))
            items.append(item)

        model.appendRow(items)
        model.setVerticalHeaderItem(row_idx, QStandardItem(str(row_id)))

    proxy = QSortFilterProxyModel()
    proxy.setSourceModel(model)
    return proxy


def create_table_proxy_model(
    data: Sequence[Sequence[object]],
    headers: list[str],
    *,
    id_column: int = 0,
) -> QSortFilterProxyModel:
    """Create a proxy model with row IDs stored in the vertical header.

    The `id_column` is excluded from displayed columns and is stored as vertical header text.
    """
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(headers)

    for row_idx, row in enumerate(data):
        items = [
            QStandardItem("" if value is None else str(value))
            for col_idx, value in enumerate(row)
            if col_idx != id_column
        ]
        model.appendRow(items)
        model.setVerticalHeaderItem(row_idx, QStandardItem(str(row[id_column])))

    proxy = QSortFilterProxyModel()
    proxy.setSourceModel(model)
    return proxy
