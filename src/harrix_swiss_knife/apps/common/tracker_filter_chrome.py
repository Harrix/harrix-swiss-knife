"""Shared Fluent progressive-disclosure filter shell for tracker apps."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.ui_chrome import MUTED_TEXT
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, SPACE_S, SPACE_XS
from harrix_swiss_knife.fluent.widgets.display import FluentTag
from harrix_swiss_knife.fluent.widgets.enums import Severity
from harrix_swiss_knife.qt_lucide_icon import CLEAR_BUTTON_ICON, apply_lucide_button_icon, create_lucide_icon

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

FILTER_MAX_POLICY = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
DATE_FIELD_MIN_WIDTH = 128


def clear_filter_layout_widgets(layout: QLayout, parent: QWidget) -> None:
    """Detach every widget from `layout` and reparent them under `parent`."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(parent)


def hide_filter_labels(*labels: QLabel) -> None:
    """Hide Designer labels replaced by progressive filter chrome."""
    for label in labels:
        label.hide()


def inline_filter_caption(caption: str, widget: QWidget, parent: QWidget) -> QWidget:
    """Keep a short caption beside a control on one baseline row."""
    field = QWidget(parent)
    field.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
    row = QHBoxLayout(field)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(SPACE_XS)
    label = QLabel(caption, field)
    label.setStyleSheet(f"color: {MUTED_TEXT};")
    label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
    row.addWidget(label, 0)
    row.addWidget(widget, 0)
    return field


def install_tracker_filter_shell(
    host: Any,
    *,
    object_name_prefix: str,
    search_edit: QLineEdit | None,
    search_placeholder: str,
    advanced_rows: Sequence[Sequence[QWidget]],
    vertical_layout: QVBoxLayout,
    table_widget: QWidget,
    toolbar_widgets: Sequence[QWidget] = (),
) -> None:
    """Rebuild a tracker filter strip: optional search + Filter + chips + advanced panel."""
    layout = host.horizontalLayout_filter
    clear_filter_layout_widgets(layout, host.groupBox_filter)

    host.pushButton_filter = QPushButton("Filter", host.groupBox_filter)
    host.pushButton_filter.setObjectName("pushButton_filter")
    host.pushButton_filter.setCheckable(True)
    host.pushButton_filter.setCursor(Qt.CursorShape.PointingHandCursor)
    host.pushButton_filter.setIcon(create_lucide_icon("list-filter", 16))
    host.pushButton_filter.setMinimumHeight(CONTROL_HEIGHT)

    style_clear_filter_button(host.pushButton_clear_filter)

    toolbar = QWidget(host.groupBox_filter)
    toolbar.setObjectName(f"{object_name_prefix}FilterToolbar")
    toolbar.setSizePolicy(FILTER_MAX_POLICY)
    toolbar_row = QHBoxLayout(toolbar)
    toolbar_row.setContentsMargins(0, 0, 0, 0)
    toolbar_row.setSpacing(SPACE_S)
    if search_edit is not None:
        search_edit.setPlaceholderText(search_placeholder)
        search_edit.setClearButtonEnabled(False)
        toolbar_row.addWidget(search_edit, 1)
    for widget in toolbar_widgets:
        toolbar_row.addWidget(widget, 1)
    if search_edit is None and not toolbar_widgets:
        toolbar_row.addStretch(1)
    toolbar_row.addWidget(host.pushButton_filter, 0)
    toolbar_row.addWidget(host.pushButton_clear_filter, 0)

    chips_host = QWidget(host.groupBox_filter)
    chips_host.setObjectName(f"{object_name_prefix}FilterChips")
    chips_host.setSizePolicy(FILTER_MAX_POLICY)
    chips_row = QHBoxLayout(chips_host)
    chips_row.setContentsMargins(0, 0, 0, 0)
    chips_row.setSpacing(SPACE_XS)
    chips_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    chips_host.hide()
    host.filter_chips_host = chips_host
    host.filter_chips_layout = chips_row

    advanced = QWidget(host.groupBox_filter)
    advanced.setObjectName(f"{object_name_prefix}FilterAdvanced")
    advanced.setSizePolicy(FILTER_MAX_POLICY)
    advanced_column = QVBoxLayout(advanced)
    advanced_column.setContentsMargins(0, SPACE_XS, 0, 0)
    advanced_column.setSpacing(SPACE_XS)
    for row_widgets in advanced_rows:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(SPACE_S)
        row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        for widget in row_widgets:
            stretch = 0 if isinstance(widget, QCheckBox) else 1
            row.addWidget(widget, stretch)
        row.addStretch(1)
        advanced_column.addLayout(row)
    advanced.hide()
    host.filter_advanced_panel = advanced

    shell = QWidget(host.groupBox_filter)
    shell.setObjectName(f"{object_name_prefix}FilterShell")
    shell.setSizePolicy(FILTER_MAX_POLICY)
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
    host.groupBox_filter.setSizePolicy(FILTER_MAX_POLICY)
    host.groupBox_filter.setStyleSheet(
        "QGroupBox#groupBox_filter { border: none; margin-top: 0px; padding-top: 0px; background: transparent; }"
        "QGroupBox#groupBox_filter::title { height: 0px; width: 0px; padding: 0px; margin: 0px; }",
    )
    vertical_layout.setAlignment(host.groupBox_filter, Qt.AlignmentFlag.AlignTop)
    group_index = vertical_layout.indexOf(host.groupBox_filter)
    if group_index >= 0:
        vertical_layout.setStretch(group_index, 0)
    table_index = vertical_layout.indexOf(table_widget)
    if table_index >= 0:
        vertical_layout.setStretch(table_index, 1)

    host.pushButton_filter.toggled.connect(advanced.setVisible)


def prepare_date_filter_fields(
    date_from: QDateEdit,
    date_to: QDateEdit,
    checkbox: QCheckBox,
    *,
    checkbox_text: str = "Date range",
) -> None:
    """Normalize date filter controls for the advanced filter row."""
    for date_edit in (date_from, date_to):
        date_edit.setMinimumWidth(DATE_FIELD_MIN_WIDTH)
        date_edit.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
    date_from.setToolTip("From date")
    date_to.setToolTip("To date")
    checkbox.setText(checkbox_text)
    checkbox.setToolTip("Filter by date range")


def prepare_filter_combo(combo: QComboBox, sample_text: str, tooltip: str) -> None:
    """Size a filter combo so its default label is not elided."""
    combo.setToolTip(tooltip)
    combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    combo.setMinimumContentsLength(max(8, len(sample_text)))
    combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


def refresh_tracker_filter_chips(host: Any, chips: Sequence[tuple[str, Callable[[], None]]]) -> None:
    """Rebuild closable chips for active advanced filters."""
    layout = host.filter_chips_layout
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    for text, on_clear in chips:
        tag = FluentTag(text, host.filter_chips_host, severity=Severity.ACCENT, closable=True)
        tag.closed.connect(on_clear)
        layout.addWidget(tag)
    layout.addStretch(1)
    host.filter_chips_host.setVisible(bool(chips))


def style_clear_filter_button(button: QPushButton) -> None:
    """Apply Lucide clear chrome to a filter clear button."""
    apply_lucide_button_icon(button, CLEAR_BUTTON_ICON)
    button.setText("")
    button.setToolTip("Clear filter")
    button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    button.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)


def sync_filter_button_marker(button: QPushButton, *, advanced_active: bool) -> None:
    """Show a dot on the Filter toggle when advanced filters are active."""
    button.setText("Filter •" if advanced_active else "Filter")
