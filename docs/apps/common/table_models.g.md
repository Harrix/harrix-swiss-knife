---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `table_models.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ColoredTableProxyModel`](#%EF%B8%8F-class-coloredtableproxymodel)
  - [⚙️ Method `lessThan`](#%EF%B8%8F-method-lessthan)
- [🔧 Function `append_colored_table_row`](#-function-append_colored_table_row)
- [🔧 Function `apply_stored_table_header_sort`](#-function-apply_stored_table_header_sort)
- [🔧 Function `bind_column_fill_on_resize`](#-function-bind_column_fill_on_resize)
- [🔧 Function `clear_stored_table_header_sort`](#-function-clear_stored_table_header_sort)
- [🔧 Function `columns_fill_viewport`](#-function-columns_fill_viewport)
- [🔧 Function `create_colored_table_proxy_model`](#-function-create_colored_table_proxy_model)
- [🔧 Function `create_table_proxy_model`](#-function-create_table_proxy_model)
- [🔧 Function `enable_record_id_corner_sort`](#-function-enable_record_id_corner_sort)
- [🔧 Function `enable_table_header_sorting`](#-function-enable_table_header_sorting)
- [🔧 Function `get_stored_table_header_sort`](#-function-get_stored_table_header_sort)
- [🔧 Function `make_table_columns_resizable`](#-function-make_table_columns_resizable)
- [🔧 Function `next_table_sort_order`](#-function-next_table_sort_order)
- [🔧 Function `set_stored_table_header_sort`](#-function-set_stored_table_header_sort)
- [🔧 Function `sort_table_by_header_click`](#-function-sort_table_by_header_click)
- [🔧 Function `sort_table_by_record_id_click`](#-function-sort_table_by_record_id_click)
- [🔧 Function `user_resized_columns`](#-function-user_resized_columns)

</details>

## 🏛️ Class `ColoredTableProxyModel`

```python
class ColoredTableProxyModel(RecordIdSortProxyModel)
```

Proxy that sorts an icon-only first column by the row database ID.

<details>
<summary>Code:</summary>

```python
class ColoredTableProxyModel(RecordIdSortProxyModel):

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
```

</details>

### ⚙️ Method `lessThan`

```python
def lessThan(self, source_left: QModelIndex | QPersistentModelIndex, source_right: QModelIndex | QPersistentModelIndex) -> bool
```

Compare icon cells by stored ID; other columns use the default sort.

<details>
<summary>Code:</summary>

```python
def lessThan(  # noqa: N802
        self,
        source_left: QModelIndex | QPersistentModelIndex,
        source_right: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        if self._sort_by_record_id:
            return super().lessThan(source_left, source_right)
        if source_left.column() == 0 and source_right.column() == 0:
            left_id = _sortable_row_id(source_left)
            right_id = _sortable_row_id(source_right)
            if left_id is not None and right_id is not None:
                return left_id < right_id
        return super().lessThan(source_left, source_right)
```

</details>

## 🔧 Function `append_colored_table_row`

```python
def append_colored_table_row(proxy: QSortFilterProxyModel, row: Sequence[object], *, id_column: int = -2, color_column: int = -1) -> None
```

Append one colored row to an existing proxy created by [`create_colored_table_proxy_model`](#-function-create_colored_table_proxy_model).

<details>
<summary>Code:</summary>

```python
def append_colored_table_row(
    proxy: QSortFilterProxyModel,
    row: Sequence[object],
    *,
    id_column: int = -2,
    color_column: int = -1,
) -> None:
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
```

</details>

## 🔧 Function `apply_stored_table_header_sort`

```python
def apply_stored_table_header_sort(table: QTableView) -> None
```

Re-apply the last header sort after the table model was replaced.

<details>
<summary>Code:</summary>

```python
def apply_stored_table_header_sort(table: QTableView) -> None:
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
```

</details>

## 🔧 Function `bind_column_fill_on_resize`

```python
def bind_column_fill_on_resize(table: QTableView, refill: Callable[[QTableView], None]) -> None
```

Refill column widths when the table resizes, until the user drags a section.

Qt's default resize mode is already Interactive, so a one-shot layout often
runs before the viewport has its final width and then never runs again.

<details>
<summary>Code:</summary>

```python
def bind_column_fill_on_resize(table: QTableView, refill: Callable[[QTableView], None]) -> None:
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
```

</details>

## 🔧 Function `clear_stored_table_header_sort`

```python
def clear_stored_table_header_sort(table: QTableView) -> None
```

Forget the header sort so the table stays in source order.

<details>
<summary>Code:</summary>

```python
def clear_stored_table_header_sort(table: QTableView) -> None:
    table.setProperty(_HEADER_SORT_SECTION_PROP, -1)
```

</details>

## 🔧 Function `columns_fill_viewport`

```python
def columns_fill_viewport(table: QTableView) -> bool
```

Return whether section widths match the viewport, with no gap and no overflow.

<details>
<summary>Code:</summary>

```python
def columns_fill_viewport(table: QTableView) -> bool:
    header = table.horizontalHeader()
    viewport_w = table.viewport().width()
    if viewport_w <= 0 or header.count() <= 0:
        return False
    return abs(header.length() - viewport_w) <= _COLUMN_FILL_SLACK_PX
```

</details>

## 🔧 Function `create_colored_table_proxy_model`

```python
def create_colored_table_proxy_model(data: Sequence[Sequence[object]], headers: list[str], *, id_column: int = -2, color_column: int = -1) -> QSortFilterProxyModel
```

Create a colored proxy model with ID and color columns excluded from display.

By default the ID is at index `-2` and the color at `-1` (last column).
A `QIcon` cell value is shown as decoration without display text.

<details>
<summary>Code:</summary>

```python
def create_colored_table_proxy_model(
    data: Sequence[Sequence[object]],
    headers: list[str],
    *,
    id_column: int = -2,
    color_column: int = -1,
) -> QSortFilterProxyModel:
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
```

</details>

## 🔧 Function `create_table_proxy_model`

```python
def create_table_proxy_model(data: Sequence[Sequence[object]], headers: list[str], *, id_column: int = 0) -> QSortFilterProxyModel
```

Create a proxy model with row IDs stored in the vertical header.

The `id_column` is excluded from displayed columns and is stored as vertical header text.

<details>
<summary>Code:</summary>

```python
def create_table_proxy_model(
    data: Sequence[Sequence[object]],
    headers: list[str],
    *,
    id_column: int = 0,
) -> QSortFilterProxyModel:
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
```

</details>

## 🔧 Function `enable_record_id_corner_sort`

```python
def enable_record_id_corner_sort(table: QTableView) -> None
```

Sort by record ID when the header corner above that column is clicked.

Qt's corner button selects every row. `QTableView` has no setter for that
button; `setCornerWidget` only fills the scrollbar corner. This disconnects
select-all and uses the same click cycle as a column header.

<details>
<summary>Code:</summary>

```python
def enable_record_id_corner_sort(table: QTableView) -> None:
    if table.property("hskRecordIdCorner"):
        return
    button = _table_corner_button(table)
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
```

</details>

## 🔧 Function `enable_table_header_sorting`

```python
def enable_table_header_sorting(table: QTableView, *, skip_section: int | None = None) -> None
```

Allow single clicks on the header to sort ascending, then descending, then unsorted.

Safe to call more than once for the same header. Sort state is stored on the
table so [`apply_stored_table_header_sort`](#-function-apply_stored_table_header_sort) can restore it after a model reload.

Args:

- `table` (`QTableView`): Table whose model supports [`sort`](record_id_sort.g.md#%EF%B8%8F-method-sort).
- `skip_section` (`int | None`): Column that must not sort. Defaults to none.

<details>
<summary>Code:</summary>

```python
def enable_table_header_sorting(
    table: QTableView,
    *,
    skip_section: int | None = None,
) -> None:
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
```

</details>

## 🔧 Function `get_stored_table_header_sort`

```python
def get_stored_table_header_sort(table: QTableView) -> tuple[int, Qt.SortOrder] | None
```

Return the last header sort stored on `table`, if any.

<details>
<summary>Code:</summary>

```python
def get_stored_table_header_sort(table: QTableView) -> tuple[int, Qt.SortOrder] | None:
    section = table.property(_HEADER_SORT_SECTION_PROP)
    order_raw = table.property(_HEADER_SORT_ORDER_PROP)
    if not isinstance(section, int) or (section < 0 and section != _ROW_ID_SORT_SECTION):
        return None
    if not isinstance(order_raw, int):
        return None
    return section, Qt.SortOrder(order_raw)
```

</details>

## 🔧 Function `make_table_columns_resizable`

```python
def make_table_columns_resizable(table: QTableView, *, stretch_last: bool = False, keep_fixed_sections: Sequence[int] | None = None, force_reinit: bool = False) -> None
```

Allow dragging header edges to change column width.

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

<details>
<summary>Code:</summary>

```python
def make_table_columns_resizable(
    table: QTableView,
    *,
    stretch_last: bool = False,
    keep_fixed_sections: Sequence[int] | None = None,
    force_reinit: bool = False,
) -> None:
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
```

</details>

## 🔧 Function `next_table_sort_order`

```python
def next_table_sort_order(current_section: int, current_order: Qt.SortOrder, clicked_section: int) -> Qt.SortOrder | None
```

Return the sort order after a header click.

A new column starts ascending. The same column then goes descending, and a
third click clears the sort (`None`).

Args:

- `current_section` (`int`): Column that currently has the sort indicator, or `-1`.
- `current_order` (`Qt.SortOrder`): Current sort direction.
- `clicked_section` (`int`): Column the user clicked.

Returns:

- `Qt.SortOrder | None`: Order to apply, or `None` to restore source order.

<details>
<summary>Code:</summary>

```python
def next_table_sort_order(
    current_section: int,
    current_order: Qt.SortOrder,
    clicked_section: int,
) -> Qt.SortOrder | None:
    if clicked_section != current_section:
        return Qt.SortOrder.AscendingOrder
    if current_order == Qt.SortOrder.AscendingOrder:
        return Qt.SortOrder.DescendingOrder
    return None
```

</details>

## 🔧 Function `set_stored_table_header_sort`

```python
def set_stored_table_header_sort(table: QTableView, section: int, order: Qt.SortOrder) -> None
```

Remember a header sort so it can be restored after a model reload.

<details>
<summary>Code:</summary>

```python
def set_stored_table_header_sort(
    table: QTableView,
    section: int,
    order: Qt.SortOrder,
) -> None:
    table.setProperty(_HEADER_SORT_SECTION_PROP, section)
    table.setProperty(_HEADER_SORT_ORDER_PROP, int(order.value))
```

</details>

## 🔧 Function `sort_table_by_header_click`

```python
def sort_table_by_header_click(table: QTableView, section: int, *, skip_section: int | None = None, current_section: int | None = None, current_order: Qt.SortOrder | None = None) -> tuple[int, Qt.SortOrder] | None
```

Sort a table from a header click, optionally ignoring `skip_section`.

Pass `current_section` and `current_order` from the last applied sort. The
header indicator cannot be used after a real click: `QHeaderView` already
toggles it when the indicator is shown.

Args:

- `table` (`QTableView`): Table whose proxy/source model supports [`sort`](record_id_sort.g.md#%EF%B8%8F-method-sort).
- `section` (`int`): Clicked logical column.
- `skip_section` (`int | None`): Column that must not sort. Defaults to none.
- `current_section` (`int | None`): Last sorted column, or `None` if unknown.
- `current_order` (`Qt.SortOrder | None`): Last sort direction, or `None` if unknown.

Returns:

- `tuple[int, Qt.SortOrder] | None`: Applied column and order, `(-1, …)` when the
  sort was cleared, or `None` when skipped.

<details>
<summary>Code:</summary>

```python
def sort_table_by_header_click(
    table: QTableView,
    section: int,
    *,
    skip_section: int | None = None,
    current_section: int | None = None,
    current_order: Qt.SortOrder | None = None,
) -> tuple[int, Qt.SortOrder] | None:
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
```

</details>

## 🔧 Function `sort_table_by_record_id_click`

```python
def sort_table_by_record_id_click(table: QTableView) -> None
```

Cycle the record-id sort from the corner above that header.

<details>
<summary>Code:</summary>

```python
def sort_table_by_record_id_click(table: QTableView) -> None:
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
```

</details>

## 🔧 Function `user_resized_columns`

```python
def user_resized_columns(table: QTableView) -> bool
```

Return whether the user has dragged a column edge on `table`.

<details>
<summary>Code:</summary>

```python
def user_resized_columns(table: QTableView) -> bool:
    return bool(table.property(_USER_SIZED_COLUMNS_PROP))
```

</details>
