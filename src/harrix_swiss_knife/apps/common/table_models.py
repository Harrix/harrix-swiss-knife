"""Qt table model helpers shared across apps."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtGui import QBrush, QIcon, QStandardItem, QStandardItemModel

if TYPE_CHECKING:
    from collections.abc import Sequence

    from PySide6.QtWidgets import QTableView


class ColoredTableProxyModel(QSortFilterProxyModel):
    """Proxy that sorts an icon-only first column by the row database ID."""

    def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Compare icon cells by stored ID; other columns use the default sort."""
        if source_left.column() == 0 and source_right.column() == 0:
            left_id = _sortable_row_id(source_left)
            right_id = _sortable_row_id(source_right)
            if left_id is not None and right_id is not None:
                return left_id < right_id
        return super().lessThan(source_left, source_right)


def append_colored_table_row(
    proxy: QSortFilterProxyModel,
    row: Sequence[object],
    *,
    id_column: int = -2,
    color_column: int = -1,
) -> None:
    """Append one colored row to an existing proxy created by `create_colored_table_proxy_model`."""
    source = proxy.sourceModel()
    if not isinstance(source, QStandardItemModel):
        return
    row_list = list(row)
    row_len = len(row_list)
    id_idx = _normalize_column_index(id_column, row_len)
    color_idx = _normalize_column_index(color_column, row_len)
    row_color = row_list[color_idx]
    row_id = row_list[id_idx]
    display_indices = [i for i in range(row_len) if i not in {id_idx, color_idx}]
    items = [_colored_standard_item(row_list[col_idx], row_color, row_id=row_id) for col_idx in display_indices]
    source.appendRow(items)
    source.setVerticalHeaderItem(source.rowCount() - 1, QStandardItem(str(row_id)))


def create_colored_table_proxy_model(
    data: Sequence[Sequence[object]],
    headers: list[str],
    *,
    id_column: int = -2,
    color_column: int = -1,
) -> QSortFilterProxyModel:
    """Create a colored proxy model with ID and color columns excluded from display.

    By default the ID is at index `-2` and the color at `-1` (last column).
    A `QIcon` cell value is shown as decoration without display text.

    """
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(headers)

    for row_idx, row in enumerate(data):
        row_list = list(row)
        row_len = len(row_list)
        id_idx = _normalize_column_index(id_column, row_len)
        color_idx = _normalize_column_index(color_column, row_len)
        row_color = row_list[color_idx]
        row_id = row_list[id_idx]

        display_indices = [i for i in range(row_len) if i not in {id_idx, color_idx}]
        items = [_colored_standard_item(row_list[col_idx], row_color, row_id=row_id) for col_idx in display_indices]

        model.appendRow(items)
        model.setVerticalHeaderItem(row_idx, QStandardItem(str(row_id)))

    proxy = ColoredTableProxyModel()
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


def next_table_sort_order(
    current_section: int,
    current_order: Qt.SortOrder,
    clicked_section: int,
) -> Qt.SortOrder:
    """Return the sort order after a header click.

    A new column starts ascending. A second click on the same column reverses
    the current order.

    Args:

    - `current_section` (`int`): Column that currently has the sort indicator, or `-1`.
    - `current_order` (`Qt.SortOrder`): Current sort direction.
    - `clicked_section` (`int`): Column the user clicked.

    Returns:

    - `Qt.SortOrder`: Order to apply to `clicked_section`.

    """
    if clicked_section == current_section:
        if current_order == Qt.SortOrder.AscendingOrder:
            return Qt.SortOrder.DescendingOrder
        return Qt.SortOrder.AscendingOrder
    return Qt.SortOrder.AscendingOrder


def sort_table_by_header_click(
    table: QTableView,
    section: int,
    *,
    skip_section: int | None = None,
    current_section: int | None = None,
    current_order: Qt.SortOrder | None = None,
) -> tuple[int, Qt.SortOrder] | None:
    """Sort a table from a header click, optionally ignoring `skip_section`.

    Pass `current_section` and `current_order` from the last applied sort. The
    header indicator cannot be used after a real click: `QHeaderView` already
    toggles it when the indicator is shown.

    Args:

    - `table` (`QTableView`): Table whose proxy/source model supports `sort`.
    - `section` (`int`): Clicked logical column.
    - `skip_section` (`int | None`): Column that must not sort. Defaults to none.
    - `current_section` (`int | None`): Last sorted column, or `None` if unknown.
    - `current_order` (`Qt.SortOrder | None`): Last sort direction, or `None` if unknown.

    Returns:

    - `tuple[int, Qt.SortOrder] | None`: Applied column and order, or `None` when skipped.

    """
    if skip_section is not None and section == skip_section:
        return None
    header = table.horizontalHeader()
    if current_section is None:
        current_section = -1
    if current_order is None:
        current_order = Qt.SortOrder.AscendingOrder
    order = next_table_sort_order(current_section, current_order, section)
    table.sortByColumn(section, order)
    header.setSortIndicatorShown(True)
    header.setSortIndicator(section, order)
    return section, order


def _as_sort_id(value: object) -> int | None:
    """Return `value` as an int ID, or `None` when it is not a numeric ID."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if text.lstrip("-").isdigit():
            return int(text)
    return None


def _colored_standard_item(value: object, row_color: object, *, row_id: object = None) -> QStandardItem:
    """Create a table item, using `QIcon` as decoration when given."""
    if isinstance(value, QIcon):
        item = QStandardItem()
        item.setIcon(value)
        item.setEditable(False)
        sort_id = _as_sort_id(row_id)
        if sort_id is not None:
            item.setData(sort_id, Qt.ItemDataRole.UserRole)
    else:
        item = QStandardItem(str(value) if value is not None else "")
    item.setBackground(QBrush(row_color))
    return item


def _normalize_column_index(index: int, row_length: int) -> int:
    """Resolve negative column indices the same way as list indexing."""
    if index < 0:
        return row_length + index
    return index


def _sortable_row_id(index: QModelIndex | QPersistentModelIndex) -> int | None:
    """Read a numeric ID stored on an icon cell for first-column sorting."""
    return _as_sort_id(index.data(Qt.ItemDataRole.UserRole))
