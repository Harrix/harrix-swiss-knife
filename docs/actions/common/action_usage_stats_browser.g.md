---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `action_usage_stats_browser.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ActionUsageStatsRow`](#%EF%B8%8F-class-actionusagestatsrow)
  - [📎 Attribute `count`](#-attribute-count)
  - [📎 Attribute `title`](#-attribute-title)
  - [📎 Attribute `icon`](#-attribute-icon)
  - [📎 Attribute `category`](#-attribute-category)
  - [📎 Attribute `gui`](#-attribute-gui)
  - [📎 Attribute `cli`](#-attribute-cli)
  - [📎 Attribute `last_used`](#-attribute-last_used)
- [🔧 Function `build_action_usage_stats_browser`](#-function-build_action_usage_stats_browser)

</details>

## 🏛️ Class `ActionUsageStatsRow`

```python
class ActionUsageStatsRow(TypedDict)
```

One row for the action usage stats table.

<details>
<summary>Code:</summary>

```python
class ActionUsageStatsRow(TypedDict):

    count: int
    title: str
    icon: str
    category: str
    gui: int
    cli: int
    last_used: str
```

</details>

### 📎 Attribute `count`

```python
count: int
```

_No docstring provided._

### 📎 Attribute `title`

```python
title: str
```

_No docstring provided._

### 📎 Attribute `icon`

```python
icon: str
```

_No docstring provided._

### 📎 Attribute `category`

```python
category: str
```

_No docstring provided._

### 📎 Attribute `gui`

```python
gui: int
```

_No docstring provided._

### 📎 Attribute `cli`

```python
cli: int
```

_No docstring provided._

### 📎 Attribute `last_used`

```python
last_used: str
```

_No docstring provided._

## 🔧 Function `build_action_usage_stats_browser`

```python
def build_action_usage_stats_browser(rows: list[ActionUsageStatsRow], *, summary: str) -> Callable[[QDialog, QVBoxLayout], None]
```

Return dialog layout builder: summary label + sortable usage table.

<details>
<summary>Code:</summary>

```python
def build_action_usage_stats_browser(
    rows: list[ActionUsageStatsRow],
    *,
    summary: str,
) -> Callable[[QDialog, QVBoxLayout], None]:

    def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
        summary_label = QLabel(summary)
        summary_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        summary_label.setWordWrap(True)
        layout.addWidget(summary_label)

        table = QTableWidget(0, len(_HEADERS))
        table.setHorizontalHeaderLabels(list(_HEADERS))
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setSortingEnabled(False)

        sort_column = _COL_COUNT
        sort_ascending = False

        def fill_table(ordered: list[ActionUsageStatsRow]) -> None:
            table.setRowCount(len(ordered))
            for row_idx, row in enumerate(ordered):
                count_item = QTableWidgetItem(str(row["count"]))
                count_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                table.setItem(row_idx, _COL_COUNT, count_item)

                action_item = QTableWidgetItem(row["title"])
                action_item.setIcon(_row_icon(row["icon"]))
                table.setItem(row_idx, _COL_ACTION, action_item)

                table.setItem(row_idx, _COL_CATEGORY, QTableWidgetItem(row["category"]))

                gui_item = QTableWidgetItem(str(row["gui"]))
                gui_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                table.setItem(row_idx, _COL_GUI, gui_item)

                cli_item = QTableWidgetItem(str(row["cli"]))
                cli_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                table.setItem(row_idx, _COL_CLI, cli_item)

                table.setItem(row_idx, _COL_LAST_USED, QTableWidgetItem(_format_last_used(row["last_used"])))

        def primary_key(row: ActionUsageStatsRow) -> int | str:
            if sort_column == _COL_COUNT:
                return row["count"]
            if sort_column == _COL_ACTION:
                return row["title"].casefold()
            if sort_column == _COL_CATEGORY:
                return row["category"].casefold()
            if sort_column == _COL_GUI:
                return row["gui"]
            if sort_column == _COL_CLI:
                return row["cli"]
            return row["last_used"]

        def apply_sort() -> None:
            nonlocal sort_column, sort_ascending
            # Stable sort: title first, then primary so ties keep title ascending.
            ordered = sorted(rows, key=lambda row: row["title"].casefold())
            ordered = sorted(ordered, key=primary_key, reverse=not sort_ascending)
            fill_table(ordered)
            header = table.horizontalHeader()
            order = Qt.SortOrder.AscendingOrder if sort_ascending else Qt.SortOrder.DescendingOrder
            header.setSortIndicator(sort_column, order)

        def on_header_clicked(logical_index: int) -> None:
            nonlocal sort_column, sort_ascending
            if logical_index == sort_column:
                sort_ascending = not sort_ascending
            else:
                sort_column = logical_index
                # Numeric columns start descending; text/date start ascending.
                sort_ascending = logical_index not in _NUMERIC_COLUMNS
            apply_sort()

        header = table.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.setSectionResizeMode(_COL_COUNT, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(_COL_ACTION, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(_COL_CATEGORY, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(_COL_GUI, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(_COL_CLI, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(_COL_LAST_USED, QHeaderView.ResizeMode.ResizeToContents)
        header.sectionClicked.connect(on_header_clicked)

        apply_sort()
        layout.addWidget(table)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        apply_emoji_dialog_buttons(close_box)
        close_box.rejected.connect(dialog.reject)
        button_layout.addWidget(close_box)
        layout.addLayout(button_layout)

    return _build
```

</details>
