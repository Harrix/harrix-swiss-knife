"""Fluent chrome for Fitness Tracker tabs beyond the Sets entry form."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QAbstractItemView, QLabel, QListView, QTableView

from harrix_swiss_knife.apps.common.tracker_layout_chrome import (
    apply_tracker_column_surfaces,
    polish_left_field_labels,
    quiet_group_box,
)
from harrix_swiss_knife.apps.common.tracker_splitter_settings import load_splitter_sizes, save_splitter_sizes
from harrix_swiss_knife.apps.common.ui_chrome import button_cta_green_qss, button_idle_qss
from harrix_swiss_knife.fluent.app_chrome import style_fluent_item_view
from harrix_swiss_knife.fluent.theme import FluentTheme, bind_theme, css, mix
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, ICON_SIZE, SPACE_S, SPACE_XS
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon

TABLE_ROW_HEIGHT = 30
_CHARTS_SPLITTER_KEY = "fitness_charts_splitter_sizes_v1"
_CHARTS_SPLITTER_DEFAULT = (320, 1248)
_EXERCISES_SPLITTER_KEY = "fitness_exercises_splitter_sizes_v1"
_EXERCISES_SPLITTER_DEFAULT = (640, 640)
_SIDE_MIN = 280
_CONTENT_MIN = 400
_SPLITTER_SAVE_DELAY_MS = 400
_TWO_PANE = 2


def install_fitness_layout_chrome(host: Any) -> None:
    """Polish Charts / Exercises / Weight / Statistics secondary tabs."""
    _polish_all(host)
    _configure_charts_splitter(host)
    _configure_exercises_splitter(host)
    if not getattr(host, "_fitness_tabs_theme_bound", False):
        bind_theme(host, lambda: _polish_all(host))
        host._fitness_tabs_theme_bound = True  # noqa: SLF001


def persist_fitness_tabs_splitter_sizes(host: Any) -> None:
    """Save Charts and Exercises splitter sizes."""
    if getattr(host, "_is_closing", False):
        return
    for attr, key, default in (
        ("splitter_charts", _CHARTS_SPLITTER_KEY, _CHARTS_SPLITTER_DEFAULT),
        ("splitter_2", _EXERCISES_SPLITTER_KEY, _EXERCISES_SPLITTER_DEFAULT),
    ):
        splitter = getattr(host, attr, None)
        if splitter is None:
            continue
        sizes = splitter.sizes()
        if len(sizes) == _TWO_PANE and all(size > 0 for size in sizes):
            save_splitter_sizes(key, [int(size) for size in sizes], default)


def _caption_qss() -> str:
    palette = FluentTheme.instance().palette()
    muted = css(mix(palette.window_bg, palette.text_secondary))
    return f"color: {muted}; font-weight: 600; padding-top: 2px;"


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
    style_fluent_item_view(view)


def _compact_table(table: QTableView) -> None:
    vertical = table.verticalHeader()
    vertical.setDefaultSectionSize(TABLE_ROW_HEIGHT)
    vertical.setMinimumSectionSize(24)
    table.setWordWrap(False)
    table.setTextElideMode(Qt.TextElideMode.ElideRight)


def _configure_charts_splitter(host: Any) -> None:
    if not hasattr(host, "splitter_charts"):
        return
    host.widget_left_panel.setMinimumWidth(_SIDE_MIN)
    host.widget_right_panel.setMinimumWidth(_CONTENT_MIN)
    _wire_two_pane(
        host,
        splitter=host.splitter_charts,
        key=_CHARTS_SPLITTER_KEY,
        default=_CHARTS_SPLITTER_DEFAULT,
        flag="fitness_charts_splitter",
        left_min=_SIDE_MIN,
        right_min=_CONTENT_MIN,
        left_max_share=3,
    )


def _configure_exercises_splitter(host: Any) -> None:
    if not hasattr(host, "splitter_2"):
        return
    _wire_two_pane(
        host,
        splitter=host.splitter_2,
        key=_EXERCISES_SPLITTER_KEY,
        default=_EXERCISES_SPLITTER_DEFAULT,
        flag="fitness_exercises_splitter",
        left_min=_CONTENT_MIN,
        right_min=_CONTENT_MIN,
        left_max_share=2,
    )


def _idle_button(host: Any, name: str, text: str, icon: str) -> None:
    button = getattr(host, name, None)
    if button is None:
        return
    button.setText(text)
    button.setMinimumHeight(CONTROL_HEIGHT)
    button.setStyleSheet(button_idle_qss())
    apply_lucide_button_icon(button, icon)


def _polish_all(host: Any) -> None:
    soft: list[tuple[Any, str]] = [
        (host.frame, "fitnessEntryForm"),
        (host.widget_middle, "fitnessExerciseList"),
    ]
    content: list[tuple[Any, str]] = [(host.widget_process, "fitnessProcessPane")]
    if hasattr(host, "widget_left_panel"):
        soft.append((host.widget_left_panel, "fitnessChartsForm"))
    if hasattr(host, "widget_right_panel"):
        content.append((host.widget_right_panel, "fitnessChartsPane"))
    if hasattr(host, "frame_4"):
        soft.append((host.frame_4, "fitnessWeightForm"))
    if hasattr(host, "frame_5"):
        soft.append((host.frame_5, "fitnessStatisticsForm"))
    if hasattr(host, "widget_top"):
        soft.append((host.widget_top, "fitnessExercisesTop"))
    if hasattr(host, "widget_bottom"):
        soft.append((host.widget_bottom, "fitnessExercisesBottom"))

    apply_tracker_column_surfaces(host, soft_panes=soft, content_panes=content)
    for name in ("groupBox", "groupBox_9", "groupBox_type_of_charts", "groupBox_4", "groupBox_6", "groupBox_10"):
        box = getattr(host, name, None)
        if box is not None:
            quiet_group_box(box)

    _polish_charts(host)
    _polish_exercises(host)
    _polish_weight(host)
    _polish_statistics(host)


def _polish_charts(host: Any) -> None:
    if hasattr(host, "groupBox_type_of_charts"):
        host.groupBox_type_of_charts.setTitle("Chart type")
    for name in (
        "label_chart_exercise",
        "label_chart_type",
        "label_chart_period",
        "label_chart_from",
        "label_chart_to",
    ):
        label = getattr(host, name, None)
        if isinstance(label, QLabel):
            label.setStyleSheet(_caption_qss())
            if name in {"label_chart_exercise", "label_chart_type"}:
                font = QFont(label.font())
                font.setBold(True)
                label.setFont(font)

    for name, text, icon in (
        ("pushButton_update_chart", "Update chart", "refresh-cw"),
        ("pushButton_chart_last_month", "Last month", "calendar"),
        ("pushButton_chart_last_year", "Last year", "calendar-range"),
        ("pushButton_chart_all_time", "All time", "infinity"),
    ):
        _idle_button(host, name, text, icon)

    for control_name in (
        "comboBox_chart_period",
        "dateEdit_chart_from",
        "dateEdit_chart_to",
        "spinBox_compare_last",
        "comboBox_compare_same_months",
    ):
        control = getattr(host, control_name, None)
        if control is not None:
            control.setMinimumHeight(CONTROL_HEIGHT)

    for view_name in ("listView_chart_exercise", "listView_chart_type"):
        view = getattr(host, view_name, None)
        if isinstance(view, QListView):
            _compact_list(view)
    if hasattr(host, "verticalLayout_18"):
        host.verticalLayout_18.setSpacing(SPACE_S)
        host.verticalLayout_18.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_XS)


def _polish_exercises(host: Any) -> None:
    for name in ("label_exercises_table", "label_exercise_types_table"):
        label = getattr(host, name, None)
        if isinstance(label, QLabel):
            label.setStyleSheet(_caption_qss())
            font = QFont(label.font())
            font.setBold(True)
            label.setFont(font)

    add_exercise = getattr(host, "pushButton_exercise_add", None)
    if add_exercise is not None:
        add_exercise.setText("Add exercise")
        add_exercise.setMinimumHeight(CONTROL_HEIGHT)
        add_exercise.setStyleSheet(button_cta_green_qss())
        apply_lucide_button_icon(add_exercise, "plus")
    add_type = getattr(host, "pushButton_type_add", None)
    if add_type is not None:
        add_type.setText("Add type")
        add_type.setMinimumHeight(CONTROL_HEIGHT)
        add_type.setStyleSheet(button_idle_qss())
        apply_lucide_button_icon(add_type, "plus")

    for table_name in ("tableView_exercises", "tableView_exercise_types"):
        table = getattr(host, table_name, None)
        if isinstance(table, QTableView):
            _compact_table(table)


def _polish_statistics(host: Any) -> None:
    if hasattr(host, "groupBox_10"):
        host.groupBox_10.setTitle("Records")

    for name, text, icon in (
        ("pushButton_statistics_refresh", "Refresh", "trophy"),
        ("pushButton_last_exercises", "Last exercises", "calendar"),
        ("pushButton_check_steps", "Check steps", "footprints"),
        ("pushButton_exercise_goal_recommendations", "Goal tips", "target"),
    ):
        _idle_button(host, name, text, icon)

    for control_name in ("comboBox_records_select_exercise", "spinBox_record_count"):
        control = getattr(host, control_name, None)
        if control is not None:
            control.setMinimumHeight(CONTROL_HEIGHT)
    if hasattr(host, "tableView_statistics"):
        _compact_table(host.tableView_statistics)


def _polish_weight(host: Any) -> None:
    if hasattr(host, "groupBox_4"):
        host.groupBox_4.setTitle("Add weight")
    if hasattr(host, "groupBox_6"):
        host.groupBox_6.setTitle("Commands")
        quiet_group_box(host.groupBox_6)

    add = getattr(host, "pushButton_weight_add", None)
    if add is not None:
        add.setText("Add weight")
        add.setMinimumHeight(CONTROL_HEIGHT)
        add.setStyleSheet(button_cta_green_qss())
        apply_lucide_button_icon(add, "plus")

    for name, text, icon in (
        ("pushButton_weight_delete", "Delete", "trash-2"),
        ("pushButton_weight_refresh", "Refresh", "refresh-cw"),
        ("pushButton_update_weight_chart", "Update chart", "refresh-cw"),
        ("pushButton_weight_last_month", "Last month", "calendar"),
        ("pushButton_weight_last_year", "Last year", "calendar-range"),
        ("pushButton_weight_all_time", "All time", "infinity"),
    ):
        _idle_button(host, name, text, icon)

    for name in ("label_weight_from", "label_weight_to"):
        label = getattr(host, name, None)
        if isinstance(label, QLabel):
            label.setStyleSheet(_caption_qss())
    polish_left_field_labels(
        host,
        (
            ("label_field_weight", "Weight:"),
            ("label_field_weight_date", "Date:"),
        ),
    )
    for control_name in (
        "doubleSpinBox_weight",
        "dateEdit_weight",
        "dateEdit_weight_from",
        "dateEdit_weight_to",
    ):
        control = getattr(host, control_name, None)
        if control is not None:
            control.setMinimumHeight(CONTROL_HEIGHT)
    if hasattr(host, "tableView_weight"):
        _compact_table(host.tableView_weight)
    if hasattr(host, "verticalLayout_9"):
        host.verticalLayout_9.setSpacing(SPACE_S)
        host.verticalLayout_9.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)


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
        timer.timeout.connect(lambda: persist_fitness_tabs_splitter_sizes(host))
        setattr(host, timer_attr, timer)
        splitter.splitterMoved.connect(on_moved)
        setattr(host, bound_attr, True)
