"""Fluent chrome for Habit Tracker secondary panes (process table + charts)."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QAbstractItemView, QLabel, QListView, QTableView

from harrix_swiss_knife.apps.common.tracker_layout_chrome import (
    apply_tracker_column_surfaces,
    quiet_group_box,
)
from harrix_swiss_knife.apps.common.tracker_splitter_settings import load_splitter_sizes, save_splitter_sizes
from harrix_swiss_knife.apps.common.ui_chrome import MUTED_TEXT, button_idle_qss
from harrix_swiss_knife.fluent.theme import bind_theme
from harrix_swiss_knife.fluent.tokens import ICON_SIZE, SPACE_S
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon

TABLE_ROW_HEIGHT = 30
_HABITS_SPLITTER_KEY = "habits_process_splitter_sizes_v1"
_HABITS_SPLITTER_DEFAULT = (320, 1248)
_CHARTS_SPLITTER_KEY = "habits_charts_splitter_sizes_v1"
_CHARTS_SPLITTER_DEFAULT = (220, 1348)
_FORM_MIN = 280
_FILTER_MIN = 180
_CONTENT_MIN = 400
_SPLITTER_SAVE_DELAY_MS = 400
_TWO_PANE = 2


def install_habits_layout_chrome(host: Any) -> None:
    """Polish Habits process column and Charts filters."""
    _polish_all(host)
    _configure_habits_splitter(host)
    _configure_charts_splitter(host)
    if not getattr(host, "_habits_tabs_theme_bound", False):
        bind_theme(host, lambda: _polish_all(host))
        host._habits_tabs_theme_bound = True  # noqa: SLF001


def persist_habits_tabs_splitter_sizes(host: Any) -> None:
    """Save Habits and Charts splitter sizes."""
    if getattr(host, "_is_closing", False):
        return
    for attr, key, default in (
        ("splitter_habits", _HABITS_SPLITTER_KEY, _HABITS_SPLITTER_DEFAULT),
        ("splitter_charts", _CHARTS_SPLITTER_KEY, _CHARTS_SPLITTER_DEFAULT),
    ):
        splitter = getattr(host, attr, None)
        if splitter is None:
            continue
        sizes = splitter.sizes()
        if len(sizes) == _TWO_PANE and all(size > 0 for size in sizes):
            save_splitter_sizes(key, [int(size) for size in sizes], default)


def _caption_qss() -> str:
    return f"color: {MUTED_TEXT}; font-weight: 600; padding-top: 2px;"


def _compact_list(view: QListView) -> None:
    view.setUniformItemSizes(True)
    view.setSpacing(0)
    view.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
    view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    view.setTextElideMode(Qt.TextElideMode.ElideRight)
    view.setSelectionRectVisible(False)
    view.setMouseTracking(True)
    view.setWordWrap(False)
    view.setStyleSheet("")


def _compact_table(table: QTableView) -> None:
    vertical = table.verticalHeader()
    vertical.setDefaultSectionSize(TABLE_ROW_HEIGHT)
    vertical.setMinimumSectionSize(24)
    table.setWordWrap(False)
    table.setTextElideMode(Qt.TextElideMode.ElideRight)


def _configure_charts_splitter(host: Any) -> None:
    if not hasattr(host, "splitter_charts"):
        return
    host.layoutWidget.setMinimumWidth(_FILTER_MIN)
    host.widget_charts_heatmap.setMinimumWidth(_CONTENT_MIN)
    _wire_two_pane(
        host,
        splitter=host.splitter_charts,
        key=_CHARTS_SPLITTER_KEY,
        default=_CHARTS_SPLITTER_DEFAULT,
        flag="habits_charts_splitter",
        left_min=_FILTER_MIN,
        right_min=_CONTENT_MIN,
        left_max_share=5,
    )


def _configure_habits_splitter(host: Any) -> None:
    if not hasattr(host, "splitter_habits"):
        return
    host.frame_habits.setMinimumWidth(_FORM_MIN)
    host.tableView_process_habits.setMinimumWidth(_CONTENT_MIN)
    _wire_two_pane(
        host,
        splitter=host.splitter_habits,
        key=_HABITS_SPLITTER_KEY,
        default=_HABITS_SPLITTER_DEFAULT,
        flag="habits_process_splitter",
        left_min=_FORM_MIN,
        right_min=_CONTENT_MIN,
        left_max_share=4,
    )


def _polish_all(host: Any) -> None:
    soft: list[tuple[Any, str]] = []
    content: list[tuple[Any, str]] = []
    if hasattr(host, "frame_habits"):
        soft.append((host.frame_habits, "habitsEntryForm"))
    if hasattr(host, "layoutWidget"):
        soft.append((host.layoutWidget, "habitsChartsForm"))
    if hasattr(host, "tableView_process_habits"):
        content.append((host.tableView_process_habits, "habitsProcessPane"))
    if hasattr(host, "widget_charts_heatmap"):
        content.append((host.widget_charts_heatmap, "habitsChartsPane"))

    apply_tracker_column_surfaces(host, soft_panes=soft, content_panes=content)
    for name in ("groupBox_habits_5", "groupBox_habits_2"):
        box = getattr(host, name, None)
        if box is not None:
            quiet_group_box(box)

    if hasattr(host, "tableView_process_habits"):
        _compact_table(host.tableView_process_habits)

    for name in ("label_filter_habit", "label_filter_habit_year"):
        label = getattr(host, name, None)
        if isinstance(label, QLabel):
            label.setStyleSheet(_caption_qss())
            font = QFont(label.font())
            font.setBold(True)
            label.setFont(font)

    for view_name in ("listView_filter_habit", "listView_filter_habit_year"):
        view = getattr(host, view_name, None)
        if isinstance(view, QListView):
            _compact_list(view)

    for name, tooltip, icon in (
        ("pushButton_charts_heatmap_prev_year", "Previous year", "chevron-left"),
        ("pushButton_charts_heatmap_next_year", "Next year", "chevron-right"),
    ):
        button = getattr(host, name, None)
        if button is None:
            continue
        button.setText("")
        button.setToolTip(tooltip)
        button.setStyleSheet(button_idle_qss())
        apply_lucide_button_icon(button, icon)

    if hasattr(host, "verticalLayout_23"):
        host.verticalLayout_23.setSpacing(SPACE_S)
        host.verticalLayout_23.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)


def _wire_two_pane(
    host: Any,
    *,
    splitter: Any,
    key: str,
    default: tuple[int, ...],
    flag: str,
    left_min: int,
    right_min: int,
    left_max_share: int,
) -> None:
    splitter.setChildrenCollapsible(False)
    splitter.setStretchFactor(0, 0)
    splitter.setStretchFactor(1, 1)
    saved = load_splitter_sizes(key, default)
    moved_attr = f"_{flag}_user_moved"
    timer_attr = f"_{flag}_save_timer"
    bound_attr = f"_{flag}_save_bound"
    setattr(host, moved_attr, False)

    def apply_sizes() -> None:
        if getattr(host, "_is_closing", False) or getattr(host, moved_attr, False):
            return
        total = splitter.width()
        if total <= 0:
            total = max(host.width(), sum(saved))
        sizes = list(saved)
        if sum(sizes) != total and total > 0:
            scale = total / max(sum(sizes), 1)
            sizes = [max(1, round(size * scale)) for size in sizes]
            sizes[1] = max(1, total - sizes[0])
        sizes[0] = min(max(sizes[0], left_min), max(left_min, total // left_max_share))
        sizes[1] = max(right_min, total - sizes[0])
        sizes[0] = max(1, total - sizes[1])
        splitter.setSizes(sizes)

    def on_moved(*_args: object) -> None:
        setattr(host, moved_attr, True)
        getattr(host, timer_attr).start()

    setattr(host, f"_apply_{flag}_sizes", apply_sizes)
    apply_sizes()
    QTimer.singleShot(60, apply_sizes)
    if not getattr(host, bound_attr, False):
        timer = QTimer(host)
        timer.setSingleShot(True)
        timer.setInterval(_SPLITTER_SAVE_DELAY_MS)
        timer.timeout.connect(lambda: persist_habits_tabs_splitter_sizes(host))
        setattr(host, timer_attr, timer)
        splitter.splitterMoved.connect(on_moved)
        setattr(host, bound_attr, True)
