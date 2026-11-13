"""Compact Fluent filter toolbar for the Fitness process table."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLineEdit

from harrix_swiss_knife.apps.common.tracker_filter_chrome import (
    hide_filter_labels,
    inline_filter_caption,
    install_tracker_filter_shell,
    prepare_date_filter_fields,
    prepare_filter_combo,
    refresh_tracker_filter_chips,
)
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT

FILTER_ALL_EXERCISES = "All exercises"
FILTER_ALL_TYPES = "All types"
_FILTER_ALL_VALUES = frozenset({"", FILTER_ALL_EXERCISES, FILTER_ALL_TYPES})


def advanced_process_filter_count(host: Any) -> int:
    """Return how many process filters are applied (search, exercise, type, date)."""
    count = 0
    if process_history_search_text(host):
        count += 1
    if selected_process_filter_value(host.comboBox_filter_exercise.currentText()):
        count += 1
    if selected_process_filter_value(host.comboBox_filter_type.currentText()):
        count += 1
    if host.checkBox_use_date_filter.isChecked():
        count += 1
    return count


def advanced_process_filter_is_active(host: Any) -> bool:
    """Return whether any process advanced filter is applied."""
    return advanced_process_filter_count(host) > 0


def install_process_filter_chrome(host: Any) -> None:
    """Rebuild the process filter strip: search + exercise/type, dates behind Filter."""
    hide_filter_labels(
        host.label_filter_exercise,
        host.label_filter_type,
        host.label_filter_date,
        host.label_filter_to,
    )
    if host.comboBox_filter_exercise.count() == 0:
        host.comboBox_filter_exercise.addItem(FILTER_ALL_EXERCISES)
    elif not host.comboBox_filter_exercise.itemText(0).strip():
        host.comboBox_filter_exercise.setItemText(0, FILTER_ALL_EXERCISES)
    if host.comboBox_filter_type.count() == 0:
        host.comboBox_filter_type.addItem(FILTER_ALL_TYPES)
    elif not host.comboBox_filter_type.itemText(0).strip():
        host.comboBox_filter_type.setItemText(0, FILTER_ALL_TYPES)
    prepare_filter_combo(host.comboBox_filter_exercise, FILTER_ALL_EXERCISES, "Exercise")
    prepare_filter_combo(host.comboBox_filter_type, FILTER_ALL_TYPES, "Type")
    prepare_date_filter_fields(
        host.dateEdit_filter_from,
        host.dateEdit_filter_to,
        host.checkBox_use_date_filter,
    )
    search_edit = getattr(host, "lineEdit_process_search", None)
    if not isinstance(search_edit, QLineEdit):
        search_edit = QLineEdit(host.groupBox_filter)
        search_edit.setObjectName("lineEdit_process_search")
        host.lineEdit_process_search = search_edit
    search_edit.setMinimumHeight(CONTROL_HEIGHT)
    search_edit.setClearButtonEnabled(True)  # noqa: FBT003
    install_tracker_filter_shell(
        host,
        object_name_prefix="process",
        search_edit=search_edit,
        search_placeholder="Search sets…",
        toolbar_widgets=(host.comboBox_filter_exercise, host.comboBox_filter_type),
        advanced_rows=(
            (
                inline_filter_caption("From", host.dateEdit_filter_from, host.groupBox_filter),
                inline_filter_caption("To", host.dateEdit_filter_to, host.groupBox_filter),
                host.checkBox_use_date_filter,
            ),
        ),
        vertical_layout=host.verticalLayout_process,
        table_widget=host.tableView_process,
    )


def process_history_search_text(host: Any) -> str:
    """Return the process-history search query (independent of catalog filter)."""
    edit = getattr(host, "lineEdit_process_search", None)
    if not isinstance(edit, QLineEdit):
        return ""
    return edit.text().strip()


def refresh_process_filter_chips(host: Any) -> None:
    """Rebuild closable chips for active process filters."""
    chips: list[tuple[str, Any]] = []
    search = process_history_search_text(host)
    if search:
        chips.append((f"Search: {search}", host.clear_process_search_filter))
    exercise = selected_process_filter_value(host.comboBox_filter_exercise.currentText())
    if exercise:
        chips.append((exercise, host.clear_process_exercise_filter))
    exercise_type = selected_process_filter_value(host.comboBox_filter_type.currentText())
    if exercise_type:
        chips.append((exercise_type, host.clear_process_type_filter))
    if host.checkBox_use_date_filter.isChecked():
        date_from = host.dateEdit_filter_from.date().toString("yyyy-MM-dd")
        date_to = host.dateEdit_filter_to.date().toString("yyyy-MM-dd")
        chips.append((f"{date_from} → {date_to}", host.clear_process_date_filter))
    refresh_tracker_filter_chips(host, chips)


def selected_process_filter_value(text: str) -> str:
    """Return a concrete process filter value, or `""` for an `all` sentinel."""
    value = text.strip()
    return "" if value in _FILTER_ALL_VALUES else value


def sync_process_filter_button(host: Any) -> None:
    """Update Filter button text with the active filter count."""
    if hasattr(host, "pushButton_filter"):
        count = advanced_process_filter_count(host)
        host.pushButton_filter.setText(f"Filter ({count})" if count else "Filter")
