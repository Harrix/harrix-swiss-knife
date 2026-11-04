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
- [🔧 Function `create_colored_table_proxy_model`](#-function-create_colored_table_proxy_model)
- [🔧 Function `create_table_proxy_model`](#-function-create_table_proxy_model)
- [🔧 Function `enable_table_header_sorting`](#-function-enable_table_header_sorting)
- [🔧 Function `get_stored_table_header_sort`](#-function-get_stored_table_header_sort)
- [🔧 Function `make_table_columns_resizable`](#-function-make_table_columns_resizable)
- [🔧 Function `next_table_sort_order`](#-function-next_table_sort_order)
- [🔧 Function `set_stored_table_header_sort`](#-function-set_stored_table_header_sort)
- [🔧 Function `sort_table_by_header_click`](#-function-sort_table_by_header_click)

</details>

## 🏛️ Class `ColoredTableProxyModel`

```python
class ColoredTableProxyModel(QSortFilterProxyModel)
```

Proxy that sorts an icon-only first column by the row database ID.

<details>
<summary>Code:</summary>

```python
class ColoredTableProxyModel(QSortFilterProxyModel):

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
    if stored is None:
        return
    section, order = stored
    table.sortByColumn(section, order)
    header = table.horizontalHeader()
    header.setSortIndicatorShown(True)
    header.setSortIndicator(section, order)
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

    proxy = QSortFilterProxyModel()
    proxy.setSourceModel(model)
    return proxy
```

</details>

## 🔧 Function `enable_table_header_sorting`

```python
def enable_table_header_sorting(table: QTableView, *, skip_section: int | None = None) -> None
```

Allow single clicks on the header to sort ascending, then descending.

Safe to call more than once for the same header. Sort state is stored on the
table so [`apply_stored_table_header_sort`](#-function-apply_stored_table_header_sort) can restore it after a model reload.

Args:

- `table` (`QTableView`): Table whose model supports `sort`.
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
    header.setSortIndicatorShown(True)
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
                header.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
            else:
                header.setSortIndicator(*stored)
            return
        set_stored_table_header_sort(table, *result)

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
    if not isinstance(section, int) or section < 0:
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
    if already_interactive and not force_reinit:
        return

    min_size = header.minimumSectionSize()
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
            header.setSectionResizeMode(i, interactive_mode)
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
        header.setSectionResizeMode(column, interactive_mode)
        width = base + (extra if index == len(flexible) - 1 else 0)
        table.setColumnWidth(column, max(width, min_size))
```

</details>

## 🔧 Function `next_table_sort_order`

```python
def next_table_sort_order(current_section: int, current_order: Qt.SortOrder, clicked_section: int) -> Qt.SortOrder
```

Return the sort order after a header click.

A new column starts ascending. A second click on the same column reverses
the current order.

Args:

- `current_section` (`int`): Column that currently has the sort indicator, or `-1`.
- `current_order` (`Qt.SortOrder`): Current sort direction.
- `clicked_section` (`int`): Column the user clicked.

Returns:

- `Qt.SortOrder`: Order to apply to `clicked_section`.

<details>
<summary>Code:</summary>

```python
def next_table_sort_order(
    current_section: int,
    current_order: Qt.SortOrder,
    clicked_section: int,
) -> Qt.SortOrder:
    if clicked_section == current_section:
        if current_order == Qt.SortOrder.AscendingOrder:
            return Qt.SortOrder.DescendingOrder
        return Qt.SortOrder.AscendingOrder
    return Qt.SortOrder.AscendingOrder
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

- `table` (`QTableView`): Table whose proxy/source model supports `sort`.
- `section` (`int`): Clicked logical column.
- `skip_section` (`int | None`): Column that must not sort. Defaults to none.
- `current_section` (`int | None`): Last sorted column, or `None` if unknown.
- `current_order` (`Qt.SortOrder | None`): Last sort direction, or `None` if unknown.

Returns:

- `tuple[int, Qt.SortOrder] | None`: Applied column and order, or `None` when skipped.

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
    table.sortByColumn(section, order)
    header.setSortIndicatorShown(True)
    header.setSortIndicator(section, order)
    return section, order
```

</details>
