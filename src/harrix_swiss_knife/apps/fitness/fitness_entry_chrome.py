"""Fluent chrome for the Fitness Sets entry columns (form + exercises + process)."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QListView,
    QTableView,
    QVBoxLayout,
)

from harrix_swiss_knife.apps.common.tracker_layout_chrome import polish_left_field_labels, quiet_group_box
from harrix_swiss_knife.apps.common.ui_chrome import MUTED_TEXT, button_cta_green_qss, button_idle_qss
from harrix_swiss_knife.apps.fitness.fitness_ui_settings import (
    EXPECTED_SETS_SPLITTER_LEN,
    load_sets_splitter_sizes,
    save_sets_splitter_sizes,
)
from harrix_swiss_knife.fluent.theme import bind_theme, css, mix, palette_for
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, ICON_SIZE, SPACE_S, SPACE_XS
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon

PROCESS_ROW_HEIGHT = 30
_FORM_MIN_WIDTH = 280
_EXERCISES_MIN_WIDTH = 280
_TABLE_MIN_WIDTH = 400
_SPLITTER_SAVE_DELAY_MS = 400
_NO_EXERCISE = "Exercise: not selected"
_EXERCISE_HINT = "Choose an exercise in the adjacent panel"
_EXERCISE_PREFIX = "Exercise: "


def exercise_state_text(display_name: str | None) -> str:
    """Return the form exercise indicator text (with optional hint when empty)."""
    name = (display_name or "").strip()
    if not name:
        return f"{_NO_EXERCISE}\n{_EXERCISE_HINT}"
    lowered = name.casefold()
    if lowered.startswith(_EXERCISE_PREFIX.casefold()):
        return name
    if lowered in {_NO_EXERCISE.casefold(), "no exercise selected"}:
        return f"{_NO_EXERCISE}\n{_EXERCISE_HINT}"
    return f"{_EXERCISE_PREFIX}{name}"


def install_fitness_entry_chrome(host: Any) -> None:
    """Polish the Sets form, exercise list, splitter, and process table chrome."""
    _ensure_exercise_list_header(host)
    _polish_form_column(host)
    _polish_exercise_list(host)
    _polish_exercise_state_label(host)
    _polish_process_table(host)
    _configure_sets_splitter(host)
    if not getattr(host, "_fitness_entry_theme_bound", False):

        def _refresh_theme() -> None:
            _polish_form_column(host)
            _polish_exercise_list(host)
            _polish_exercise_state_label(host)

        bind_theme(host, _refresh_theme)
        host._fitness_entry_theme_bound = True  # noqa: SLF001


def persist_sets_splitter_sizes(host: Any) -> None:
    """Save current Sets-tab splitter sizes."""
    if getattr(host, "_is_closing", False) or not hasattr(host, "splitter"):
        return
    sizes = host.splitter.sizes()
    if len(sizes) == EXPECTED_SETS_SPLITTER_LEN and all(size > 0 for size in sizes):
        save_sets_splitter_sizes([int(size) for size in sizes])


def refresh_exercise_state_label(host: Any, display_name: str | None = None) -> None:
    """Update `label_exercise` with a Fluent status string."""
    text = exercise_state_text(display_name)
    selected = bool((display_name or "").strip()) and not text.startswith(_NO_EXERCISE)
    host.label_exercise.setText(text)
    host.label_exercise.setWordWrap(True)
    host.label_exercise.setToolTip(_EXERCISE_HINT if not selected else text.split("\n", 1)[0])
    host.label_exercise.setProperty("hskExerciseSelected", selected)
    host.label_exercise.style().unpolish(host.label_exercise)
    host.label_exercise.style().polish(host.label_exercise)


def _configure_sets_splitter(host: Any) -> None:
    host.frame.setMinimumWidth(_FORM_MIN_WIDTH)
    host.widget_middle.setMinimumWidth(_EXERCISES_MIN_WIDTH)
    host.widget_process.setMinimumWidth(_TABLE_MIN_WIDTH)
    host.splitter.setChildrenCollapsible(False)
    host.splitter.setStretchFactor(0, 0)
    host.splitter.setStretchFactor(1, 0)
    host.splitter.setStretchFactor(2, 1)

    saved = load_sets_splitter_sizes()
    host._sets_splitter_user_moved = False  # noqa: SLF001

    def apply_sizes() -> None:
        if getattr(host, "_is_closing", False) or getattr(host, "_sets_splitter_user_moved", False):
            return
        total = host.splitter.width()
        if total <= 0:
            total = max(host.width(), sum(saved))
        sizes = list(saved)
        if sum(sizes) != total and total > 0:
            scale = total / max(sum(sizes), 1)
            sizes = [max(1, round(size * scale)) for size in sizes]
            sizes[2] = max(1, total - sizes[0] - sizes[1])
        sizes[0] = min(sizes[0], max(_FORM_MIN_WIDTH, total // 4))
        sizes[1] = max(sizes[1], _EXERCISES_MIN_WIDTH)
        sizes[2] = max(1, total - sizes[0] - sizes[1])
        host.splitter.setSizes(sizes)

    def on_splitter_moved(*_args: object) -> None:
        host._sets_splitter_user_moved = True  # noqa: SLF001
        host._sets_splitter_save_timer.start()  # noqa: SLF001

    host._apply_sets_splitter_sizes = apply_sizes  # noqa: SLF001
    apply_sizes()
    QTimer.singleShot(60, apply_sizes)

    if not getattr(host, "_sets_splitter_save_bound", False):
        host._sets_splitter_save_timer = QTimer(host)  # noqa: SLF001
        host._sets_splitter_save_timer.setSingleShot(True)  # noqa: SLF001
        host._sets_splitter_save_timer.setInterval(_SPLITTER_SAVE_DELAY_MS)  # noqa: SLF001
        host._sets_splitter_save_timer.timeout.connect(  # noqa: SLF001
            lambda: persist_sets_splitter_sizes(host),
        )
        host.splitter.splitterMoved.connect(on_splitter_moved)
        host._sets_splitter_save_bound = True  # noqa: SLF001


def _ensure_exercise_list_header(host: Any) -> None:
    if isinstance(getattr(host, "label_exercises_list", None), QLabel):
        return
    label = QLabel(host.widget_middle)
    label.setObjectName("label_exercises_list")
    host.label_exercises_list = label
    layout = host.verticalLayout
    if isinstance(layout, QVBoxLayout):
        # Keep select + filter above the list; insert caption before the list.
        list_index = layout.indexOf(host.listView_exercises)
        if list_index < 0:
            layout.insertWidget(0, label)
        else:
            layout.insertWidget(list_index, label)


def _field_caption_qss() -> str:
    return f"color: {MUTED_TEXT}; font-weight: 600;"


def _polish_exercise_list(host: Any) -> None:
    view: QListView = host.listView_exercises
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
    label = getattr(host, "label_exercises_list", None)
    if isinstance(label, QLabel):
        label.setText("Exercise")
        label.setStyleSheet(f"{_field_caption_qss()} border: none; background: transparent;")
        font = QFont(label.font())
        font.setBold(True)
        label.setFont(font)
        label.setToolTip("Select the exercise for the new set")


def _polish_exercise_state_label(host: Any) -> None:
    palette = palette_for(host)
    text = css(mix(palette.window_bg, palette.text_primary))
    muted = css(mix(palette.window_bg, palette.text_secondary))
    host.label_exercise.setObjectName("label_exercise")
    host.label_exercise.setStyleSheet(
        f"""
        QLabel#label_exercise {{
            color: {muted};
            font-weight: 600;
            padding: 2px 0px {SPACE_XS}px 0px;
            border: none;
            background: transparent;
        }}
        QLabel#label_exercise[hskExerciseSelected="true"] {{
            color: {text};
        }}
        """,
    )


def _polish_form_column(host: Any) -> None:
    host.groupBox.setTitle("New set")
    quiet_group_box(host.groupBox)
    if hasattr(host, "groupBox_9"):
        quiet_group_box(host.groupBox_9)

    form_layout = host.verticalLayout_3
    form_layout.setSpacing(SPACE_S)
    form_layout.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)
    host.verticalLayout_5.setSpacing(SPACE_XS)

    for name in ("label_unit", "label_last_date_count_today"):
        label = getattr(host, name, None)
        if isinstance(label, QLabel):
            label.setStyleSheet(_field_caption_qss())

    polish_left_field_labels(
        host,
        (
            ("label_field_count", "Count:"),
            ("label_field_type", "Type:"),
            ("label_field_date", "Date:"),
        ),
    )

    for control_name in (
        "spinBox_count",
        "comboBox_type",
        "dateEdit",
        "pushButton_add",
        "pushButton_add_by_voice",
        "pushButton_select_exercise",
        "lineEdit_exercises_filter",
    ):
        control = getattr(host, control_name, None)
        if control is not None:
            control.setMinimumHeight(CONTROL_HEIGHT)

    host.pushButton_add.setText("Add set")
    host.pushButton_add.setStyleSheet(button_cta_green_qss())
    apply_lucide_button_icon(host.pushButton_add, "plus")

    host.pushButton_add_by_voice.setText("Add by voice")
    host.pushButton_add_by_voice.setStyleSheet(button_idle_qss())
    apply_lucide_button_icon(host.pushButton_add_by_voice, "mic")

    host.pushButton_select_exercise.setText("Select exercise")
    host.pushButton_select_exercise.setStyleSheet(button_idle_qss())
    apply_lucide_button_icon(host.pushButton_select_exercise, "dumbbell")

    current = host.label_exercise.text().strip()
    if current and current.casefold() not in {"no exercise selected", "database error"}:
        refresh_exercise_state_label(host, current)
    else:
        refresh_exercise_state_label(host, None)


def _polish_process_table(host: Any) -> None:
    table: QTableView = host.tableView_process
    vertical = table.verticalHeader()
    vertical.setDefaultSectionSize(PROCESS_ROW_HEIGHT)
    vertical.setMinimumSectionSize(24)
    table.setWordWrap(False)
    table.setTextElideMode(Qt.TextElideMode.ElideRight)
