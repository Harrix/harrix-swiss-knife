"""Fluent chrome for Finance tabs beyond Transactions (Accounts…Reports)."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QAbstractItemView, QLabel, QListView, QSizePolicy, QTableView

from harrix_swiss_knife.apps.common.table_models import (
    bind_column_fill_on_resize,
    columns_fill_viewport,
    user_resized_columns,
)
from harrix_swiss_knife.apps.common.tracker_layout_chrome import (
    apply_tracker_column_surfaces,
    quiet_group_box,
    show_splitter_hairlines,
)
from harrix_swiss_knife.apps.common.ui_chrome import button_cta_mint_qss, button_idle_qss
from harrix_swiss_knife.apps.finance.finance_tabs_ui_settings import (
    load_accounts_splitter_sizes,
    load_charts_splitter_sizes,
    load_exchange_splitter_sizes,
    load_rates_splitter_sizes,
    load_reports_splitter_sizes,
    save_accounts_splitter_sizes,
    save_charts_splitter_sizes,
    save_exchange_splitter_sizes,
    save_rates_splitter_sizes,
    save_reports_splitter_sizes,
)
from harrix_swiss_knife.fluent.app_chrome import style_fluent_item_view
from harrix_swiss_knife.fluent.theme import FluentTheme, bind_theme, css, mix
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, ICON_SIZE, SPACE_S, SPACE_XS
from harrix_swiss_knife.qt_flow_layout import FlowLayout
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon

TABLE_ROW_HEIGHT = 30
_FORM_MIN_WIDTH = 280
# Currency Exchange / Rates / Charts need room for Lucide CTAs beside spin boxes.
_EXCHANGE_FORM_MIN_WIDTH = 440
_SIDE_MIN_WIDTH = 360
_CONTENT_MIN_WIDTH = 400
_EXCHANGE_LABEL_WIDTH = 90
_EXCHANGE_FIELD_MIN_WIDTH = 100
_SPLITTER_SAVE_DELAY_MS = 400
_TWO_PANE_SPLITTER_LEN = 2
# Exchange rates table: From / To / Rate / Date — Rate needs the leftover width.
_RATES_COL_FROM = 0
_RATES_COL_TO = 1
_RATES_COL_RATE = 2
_RATES_COL_DATE = 3
_RATES_FROM_WIDTH = 48
_RATES_TO_WIDTH = 48
_RATES_DATE_WIDTH = 100
_RATES_RATE_MIN_WIDTH = 96
_RATES_COLUMN_COUNT = 4


def apply_exchange_rates_table_column_widths(table: QTableView, *, force: bool = False) -> None:
    """Give Rate the leftover width; keep From/To/Date compact so values fit."""
    bind_column_fill_on_resize(table, apply_exchange_rates_table_column_widths)
    if not table.isVisible() or user_resized_columns(table):
        return
    header = table.horizontalHeader()
    if header.count() < _RATES_COLUMN_COUNT or table.property("hskColumnFillGuard"):
        return
    viewport_w = table.viewport().width()
    if viewport_w <= 0:
        return
    if not force and columns_fill_viewport(table):
        return

    rate_w = max(
        viewport_w - _RATES_FROM_WIDTH - _RATES_TO_WIDTH - _RATES_DATE_WIDTH,
        _RATES_RATE_MIN_WIDTH,
    )
    widths = {
        _RATES_COL_FROM: _RATES_FROM_WIDTH,
        _RATES_COL_TO: _RATES_TO_WIDTH,
        _RATES_COL_RATE: rate_w,
        _RATES_COL_DATE: _RATES_DATE_WIDTH,
    }
    header.setStretchLastSection(False)
    table.setProperty("hskColumnFillGuard", 1)
    try:
        for column, width in widths.items():
            header.setSectionResizeMode(column, header.ResizeMode.Interactive)
            table.setColumnWidth(column, width)
    finally:
        table.setProperty("hskColumnFillGuard", 0)


def install_finance_layout_chrome(host: Any) -> None:
    """Polish Accounts / Exchange / Rates / Charts / Reports with flat panes."""
    _polish_all_tabs(host)
    _configure_all_splitters(host)
    if not getattr(host, "_finance_tabs_theme_bound", False):
        bind_theme(host, lambda: _polish_all_tabs(host))
        host._finance_tabs_theme_bound = True  # noqa: SLF001


def persist_finance_tabs_splitter_sizes(host: Any) -> None:
    """Save splitter sizes for every non-Transactions Finance tab."""
    if getattr(host, "_is_closing", False):
        return
    _persist_named_splitter(host, "splitter_2", save_accounts_splitter_sizes)
    _persist_named_splitter(host, "splitter_4", save_exchange_splitter_sizes)
    _persist_named_splitter(host, "splitter_6", save_rates_splitter_sizes)
    _persist_named_splitter(host, "splitter_7", save_charts_splitter_sizes)
    _persist_named_splitter(host, "splitter_5", save_reports_splitter_sizes)


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
    # Re-apply Fluent list ink — do not clear the sheet (resets to system black).
    style_fluent_item_view(view)


def _compact_table(table: QTableView) -> None:
    vertical = table.verticalHeader()
    vertical.setDefaultSectionSize(TABLE_ROW_HEIGHT)
    vertical.setMinimumSectionSize(24)
    table.setWordWrap(False)
    table.setTextElideMode(Qt.TextElideMode.ElideRight)


def _configure_all_splitters(host: Any) -> None:
    _configure_two_pane_splitter(
        host,
        splitter_attr="splitter_2",
        left=host.frame_accounts,
        right=host.tableView_accounts,
        left_min=_FORM_MIN_WIDTH,
        right_min=_CONTENT_MIN_WIDTH,
        load_sizes=load_accounts_splitter_sizes,
        save_sizes=save_accounts_splitter_sizes,
        flag="finance_accounts_splitter",
        left_max_share=4,
    )
    _configure_two_pane_splitter(
        host,
        splitter_attr="splitter_4",
        left=host.frame_exchange,
        right=host.tableView_exchange,
        left_min=_EXCHANGE_FORM_MIN_WIDTH,
        right_min=_CONTENT_MIN_WIDTH,
        load_sizes=load_exchange_splitter_sizes,
        save_sizes=save_exchange_splitter_sizes,
        flag="finance_exchange_splitter",
        left_max_share=3,
    )
    _configure_two_pane_splitter(
        host,
        splitter_attr="splitter_6",
        left=host.frame_rates,
        right=host.widget_exchange_rates_right,
        left_min=_SIDE_MIN_WIDTH,
        right_min=_CONTENT_MIN_WIDTH,
        load_sizes=load_rates_splitter_sizes,
        save_sizes=save_rates_splitter_sizes,
        flag="finance_rates_splitter",
        left_max_share=3,
    )
    _configure_two_pane_splitter(
        host,
        splitter_attr="splitter_7",
        left=host.frame_accounts_2,
        right=host.layoutWidget,
        left_min=_EXCHANGE_FORM_MIN_WIDTH,
        right_min=_CONTENT_MIN_WIDTH,
        load_sizes=load_charts_splitter_sizes,
        save_sizes=save_charts_splitter_sizes,
        flag="finance_charts_splitter",
        left_max_share=3,
    )
    _configure_two_pane_splitter(
        host,
        splitter_attr="splitter_5",
        left=host.frame_5,
        right=host.tableView_reports,
        left_min=_FORM_MIN_WIDTH,
        right_min=_CONTENT_MIN_WIDTH,
        load_sizes=load_reports_splitter_sizes,
        save_sizes=save_reports_splitter_sizes,
        flag="finance_reports_splitter",
        left_max_share=4,
    )


def _configure_two_pane_splitter(
    host: Any,
    *,
    splitter_attr: str,
    left: Any,
    right: Any,
    left_min: int,
    right_min: int,
    load_sizes: Any,
    save_sizes: Any,
    flag: str,
    left_max_share: int,
) -> None:
    splitter = getattr(host, splitter_attr, None)
    if splitter is None:
        return
    left.setMinimumWidth(left_min)
    right.setMinimumWidth(right_min)
    splitter.setChildrenCollapsible(False)
    splitter.setStretchFactor(0, 0)
    splitter.setStretchFactor(1, 1)

    saved = load_sizes()
    moved_attr = f"{flag}_user_moved"
    timer_attr = f"{flag}_save_timer"
    bound_attr = f"{flag}_save_bound"
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
        sizes[0] = min(sizes[0], max(left_min, total // left_max_share))
        sizes[0] = max(sizes[0], left_min)
        sizes[1] = max(right_min, total - sizes[0])
        sizes[0] = max(1, total - sizes[1])
        splitter.setSizes(sizes)

    def on_moved(*_args: object) -> None:
        setattr(host, moved_attr, True)
        getattr(host, timer_attr).start()

    apply_attr = f"_apply_{flag}_sizes"
    setattr(host, apply_attr, apply_sizes)
    apply_sizes()
    QTimer.singleShot(60, apply_sizes)

    if not getattr(host, bound_attr, False):
        timer = QTimer(host)
        timer.setSingleShot(True)
        timer.setInterval(_SPLITTER_SAVE_DELAY_MS)
        timer.timeout.connect(lambda: _persist_named_splitter(host, splitter_attr, save_sizes))
        setattr(host, timer_attr, timer)
        splitter.splitterMoved.connect(on_moved)
        setattr(host, bound_attr, True)


def _persist_named_splitter(host: Any, splitter_attr: str, save_sizes: Any) -> None:
    splitter = getattr(host, splitter_attr, None)
    if splitter is None:
        return
    sizes = splitter.sizes()
    if len(sizes) == _TWO_PANE_SPLITTER_LEN and all(size > 0 for size in sizes):
        save_sizes([int(size) for size in sizes])


def _polish_accounts(host: Any) -> None:
    host.groupBox_balance_accounts.setTitle("Balance")
    quiet_group_box(host.groupBox_balance_accounts)
    host.verticalLayout_21.setSpacing(SPACE_S)
    host.verticalLayout_21.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)

    for label_name in ("label_balance_accounts", "label_balance_account_details"):
        label = getattr(host, label_name, None)
        if isinstance(label, QLabel):
            font = QFont(label.font())
            if label_name == "label_balance_accounts":
                font.setPointSize(max(12, font.pointSize() if font.pointSize() > 0 else 12))
                font.setBold(True)
            label.setFont(font)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    if isinstance(host.label_balance_account_details, QLabel):
        host.label_balance_account_details.setStyleSheet(_caption_qss())
        host.label_balance_account_details.setWordWrap(True)

    host.pushButton_balance_check.setText("Balance check")
    host.pushButton_balance_check.setMinimumHeight(CONTROL_HEIGHT)
    host.pushButton_balance_check.setStyleSheet(button_cta_mint_qss())
    apply_lucide_button_icon(host.pushButton_balance_check, "calculator")
    _compact_table(host.tableView_accounts)


def _polish_all_tabs(host: Any) -> None:
    apply_tracker_column_surfaces(
        host,
        soft_panes=(),
        content_panes=(
            (host.frame_accounts, "financeAccountsForm"),
            (host.frame_exchange, "financeExchangeForm"),
            (host.frame_rates, "financeRatesForm"),
            (host.frame_accounts_2, "financeChartsForm"),
            (host.frame_5, "financeReportsForm"),
            (host.widget_exchange_rates_right, "financeRatesChartPane"),
            (host.layoutWidget, "financeChartsPane"),
            # Tables stay out of content_panes — setStyleSheet would wipe Fluent header chrome.
        ),
    )
    show_splitter_hairlines(
        (
            getattr(host, "splitter_2", None),
            getattr(host, "splitter_4", None),
            getattr(host, "splitter_5", None),
            getattr(host, "splitter_6", None),
            getattr(host, "splitter_7", None),
        ),
    )
    _polish_accounts(host)
    _polish_exchange(host)
    _polish_rates(host)
    _polish_charts(host)
    _polish_reports(host)


def _polish_charts(host: Any) -> None:
    host.groupBox_type_of_charts.setTitle("Chart type")
    quiet_group_box(host.groupBox_type_of_charts)
    host.verticalLayout_24.setSpacing(SPACE_S)
    host.verticalLayout_24.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)
    if isinstance(host.label_3, QLabel):
        host.label_3.setText("Categories")
        host.label_3.setStyleSheet(_caption_qss())
        font = QFont(host.label_3.font())
        font.setBold(True)
        host.label_3.setFont(font)

    from harrix_swiss_knife.apps.finance.transaction_filter_chrome import (  # noqa: PLC0415
        EXPENSE_LUCIDE_ICON,
        INCOME_LUCIDE_ICON,
    )

    host.pushButton_select_all.setText("Select all")
    host.pushButton_select_deselect_all.setText("Deselect all")
    host.pushButton_select_only_expense.setText("Select only expense")
    host.pushButton_select_only_income.setText("Select only income")
    _wrap_chart_category_buttons(host)

    for name, icon in (
        ("pushButton_select_all", "square-check"),
        ("pushButton_select_deselect_all", "square"),
        ("pushButton_select_only_expense", EXPENSE_LUCIDE_ICON),
        ("pushButton_select_only_income", INCOME_LUCIDE_ICON),
        ("pushButton_chart_last_month", "calendar"),
        ("pushButton_chart_last_year", "calendar-range"),
        ("pushButton_chart_all_time", "infinity"),
    ):
        button = getattr(host, name, None)
        if button is None:
            continue
        button.setMinimumHeight(CONTROL_HEIGHT)
        button.setStyleSheet(button_idle_qss())
        apply_lucide_button_icon(button, icon)

    for name in (
        "label_chart_period",
        "label_chart_from",
        "label_chart_to",
        "label_compare_last",
        "label_exchange_rates_currency",
        "label_exchange_rates_from",
        "label_exchange_rates_to",
    ):
        label = getattr(host, name, None)
        if isinstance(label, QLabel):
            label.setStyleSheet(_caption_qss())

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

    _compact_list(host.list_chart_categories)


def _polish_exchange(host: Any) -> None:
    host.groupBox_exchange_operation.setTitle("Currency exchange")
    quiet_group_box(host.groupBox_exchange_operation)
    host.verticalLayout_exchange.setSpacing(SPACE_S)
    host.verticalLayout_exchange.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)
    host.verticalLayout_exchange_operation.setSpacing(SPACE_XS)

    for name in (
        "label_exchange_from",
        "label_exchange_to",
        "label_exchange_rate",
        "label_exchange_fee",
        "label_exchange_description",
        "label_exchange_date",
    ):
        label = getattr(host, name, None)
        if isinstance(label, QLabel):
            label.setStyleSheet(_caption_qss())
            label.setMinimumWidth(_EXCHANGE_LABEL_WIDTH)
            label.setFixedWidth(_EXCHANGE_LABEL_WIDTH)

    for control_name in (
        "comboBox_exchange_from",
        "comboBox_exchange_to",
        "doubleSpinBox_exchange_from",
        "doubleSpinBox_exchange_to",
        "doubleSpinBox_exchange_rate",
        "doubleSpinBox_exchange_fee",
        "lineEdit_exchange_description",
        "dateEdit_exchange",
        "pushButton_calculate_exchange",
        "pushButton_calculate_fee",
        "pushButton_exchange_add",
    ):
        control = getattr(host, control_name, None)
        if control is not None:
            control.setMinimumHeight(CONTROL_HEIGHT)

    # Fee / description had 260px mins in the .ui; that crushed the Calculate buttons.
    for field_name in (
        "doubleSpinBox_exchange_from",
        "doubleSpinBox_exchange_to",
        "doubleSpinBox_exchange_rate",
        "doubleSpinBox_exchange_fee",
        "lineEdit_exchange_description",
    ):
        field = getattr(host, field_name, None)
        if field is not None:
            field.setMinimumWidth(_EXCHANGE_FIELD_MIN_WIDTH)
            field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    host.pushButton_exchange_add.setText("Add exchange")
    host.pushButton_exchange_add.setStyleSheet(button_cta_mint_qss())
    apply_lucide_button_icon(host.pushButton_exchange_add, "plus")

    host.pushButton_calculate_exchange.setText("Calculate to by rate")
    host.pushButton_calculate_exchange.setStyleSheet(button_idle_qss())
    apply_lucide_button_icon(host.pushButton_calculate_exchange, "calculator")
    host.pushButton_calculate_exchange.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

    host.pushButton_calculate_fee.setText("Calculate fee")
    host.pushButton_calculate_fee.setStyleSheet(button_idle_qss())
    apply_lucide_button_icon(host.pushButton_calculate_fee, "percent")
    host.pushButton_calculate_fee.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
    _compact_table(host.tableView_exchange)


def _polish_rates(host: Any) -> None:
    host.groupBox_rate_commands.setTitle("Commands")
    host.groupBox_filter_2.setTitle("Table filter")
    quiet_group_box(host.groupBox_rate_commands)
    quiet_group_box(host.groupBox_filter_2)
    host.verticalLayout_14.setSpacing(SPACE_S)
    host.verticalLayout_14.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)
    host.verticalLayout_rate_panels.setSpacing(SPACE_S)
    host.verticalLayout_rate_panels.setContentsMargins(0, 0, 0, 0)

    for name in (
        "label",
        "label_2",
        "label_exchange_item_update",
        "label_exchange_item_update_2",
        "label_filter_currency_2",
        "label_filter_date_2",
        "label_filter_to_2",
    ):
        label = getattr(host, name, None)
        if isinstance(label, QLabel):
            label.setStyleSheet(_caption_qss())

    for control_name in (
        "pushButton_exchange_update",
        "pushButton_rates_refresh",
        "spinBox_exchange_rate_count_days",
        "pushButton_rates_delete",
        "comboBox_exchange_item_update",
        "dateEdit_exchange_item_update",
        "doubleSpinBox_exchange_item_update",
        "pushButton_exchange_item_update",
        "comboBox_exchange_rates_filter_currency",
        "dateEdit_filter_exchange_rates_from",
        "dateEdit_filter_exchange_rates_to",
        "pushButton_filter_exchange_rates_clear",
        "pushButton_filter_exchange_rates_apply",
        "pushButton_exchange_rates_last_month",
        "pushButton_exchange_rates_last_year",
        "pushButton_exchange_rates_all_time",
    ):
        control = getattr(host, control_name, None)
        if control is not None:
            control.setMinimumHeight(CONTROL_HEIGHT)

    host.pushButton_exchange_update.setText("Update")
    host.pushButton_exchange_update.setStyleSheet(button_cta_mint_qss())
    apply_lucide_button_icon(host.pushButton_exchange_update, "refresh-cw")

    for name, text, icon in (
        ("pushButton_rates_refresh", "Refresh table", "table"),
        ("pushButton_rates_delete", "Delete", "trash-2"),
        ("pushButton_exchange_item_update", "Update rate", "pencil"),
        ("pushButton_filter_exchange_rates_clear", "Clear filter", "x"),
        ("pushButton_filter_exchange_rates_apply", "Apply filter", "check"),
        ("pushButton_exchange_rates_last_month", "Last month", "calendar"),
        ("pushButton_exchange_rates_last_year", "Last year", "calendar-range"),
        ("pushButton_exchange_rates_all_time", "All time", "infinity"),
    ):
        button = getattr(host, name)
        button.setText(text)
        button.setStyleSheet(button_idle_qss())
        apply_lucide_button_icon(button, icon)

    _compact_table(host.tableView_exchange_rates)
    if host.tableView_exchange_rates.model() is not None:
        apply_exchange_rates_table_column_widths(host.tableView_exchange_rates, force=True)


def _polish_reports(host: Any) -> None:
    host.groupBox_10.setTitle("Generate report")
    host.groupBox_summary.setTitle("Quick summary")
    quiet_group_box(host.groupBox_10)
    quiet_group_box(host.groupBox_summary)
    host.verticalLayout_7.setSpacing(SPACE_S)
    host.verticalLayout_7.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)
    _compact_list(host.listView_report_type)
    _compact_table(host.tableView_reports)

    if isinstance(host.label_total_income, QLabel):
        host.label_total_income.setWordWrap(True)
        host.label_total_income.setStyleSheet("color: #4caf50; font-weight: 700;")
    if isinstance(host.label_total_expenses, QLabel):
        host.label_total_expenses.setWordWrap(True)
        host.label_total_expenses.setStyleSheet("color: #cc584c; font-weight: 700;")


def _wrap_chart_category_buttons(host: Any) -> None:
    """Replace the single-row category actions with a wrapping flow layout."""
    if getattr(host, "_finance_chart_category_buttons_wrapped", False):
        return
    row = getattr(host, "horizontalLayout_14", None)
    column = getattr(host, "verticalLayout_24", None)
    if row is None or column is None:
        return
    buttons = (
        host.pushButton_select_all,
        host.pushButton_select_deselect_all,
        host.pushButton_select_only_expense,
        host.pushButton_select_only_income,
    )
    index = column.indexOf(row)
    if index < 0:
        return
    while row.count():
        row.takeAt(0)
    column.removeItem(row)
    flow = FlowLayout(margin=0, h_spacing=SPACE_XS, v_spacing=SPACE_XS)
    for button in buttons:
        button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        flow.addWidget(button)
    column.insertLayout(index, flow)
    host.horizontalLayout_14 = flow
    host._finance_chart_category_buttons_wrapped = True  # noqa: SLF001
