"""Shared labels and helpers for app table context menus.

Menu order:

1. Row / cell actions (Edit, Open, Favorite, …)
2. Date-in-form actions
3. Create / add actions
4. Table utilities (Refresh, Export)
5. Disabled info rows (sum, totals)
6. Filters + Clear all filters
7. Delete — always last

"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import QMenu

LABEL_CLEAR_CELL = "🗑️ Clear cell"
LABEL_CLEAR_FILTERS = "🧹 Clear all filters"
LABEL_DELETE = "🗑️ Delete"
LABEL_EDIT = "✏️ Edit"
LABEL_EXPORT_CSV = "📤 Export to CSV"
LABEL_EXPORT_EXCEL = "📊 Export to Excel"
LABEL_FILTER_BY_CATEGORY = "🔍 Filter by this category"
LABEL_FILTER_BY_DATE = "📅 Filter by this date"
LABEL_FILTER_BY_EXERCISE = "🔍 Filter by this exercise"
LABEL_FILTER_BY_NAME = "🔍 Filter by this name"
LABEL_FILTER_BY_TYPE = "🔍 Filter by this type"
LABEL_OPEN_LIGHTBOX = "🖼️ Open image in lightbox"
LABEL_REFRESH = "🔄 Refresh"
LABEL_REVEAL_IN_EXPLORER = "📂 Reveal in File Explorer"
LABEL_SET_DATE = "📅 Set this date in main field"
LABEL_SET_DATE_MINUS_ONE = "📅 Set this date - 1 day in main field"
LABEL_SET_DATE_PLUS_ONE = "📅 Set this date + 1 day in main field"
LABEL_SET_DATE_SELECTED = "✍️ Set date for selected rows…"
LABEL_SHOW_ALL_RECORDS = "📋 Show all records"


def add_clear_filters_action(menu: QMenu) -> QAction:
    """Add `Clear all filters` inside the filters block above Delete."""
    return menu.addAction(LABEL_CLEAR_FILTERS)


def add_date_in_main_field_actions(menu: QMenu) -> tuple[QAction, QAction, QAction]:
    """Add the three “set this date in the main field” commands."""
    add_separator(menu)
    set_date = menu.addAction(LABEL_SET_DATE)
    plus_one = menu.addAction(LABEL_SET_DATE_PLUS_ONE)
    minus_one = menu.addAction(LABEL_SET_DATE_MINUS_ONE)
    return set_date, plus_one, minus_one


def add_delete_action(menu: QMenu) -> QAction:
    """Add `Delete` as the last command, after a separator when needed."""
    add_separator(menu)
    return menu.addAction(LABEL_DELETE)


def add_export_actions(menu: QMenu) -> tuple[QAction, QAction]:
    """Add CSV and Excel export commands."""
    csv_action = menu.addAction(LABEL_EXPORT_CSV)
    excel_action = menu.addAction(LABEL_EXPORT_EXCEL)
    return csv_action, excel_action


def add_info_action(menu: QMenu, text: str) -> QAction:
    """Add a disabled informational row (sum, totals) before Delete."""
    add_separator(menu)
    action = menu.addAction(text)
    action.setEnabled(False)
    return action


def add_separator(menu: QMenu) -> None:
    """Add a separator unless the menu is empty or already ends with one."""
    if menu.isEmpty() or last_action_is_separator(menu):
        return
    menu.addSeparator()


def begin_filters_block(menu: QMenu) -> None:
    """Start the Filter-by / Clear-filters group placed immediately above Delete."""
    add_separator(menu)


def last_action_is_separator(menu: QMenu) -> bool:
    """Return whether the last menu item is already a separator."""
    actions = menu.actions()
    return bool(actions) and actions[-1].isSeparator()


def show_records_label(*, show_all: bool, last_count: int) -> str:
    """Label that toggles between all records and the last `last_count`."""
    if show_all:
        return f"📋 Show last {last_count}"
    return LABEL_SHOW_ALL_RECORDS
