"""Fluent chrome for Food Tracker tabs beyond the main entry form."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QTableView

from harrix_swiss_knife.apps.common.tracker_layout_chrome import (
    apply_tracker_column_surfaces,
    install_tracker_column_chrome,
    show_splitter_hairlines,
)
from harrix_swiss_knife.apps.common.tracker_splitter_settings import load_splitter_sizes, save_splitter_sizes
from harrix_swiss_knife.apps.common.ui_chrome import button_idle_qss, muted_caption_qss
from harrix_swiss_knife.fluent.theme import bind_theme
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, SPACE_S
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon

TABLE_ROW_HEIGHT = 30
_STATS_SPLITTER_KEY = "food_stats_splitter_sizes_v1"
_STATS_SPLITTER_DEFAULT = (480, 1088)
_STATS_LEFT_MIN = 360
_STATS_RIGHT_MIN = 400
_SPLITTER_SAVE_DELAY_MS = 400
_TWO_PANE = 2


def install_food_layout_chrome(host: Any) -> None:
    """Apply flat panes plus Stats-tab Fluent polish."""
    content = [
        (host.frame_food_controls, "foodEntryForm"),
        (host.widget_food_middle, "foodEntryItems"),
        (host.widget_food_log, "foodLogPane"),
    ]
    if hasattr(host, "frame") and host.frame is not None:
        content.append((host.frame, "foodStatsTablePane"))
    if hasattr(host, "widget_food_stats_chart"):
        content.append((host.widget_food_stats_chart, "foodStatsChartPane"))

    boxes = [
        host.groupBox_food_add,
        host.groupBox_food_commands,
        host.groupBox_food_today,
        host.groupBox_food_yesterday,
    ]
    splitters = []
    if hasattr(host, "splitter_food"):
        splitters.append(host.splitter_food)
    if hasattr(host, "splitter_food_stats"):
        splitters.append(host.splitter_food_stats)
    install_tracker_column_chrome(
        host,
        soft_panes=(),
        content_panes=content,
        quiet_boxes=boxes,
        splitters=splitters,
        theme_flag="_food_layout_chrome_theme_bound",
    )
    _polish_stats_tab(host)
    _configure_stats_splitter(host)
    if not getattr(host, "_food_stats_theme_bound", False):
        bind_theme(host, lambda: _polish_stats_tab(host))
        host._food_stats_theme_bound = True  # noqa: SLF001


def persist_food_stats_splitter_sizes(host: Any) -> None:
    """Save Food Statistics splitter sizes."""
    if getattr(host, "_is_closing", False) or not hasattr(host, "splitter_food_stats"):
        return
    sizes = host.splitter_food_stats.sizes()
    if len(sizes) == _TWO_PANE and all(size > 0 for size in sizes):
        save_splitter_sizes(_STATS_SPLITTER_KEY, [int(size) for size in sizes], _STATS_SPLITTER_DEFAULT)


def _caption_qss() -> str:
    return muted_caption_qss(extra=" padding-top: 2px;")


def _compact_table(table: QTableView) -> None:
    vertical = table.verticalHeader()
    vertical.setDefaultSectionSize(TABLE_ROW_HEIGHT)
    vertical.setMinimumSectionSize(24)
    table.setWordWrap(False)
    table.setTextElideMode(Qt.TextElideMode.ElideRight)


def _configure_stats_splitter(host: Any) -> None:
    if not hasattr(host, "splitter_food_stats"):
        return
    host.frame.setMinimumWidth(_STATS_LEFT_MIN)
    host.widget_food_stats_chart.setMinimumWidth(_STATS_RIGHT_MIN)
    host.splitter_food_stats.setChildrenCollapsible(False)
    host.splitter_food_stats.setStretchFactor(0, 0)
    host.splitter_food_stats.setStretchFactor(1, 1)
    saved = load_splitter_sizes(_STATS_SPLITTER_KEY, _STATS_SPLITTER_DEFAULT)
    host._food_stats_splitter_user_moved = False  # noqa: SLF001

    def apply_sizes() -> None:
        if getattr(host, "_is_closing", False) or getattr(host, "_food_stats_splitter_user_moved", False):
            return
        total = host.splitter_food_stats.width()
        if total <= 0:
            total = max(host.width(), sum(saved))
        sizes = list(saved)
        if sum(sizes) != total and total > 0:
            scale = total / max(sum(sizes), 1)
            sizes = [max(1, round(size * scale)) for size in sizes]
            sizes[1] = max(1, total - sizes[0])
        sizes[0] = min(max(sizes[0], _STATS_LEFT_MIN), max(_STATS_LEFT_MIN, total // 2))
        sizes[1] = max(_STATS_RIGHT_MIN, total - sizes[0])
        sizes[0] = max(1, total - sizes[1])
        host.splitter_food_stats.setSizes(sizes)

    def on_moved(*_args: object) -> None:
        host._food_stats_splitter_user_moved = True  # noqa: SLF001
        host._food_stats_splitter_save_timer.start()  # noqa: SLF001

    host._apply_food_stats_splitter_sizes = apply_sizes  # noqa: SLF001
    apply_sizes()
    QTimer.singleShot(60, apply_sizes)
    if not getattr(host, "_food_stats_splitter_save_bound", False):
        timer = QTimer(host)
        timer.setSingleShot(True)
        timer.setInterval(_SPLITTER_SAVE_DELAY_MS)
        timer.timeout.connect(lambda: persist_food_stats_splitter_sizes(host))
        host._food_stats_splitter_save_timer = timer  # noqa: SLF001
        host.splitter_food_stats.splitterMoved.connect(on_moved)
        host._food_stats_splitter_save_bound = True  # noqa: SLF001


def _polish_stats_tab(host: Any) -> None:
    if not hasattr(host, "frame_food_stats_controls"):
        return
    apply_tracker_column_surfaces(
        host,
        soft_panes=(),
        content_panes=(
            (host.frame, "foodStatsTablePane"),
            (host.widget_food_stats_chart, "foodStatsChartPane"),
        ),
    )
    if hasattr(host, "splitter_food_stats"):
        show_splitter_hairlines((host.splitter_food_stats,))
    if isinstance(getattr(host, "label", None), QLabel):
        host.label.setText("Daily calories")
        host.label.setStyleSheet(_caption_qss())
        font = QFont(host.label.font())
        font.setBold(True)
        host.label.setFont(font)
    for name in ("label_food_stats_from", "label_food_stats_to"):
        label = getattr(host, name, None)
        if isinstance(label, QLabel):
            label.setStyleSheet(_caption_qss())

    for name, text, icon in (
        ("pushButton_food_stats_last_week", "Last week", "calendar"),
        ("pushButton_food_stats_last_month", "Last month", "calendar"),
        ("pushButton_food_stats_last_year", "Last year", "calendar-range"),
        ("pushButton_food_stats_all_time", "All time", "infinity"),
        ("pushButton_food_stats_update", "Update", "refresh-cw"),
        ("pushButton_food_stats_food_weight", "Food weight", "scale"),
        ("pushButton_food_stats_drink", "Drinks", "cup-soda"),
    ):
        button = getattr(host, name, None)
        if button is None:
            continue
        button.setText(text)
        button.setMinimumHeight(CONTROL_HEIGHT)
        button.setStyleSheet(button_idle_qss())
        apply_lucide_button_icon(button, icon)

    for control_name in (
        "dateEdit_food_stats_from",
        "dateEdit_food_stats_to",
        "comboBox_food_stats_period",
    ):
        control = getattr(host, control_name, None)
        if control is not None:
            control.setMinimumHeight(CONTROL_HEIGHT)

    # Runtime macro chart buttons (created in main).
    for name, text, icon in (
        ("pushButton_food_stats_macros_protein", "Protein", "drumstick"),
        ("pushButton_food_stats_macros_fat", "Fat", "droplet"),
        ("pushButton_food_stats_macros_carb", "Carbs", "wheat"),
    ):
        button = getattr(host, name, None)
        if button is None:
            continue
        button.setText(text)
        button.setMinimumHeight(CONTROL_HEIGHT)
        button.setStyleSheet(button_idle_qss())
        apply_lucide_button_icon(button, icon)

    if hasattr(host, "tableView_kcal_per_day"):
        _compact_table(host.tableView_kcal_per_day)
    if hasattr(host, "frame_food_stats_controls"):
        host.frame_food_stats_controls.setStyleSheet(
            "QFrame#frame_food_stats_controls { background: transparent; border: none; }",
        )
    if hasattr(host, "verticalLayout_food_stats_controls"):
        host.verticalLayout_food_stats_controls.setSpacing(SPACE_S)
