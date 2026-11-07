"""Compact Fluent filter toolbar for the Food log table."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.apps.common.tracker_filter_chrome import (
    hide_filter_labels,
    inline_filter_caption,
    install_tracker_filter_shell,
    prepare_date_filter_fields,
    prepare_filter_combo,
    refresh_tracker_filter_chips,
    sync_filter_button_marker,
)
from harrix_swiss_knife.qt_lucide_icon import create_lucide_icon

if TYPE_CHECKING:
    from PySide6.QtWidgets import QComboBox

FILTER_ALL_TYPES = "All types"
FILTER_TYPE_DRINK = "Drink"
FILTER_TYPE_FOOD = "Food"
FOOD_LUCIDE_ICON = "utensils"
DRINK_LUCIDE_ICON = "cup-soda"
_FILTER_TYPE_ICON_SIZE = 16


def advanced_food_log_filter_is_active(host: Any) -> bool:
    """Return whether any non-search food log filter is applied."""
    if food_log_filter_type_value(host.comboBox_filter_type) in {FILTER_TYPE_FOOD, FILTER_TYPE_DRINK}:
        return True
    return bool(host.checkBox_use_date_filter.isChecked())


def food_log_filter_type_value(combo: QComboBox) -> str:
    """Return the stored food/drink filter value (`itemData`)."""
    data = combo.currentData()
    if isinstance(data, str):
        return data.strip()
    if data is not None:
        text = str(data).strip()
        if text:
            return text
    text = combo.currentText().strip()
    if text in {FILTER_TYPE_FOOD, FILTER_TYPE_DRINK}:
        return text
    return ""


def install_food_log_filter_chrome(host: Any) -> None:
    """Rebuild the food log filter strip: search + Filter + chips + advanced panel."""
    hide_filter_labels(
        host.label_filter_name,
        host.label_filter_type,
        host.label_filter_date,
        host.label_filter_to,
    )
    populate_food_log_type_filter(host.comboBox_filter_type)
    prepare_date_filter_fields(
        host.dateEdit_filter_from,
        host.dateEdit_filter_to,
        host.checkBox_use_date_filter,
    )
    install_tracker_filter_shell(
        host,
        object_name_prefix="foodLog",
        search_edit=host.lineEdit_filter_name,
        search_placeholder="Search name…",
        advanced_rows=(
            (host.comboBox_filter_type,),
            (
                inline_filter_caption("From", host.dateEdit_filter_from, host.groupBox_filter),
                inline_filter_caption("To", host.dateEdit_filter_to, host.groupBox_filter),
                host.checkBox_use_date_filter,
            ),
        ),
        vertical_layout=host.verticalLayout_food_log,
        table_widget=host.tableView_food_log,
    )


def populate_food_log_type_filter(combo: QComboBox) -> None:
    """Fill the food log type filter with Food/Drink Lucide icons."""
    selected = food_log_filter_type_value(combo)
    combo.blockSignals(True)  # noqa: FBT003
    try:
        combo.clear()
        combo.addItem(FILTER_ALL_TYPES, "")
        combo.addItem(
            create_lucide_icon(FOOD_LUCIDE_ICON, _FILTER_TYPE_ICON_SIZE),
            FILTER_TYPE_FOOD,
            FILTER_TYPE_FOOD,
        )
        combo.addItem(
            create_lucide_icon(DRINK_LUCIDE_ICON, _FILTER_TYPE_ICON_SIZE),
            FILTER_TYPE_DRINK,
            FILTER_TYPE_DRINK,
        )
        combo.setCurrentIndex(max(combo.findData(selected), 0))
    finally:
        combo.blockSignals(False)  # noqa: FBT003
    prepare_filter_combo(combo, FILTER_ALL_TYPES, "Type")


def refresh_food_log_filter_chips(host: Any) -> None:
    """Rebuild closable chips for active advanced food log filters."""
    chips: list[tuple[str, Any]] = []
    type_value = food_log_filter_type_value(host.comboBox_filter_type)
    if type_value == FILTER_TYPE_FOOD:
        chips.append((FILTER_TYPE_FOOD, host.clear_food_log_type_filter))
    elif type_value == FILTER_TYPE_DRINK:
        chips.append((FILTER_TYPE_DRINK, host.clear_food_log_type_filter))
    if host.checkBox_use_date_filter.isChecked():
        date_from = host.dateEdit_filter_from.date().toString("yyyy-MM-dd")
        date_to = host.dateEdit_filter_to.date().toString("yyyy-MM-dd")
        chips.append((f"{date_from} → {date_to}", host.clear_food_log_date_filter))
    refresh_tracker_filter_chips(host, chips)


def sync_food_log_filter_button(host: Any) -> None:
    """Update Filter button marker for advanced food log filters."""
    if hasattr(host, "pushButton_filter"):
        sync_filter_button_marker(
            host.pushButton_filter,
            advanced_active=advanced_food_log_filter_is_active(host),
        )
