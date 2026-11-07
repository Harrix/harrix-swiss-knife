"""Compact Fluent filter toolbar for the Fitness process table."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.apps.common.tracker_filter_chrome import (
    hide_filter_labels,
    inline_filter_caption,
    install_tracker_filter_shell,
    prepare_date_filter_fields,
    prepare_filter_combo,
    refresh_tracker_filter_chips,
    sync_filter_button_marker,
)

FILTER_ALL_EXERCISES = "All exercises"
FILTER_ALL_TYPES = "All types"
_FILTER_ALL_VALUES = frozenset({"", FILTER_ALL_EXERCISES, FILTER_ALL_TYPES})


def advanced_process_filter_is_active(host: Any) -> bool:
    """Return whether any process advanced filter is applied."""
    if selected_process_filter_value(host.comboBox_filter_exercise.currentText()):
        return True
    if selected_process_filter_value(host.comboBox_filter_type.currentText()):
        return True
    return bool(host.checkBox_use_date_filter.isChecked())


def install_process_filter_chrome(host: Any) -> None:
    """Rebuild the process filter strip: Filter + chips + advanced panel."""
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
    install_tracker_filter_shell(
        host,
        object_name_prefix="process",
        search_edit=None,
        search_placeholder="",
        advanced_rows=(
            (host.comboBox_filter_exercise, host.comboBox_filter_type),
            (
                inline_filter_caption("From", host.dateEdit_filter_from, host.groupBox_filter),
                inline_filter_caption("To", host.dateEdit_filter_to, host.groupBox_filter),
                host.checkBox_use_date_filter,
            ),
        ),
        vertical_layout=host.verticalLayout_process,
        table_widget=host.tableView_process,
    )


def refresh_process_filter_chips(host: Any) -> None:
    """Rebuild closable chips for active process filters."""
    chips: list[tuple[str, Any]] = []
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
    """Update Filter button marker for advanced process filters."""
    if hasattr(host, "pushButton_filter"):
        sync_filter_button_marker(
            host.pushButton_filter,
            advanced_active=advanced_process_filter_is_active(host),
        )
