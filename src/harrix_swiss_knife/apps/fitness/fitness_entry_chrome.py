"""Fluent chrome for the Fitness Sets entry columns (form + exercises + process)."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QPoint, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QListView,
    QMenu,
    QSizePolicy,
    QTableView,
    QVBoxLayout,
)

from harrix_swiss_knife.apps.common.table_models import (
    bind_column_fill_on_resize,
    columns_fill_viewport,
    user_resized_columns,
)
from harrix_swiss_knife.apps.common.tracker_layout_chrome import polish_left_field_labels, quiet_group_box
from harrix_swiss_knife.apps.common.ui_chrome import (
    apply_soft_form_spin_fills,
    button_cta_green_qss,
    button_idle_qss,
    media_preview_plate_qss,
    muted_caption_qss,
)
from harrix_swiss_knife.apps.fitness.fitness_ui_settings import (
    ALWAYS_HIDDEN_COLUMNS,
    EXPECTED_SETS_SPLITTER_LEN,
    GROUPED_HIDDEN_COLUMNS,
    PROCESS_COL_DATE,
    PROCESS_COL_EXERCISE,
    PROCESS_COL_QUANTITY,
    PROCESS_COL_TYPE,
    TOGGLEABLE_COLUMNS,
    load_column_visibility,
    load_sets_splitter_sizes,
    save_column_visibility,
    save_sets_splitter_sizes,
)
from harrix_swiss_knife.fluent.app_chrome import style_fluent_item_view
from harrix_swiss_knife.fluent.theme import bind_theme, css, mix, palette_for
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, SPACE_S, SPACE_XS
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon

PROCESS_ROW_HEIGHT = 30
EXERCISE_LIST_ICON_SIZE = 64
_FORM_MIN_WIDTH = 280
_EXERCISES_MIN_WIDTH = 280
_TABLE_MIN_WIDTH = 400
_SPLITTER_SAVE_DELAY_MS = 400
_NO_EXERCISE = "Exercise: not selected"
_EXERCISE_HINT = "Choose an exercise in the adjacent panel"
_EXERCISE_PREFIX = "Exercise: "
_FIXED_COLUMN_WIDTHS: dict[int, int] = {
    PROCESS_COL_TYPE: 110,
    PROCESS_COL_QUANTITY: 100,
    PROCESS_COL_DATE: 100,
}
_FLEX_COLUMN_WEIGHTS: dict[int, int] = {
    PROCESS_COL_EXERCISE: 5,
    PROCESS_COL_TYPE: 2,
}
GOAL_REMAINDER_TOOLTIP = (
    "Remaining toward today's daily goal in this exercise's units — not the number of sets"
)


def apply_process_column_visibility(host: Any) -> None:
    """Re-apply persisted column visibility after the process table model is ready."""
    table = host.tableView_process
    flags = load_column_visibility()
    for key, column, _label in TOGGLEABLE_COLUMNS:
        visible = flags.get(key, True)
        if column < 0:
            _set_record_id_visible(table, visible=visible, persist=False)
        else:
            _set_data_column_visible(table, column, visible=visible, persist=False, refill=False)
    _apply_day_header_column_policy(table)
    from harrix_swiss_knife.apps.fitness.process_day_headers import (  # noqa: PLC0415
        ProcessDayHeaderProxy,
        apply_process_day_header_spans,
    )

    if isinstance(table.model(), ProcessDayHeaderProxy):
        apply_process_day_header_spans(table)
    else:
        table.clearSpans()
    apply_process_table_column_widths(table, force=True)


def apply_process_table_column_widths(table_view: QTableView, *, force: bool = False) -> None:
    """Fill the viewport among visible process columns, then keep them Interactive."""
    bind_column_fill_on_resize(table_view, apply_process_table_column_widths)
    if not table_view.isVisible() or user_resized_columns(table_view):
        return
    header = table_view.horizontalHeader()
    count = header.count()
    if count <= 0 or table_view.property("hskColumnFillGuard"):
        return
    viewport_w = table_view.viewport().width()
    if viewport_w <= 0:
        return
    if not force and columns_fill_viewport(table_view):
        return

    visible = [i for i in range(count) if not table_view.isColumnHidden(i)]
    if not visible:
        return

    header.setStretchLastSection(False)
    header.setMinimumSectionSize(min(header.minimumSectionSize(), 24))
    min_size = header.minimumSectionSize()
    widths = _visible_process_column_widths(
        viewport_w,
        count,
        visible=visible,
        min_size=min_size,
    )

    table_view.setProperty("hskColumnFillGuard", 1)
    try:
        for column in range(count):
            header.setSectionResizeMode(column, header.ResizeMode.Interactive)
            table_view.setColumnWidth(column, widths[column] if column in set(visible) else 0)
    finally:
        table_view.setProperty("hskColumnFillGuard", 0)


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
    _ensure_process_empty_label(host)
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


def set_process_empty_visible(host: Any, *, visible: bool) -> None:
    """Show or hide the process-history empty state."""
    label = getattr(host, "label_process_empty", None)
    if isinstance(label, QLabel):
        label.setVisible(visible)  # noqa: FBT003
    table = getattr(host, "tableView_process", None)
    if table is not None:
        table.setVisible(not visible)  # noqa: FBT003


def _apply_day_header_column_policy(table: QTableView) -> None:
    model = table.model()
    if model is None:
        return
    from harrix_swiss_knife.apps.fitness.process_day_headers import ProcessDayHeaderProxy  # noqa: PLC0415

    grouped = isinstance(model, ProcessDayHeaderProxy)
    hide_columns = GROUPED_HIDDEN_COLUMNS if grouped else ALWAYS_HIDDEN_COLUMNS
    for column in range(model.columnCount()):
        if column in hide_columns:
            table.setColumnHidden(column, True)  # noqa: FBT003
        elif column == PROCESS_COL_DATE and not grouped:
            table.setColumnHidden(column, False)  # noqa: FBT003


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
        list_index = layout.indexOf(host.listView_exercises)
        if list_index < 0:
            layout.insertWidget(0, label)
        else:
            layout.insertWidget(list_index, label)


def _ensure_process_empty_label(host: Any) -> None:
    if isinstance(getattr(host, "label_process_empty", None), QLabel):
        return
    label = QLabel(host.widget_process)
    label.setObjectName("label_process_empty")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setWordWrap(True)
    label.setText("Nothing found")
    label.hide()
    host.label_process_empty = label
    layout = getattr(host, "verticalLayout_process", None)
    if isinstance(layout, QVBoxLayout):
        table_index = layout.indexOf(host.tableView_process)
        if table_index < 0:
            layout.addWidget(label)
        else:
            layout.insertWidget(table_index + 1, label)


def _install_column_visibility_menu(host: Any, table: QTableView) -> None:
    header = table.horizontalHeader()
    header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def show_menu(pos: QPoint) -> None:
        menu = QMenu(table)
        flags = load_column_visibility()
        for key, column, label in TOGGLEABLE_COLUMNS:
            action = QAction(label, menu)
            action.setCheckable(True)
            action.setChecked(flags.get(key, True))
            if column < 0:
                action.toggled.connect(lambda checked, table=table: _set_record_id_visible(table, visible=checked))
            else:
                action.toggled.connect(
                    lambda checked, table=table, column=column, key=key: _set_data_column_visible(
                        table,
                        column,
                        visible=checked,
                        key=key,
                    ),
                )
            menu.addAction(action)
        menu.exec(header.mapToGlobal(pos))

    if not getattr(host, "_process_column_menu_bound", False):
        header.customContextMenuRequested.connect(show_menu)
        host._process_column_menu_bound = True  # noqa: SLF001

    apply_process_column_visibility(host)


def _polish_exercise_list(host: Any) -> None:
    view: QListView = host.listView_exercises
    view.setUniformItemSizes(False)
    view.setSpacing(0)
    view.setIconSize(QSize(EXERCISE_LIST_ICON_SIZE, EXERCISE_LIST_ICON_SIZE))
    view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    view.setTextElideMode(Qt.TextElideMode.ElideRight)
    view.setSelectionRectVisible(False)
    view.setMouseTracking(True)
    view.setWordWrap(False)
    style_fluent_item_view(view)
    label = getattr(host, "label_exercises_list", None)
    if isinstance(label, QLabel):
        label.setText("Exercise")
        label.setStyleSheet(f"{muted_caption_qss()} border: none; background: transparent;")
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
        host.groupBox_9.setTitle("Sets today")
        quiet_group_box(host.groupBox_9)

    form_layout = host.verticalLayout_3
    form_layout.setSpacing(SPACE_S)
    form_layout.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)
    host.verticalLayout_5.setSpacing(SPACE_XS)

    for name in ("label_unit", "label_last_date_count_today"):
        label = getattr(host, name, None)
        if isinstance(label, QLabel):
            label.setStyleSheet(muted_caption_qss())

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

    apply_soft_form_spin_fills(
        host,
        ("spinBox_count", "spinBox_count_minutes", "spinBox_count_seconds"),
    )

    avif = getattr(host, "label_exercise_avif", None)
    if isinstance(avif, QLabel):
        avif.setStyleSheet(media_preview_plate_qss(selector="QLabel#label_exercise_avif"))

    count_label = getattr(host, "label_count_sets_today", None)
    if isinstance(count_label, QLabel):
        font = QFont(count_label.font())
        if font.pointSize() > 0:
            font.setPointSize(max(11, min(font.pointSize(), 13)))
        elif font.pixelSize() > 0:
            font.setPixelSize(max(14, min(font.pixelSize(), 18)))
        font.setBold(True)
        count_label.setFont(font)
        count_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        count_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    empty = getattr(host, "label_process_empty", None)
    if isinstance(empty, QLabel):
        empty.setStyleSheet(f"{muted_caption_qss(bold=False)} padding: {SPACE_S}px;")

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
    header = table.horizontalHeader()
    if isinstance(header, QHeaderView):
        header.setStretchLastSection(False)
        header.setSectionsMovable(False)
    table.setWordWrap(False)
    table.setTextElideMode(Qt.TextElideMode.ElideRight)
    _install_column_visibility_menu(host, table)


def _set_data_column_visible(
    table: QTableView,
    column: int,
    *,
    visible: bool,
    persist: bool = True,
    key: str | None = None,
    refill: bool = True,
) -> None:
    model = table.model()
    if model is not None and 0 <= column < model.columnCount():
        table.setColumnHidden(column, not visible)
    if persist and key is not None:
        flags = load_column_visibility()
        flags[key] = visible
        save_column_visibility(flags)
    _apply_day_header_column_policy(table)
    if refill:
        apply_process_table_column_widths(table, force=True)


def _set_record_id_visible(table: QTableView, *, visible: bool, persist: bool = True) -> None:
    table.verticalHeader().setVisible(visible)
    if persist:
        flags = load_column_visibility()
        flags["record_id"] = visible
        save_column_visibility(flags)


def _visible_process_column_widths(
    viewport_w: int,
    count: int,
    *,
    visible: list[int],
    min_size: int,
) -> list[int]:
    """Split `viewport_w` with Exercise weighted larger than other flex cols."""
    widths = [0] * count
    if not visible:
        return widths

    fixed_total = 0
    flex: list[int] = []
    for column in visible:
        fixed = _FIXED_COLUMN_WIDTHS.get(column)
        if fixed is not None and column != PROCESS_COL_EXERCISE:
            widths[column] = max(min_size, fixed)
            fixed_total += widths[column]
        else:
            flex.append(column)

    remaining = max(0, viewport_w - fixed_total)
    weight_sum = sum(_FLEX_COLUMN_WEIGHTS.get(column, 1) for column in flex) or 1
    allocated = 0
    for index, column in enumerate(flex):
        if index == len(flex) - 1:
            widths[column] = max(min_size, remaining - allocated)
        else:
            share = max(min_size, int(remaining * _FLEX_COLUMN_WEIGHTS.get(column, 1) / weight_sum))
            widths[column] = share
            allocated += share
    return widths
