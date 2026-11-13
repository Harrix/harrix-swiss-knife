"""Fluent chrome for the Food Tracker entry columns (form + food items + log)."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QPoint, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QFont, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListView,
    QMenu,
    QSizePolicy,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.table_models import (
    bind_column_fill_on_resize,
    columns_fill_viewport,
    user_resized_columns,
)
from harrix_swiss_knife.apps.common.tracker_layout_chrome import polish_left_field_labels, quiet_group_box
from harrix_swiss_knife.apps.common.ui_chrome import (
    SELECTION_BG,
    SELECTION_TEXT,
    apply_soft_form_spin_fills,
    button_cta_cyan_qss,
    button_idle_qss,
    muted_caption_qss,
)
from harrix_swiss_knife.apps.food.food_log_calories import (
    FOOD_LOG_COL_CALORIES,
    FOOD_LOG_COL_DATE,
    FOOD_LOG_COL_NAME_EN,
    FOOD_LOG_COL_WEIGHT,
)
from harrix_swiss_knife.apps.food.food_ui_settings import (
    EXPECTED_FOOD_SPLITTER_LEN,
    FLAT_HIDDEN_COLUMNS,
    FOOD_LOG_COL_IS_DRINK,
    FOOD_LOG_COL_NAME,
    GROUPED_HIDDEN_COLUMNS,
    TOGGLEABLE_COLUMNS,
    load_column_visibility,
    load_food_splitter_sizes,
    save_column_visibility,
    save_food_splitter_sizes,
)
from harrix_swiss_knife.fluent.app_chrome import style_fluent_item_view
from harrix_swiss_knife.fluent.theme import bind_theme, css, mix, palette_for
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, SPACE_S, SPACE_XS
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon, install_line_edit_search_chrome

FOOD_LOG_ROW_HEIGHT = 30
_FORM_MIN_WIDTH = 280
_ITEMS_MIN_WIDTH = 240
_TABLE_MIN_WIDTH = 400
_SPLITTER_SAVE_DELAY_MS = 400
_FIELD_LABEL_WIDTH = 90
_FORM_VALUE_MIN_WIDTH = 160
_NO_ITEM = "Item: not selected"
_ITEM_HINT = "Choose a food item in the adjacent panel"
_ITEM_PREFIX = "Item: "
_FIXED_COLUMN_WIDTHS: dict[int, int] = {
    FOOD_LOG_COL_IS_DRINK: 72,
    FOOD_LOG_COL_WEIGHT: 88,
    FOOD_LOG_COL_CALORIES: 100,
    FOOD_LOG_COL_DATE: 100,
}
_FLEX_COLUMN_WEIGHTS: dict[int, int] = {
    FOOD_LOG_COL_NAME: 5,
    FOOD_LOG_COL_NAME_EN: 2,
}


def apply_food_log_column_visibility(host: Any) -> None:
    """Re-apply persisted column visibility after the food log model is ready."""
    table = host.tableView_food_log
    flags = load_column_visibility()
    for key, column, _label in TOGGLEABLE_COLUMNS:
        visible = flags.get(key, True)
        if column < 0:
            _set_record_id_visible(table, visible=visible, persist=False)
        else:
            _set_data_column_visible(table, column, visible=visible, persist=False, refill=False)
    _apply_day_header_column_policy(table)
    from harrix_swiss_knife.apps.food.food_day_headers import (  # noqa: PLC0415
        FoodDayHeaderProxy,
        apply_food_day_header_spans,
    )

    if isinstance(table.model(), FoodDayHeaderProxy):
        apply_food_day_header_spans(table)
    else:
        table.clearSpans()
    apply_food_log_table_column_widths(table, force=True)


def apply_food_log_table_column_widths(table_view: QTableView, *, force: bool = False) -> None:
    """Fill the viewport among visible food-log columns, then keep them Interactive."""
    bind_column_fill_on_resize(table_view, apply_food_log_table_column_widths)
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
    widths = _visible_food_log_column_widths(
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


def food_item_state_text(display_name: str | None) -> str:
    """Return the form item indicator text (with optional hint when empty)."""
    name = (display_name or "").strip()
    if not name:
        return f"{_NO_ITEM}\n{_ITEM_HINT}"
    lowered = name.casefold()
    if lowered.startswith(_ITEM_PREFIX.casefold()):
        return name
    if lowered in {_NO_ITEM.casefold(), "no item selected"}:
        return f"{_NO_ITEM}\n{_ITEM_HINT}"
    return f"{_ITEM_PREFIX}{name}"


def install_food_entry_chrome(host: Any) -> None:
    """Polish the Food form, items list, splitter, and log table chrome."""
    _ensure_item_state_label(host)
    _ensure_catalog_search(host)
    _ensure_food_log_empty_label(host)
    _polish_form_column(host)
    _polish_items_list(host)
    _polish_item_state_label(host)
    _polish_food_log_table(host)
    _configure_food_splitter(host)
    if not getattr(host, "_food_entry_theme_bound", False):

        def _refresh_theme() -> None:
            _polish_form_column(host)
            _polish_items_list(host)
            _polish_item_state_label(host)

        bind_theme(host, _refresh_theme)
        host._food_entry_theme_bound = True  # noqa: SLF001


def persist_food_splitter_sizes(host: Any) -> None:
    """Save current Food-tab splitter sizes."""
    if getattr(host, "_is_closing", False) or not hasattr(host, "splitter_food"):
        return
    sizes = host.splitter_food.sizes()
    if len(sizes) == EXPECTED_FOOD_SPLITTER_LEN and all(size > 0 for size in sizes):
        save_food_splitter_sizes([int(size) for size in sizes])


def refresh_food_item_state_label(host: Any, display_name: str | None = None) -> None:
    """Update the form item indicator with a Fluent status string."""
    label = getattr(host, "label_food_item_now", None)
    if not isinstance(label, QLabel):
        return
    text = food_item_state_text(display_name)
    selected = bool((display_name or "").strip()) and not text.startswith(_NO_ITEM)
    label.setText(text)
    label.setWordWrap(True)
    label.setToolTip(_ITEM_HINT if not selected else text.split("\n", 1)[0])
    label.setProperty("hskFoodItemSelected", selected)
    label.style().unpolish(label)
    label.style().polish(label)


def set_food_log_empty_visible(host: Any, *, visible: bool) -> None:
    """Show or hide the food-log empty state."""
    label = getattr(host, "label_food_log_empty", None)
    if isinstance(label, QLabel):
        label.setVisible(visible)
    table = getattr(host, "tableView_food_log", None)
    if table is not None:
        table.setVisible(not visible)


def _apply_day_header_column_policy(table: QTableView) -> None:
    """Hide Date/Total while grouped; flat mode hides Total only and shows Date."""
    model = table.model()
    if model is None:
        return
    from harrix_swiss_knife.apps.food.food_day_headers import FoodDayHeaderProxy  # noqa: PLC0415

    grouped = isinstance(model, FoodDayHeaderProxy)
    hide_columns = GROUPED_HIDDEN_COLUMNS if grouped else FLAT_HIDDEN_COLUMNS
    for column in range(model.columnCount()):
        if column in hide_columns:
            table.setColumnHidden(column, True)  # noqa: FBT003
        elif column == FOOD_LOG_COL_DATE and not grouped:
            table.setColumnHidden(column, False)  # noqa: FBT003


def _configure_food_splitter(host: Any) -> None:
    host.frame_food_controls.setMinimumWidth(_FORM_MIN_WIDTH)
    host.widget_food_middle.setMinimumWidth(_ITEMS_MIN_WIDTH)
    host.widget_food_log.setMinimumWidth(_TABLE_MIN_WIDTH)
    host.splitter_food.setChildrenCollapsible(False)
    host.splitter_food.setStretchFactor(0, 0)
    host.splitter_food.setStretchFactor(1, 0)
    host.splitter_food.setStretchFactor(2, 1)

    saved = load_food_splitter_sizes()
    host._food_splitter_user_moved = False  # noqa: SLF001

    def apply_sizes() -> None:
        if getattr(host, "_is_closing", False) or getattr(host, "_food_splitter_user_moved", False):
            return
        total = host.splitter_food.width()
        if total <= 0:
            total = max(host.width(), sum(saved))
        sizes = list(saved)
        if sum(sizes) != total and total > 0:
            scale = total / max(sum(sizes), 1)
            sizes = [max(1, round(size * scale)) for size in sizes]
            sizes[2] = max(1, total - sizes[0] - sizes[1])
        sizes[0] = min(sizes[0], max(_FORM_MIN_WIDTH, total // 4))
        sizes[1] = max(sizes[1], _ITEMS_MIN_WIDTH)
        sizes[2] = max(1, total - sizes[0] - sizes[1])
        host.splitter_food.setSizes(sizes)

    def on_splitter_moved(*_args: object) -> None:
        host._food_splitter_user_moved = True  # noqa: SLF001
        host._food_splitter_save_timer.start()  # noqa: SLF001

    host._apply_food_splitter_sizes = apply_sizes  # noqa: SLF001
    apply_sizes()
    QTimer.singleShot(60, apply_sizes)

    if not getattr(host, "_food_splitter_save_bound", False):
        host._food_splitter_save_timer = QTimer(host)  # noqa: SLF001
        host._food_splitter_save_timer.setSingleShot(True)  # noqa: SLF001
        host._food_splitter_save_timer.setInterval(_SPLITTER_SAVE_DELAY_MS)  # noqa: SLF001
        host._food_splitter_save_timer.timeout.connect(  # noqa: SLF001
            lambda: persist_food_splitter_sizes(host),
        )
        host.splitter_food.splitterMoved.connect(on_splitter_moved)
        host._food_splitter_save_bound = True  # noqa: SLF001


def _ensure_catalog_search(host: Any) -> None:
    if isinstance(getattr(host, "lineEdit_food_items_search", None), QLineEdit):
        return
    mid = getattr(host, "widget_food_middle", None)
    if mid is None:
        return
    edit = QLineEdit(mid)
    edit.setObjectName("lineEdit_food_items_search")
    edit.setPlaceholderText("Search catalog…")
    edit.setClearButtonEnabled(False)
    install_line_edit_search_chrome(edit, clear_tooltip="Clear catalog search")
    host.lineEdit_food_items_search = edit
    layout = getattr(host, "verticalLayout_food_middle", None)
    if not isinstance(layout, QVBoxLayout):
        layout = mid.layout()
    if isinstance(layout, QVBoxLayout):
        list_index = layout.indexOf(host.label_food_items)
        if list_index < 0:
            layout.insertWidget(0, edit)
        else:
            layout.insertWidget(list_index + 1, edit)


def _ensure_food_log_empty_label(host: Any) -> None:
    if isinstance(getattr(host, "label_food_log_empty", None), QLabel):
        return
    log_host = getattr(host, "widget_food_log", None)
    if log_host is None:
        return
    label = QLabel(log_host)
    label.setObjectName("label_food_log_empty")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setWordWrap(True)
    label.setText("Nothing found")
    label.hide()
    host.label_food_log_empty = label
    layout = getattr(host, "verticalLayout_food_log", None)
    if isinstance(layout, QVBoxLayout):
        table_index = layout.indexOf(host.tableView_food_log)
        if table_index < 0:
            layout.addWidget(label)
        else:
            layout.insertWidget(table_index + 1, label)


def _ensure_item_state_label(host: Any) -> None:
    if isinstance(getattr(host, "label_food_item_now", None), QLabel):
        return
    label = QLabel(host.groupBox_food_add)
    label.setObjectName("label_food_item_now")
    host.label_food_item_now = label
    layout = host.verticalLayout
    layout.insertWidget(0, label)


def _expand_food_form_value_fields(host: Any) -> None:
    """Let Weight, kcal/100g, and Date use the leftover row width."""
    for layout_name, control_name in (
        ("horizontalLayout_food_weight", "spinBox_food_weight"),
        ("horizontalLayout_food_kcal", "doubleSpinBox_food_calories"),
        ("horizontalLayout_food_date", "dateEdit_food"),
    ):
        control = getattr(host, control_name, None)
        layout = getattr(host, layout_name, None)
        if control is None:
            continue
        control.setMinimumWidth(_FORM_VALUE_MIN_WIDTH)
        control.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        if isinstance(layout, QHBoxLayout):
            _remove_trailing_stretches(layout)
            index = layout.indexOf(control)
            if index >= 0:
                layout.setStretch(index, 1)


def _field_label_spacer(parent: QWidget) -> QWidget:
    spacer = QWidget(parent)
    spacer.setFixedWidth(_FIELD_LABEL_WIDTH)
    return spacer


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

    if not getattr(host, "_food_log_column_menu_bound", False):
        header.customContextMenuRequested.connect(show_menu)
        host._food_log_column_menu_bound = True  # noqa: SLF001

    apply_food_log_column_visibility(host)


def _polish_food_log_table(host: Any) -> None:
    table: QTableView = host.tableView_food_log
    vertical = table.verticalHeader()
    vertical.setDefaultSectionSize(FOOD_LOG_ROW_HEIGHT)
    vertical.setMinimumSectionSize(24)
    header = table.horizontalHeader()
    if isinstance(header, QHeaderView):
        header.setStretchLastSection(False)
        header.setSectionsMovable(False)
    table.setWordWrap(False)
    table.setTextElideMode(Qt.TextElideMode.ElideRight)
    # Row selection keeps day-band fills coherent; avoid a lone “gray Name cell”.
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    _install_column_visibility_menu(host, table)

    empty = getattr(host, "label_food_log_empty", None)
    if isinstance(empty, QLabel):
        empty.setStyleSheet(f"{muted_caption_qss(bold=False)} padding: {SPACE_S}px;")


def _polish_form_column(host: Any) -> None:
    _restructure_food_form(host)

    host.groupBox_food_add.setTitle("New food entry")
    host.groupBox_food_commands.setTitle("")
    host.groupBox_food_commands.setFlat(True)
    host.groupBox_food_today.setTitle("Today")
    host.groupBox_food_yesterday.setTitle("Yesterday")
    quiet_group_box(host.groupBox_food_add)
    quiet_group_box(host.groupBox_food_commands, untitled=True)
    quiet_group_box(host.groupBox_food_today)
    quiet_group_box(host.groupBox_food_yesterday)

    form_layout = host.verticalLayout_food_controls
    form_layout.setSpacing(SPACE_S)
    form_layout.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)
    host.verticalLayout.setSpacing(SPACE_XS)
    host.verticalLayout_2.setContentsMargins(0, SPACE_XS, 0, 0)
    host.verticalLayout_2.setSpacing(SPACE_XS)

    for name in ("label_food_weight_unit", "label_food_calories"):
        label = getattr(host, name, None)
        if isinstance(label, QLabel):
            label.setStyleSheet(muted_caption_qss())

    polish_left_field_labels(
        host,
        (
            ("label_field_food_name", "Description:"),
            ("label_field_food_weight", "Weight:"),
            ("label_field_food_calories", "Calories:"),
            ("label_field_food_date", "Date:"),
        ),
    )

    host.lineEdit_food_manual_name.setPlaceholderText("What did you eat?")
    host.lineEdit_food_manual_name.setToolTip("Food or drink name")

    for control_name in (
        "lineEdit_food_manual_name",
        "spinBox_food_weight",
        "doubleSpinBox_food_calories",
        "dateEdit_food",
        "pushButton_food_add",
        "pushButton_food_add_with_ai",
        "pushButton_food_add_by_voice",
        "pushButton_food_analyze_macros",
        "pushButton_kcal_with_ai",
        "pushButton_portion_calories",
    ):
        control = getattr(host, control_name, None)
        if control is not None:
            control.setMinimumHeight(CONTROL_HEIGHT)

    host.pushButton_food_add.setText("Add food")
    host.pushButton_food_add.setStyleSheet(button_cta_cyan_qss())
    apply_lucide_button_icon(host.pushButton_food_add, "plus")

    host.pushButton_food_add_with_ai.setText("Add with AI")
    host.pushButton_food_add_with_ai.setStyleSheet(button_idle_qss())
    apply_lucide_button_icon(host.pushButton_food_add_with_ai, "sparkles")

    host.pushButton_food_add_by_voice.setText("Add by voice")
    host.pushButton_food_add_by_voice.setStyleSheet(button_idle_qss())
    apply_lucide_button_icon(host.pushButton_food_add_by_voice, "mic")

    host.pushButton_food_analyze_macros.setText("Analyze macros")
    host.pushButton_food_analyze_macros.setStyleSheet(button_idle_qss())
    apply_lucide_button_icon(host.pushButton_food_analyze_macros, "chart-pie")

    for label_name in ("label_food_today", "label_food_yesterday"):
        label = getattr(host, label_name, None)
        if isinstance(label, QLabel):
            font = QFont(label.font())
            if font.pointSize() > 0:
                font.setPointSize(max(10, min(font.pointSize(), 12)))
            elif font.pixelSize() > 0:
                font.setPixelSize(max(13, min(font.pixelSize(), 16)))
            font.setBold(True)
            label.setFont(font)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    apply_soft_form_spin_fills(host, ("spinBox_food_weight", "doubleSpinBox_food_calories"))
    _expand_food_form_value_fields(host)
    refresh_food_item_state_label(host, host.lineEdit_food_manual_name.text() or None)


def _polish_item_state_label(host: Any) -> None:
    label = getattr(host, "label_food_item_now", None)
    if not isinstance(label, QLabel):
        return
    palette = palette_for(host)
    text = css(mix(palette.window_bg, palette.text_primary))
    muted = css(mix(palette.window_bg, palette.text_secondary))
    label.setStyleSheet(
        f"""
        QLabel#label_food_item_now {{
            color: {muted};
            font-weight: 600;
            padding: 2px 0px {SPACE_XS}px 0px;
            border: none;
            background: transparent;
        }}
        QLabel#label_food_item_now[hskFoodItemSelected="true"] {{
            color: {text};
        }}
        """,
    )


def _polish_items_list(host: Any) -> None:
    view: QListView = host.listView_food_items
    view.setUniformItemSizes(True)
    view.setSpacing(0)
    view.setIconSize(QSize(0, 0))
    view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    view.setTextElideMode(Qt.TextElideMode.ElideRight)
    view.setSelectionRectVisible(False)
    view.setMouseTracking(True)
    view.setWordWrap(False)
    style_fluent_item_view(view)
    tuned = view.palette()
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive, QPalette.ColorGroup.Disabled):
        tuned.setColor(group, QPalette.ColorRole.Highlight, QColor(SELECTION_BG))
        tuned.setColor(group, QPalette.ColorRole.HighlightedText, QColor(SELECTION_TEXT))
    view.setPalette(tuned)
    host.label_food_items.setText("Food item")
    host.label_food_items.setStyleSheet(f"{muted_caption_qss()} border: none; background: transparent;")
    font = QFont(host.label_food_items.font())
    font.setBold(True)
    host.label_food_items.setFont(font)
    host.label_food_items.setToolTip("Select a catalog item for the new food log entry")

    search = getattr(host, "lineEdit_food_items_search", None)
    if search is not None:
        search.setMinimumHeight(CONTROL_HEIGHT)


def _restructure_food_form(host: Any) -> None:
    """Split the generated food form into one control row per field; Add food spans the column."""
    if getattr(host, "_food_form_restructured", False):
        return
    host._food_form_restructured = True  # noqa: SLF001

    gb = host.groupBox_food_add
    vlayout: QVBoxLayout = host.verticalLayout
    weight_row: QHBoxLayout = host.horizontalLayout_food_weight
    date_row: QHBoxLayout = host.horizontalLayout_food_date

    while weight_row.count():
        item = weight_row.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)

    date_row.removeWidget(host.pushButton_food_add)
    host.pushButton_food_add.setParent(gb)

    host.spinBox_food_weight.setMinimumWidth(_FORM_VALUE_MIN_WIDTH)
    host.spinBox_food_weight.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    weight_row.addWidget(host.label_field_food_weight)
    weight_row.addWidget(host.spinBox_food_weight, 1)
    weight_row.addWidget(host.label_food_weight_unit)

    host.doubleSpinBox_food_calories.setMinimumWidth(_FORM_VALUE_MIN_WIDTH)
    host.doubleSpinBox_food_calories.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    calories_label = QLabel("Calories:", gb)
    calories_label.setObjectName("label_field_food_calories")
    host.label_field_food_calories = calories_label
    kcal_row = QHBoxLayout()
    kcal_row.setObjectName("horizontalLayout_food_kcal")
    host.horizontalLayout_food_kcal = kcal_row
    kcal_row.addWidget(calories_label)
    kcal_row.addWidget(host.doubleSpinBox_food_calories, 1)
    kcal_row.addWidget(host.label_food_calories)
    kcal_row.addWidget(host.pushButton_portion_calories)

    drink_row = QHBoxLayout()
    drink_row.setObjectName("horizontalLayout_food_drink")
    host.horizontalLayout_food_drink = drink_row
    drink_row.addWidget(_field_label_spacer(gb))
    drink_row.addWidget(host.checkBox_food_is_drink)
    drink_row.addStretch(1)

    while date_row.count():
        item = date_row.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
    host.dateEdit_food.setMinimumWidth(_FORM_VALUE_MIN_WIDTH)
    host.dateEdit_food.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    date_row.addWidget(host.label_field_food_date)
    date_row.addWidget(host.dateEdit_food, 1)

    add_row = QHBoxLayout()
    add_row.setObjectName("horizontalLayout_food_add")
    host.horizontalLayout_food_add = add_row
    host.pushButton_food_add.setSizePolicy(
        QSizePolicy.Policy.Expanding,
        QSizePolicy.Policy.Fixed,
    )
    add_row.addWidget(host.pushButton_food_add)

    weight_index = vlayout.indexOf(weight_row)
    if weight_index >= 0:
        vlayout.insertLayout(weight_index + 1, kcal_row)
        vlayout.insertLayout(weight_index + 2, drink_row)
    else:
        vlayout.addLayout(kcal_row)
        vlayout.addLayout(drink_row)

    date_index = vlayout.indexOf(date_row)
    if date_index >= 0:
        vlayout.insertLayout(date_index + 1, add_row)
    else:
        vlayout.addLayout(add_row)


def _remove_trailing_stretches(layout: QHBoxLayout) -> None:
    """Drop end-of-row stretches so Expanding value fields can fill the row."""
    while layout.count() > 0:
        item = layout.itemAt(layout.count() - 1)
        if item is None or item.spacerItem() is None:
            break
        taken = layout.takeAt(layout.count() - 1)
        del taken


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
        apply_food_log_table_column_widths(table, force=True)


def _set_record_id_visible(table: QTableView, *, visible: bool, persist: bool = True) -> None:
    table.verticalHeader().setVisible(visible)
    if persist:
        flags = load_column_visibility()
        flags["record_id"] = visible
        save_column_visibility(flags)


def _visible_food_log_column_widths(
    viewport_w: int,
    count: int,
    *,
    visible: list[int],
    min_size: int,
) -> list[int]:
    """Split `viewport_w` with Name weighted larger than English Name."""
    widths = [0] * count
    if not visible:
        return widths

    fixed = [col for col in visible if col in _FIXED_COLUMN_WIDTHS]
    flexible = [col for col in visible if col not in _FIXED_COLUMN_WIDTHS]
    fixed_total = sum(_FIXED_COLUMN_WIDTHS[col] for col in fixed)
    flex_min = len(flexible) * min_size

    if fixed_total + flex_min > viewport_w and fixed:
        scale = max(viewport_w - flex_min, 0) / max(fixed_total, 1)
        for col in fixed:
            widths[col] = max(int(_FIXED_COLUMN_WIDTHS[col] * scale), min_size // 2)
        fixed_total = sum(widths[col] for col in fixed)
    else:
        for col in fixed:
            widths[col] = _FIXED_COLUMN_WIDTHS[col]

    flex_budget = max(viewport_w - fixed_total, flex_min if flexible else 0)
    if not flexible:
        if fixed:
            widths[fixed[-1]] = max(widths[fixed[-1]] + (viewport_w - sum(widths[c] for c in fixed)), min_size)
        return widths

    weight_sum = sum(_FLEX_COLUMN_WEIGHTS.get(col, 1) for col in flexible)
    assigned = 0
    for col in flexible[:-1]:
        share = max(flex_budget * _FLEX_COLUMN_WEIGHTS.get(col, 1) // weight_sum, min_size)
        widths[col] = share
        assigned += share
    widths[flexible[-1]] = max(flex_budget - assigned, min_size)

    used = sum(widths[col] for col in visible)
    drift = viewport_w - used
    if drift != 0:
        sink = FOOD_LOG_COL_NAME if FOOD_LOG_COL_NAME in visible else flexible[-1]
        widths[sink] = max(widths[sink] + drift, min_size)
    return widths
