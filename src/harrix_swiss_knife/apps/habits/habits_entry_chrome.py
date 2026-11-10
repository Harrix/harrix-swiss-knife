"""Fluent chrome for Habit Tracker entry panels (sets of habits form)."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.apps.common.tracker_layout_chrome import polish_left_field_labels, quiet_group_box
from harrix_swiss_knife.apps.common.ui_chrome import button_cta_cyan_qss, button_idle_qss
from harrix_swiss_knife.fluent.theme import bind_theme
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, SPACE_S, SPACE_XS
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon


def install_habits_entry_chrome(host: Any) -> None:
    """Polish Habit form buttons, captions, and quiet GroupBoxes."""
    _polish_form(host)
    if not getattr(host, "_habits_entry_theme_bound", False):
        bind_theme(host, lambda: _polish_form(host))
        host._habits_entry_theme_bound = True  # noqa: SLF001


def _polish_form(host: Any) -> None:
    if hasattr(host, "groupBox_habits_2"):
        host.groupBox_habits_2.setTitle("New habit")
        quiet_group_box(host.groupBox_habits_2)
    if hasattr(host, "groupBox_habits_5"):
        host.groupBox_habits_5.setTitle("Commands")
        quiet_group_box(host.groupBox_habits_5)

    if hasattr(host, "verticalLayout_23"):
        host.verticalLayout_23.setSpacing(SPACE_S)
        host.verticalLayout_23.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)

    polish_left_field_labels(
        host,
        (
            ("label_habits_5", "Name:"),
            ("label_habit_emoji", "Emoji:"),
        ),
    )

    for control_name in (
        "lineEdit_habit_name",
        "lineEdit_habit_emoji",
        "pushButton_habit_add_new",
        "pushButton_habit_choose_emoji",
        "pushButton_habits_delete",
        "pushButton_habits_refresh",
        "pushButton_habits_show_all_records",
        "pushButton_habits_export_csv",
    ):
        control = getattr(host, control_name, None)
        if control is not None:
            control.setMinimumHeight(CONTROL_HEIGHT)

    add_button = getattr(host, "pushButton_habit_add_new", None)
    if add_button is not None:
        add_button.setText("Add habit")
        add_button.setStyleSheet(button_cta_cyan_qss())
        apply_lucide_button_icon(add_button, "plus")

    for name, icon in (
        ("pushButton_habits_delete", "trash-2"),
        ("pushButton_habits_refresh", "refresh-cw"),
        ("pushButton_habits_show_all_records", "list"),
        ("pushButton_habits_export_csv", "download"),
        ("pushButton_habit_choose_emoji", "smile"),
    ):
        button = getattr(host, name, None)
        if button is not None:
            button.setStyleSheet(button_idle_qss())
            apply_lucide_button_icon(button, icon)

    # Keep a little air under the commands block before the add form.
    if hasattr(host, "verticalLayout_habits_10"):
        host.verticalLayout_habits_10.setSpacing(SPACE_XS)
