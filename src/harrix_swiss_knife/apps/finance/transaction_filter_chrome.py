"""Compact Fluent filter toolbar for the Finance transactions table."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from harrix_swiss_knife.apps.common.ui_chrome import MUTED_TEXT
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, SPACE_S, SPACE_XS
from harrix_swiss_knife.fluent.widgets.display import FluentTag
from harrix_swiss_knife.fluent.widgets.enums import Severity
from harrix_swiss_knife.qt_lucide_icon import CLEAR_BUTTON_ICON, apply_lucide_button_icon, create_lucide_icon

_FILTER_MAX_POLICY = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)


def advanced_transactions_filter_is_active(host: Any) -> bool:
    """Return whether any non-search transaction filter is applied."""
    if host.comboBox_filter_type.currentText().strip() in {"Expense", "Income"}:
        return True
    if host.comboBox_filter_category.currentText().strip():
        return True
    if host.comboBox_filter_currency.currentText().strip():
        return True
    return bool(host.checkBox_use_date_filter.isChecked())


def install_transactions_filter_chrome(host: Any) -> None:
    """Rebuild the transactions filter strip: search + Filter + chips + advanced panel."""
    layout = host.horizontalLayout_filter
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(host.groupBox_filter)

    for label in (
        host.label_filter_description,
        host.label_filter_type,
        host.label_filter_category,
        host.label_filter_currency,
        host.label_filter_date,
        host.label_filter_to,
    ):
        label.hide()

    host.lineEdit_filter_description.setPlaceholderText("Search description…")
    host.lineEdit_filter_description.setClearButtonEnabled(False)

    host.pushButton_filter = QPushButton("Filter", host.groupBox_filter)
    host.pushButton_filter.setObjectName("pushButton_filter")
    host.pushButton_filter.setCheckable(True)
    host.pushButton_filter.setCursor(Qt.CursorShape.PointingHandCursor)
    host.pushButton_filter.setIcon(create_lucide_icon("list-filter", 16))
    host.pushButton_filter.setMinimumHeight(CONTROL_HEIGHT)

    apply_lucide_button_icon(host.pushButton_clear_filter, CLEAR_BUTTON_ICON)
    host.pushButton_clear_filter.setText("")
    host.pushButton_clear_filter.setToolTip("Clear filter")
    host.pushButton_clear_filter.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    host.pushButton_clear_filter.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)

    toolbar = QWidget(host.groupBox_filter)
    toolbar.setObjectName("transactionsFilterToolbar")
    toolbar.setSizePolicy(_FILTER_MAX_POLICY)
    toolbar_row = QHBoxLayout(toolbar)
    toolbar_row.setContentsMargins(0, 0, 0, 0)
    toolbar_row.setSpacing(SPACE_S)
    toolbar_row.addWidget(host.lineEdit_filter_description, 1)
    toolbar_row.addWidget(host.pushButton_filter, 0)
    toolbar_row.addWidget(host.pushButton_clear_filter, 0)

    chips_host = QWidget(host.groupBox_filter)
    chips_host.setObjectName("transactionsFilterChips")
    chips_host.setSizePolicy(_FILTER_MAX_POLICY)
    chips_row = QHBoxLayout(chips_host)
    chips_row.setContentsMargins(0, 0, 0, 0)
    chips_row.setSpacing(SPACE_XS)
    chips_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    chips_host.hide()
    host.filter_chips_host = chips_host
    host.filter_chips_layout = chips_row

    if host.comboBox_filter_type.itemText(0).strip() in {"", "All"}:
        host.comboBox_filter_type.setItemText(0, "All types")
    host.comboBox_filter_category.setPlaceholderText("Category")
    host.comboBox_filter_currency.setPlaceholderText("Currency")
    host.comboBox_filter_type.setToolTip("Type")
    host.comboBox_filter_category.setToolTip("Category")
    host.comboBox_filter_currency.setToolTip("Currency")
    host.dateEdit_filter_from.setToolTip("From date")
    host.dateEdit_filter_to.setToolTip("To date")
    host.checkBox_use_date_filter.setText("Use date range")

    advanced = QWidget(host.groupBox_filter)
    advanced.setObjectName("transactionsFilterAdvanced")
    advanced.setSizePolicy(_FILTER_MAX_POLICY)
    advanced_row = QHBoxLayout(advanced)
    advanced_row.setContentsMargins(0, SPACE_XS, 0, 0)
    advanced_row.setSpacing(SPACE_S)
    advanced_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    for widget, stretch in (
        (host.comboBox_filter_type, 1),
        (host.comboBox_filter_category, 2),
        (host.comboBox_filter_currency, 1),
        (_inline_caption("From", host.dateEdit_filter_from, advanced), 1),
        (_inline_caption("To", host.dateEdit_filter_to, advanced), 1),
        (host.checkBox_use_date_filter, 0),
    ):
        advanced_row.addWidget(widget, stretch)
    advanced_row.addStretch(1)
    advanced.hide()
    host.filter_advanced_panel = advanced

    shell = QWidget(host.groupBox_filter)
    shell.setObjectName("transactionsFilterShell")
    shell.setSizePolicy(_FILTER_MAX_POLICY)
    shell_column = QVBoxLayout(shell)
    shell_column.setContentsMargins(0, 0, 0, 0)
    shell_column.setSpacing(SPACE_XS)
    shell_column.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinAndMaxSize)
    shell_column.addWidget(toolbar, 0)
    shell_column.addWidget(chips_host, 0)
    shell_column.addWidget(advanced, 0)
    layout.setContentsMargins(SPACE_S, SPACE_XS, SPACE_S, SPACE_XS)
    layout.setSpacing(0)
    layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    layout.addWidget(shell, 0)

    host.groupBox_filter.setTitle("")
    host.groupBox_filter.setFlat(True)
    host.groupBox_filter.setSizePolicy(_FILTER_MAX_POLICY)
    host.groupBox_filter.setStyleSheet(
        "QGroupBox#groupBox_filter { border: none; margin-top: 0px; padding-top: 0px; background: transparent; }"
        "QGroupBox#groupBox_filter::title { height: 0px; width: 0px; padding: 0px; margin: 0px; }",
    )
    transactions_layout = host.verticalLayout_transactions
    transactions_layout.setAlignment(host.groupBox_filter, Qt.AlignmentFlag.AlignTop)
    transactions_layout.setStretch(transactions_layout.indexOf(host.groupBox_filter), 0)
    table_index = transactions_layout.indexOf(host.tableView_transactions)
    if table_index >= 0:
        transactions_layout.setStretch(table_index, 1)

    host.pushButton_filter.toggled.connect(advanced.setVisible)


def refresh_transactions_filter_chips(host: Any) -> None:
    """Rebuild closable chips for active advanced filters (not description search)."""
    layout = host.filter_chips_layout
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    chips: list[tuple[str, Any]] = []
    type_text = host.comboBox_filter_type.currentText().strip()
    if type_text in {"Expense", "Income"}:
        chips.append((type_text, host.clear_transactions_type_filter))
    category = host.comboBox_filter_category.currentText().strip()
    if category:
        chips.append((category, host.clear_transactions_category_filter))
    currency = host.comboBox_filter_currency.currentText().strip()
    if currency:
        chips.append((currency, host.clear_transactions_currency_filter))
    if host.checkBox_use_date_filter.isChecked():
        date_from = host.dateEdit_filter_from.date().toString("yyyy-MM-dd")
        date_to = host.dateEdit_filter_to.date().toString("yyyy-MM-dd")
        chips.append((f"{date_from} → {date_to}", host.clear_transactions_date_filter))

    for text, on_clear in chips:
        tag = FluentTag(text, host.filter_chips_host, severity=Severity.ACCENT, closable=True)
        tag.closed.connect(on_clear)
        layout.addWidget(tag)
    layout.addStretch(1)
    host.filter_chips_host.setVisible(bool(chips))


def _inline_caption(caption: str, widget: QWidget, parent: QWidget) -> QWidget:
    """Keep a short caption beside a control on one baseline row."""
    field = QWidget(parent)
    field.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed))
    row = QHBoxLayout(field)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(SPACE_XS)
    label = QLabel(caption, field)
    label.setStyleSheet(f"color: {MUTED_TEXT};")
    label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
    row.addWidget(label, 0)
    row.addWidget(widget, 1)
    return field
