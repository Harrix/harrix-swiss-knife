"""Fluent chrome for the Food Tracker entry columns (form + food items + log)."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QListView,
    QSizePolicy,
    QTableView,
)

from harrix_swiss_knife.apps.common.tracker_layout_chrome import polish_left_field_labels, quiet_group_box
from harrix_swiss_knife.apps.common.ui_chrome import MUTED_TEXT, button_idle_qss
from harrix_swiss_knife.apps.food.food_ui_settings import (
    EXPECTED_FOOD_SPLITTER_LEN,
    load_food_splitter_sizes,
    save_food_splitter_sizes,
)
from harrix_swiss_knife.fluent.app_chrome import style_fluent_item_view
from harrix_swiss_knife.fluent.theme import bind_theme, css, mix, palette_for
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, ICON_SIZE, SPACE_S, SPACE_XS
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon

FOOD_LOG_ROW_HEIGHT = 30
_FORM_MIN_WIDTH = 280
_ITEMS_MIN_WIDTH = 240
_TABLE_MIN_WIDTH = 400
_SPLITTER_SAVE_DELAY_MS = 400
_NO_ITEM = "Item: not selected"
_ITEM_HINT = "Choose a food item in the adjacent panel"
_ITEM_PREFIX = "Item: "


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


def _ensure_item_state_label(host: Any) -> None:
    if isinstance(getattr(host, "label_food_item_now", None), QLabel):
        return
    label = QLabel(host.groupBox_food_add)
    label.setObjectName("label_food_item_now")
    host.label_food_item_now = label
    layout = host.verticalLayout
    layout.insertWidget(0, label)


def _field_caption_qss() -> str:
    return f"color: {MUTED_TEXT}; font-weight: 600;"


def _polish_food_log_table(host: Any) -> None:
    table: QTableView = host.tableView_food_log
    vertical = table.verticalHeader()
    vertical.setDefaultSectionSize(FOOD_LOG_ROW_HEIGHT)
    vertical.setMinimumSectionSize(24)
    table.setWordWrap(False)
    table.setTextElideMode(Qt.TextElideMode.ElideRight)


def _polish_form_column(host: Any) -> None:
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
            label.setStyleSheet(_field_caption_qss())

    polish_left_field_labels(
        host,
        (
            ("label_field_food_name", "Description:"),
            ("label_field_food_weight", "Weight:"),
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
    ):
        control = getattr(host, control_name, None)
        if control is not None:
            control.setMinimumHeight(CONTROL_HEIGHT)

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
            font.setPointSize(max(10, font.pointSize() if font.pointSize() > 0 else 10))
            font.setBold(True)
            label.setFont(font)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

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
    view.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
    view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    view.setTextElideMode(Qt.TextElideMode.ElideRight)
    view.setSelectionRectVisible(False)
    view.setMouseTracking(True)
    view.setWordWrap(False)
    # Do not clear the sheet: empty QSS re-polishes onto a white system Base.
    style_fluent_item_view(view)
    host.label_food_items.setText("Food item")
    host.label_food_items.setStyleSheet(f"{_field_caption_qss()} border: none; background: transparent;")
    font = QFont(host.label_food_items.font())
    font.setBold(True)
    host.label_food_items.setFont(font)
    host.label_food_items.setToolTip("Select a catalog item for the new food log entry")
