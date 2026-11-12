"""Fluent chrome for the Finance Transactions entry columns (form + categories)."""

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
)

from harrix_swiss_knife.apps.common.table_models import (
    bind_column_fill_on_resize,
    columns_fill_viewport,
    user_resized_columns,
)
from harrix_swiss_knife.apps.common.tracker_layout_chrome import (
    apply_tracker_column_surfaces,
    polish_left_field_labels,
    quiet_group_box,
)
from harrix_swiss_knife.apps.common.ui_chrome import button_cta_mint_qss, button_idle_qss, muted_caption_qss
from harrix_swiss_knife.apps.finance.transactions_ui_settings import (
    ALWAYS_HIDDEN_COLUMNS,
    EXPECTED_SPLITTER_LEN,
    TOGGLEABLE_COLUMNS,
    TRANSACTION_COL_AMOUNT,
    TRANSACTION_COL_CATEGORY,
    TRANSACTION_COL_CURRENCY,
    TRANSACTION_COL_DESCRIPTION,
    TRANSACTION_COL_ENGLISH,
    TRANSACTION_COL_TAG,
    load_column_visibility,
    load_splitter_sizes,
    save_column_visibility,
    save_splitter_sizes,
)
from harrix_swiss_knife.fluent.app_chrome import style_fluent_item_view
from harrix_swiss_knife.fluent.theme import bind_theme, css, mix, palette_for
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, ICON_SIZE, SPACE_S, SPACE_XS
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon

TRANSACTIONS_ROW_HEIGHT = 30
_FORM_MIN_WIDTH = 280
_CATEGORIES_MIN_WIDTH = 260
_TABLE_MIN_WIDTH = 400
_SPLITTER_SAVE_DELAY_MS = 400
# Compact columns stay fixed; Description absorbs most leftover width.
_FIXED_COLUMN_WIDTHS: dict[int, int] = {
    TRANSACTION_COL_AMOUNT: 118,
    TRANSACTION_COL_CURRENCY: 72,
    TRANSACTION_COL_TAG: 110,
}
_FLEX_COLUMN_WEIGHTS: dict[int, int] = {
    TRANSACTION_COL_DESCRIPTION: 5,
    TRANSACTION_COL_ENGLISH: 2,
    TRANSACTION_COL_CATEGORY: 2,
}
_NO_CATEGORY = "Category: not selected"
_CATEGORY_HINT = "Choose a category in the adjacent panel"
_CATEGORY_PREFIX = "Category: "


def apply_transactions_column_visibility(host: Any) -> None:
    """Re-apply persisted column visibility after the table model is ready."""
    table = host.tableView_transactions
    flags = load_column_visibility()
    for key, column, _label in TOGGLEABLE_COLUMNS:
        visible = flags.get(key, True)
        if column < 0:
            _set_record_id_visible(table, visible=visible, persist=False)
        else:
            _set_data_column_visible(table, column, visible=visible, persist=False, refill=False)
    _hide_day_header_source_columns(table)
    from harrix_swiss_knife.apps.finance.transaction_day_headers import (  # noqa: PLC0415
        apply_transaction_day_header_spans,
    )

    apply_transaction_day_header_spans(table)
    apply_transactions_table_column_widths(table, force=True)


def apply_transactions_table_column_widths(table_view: QTableView, *, force: bool = False) -> None:
    """Fill the viewport among _visible_ columns, then keep them Interactive.

    Date / Total (and any user-hidden columns) must not reserve space.
    Description gets a larger share than English / Category; Amount / Currency /
    Tag stay compact.

    """
    bind_column_fill_on_resize(table_view, apply_transactions_table_column_widths)
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
    widths = _visible_transaction_column_widths(
        viewport_w,
        count,
        visible=visible,
        min_size=min_size,
    )

    table_view.setProperty("hskColumnFillGuard", 1)
    try:
        for column in range(count):
            header.setSectionResizeMode(column, header.ResizeMode.Interactive)
            # Zero hidden sections so they cannot inflate header.length().
            table_view.setColumnWidth(column, widths[column] if column in set(visible) else 0)
    finally:
        table_view.setProperty("hskColumnFillGuard", 0)


def category_state_text(display_name: str | None) -> str:
    """Return the one-line form category indicator (long hint stays in the tooltip)."""
    name = (display_name or "").strip()
    if not name:
        return _NO_CATEGORY
    lowered = name.casefold()
    if lowered.startswith(_CATEGORY_PREFIX.casefold()):
        return name.split("\n", 1)[0].strip()
    if lowered in {_NO_CATEGORY.casefold(), "no category selected"}:
        return _NO_CATEGORY
    return f"{_CATEGORY_PREFIX}{name}"


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
    text = category_state_text(display_name)
    selected = bool((display_name or "").strip()) and not text.startswith(_NO_CATEGORY)
    host.label_category_now.setText(text)
    host.label_category_now.setWordWrap(True)
    host.label_category_now.setToolTip(_CATEGORY_HINT if not selected else text.split("\n", 1)[0])
    host.label_category_now.setProperty("hskCategorySelected", selected)
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
        # Keep form from eating table space after DPI scale.
        sizes[0] = min(sizes[0], max(_FORM_MIN_WIDTH, total // 4))
        sizes[1] = max(sizes[1], _CATEGORIES_MIN_WIDTH)
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


def _hide_day_header_source_columns(table: QTableView) -> None:
    model = table.model()
    if model is None:
        return
    for column in ALWAYS_HIDDEN_COLUMNS:
        if column < model.columnCount():
            table.setColumnHidden(column, True)  # noqa: FBT003


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

    if not getattr(host, "_transactions_column_menu_bound", False):
        header.customContextMenuRequested.connect(show_menu)
        host._transactions_column_menu_bound = True  # noqa: SLF001

    apply_transactions_column_visibility(host)


def _polish_ai_attach_block(host: Any) -> None:
    """Keep AI add + image attach compact without a permanent dashed card."""
    drop_zone = getattr(host, "_ai_image_drop_zone", None)
    if drop_zone is None:
        return
    set_quiet = getattr(drop_zone, "set_quiet_idle", None)
    if callable(set_quiet):
        set_quiet(quiet=True)
    hint = getattr(drop_zone, "set_hint_text", None)
    if callable(hint):
        hint("Attach receipt · Ctrl+V")
    elif hasattr(drop_zone, "_drop_hint") and drop_zone._drop_hint is not None:  # noqa: SLF001
        drop_zone._drop_hint.setText("Attach receipt · Ctrl+V")  # noqa: SLF001


def _polish_category_list(host: Any) -> None:
    view: QListView = host.listView_categories
    # Section headers and category rows have different heights.
    view.setUniformItemSizes(False)
    view.setSpacing(0)
    view.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
    view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    view.setTextElideMode(Qt.TextElideMode.ElideRight)
    view.setSelectionRectVisible(False)
    view.setMouseTracking(True)
    view.setWordWrap(False)
    style_fluent_item_view(view)
    host.label_categories.setText("Transaction category")
    host.label_categories.setStyleSheet(muted_caption_qss())
    font = QFont(host.label_categories.font())
    font.setBold(True)
    host.label_categories.setFont(font)
    host.label_categories.setToolTip("Select the category for the new transaction")


def _polish_entry_surfaces(host: Any) -> None:
    palette = palette_for(host)
    text = css(mix(palette.window_bg, palette.text_primary))
    muted = css(mix(palette.window_bg, palette.text_secondary))

    # Flat panes on the shared window surface — columns separate by a thin
    # splitter hairline, not by card fills, radius, or nested frames.
    quiet_boxes = [host.groupBox_transaction]
    if hasattr(host, "groupBox_expenses"):
        quiet_boxes.append(host.groupBox_expenses)
    apply_tracker_column_surfaces(
        host,
        soft_panes=(),
        content_panes=(
            (host.frame, "financeEntryForm"),
            (host.widget_middle, "financeEntryCategories"),
            (host.widget_transactions, "financeTransactionsPane"),
        ),
        quiet_boxes=quiet_boxes,
    )
    quiet_group_box(host.groupBox_commands, untitled=True)
    # Keep a light idle splitter hairline; handle width stays SPACE_S for grip.
    host.splitter.setProperty("_hskQuietSplitter", False)  # noqa: FBT003
    host.label_category_now.setStyleSheet(
        f"""
        QLabel#label_category_now {{
            color: {muted};
            font-weight: 600;
            padding: 2px 0px {SPACE_XS}px 0px;
            border: none;
            background: transparent;
        }}
        QLabel#label_category_now[hskCategorySelected="true"] {{
            color: {text};
        }}
        """,
    )
    host.label_categories.setStyleSheet(f"{muted_caption_qss()} border: none; background: transparent;")


def _polish_form_column(host: Any) -> None:
    host.groupBox_transaction.setTitle("New transaction")
    host.groupBox_commands.setTitle("")
    host.groupBox_commands.setFlat(True)
    if hasattr(host, "groupBox_expenses"):
        host.groupBox_expenses.setTitle("Expenses")

    form_layout = host.verticalLayout_5
    form_layout.setSpacing(SPACE_S)
    form_layout.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)
    host.verticalLayout_3.setSpacing(SPACE_XS)
    host.verticalLayout_2.setContentsMargins(0, SPACE_XS, 0, 0)
    host.verticalLayout_2.setSpacing(SPACE_XS)

    for name in (
        "label_expense_today_caption",
        "label_expense_yesterday_caption",
    ):
        label = getattr(host, name, None)
        if isinstance(label, QLabel):
            label.setStyleSheet(muted_caption_qss())

    polish_left_field_labels(
        host,
        (
            ("label_field_description", "Description:"),
            ("label_field_amount", "Amount:"),
            ("label_field_date", "Date:"),
            ("label_field_tag", "Tags:"),
        ),
    )

    if hasattr(host, "label_tag"):
        host.label_tag.hide()

    for control_name in (
        "lineEdit_description",
        "doubleSpinBox_amount",
        "comboBox_currency",
        "dateEdit",
        "lineEdit_tag",
        "pushButton_add",
        "pushButton_add_as_text_with_ai",
    ):
        control = getattr(host, control_name, None)
        if control is not None:
            control.setMinimumHeight(CONTROL_HEIGHT)

    host.pushButton_add.setText("Add transaction")
    host.pushButton_add.setStyleSheet(button_cta_mint_qss())
    apply_lucide_button_icon(host.pushButton_add, "plus")

    host.pushButton_add_as_text_with_ai.setText("Add with AI")
    host.pushButton_add_as_text_with_ai.setStyleSheet(button_idle_qss())
    apply_lucide_button_icon(host.pushButton_add_as_text_with_ai, "sparkles")
    _polish_ai_attach_block(host)

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
    _hide_day_header_source_columns(table)
    if refill:
        apply_transactions_table_column_widths(table, force=True)


def _set_record_id_visible(table: QTableView, *, visible: bool, persist: bool = True) -> None:
    table.verticalHeader().setVisible(visible)
    if persist:
        flags = load_column_visibility()
        flags["record_id"] = visible
        save_column_visibility(flags)


def _visible_transaction_column_widths(
    viewport_w: int,
    count: int,
    *,
    visible: list[int],
    min_size: int,
) -> list[int]:
    """Split `viewport_w` with Description weighted larger than other flex cols."""
    widths = [0] * count
    if not visible:
        return widths

    fixed = [col for col in visible if col in _FIXED_COLUMN_WIDTHS]
    flexible = [col for col in visible if col not in _FIXED_COLUMN_WIDTHS]
    fixed_total = sum(_FIXED_COLUMN_WIDTHS[col] for col in fixed)
    flex_min = len(flexible) * min_size

    if fixed_total + flex_min > viewport_w and fixed:
        # Shrink fixed columns proportionally when the pane is too narrow.
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

    # Prefer giving remainder / rounding drift to Description when present.
    used = sum(widths[col] for col in visible)
    drift = viewport_w - used
    if drift != 0:
        sink = TRANSACTION_COL_DESCRIPTION if TRANSACTION_COL_DESCRIPTION in visible else flexible[-1]
        widths[sink] = max(widths[sink] + drift, min_size)
    return widths
