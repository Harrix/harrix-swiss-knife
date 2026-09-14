"""Action usage statistics table dialog builder."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, TypedDict

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from harrix_swiss_knife.apps.common.table_export import export_table_via_dialog
from harrix_swiss_knife.qt_action_icon import create_menu_icon
from harrix_swiss_knife.qt_lucide_icon import (
    apply_lucide_dialog_buttons,
    make_lucide_push_button,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtCore import QPoint
    from PySide6.QtGui import QIcon


class ActionUsageStatsRow(TypedDict):
    """One row for the action usage stats table."""

    count: int
    title: str
    icon: str
    category: str
    gui: int
    cli: int
    last_used: str


def build_action_usage_stats_browser(
    rows: list[ActionUsageStatsRow],
    *,
    summary: str,
) -> Callable[[QDialog, QVBoxLayout], None]:
    """Return dialog layout builder: summary label + sortable usage table."""

    def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
        summary_label = QLabel(summary)
        summary_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        summary_label.setWordWrap(True)
        layout.addWidget(summary_label)

        table = QTableWidget(0, len(_HEADERS))
        table.setHorizontalHeaderLabels(list(_HEADERS))
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setSortingEnabled(False)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

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

        def on_copy() -> None:
            copy_table_widget_selection(table)

        def on_save_excel() -> None:
            export_table_via_dialog(
                dialog,
                table.model(),
                prefer="xlsx",
                title="Save action usage stats",
                sheet_name="Action usage",
            )

        def on_context_menu(pos: QPoint) -> None:
            menu = QMenu(table)
            copy_action = menu.addAction("Copy")
            excel_action = menu.addAction("Save as Excel…")
            chosen = menu.exec_(table.viewport().mapToGlobal(pos))
            if chosen is copy_action:
                on_copy()
            elif chosen is excel_action:
                on_save_excel()

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
        table.customContextMenuRequested.connect(on_context_menu)

        copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, table)
        copy_shortcut.activated.connect(on_copy)

        apply_sort()
        layout.addWidget(table)

        button_layout = QHBoxLayout()
        save_excel_button = make_lucide_push_button("Save as Excel…", "chart-column")
        save_excel_button.clicked.connect(on_save_excel)
        button_layout.addWidget(save_excel_button)
        button_layout.addStretch()
        close_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        apply_lucide_dialog_buttons(close_box)
        close_box.rejected.connect(dialog.reject)
        button_layout.addWidget(close_box)
        layout.addLayout(button_layout)

    return _build


def copy_table_widget_selection(table: QTableWidget) -> str:
    """Copy selected cells to the clipboard as tab-separated text.

    Returns the copied text (empty when nothing is selected).

    """
    indexes = table.selectedIndexes()
    if not indexes:
        return ""
    indexes = sorted(indexes, key=lambda index: (index.row(), index.column()))
    rows_data: dict[int, dict[int, str]] = {}
    for index in indexes:
        item = table.item(index.row(), index.column())
        rows_data.setdefault(index.row(), {})[index.column()] = item.text() if item is not None else ""
    lines: list[str] = []
    for row in sorted(rows_data):
        cells = rows_data[row]
        min_col = min(cells)
        max_col = max(cells)
        lines.append("\t".join(cells.get(col, "") for col in range(min_col, max_col + 1)))
    text = "\n".join(lines)
    clipboard = QApplication.clipboard()
    if clipboard is not None and text:
        clipboard.setText(text)
    return text


def _format_last_used(value: str) -> str:
    """Return local date-time without timezone offset."""
    if not value:
        return "—"
    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return value.replace("T", " ")


def _row_icon(icon_name: str) -> QIcon:
    """Build a table icon from the GUI action icon spec (custom SVG or emoji)."""
    return create_menu_icon(icon_name, 18)


_COL_COUNT = 0
_COL_ACTION = 1
_COL_CATEGORY = 2
_COL_GUI = 3
_COL_CLI = 4
_COL_LAST_USED = 5

_HEADERS = ("Count", "Action", "Category", "GUI", "CLI", "Last used")
_NUMERIC_COLUMNS = frozenset({_COL_COUNT, _COL_GUI, _COL_CLI})
