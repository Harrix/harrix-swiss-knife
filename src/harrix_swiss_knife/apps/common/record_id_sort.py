"""Sort proxy for the record ID stored in the vertical header.

Kept in its own module so alphabetical class sorting cannot place a subclass
above this base.

"""

from __future__ import annotations

from PySide6.QtCore import QModelIndex, QObject, QPersistentModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtGui import QStandardItemModel

ROW_ID_SORT_SECTION = -2


class RecordIdSortProxyModel(QSortFilterProxyModel):
    """Proxy that can sort rows by the database ID stored in the vertical header."""

    def __init__(self, parent: QObject | None = None) -> None:
        """Create a proxy that sorts by a column or by the vertical-header record ID."""
        super().__init__(parent)
        self._sort_by_record_id = False

    def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Compare record ids when that sort is active; otherwise use the column value."""
        if self._sort_by_record_id:
            return _row_id_less_than(source_left, source_right)
        return super().lessThan(source_left, source_right)

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        """Sort by record ID when `column` is the ID sentinel, otherwise by that column."""
        self._sort_by_record_id = column == ROW_ID_SORT_SECTION
        if self._sort_by_record_id:
            super().sort(0, order)
            return
        super().sort(column, order)


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


def _row_id_less_than(
    left: QModelIndex | QPersistentModelIndex,
    right: QModelIndex | QPersistentModelIndex,
) -> bool:
    """Return whether `left`'s record ID is lower than `right`'s."""
    left_id = _vertical_header_id(left)
    right_id = _vertical_header_id(right)
    if left_id is None and right_id is None:
        return False
    if left_id is None:
        return False
    if right_id is None:
        return True
    return left_id < right_id


def _vertical_header_id(index: QModelIndex | QPersistentModelIndex) -> int | None:
    """Return the numeric record ID stored on the source row of `index`."""
    model = index.model()
    if not isinstance(model, QStandardItemModel):
        return None
    item = model.verticalHeaderItem(index.row())
    if item is None:
        return None
    return _as_sort_id(item.text())
