"""Fluent chrome for the Finance Transactions entry columns (form + categories)."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QPoint, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QLabel,
    QListView,
    QMenu,
    QSizePolicy,
    QTableView,
)

from harrix_swiss_knife.apps.common.ui_chrome import MUTED_TEXT, button_cta_mint_qss, button_idle_qss
from harrix_swiss_knife.apps.finance.transactions_ui_settings import (
    EXPECTED_SPLITTER_LEN,
    OPTIONAL_COLUMN_ENGLISH,
    load_column_visibility,
    load_splitter_sizes,
    save_column_visibility,
    save_splitter_sizes,
)
from harrix_swiss_knife.fluent.theme import bind_theme, css, mix, palette_for
from harrix_swiss_knife.fluent.tokens import ICON_SIZE, SPACE_XS
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon

TRANSACTIONS_ROW_HEIGHT = 30
_FORM_MIN_WIDTH = 320
_CATEGORIES_MIN_WIDTH = 200
_TABLE_MIN_WIDTH = 360
_SPLITTER_SAVE_DELAY_MS = 400
_VIS_KEY_ENGLISH = "english"
_VIS_KEY_RECORD_ID = "record_id"
_NO_CATEGORY = "No category selected"


def apply_transactions_column_visibility(host: Any) -> None:
    """Re-apply persisted English/ID visibility after the table model is ready."""
    table = host.tableView_transactions
    flags = load_column_visibility()
    _set_english_visible(table, visible=flags.get(_VIS_KEY_ENGLISH, True), persist=False)
    _set_record_id_visible(table, visible=flags.get(_VIS_KEY_RECORD_ID, True), persist=False)


def category_state_text(display_name: str | None) -> str:
    """Return the form category indicator text."""
    name = (display_name or "").strip()
    if not name:
        return _NO_CATEGORY
    lowered = name.casefold()
    if lowered.startswith("category:"):
        return name
    if lowered == _NO_CATEGORY.casefold():
        return _NO_CATEGORY
    return f"Category: {name}"


def install_transactions_entry_chrome(host: Any) -> None:
    """Polish the Transactions form, category list, splitter, and table chrome."""
    _polish_form_column(host)
    _polish_category_list(host)
    _polish_entry_surfaces(host)
    _polish_transactions_table(host)
    _configure_transactions_splitter(host)
    if not getattr(host, "_transactions_entry_theme_bound", False):

        def _refresh_theme() -> None:
            _polish_form_column(host)
            _polish_category_list(host)
            _polish_entry_surfaces(host)

        bind_theme(host, _refresh_theme)
        host._transactions_entry_theme_bound = True  # noqa: SLF001


def persist_transactions_splitter_sizes(host: Any) -> None:
    """Save current Transactions-tab splitter sizes."""
    if getattr(host, "_is_closing", False) or not hasattr(host, "splitter"):
        return
    sizes = host.splitter.sizes()
    if len(sizes) == EXPECTED_SPLITTER_LEN and all(size > 0 for size in sizes):
        save_splitter_sizes([int(size) for size in sizes])


def refresh_category_state_label(host: Any, display_name: str | None = None) -> None:
    """Update `label_category_now` with a Fluent status string."""
    host.label_category_now.setText(category_state_text(display_name))
    host.label_category_now.setProperty("hskCategorySelected", bool((display_name or "").strip()))
    host.label_category_now.style().unpolish(host.label_category_now)
    host.label_category_now.style().polish(host.label_category_now)


def _configure_transactions_splitter(host: Any) -> None:
    host.frame.setMinimumWidth(_FORM_MIN_WIDTH)
    host.widget_middle.setMinimumWidth(_CATEGORIES_MIN_WIDTH)
    host.widget_transactions.setMinimumWidth(_TABLE_MIN_WIDTH)
    host.splitter.setChildrenCollapsible(False)
    host.splitter.setStretchFactor(0, 0)
    host.splitter.setStretchFactor(1, 0)
    host.splitter.setStretchFactor(2, 1)

    saved = load_splitter_sizes()
    host._transactions_splitter_user_moved = False  # noqa: SLF001

    def apply_sizes() -> None:
        if getattr(host, "_is_closing", False) or getattr(host, "_transactions_splitter_user_moved", False):
            return
        total = host.splitter.width()
        if total <= 0:
            total = max(host.width(), sum(saved))
        sizes = list(saved)
        if sum(sizes) != total and total > 0:
            scale = total / max(sum(sizes), 1)
            sizes = [max(1, round(size * scale)) for size in sizes]
            sizes[2] = max(1, total - sizes[0] - sizes[1])
        host.splitter.setSizes(sizes)

    def on_splitter_moved(*_args: object) -> None:
        host._transactions_splitter_user_moved = True  # noqa: SLF001
        host._transactions_splitter_save_timer.start()  # noqa: SLF001

    host._apply_transactions_splitter_sizes = apply_sizes  # noqa: SLF001
    apply_sizes()
    QTimer.singleShot(60, apply_sizes)

    if not getattr(host, "_transactions_splitter_save_bound", False):
        host._transactions_splitter_save_timer = QTimer(host)  # noqa: SLF001
        host._transactions_splitter_save_timer.setSingleShot(True)  # noqa: SLF001
        host._transactions_splitter_save_timer.setInterval(_SPLITTER_SAVE_DELAY_MS)  # noqa: SLF001
        host._transactions_splitter_save_timer.timeout.connect(  # noqa: SLF001
            lambda: persist_transactions_splitter_sizes(host),
        )
        host.splitter.splitterMoved.connect(on_splitter_moved)
        host._transactions_splitter_save_bound = True  # noqa: SLF001


def _field_caption_qss() -> str:
    return f"color: {MUTED_TEXT}; font-weight: 600; padding-top: 2px;"


def _install_column_visibility_menu(host: Any, table: QTableView) -> None:
    header = table.horizontalHeader()
    header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def show_menu(pos: QPoint) -> None:
        menu = QMenu(table)
        flags = load_column_visibility()
        english_visible = flags.get(_VIS_KEY_ENGLISH, True)
        ids_visible = flags.get(_VIS_KEY_RECORD_ID, True)

        english_action = QAction("Show English", menu)
        english_action.setCheckable(True)
        english_action.setChecked(english_visible)
        english_action.toggled.connect(lambda checked: _set_english_visible(table, visible=checked))
        menu.addAction(english_action)

        id_action = QAction("Show record ID", menu)
        id_action.setCheckable(True)
        id_action.setChecked(ids_visible)
        id_action.toggled.connect(lambda checked: _set_record_id_visible(table, visible=checked))
        menu.addAction(id_action)
        menu.exec(header.mapToGlobal(pos))

    if not getattr(host, "_transactions_column_menu_bound", False):
        header.customContextMenuRequested.connect(show_menu)
        host._transactions_column_menu_bound = True  # noqa: SLF001

    apply_transactions_column_visibility(host)


def _polish_category_list(host: Any) -> None:
    view: QListView = host.listView_categories
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
    host.label_categories.setText("Categories")
    host.label_categories.setStyleSheet(_field_caption_qss())
    font = QFont(host.label_categories.font())
    font.setBold(True)
    host.label_categories.setFont(font)


def _polish_entry_surfaces(host: Any) -> None:
    palette = palette_for(host)
    panel = css(mix(palette.window_bg, palette.layer_alt_bg))
    soft_divider = css(mix(palette.window_bg, palette.divider))
    strong_divider = css(mix(palette.window_bg, palette.card_stroke))
    text = css(mix(palette.window_bg, palette.text_primary))
    muted = css(mix(palette.window_bg, palette.text_secondary))

    host.frame.setObjectName("financeEntryForm")
    host.widget_middle.setObjectName("financeEntryCategories")
    host.widget_transactions.setObjectName("financeTransactionsPane")
    host.frame.setFrameShape(QFrame.Shape.NoFrame)
    for pane in (host.frame, host.widget_middle):
        pane.setAutoFillBackground(False)

    host.splitter.setStyleSheet(
        f"""
        QSplitter#splitter {{
            background: transparent;
        }}
        QSplitter#splitter::handle {{
            background: {soft_divider};
            width: 1px;
            margin: 8px 0px;
        }}
        QSplitter#splitter::handle:horizontal {{
            width: 1px;
        }}
        QFrame#financeEntryForm, QWidget#financeEntryCategories {{
            background: {panel};
            border: none;
        }}
        QWidget#financeEntryCategories {{
            border-left: 1px solid {soft_divider};
        }}
        QWidget#financeTransactionsPane {{
            background: transparent;
            border-left: 1px solid {strong_divider};
        }}
        QLabel#label_category_now {{
            color: {muted};
            font-weight: 600;
            padding: 2px 0px {SPACE_XS}px 0px;
        }}
        QLabel#label_category_now[hskCategorySelected="true"] {{
            color: {text};
        }}
        """,
    )


def _polish_form_column(host: Any) -> None:
    host.groupBox_transaction.setTitle("New transaction")
    host.groupBox_commands.setTitle("")
    host.groupBox_commands.setFlat(True)
    if hasattr(host, "groupBox_expenses"):
        host.groupBox_expenses.setTitle("Expenses")

    for name in (
        "label_field_description",
        "label_field_amount",
        "label_field_date",
        "label_field_tag",
        "label_expense_today_caption",
        "label_expense_yesterday_caption",
    ):
        label = getattr(host, name, None)
        if isinstance(label, QLabel):
            label.setStyleSheet(_field_caption_qss())

    if hasattr(host, "label_tag"):
        host.label_tag.hide()

    host.pushButton_add.setText("Add transaction")
    host.pushButton_add.setStyleSheet(button_cta_mint_qss())
    apply_lucide_button_icon(host.pushButton_add, "plus")

    host.pushButton_add_as_text_with_ai.setText("Add with AI")
    host.pushButton_add_as_text_with_ai.setStyleSheet(button_idle_qss())
    apply_lucide_button_icon(host.pushButton_add_as_text_with_ai, "sparkles")

    for label_name in ("label_today_expense", "label_yesterday_expense"):
        label = getattr(host, label_name, None)
        if isinstance(label, QLabel):
            font = QFont(label.font())
            font.setPointSize(max(10, font.pointSize() if font.pointSize() > 0 else 10))
            font.setBold(True)
            label.setFont(font)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    refresh_category_state_label(host, None)


def _polish_transactions_table(host: Any) -> None:
    table: QTableView = host.tableView_transactions
    vertical = table.verticalHeader()
    vertical.setDefaultSectionSize(TRANSACTIONS_ROW_HEIGHT)
    vertical.setMinimumSectionSize(24)
    header = table.horizontalHeader()
    if isinstance(header, QHeaderView):
        header.setStretchLastSection(False)
        header.setSectionsMovable(False)
    table.setWordWrap(False)
    table.setTextElideMode(Qt.TextElideMode.ElideRight)
    _install_column_visibility_menu(host, table)


def _set_english_visible(table: QTableView, *, visible: bool, persist: bool = True) -> None:
    model = table.model()
    if model is not None and model.columnCount() > OPTIONAL_COLUMN_ENGLISH:
        table.setColumnHidden(OPTIONAL_COLUMN_ENGLISH, not visible)
    if persist:
        flags = load_column_visibility()
        flags[_VIS_KEY_ENGLISH] = visible
        save_column_visibility(flags)


def _set_record_id_visible(table: QTableView, *, visible: bool, persist: bool = True) -> None:
    table.verticalHeader().setVisible(visible)
    if persist:
        flags = load_column_visibility()
        flags[_VIS_KEY_RECORD_ID] = visible
        save_column_visibility(flags)
