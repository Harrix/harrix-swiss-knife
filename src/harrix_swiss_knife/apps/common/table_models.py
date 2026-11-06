"""Qt table model helpers shared across apps."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import (
    QEvent,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QRect,
    QSortFilterProxyModel,
    Qt,
    QTimer,
)
from PySide6.QtGui import QBrush, QGuiApplication, QIcon, QPainter, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QAbstractButton, QStyle, QStyleOptionHeader, QWidget

from harrix_swiss_knife.apps.common.record_id_sort import ROW_ID_SORT_SECTION as _ROW_ID_SORT_SECTION
from harrix_swiss_knife.apps.common.record_id_sort import RecordIdSortProxyModel

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from PySide6.QtGui import QPaintEvent
    from PySide6.QtWidgets import QTableView

_COLUMN_FILL_GUARD_PROP = "hskColumnFillGuard"
_COLUMN_FILL_SLACK_PX = 4
_HEADER_SORT_CONNECTED_PROP = "hskHeaderSortConnected"
_HEADER_SORT_ORDER_PROP = "hskHeaderSortOrder"
_HEADER_SORT_SECTION_PROP = "hskHeaderSortSection"
_HEADER_SORT_SKIP_PROP = "hskHeaderSortSkipSection"
_NO_SKIP_SECTION = -999
_USER_SIZED_COLUMNS_PROP = "hskUserSizedColumns"


class ColoredTableProxyModel(RecordIdSortProxyModel):
    """Proxy that sorts an icon-only first column by the row database ID."""

    def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        """Compare icon cells by stored ID; other columns use the default sort."""
        if self._sort_by_record_id:
            return super().lessThan(source_left, source_right)
        if source_left.column() == 0 and source_right.column() == 0:
            left_id = _sortable_row_id(source_left)
            right_id = _sortable_row_id(source_right)
            if left_id is not None and right_id is not None:
                return left_id < right_id
        return super().lessThan(source_left, source_right)


class _RecordIdCornerMark(QWidget):
    """Sort triangle drawn on top of the table's header-corner button."""

    def __init__(self, button: QAbstractButton) -> None:
        """Cover `button` without taking its clicks."""
        super().__init__(button)
        self._order: Qt.SortOrder | None = None
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        button.installEventFilter(self)
        self.setGeometry(button.rect())

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Keep the mark the same size as the corner button."""
        if event.type() in {QEvent.Type.Resize, QEvent.Type.Show}:
            self.setGeometry(watched.rect())
        return False

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Draw the current id-sort direction, or nothing when unsorted."""
        if self._order is None:
            return
        painter = QPainter(self)
        _paint_header_sort_indicator(painter, self._indicator_widget(), self.rect(), self._order)
        painter.end()

    def set_order(self, order: Qt.SortOrder | None) -> None:
        """Show an up or down mark, or nothing when the ID column is not sorted."""
        self._order = order
        self.update()

    def _indicator_widget(self) -> QWidget:
        """Use the column header so the ID mark is drawn with that header's arrow."""
        button = self.parentWidget()
        table = button.parentWidget() if button is not None else None
        header_getter = getattr(table, "horizontalHeader", None)
        if callable(header_getter):
            header = header_getter()
            if isinstance(header, QWidget):
                return header
        return self


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


def apply_stored_table_header_sort(table: QTableView) -> None:
    """Re-apply the last header sort after the table model was replaced."""
    stored = get_stored_table_header_sort(table)
    _set_record_id_corner_order(table, None)
    if stored is None:
        return
    section, order = stored
    if section == _ROW_ID_SORT_SECTION:
        model = table.model()
        if model is not None:
            model.sort(_ROW_ID_SORT_SECTION, order)
        table.horizontalHeader().setSortIndicatorShown(False)
        _set_record_id_corner_order(table, order)
        return
    table.sortByColumn(section, order)
    header = table.horizontalHeader()
    header.setSortIndicatorShown(True)
    header.setSortIndicator(section, order)


def bind_column_fill_on_resize(table: QTableView, refill: Callable[[QTableView], None]) -> None:
    """Refill column widths when the table resizes, until the user drags a section.

    Qt's default resize mode is already Interactive, so a one-shot layout often
    runs before the viewport has its final width and then never runs again.

    """
    if getattr(table, "_hsk_column_fill_hook", None) is not None:
        return
    header = table.horizontalHeader()

    def _on_section_resized(_logical: int, old_size: int, new_size: int) -> None:
        if table.property(_COLUMN_FILL_GUARD_PROP) or old_size == new_size:
            return
        if QGuiApplication.mouseButtons() & Qt.MouseButton.LeftButton:
            table.setProperty(_USER_SIZED_COLUMNS_PROP, 1)

    header.sectionResized.connect(_on_section_resized)

    class _ResizeHook(QObject):
        def eventFilter(self, _watched: QObject, event: QEvent) -> bool:  # noqa: N802
            if (
                event.type() == QEvent.Type.Resize
                and not user_resized_columns(table)
                and not table.property(_COLUMN_FILL_GUARD_PROP)
            ):
                QTimer.singleShot(0, _refill_if_alive)
            return False

    def _refill_if_alive() -> None:
        try:
            refill(table)
        except RuntimeError:
            return

    hook = _ResizeHook(table)
    table.installEventFilter(hook)
    table._hsk_column_fill_hook = hook  # type: ignore[attr-defined]  # noqa: SLF001


def clear_stored_table_header_sort(table: QTableView) -> None:
    """Forget the header sort so the table stays in source order."""
    table.setProperty(_HEADER_SORT_SECTION_PROP, -1)


def columns_fill_viewport(table: QTableView) -> bool:
    """Return whether section widths match the viewport, with no gap and no overflow."""
    header = table.horizontalHeader()
    viewport_w = table.viewport().width()
    if viewport_w <= 0 or header.count() <= 0:
        return False
    return abs(header.length() - viewport_w) <= _COLUMN_FILL_SLACK_PX


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

    proxy = RecordIdSortProxyModel()
    proxy.setSourceModel(model)
    return proxy


def enable_record_id_corner_sort(table: QTableView) -> None:
    """Sort by record ID when the header corner above that column is clicked.

    Qt's corner button selects every row. `QTableView` has no setter for that
    button; `setCornerWidget` only fills the scrollbar corner. This disconnects
    select-all and uses the same click cycle as a column header.

    """
    if table.property("hskRecordIdCorner"):
        return
    button = table_corner_button(table)
    if button is None:
        return
    button.clicked.disconnect()

    def _on_corner_clicked() -> None:
        sort_table_by_record_id_click(table)

    table._hsk_record_id_corner_slot = _on_corner_clicked  # type: ignore[attr-defined]  # noqa: SLF001
    button.clicked.connect(_on_corner_clicked)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setToolTip("Sort by ID")
    mark = _RecordIdCornerMark(button)
    table.setProperty("hskRecordIdCorner", 1)
    table._hsk_record_id_corner = mark  # type: ignore[attr-defined]  # noqa: SLF001
    stored = get_stored_table_header_sort(table)
    if stored is not None and stored[0] == _ROW_ID_SORT_SECTION:
        mark.set_order(stored[1])


def enable_table_header_sorting(
    table: QTableView,
    *,
    skip_section: int | None = None,
) -> None:
    """Allow single clicks on the header to sort ascending, then descending, then unsorted.

    Safe to call more than once for the same header. Sort state is stored on the
    table so `apply_stored_table_header_sort` can restore it after a model reload.

    Args:

    - `table` (`QTableView`): Table whose model supports `sort`.
    - `skip_section` (`int | None`): Column that must not sort. Defaults to none.

    """
    header = table.horizontalHeader()
    header.setSectionsClickable(True)
    if get_stored_table_header_sort(table) is None:
        header.setSortIndicatorShown(False)
    table.setProperty(
        _HEADER_SORT_SKIP_PROP,
        skip_section if skip_section is not None else _NO_SKIP_SECTION,
    )
    if bool(header.property(_HEADER_SORT_CONNECTED_PROP)):
        return

    def _on_section_clicked(section: int) -> None:
        skip_raw = table.property(_HEADER_SORT_SKIP_PROP)
        skip = skip_raw if isinstance(skip_raw, int) and skip_raw >= 0 else None
        stored = get_stored_table_header_sort(table)
        current_section, current_order = stored if stored is not None else (None, None)
        result = sort_table_by_header_click(
            table,
            section,
            skip_section=skip,
            current_section=current_section,
            current_order=current_order,
        )
        if result is None:
            if stored is None:
                header.setSortIndicatorShown(False)
            else:
                header.setSortIndicator(*stored)
            return
        section, order = result
        if section == _ROW_ID_SORT_SECTION:
            set_stored_table_header_sort(table, section, order)
            return
        if section < 0:
            clear_stored_table_header_sort(table)
            return
        set_stored_table_header_sort(table, section, order)

    header.sectionClicked.connect(_on_section_clicked)
    header.setProperty(_HEADER_SORT_CONNECTED_PROP, 1)


def get_stored_table_header_sort(table: QTableView) -> tuple[int, Qt.SortOrder] | None:
    """Return the last header sort stored on `table`, if any."""
    section = table.property(_HEADER_SORT_SECTION_PROP)
    order_raw = table.property(_HEADER_SORT_ORDER_PROP)
    if not isinstance(section, int) or (section < 0 and section != _ROW_ID_SORT_SECTION):
        return None
    if not isinstance(order_raw, int):
        return None
    return section, Qt.SortOrder(order_raw)


def make_table_columns_resizable(
    table: QTableView,
    *,
    stretch_last: bool = False,
    keep_fixed_sections: Sequence[int] | None = None,
    force_reinit: bool = False,
) -> None:
    """Allow dragging header edges to change column width.

    Fills the viewport first (like Stretch), then switches flexible columns to
    Interactive so the user can drag edges. Optionally leaves some sections Fixed
    and/or keeps the last column stretching. When columns are already Interactive,
    existing widths are kept unless `force_reinit` is set.

    Args:

    - `table` (`QTableView`): Table whose horizontal header should be resizable.
    - `stretch_last` (`bool`): Keep the last column in Stretch mode. Defaults to
      `False`.
    - `keep_fixed_sections` (`Sequence[int] | None`): Columns that stay Fixed.
    - `force_reinit` (`bool`): Rebuild Interactive modes even when already set.

    """
    header = table.horizontalHeader()
    count = header.count()
    if count <= 0:
        return

    fixed = set(keep_fixed_sections or ())
    last = count - 1
    interactive_mode = header.ResizeMode.Interactive
    already_interactive = all(
        (i in fixed and header.sectionResizeMode(i) == header.ResizeMode.Fixed)
        or (stretch_last and i == last and header.sectionResizeMode(i) == header.ResizeMode.Stretch)
        or (i not in fixed and not (stretch_last and i == last) and header.sectionResizeMode(i) == interactive_mode)
        for i in range(count)
    )
    # Default Qt mode is Interactive, so "already interactive" is not a finished layout.
    if user_resized_columns(table) or bool(table.property(_COLUMN_FILL_GUARD_PROP)):
        return
    if already_interactive and columns_fill_viewport(table) and not force_reinit:
        return

    min_size = header.minimumSectionSize()
    table.setProperty(_COLUMN_FILL_GUARD_PROP, 1)
    try:
        _assign_resizable_column_widths(
            table,
            fixed=fixed,
            last=last,
            stretch_last=stretch_last,
            min_size=min_size,
        )
    finally:
        table.setProperty(_COLUMN_FILL_GUARD_PROP, 0)


def next_table_sort_order(
    current_section: int,
    current_order: Qt.SortOrder,
    clicked_section: int,
) -> Qt.SortOrder | None:
    """Return the sort order after a header click.

    A new column starts ascending. The same column then goes descending, and a
    third click clears the sort (`None`).

    Args:

    - `current_section` (`int`): Column that currently has the sort indicator, or `-1`.
    - `current_order` (`Qt.SortOrder`): Current sort direction.
    - `clicked_section` (`int`): Column the user clicked.

    Returns:

    - `Qt.SortOrder | None`: Order to apply, or `None` to restore source order.

    """
    if clicked_section != current_section:
        return Qt.SortOrder.AscendingOrder
    if current_order == Qt.SortOrder.AscendingOrder:
        return Qt.SortOrder.DescendingOrder
    return None


def set_stored_table_header_sort(
    table: QTableView,
    section: int,
    order: Qt.SortOrder,
) -> None:
    """Remember a header sort so it can be restored after a model reload."""
    table.setProperty(_HEADER_SORT_SECTION_PROP, section)
    table.setProperty(_HEADER_SORT_ORDER_PROP, int(order.value))


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

    - `tuple[int, Qt.SortOrder] | None`: Applied column and order, `(-1, …)` when the
      sort was cleared, or `None` when skipped.

    """
    if skip_section is not None and section == skip_section:
        return None
    header = table.horizontalHeader()
    if current_section is None:
        current_section = -1
    if current_order is None:
        current_order = Qt.SortOrder.AscendingOrder
    order = next_table_sort_order(current_section, current_order, section)
    if order is None:
        model = table.model()
        if model is not None:
            model.sort(-1)
        header.setSortIndicatorShown(False)
        _set_record_id_corner_order(table, None)
        return -1, Qt.SortOrder.AscendingOrder
    table.sortByColumn(section, order)
    header.setSortIndicatorShown(True)
    header.setSortIndicator(section, order)
    _set_record_id_corner_order(table, None)
    return section, order


def sort_table_by_record_id_click(table: QTableView) -> None:
    """Cycle the record-id sort from the corner above that header."""
    model = table.model()
    if not isinstance(model, RecordIdSortProxyModel):
        return
    stored = get_stored_table_header_sort(table)
    current_section, current_order = stored if stored is not None else (-1, Qt.SortOrder.AscendingOrder)
    order = next_table_sort_order(current_section, current_order, _ROW_ID_SORT_SECTION)
    header = table.horizontalHeader()
    if order is None:
        model.sort(-1)
        header.setSortIndicatorShown(False)
        clear_stored_table_header_sort(table)
        _set_record_id_corner_order(table, None)
        return
    model.sort(_ROW_ID_SORT_SECTION, order)
    header.setSortIndicatorShown(False)
    set_stored_table_header_sort(table, _ROW_ID_SORT_SECTION, order)
    _set_record_id_corner_order(table, order)


def table_corner_button(table: QTableView) -> QAbstractButton | None:
    """Return the header-corner button that Qt uses to select every row."""
    for child in table.findChildren(QAbstractButton):
        if child.metaObject().className() == "QTableCornerButton":
            return child
    return None


def user_resized_columns(table: QTableView) -> bool:
    """Return whether the user has dragged a column edge on `table`."""
    return bool(table.property(_USER_SIZED_COLUMNS_PROP))


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


def _assign_resizable_column_widths(
    table: QTableView,
    *,
    fixed: set[int],
    last: int,
    stretch_last: bool,
    min_size: int,
) -> None:
    """Set Interactive widths that cover the current viewport."""
    header = table.horizontalHeader()
    count = header.count()
    header.setStretchLastSection(False)
    for i in fixed:
        header.setSectionResizeMode(i, header.ResizeMode.Fixed)
        table.setColumnWidth(i, max(header.sectionSize(i), min_size))

    flexible = [i for i in range(count) if i not in fixed and not (stretch_last and i == last)]
    viewport_w = table.viewport().width()
    if viewport_w <= 0:
        viewport_w = max(table.width(), 0)
    fixed_total = sum(max(header.sectionSize(i), min_size) for i in fixed)

    if stretch_last:
        slots = len(flexible) + 1
        share = max((viewport_w - fixed_total) // slots, min_size) if viewport_w > 0 else min_size
        for i in flexible:
            header.setSectionResizeMode(i, header.ResizeMode.Interactive)
            table.setColumnWidth(i, share)
        header.setSectionResizeMode(last, header.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        return

    if not flexible:
        return
    remaining = max(viewport_w - fixed_total, len(flexible) * min_size) if viewport_w > 0 else len(flexible) * min_size
    base = remaining // len(flexible)
    extra = remaining - base * len(flexible)
    for index, column in enumerate(flexible):
        header.setSectionResizeMode(column, header.ResizeMode.Interactive)
        width = base + (extra if index == len(flexible) - 1 else 0)
        table.setColumnWidth(column, max(width, min_size))


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


def _paint_header_sort_indicator(painter: QPainter, widget: QWidget, rect: QRect, order: Qt.SortOrder) -> None:
    """Draw the same sort chevron a column header uses for `order`."""
    style = widget.style()
    if style is None:
        return
    option = QStyleOptionHeader()
    option.initFrom(widget)
    option.rect = rect
    option.position = QStyleOptionHeader.SectionPosition.OnlyOneSection
    # Ascending is SortDown in Qt. That value is the header's up chevron.
    option.sortIndicator = (
        QStyleOptionHeader.SortIndicator.SortDown
        if order == Qt.SortOrder.AscendingOrder
        else QStyleOptionHeader.SortIndicator.SortUp
    )
    arrow = style.subElementRect(QStyle.SubElement.SE_HeaderArrow, option, widget)
    if not arrow.isValid():
        return
    option.rect = arrow
    style.drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorHeaderArrow, option, painter, widget)


def _set_record_id_corner_order(table: QTableView, order: Qt.SortOrder | None) -> None:
    corner = getattr(table, "_hsk_record_id_corner", None)
    if isinstance(corner, _RecordIdCornerMark):
        corner.set_order(order)


def _sortable_row_id(index: QModelIndex | QPersistentModelIndex) -> int | None:
    """Read a numeric ID stored on an icon cell for first-column sorting."""
    return _as_sort_id(index.data(Qt.ItemDataRole.UserRole))
