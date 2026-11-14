"""Shared chart-page shell: Chart radios + two-row toolbar with mode visibility.

Tracker chart tabs keep their own series and domain filters, but use the same
control slots and the same show/hide rules for period, dates, compare, and
heatmap year navigation.

"""

from __future__ import annotations

import calendar
from typing import TYPE_CHECKING, Any, Literal

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.chart_theme import chart_info_panel_qss
from harrix_swiss_knife.apps.common.tracker_layout_chrome import quiet_group_box
from harrix_swiss_knife.apps.common.ui_chrome import button_idle_qss, muted_caption_qss
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT, SPACE_S
from harrix_swiss_knife.qt_compact_spin_box import CompactSpinBox
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_button_icon, make_lucide_push_button

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

_MONTHS_IN_YEAR = 12

ChartToolbarMode = Literal[
    "range",
    "compare_last",
    "compare_same",
    "compare_years",
    "count",
    "heatmap",
    "labels_only",
]

PERIOD_ITEMS: tuple[str, ...] = ("Days", "Months", "Years")
LABEL_MODE_ITEMS: tuple[tuple[str, str], ...] = (("auto", "Auto"), ("all", "All"), ("off", "Off"))


class ChartToolbar:
    """Two-row chart controls with mode-based visibility.

    Bind to widgets from a `.ui` host or build a fresh frame for programmatic
    pages (TickTick). Missing slots are created when `ensure_missing` runs.

    """

    def __init__(self) -> None:
        """Create an empty binder; call `bind_host` or `build` next."""
        self.frame: QFrame | None = None
        self.row1: QHBoxLayout | None = None
        self.row2: QHBoxLayout | None = None
        self.mode: ChartToolbarMode = "range"

        self.label_period: QLabel | None = None
        self.combo_period: QComboBox | None = None
        self.label_labels: QLabel | None = None
        self.combo_labels: QComboBox | None = None
        self.extra_slot: QWidget | None = None
        self.refresh_button: QPushButton | None = None

        self.label_from: QLabel | None = None
        self.date_from: QDateEdit | None = None
        self.label_to: QLabel | None = None
        self.date_to: QDateEdit | None = None
        self.button_last_week: QPushButton | None = None
        self.button_last_month: QPushButton | None = None
        self.button_last_year: QPushButton | None = None
        self.button_all_time: QPushButton | None = None
        self.button_prev_year: QPushButton | None = None
        self.button_next_year: QPushButton | None = None
        self.label_count: QLabel | None = None
        self.spin_count: QSpinBox | None = None
        self.label_month: QLabel | None = None
        self.combo_month: QComboBox | None = None

        self._on_changed: Callable[[], None] | None = None
        self._on_refresh: Callable[[], None] | None = None

    def bind_host(
        self,
        host: Any,
        *,
        frame_attr: str = "frame_charts_controls",
        row1_attr: str = "horizontalLayout_charts_controls_1",
        row2_attr: str = "horizontalLayout_charts_controls_2",
        period_combo_attr: str = "comboBox_chart_period",
        period_label_attr: str = "label_chart_period",
        date_from_attr: str = "dateEdit_chart_from",
        date_to_attr: str = "dateEdit_chart_to",
        label_from_attr: str = "label_chart_from",
        label_to_attr: str = "label_chart_to",
        last_month_attr: str = "pushButton_chart_last_month",
        last_year_attr: str = "pushButton_chart_last_year",
        all_time_attr: str = "pushButton_chart_all_time",
        last_week_attr: str = "pushButton_chart_last_week",
        refresh_attr: str = "pushButton_update_chart",
        count_label_attr: str = "label_compare_last",
        count_spin_attr: str = "spinBox_compare_last",
        month_combo_attr: str = "comboBox_compare_same_months",
        month_label_attr: str = "label_compare_same_months",
        prev_year_attr: str = "pushButton_charts_heatmap_prev_year",
        next_year_attr: str = "pushButton_charts_heatmap_next_year",
        extra_slot: QWidget | None = None,
        ensure_missing: bool = True,
    ) -> ChartToolbar:
        """Attach to widgets already created on `host` (typically from `.ui`)."""
        self.frame = getattr(host, frame_attr, None)
        self.row1 = getattr(host, row1_attr, None)
        self.row2 = getattr(host, row2_attr, None)
        self.label_period = getattr(host, period_label_attr, None)
        self.combo_period = getattr(host, period_combo_attr, None)
        self.label_from = getattr(host, label_from_attr, None)
        self.date_from = getattr(host, date_from_attr, None)
        self.label_to = getattr(host, label_to_attr, None)
        self.date_to = getattr(host, date_to_attr, None)
        self.button_last_month = getattr(host, last_month_attr, None)
        self.button_last_year = getattr(host, last_year_attr, None)
        self.button_all_time = getattr(host, all_time_attr, None)
        self.button_last_week = getattr(host, last_week_attr, None)
        self.refresh_button = getattr(host, refresh_attr, None)
        self.label_count = getattr(host, count_label_attr, None)
        self.spin_count = getattr(host, count_spin_attr, None)
        self.combo_month = getattr(host, month_combo_attr, None)
        self.label_month = getattr(host, month_label_attr, None)
        self.button_prev_year = getattr(host, prev_year_attr, None)
        self.button_next_year = getattr(host, next_year_attr, None)
        self.extra_slot = extra_slot
        self.combo_labels = getattr(host, "comboBox_chart_label_mode", None)
        self.label_labels = getattr(host, "label_chart_label_mode", None)

        if ensure_missing:
            self._ensure_missing_controls(host)
        self._normalize_preset_labels()
        self._ensure_month_items()
        self._arrange()
        return self

    def build(self, parent: QWidget | None = None) -> QFrame:
        """Create a full toolbar frame for pages built in code."""
        frame = QFrame(parent)
        frame.setObjectName("frame_charts_controls")
        frame.setFrameShape(QFrame.Shape.NoFrame)
        frame.setMaximumHeight(120)
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        root = QVBoxLayout(frame)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(SPACE_S)

        self.row1 = QHBoxLayout()
        self.row2 = QHBoxLayout()
        root.addLayout(self.row1)
        root.addLayout(self.row2)

        self.label_period = _caption("Period")
        self.combo_period = QComboBox()
        self.combo_period.setObjectName("comboBox_chart_period")
        self.combo_period.setMinimumHeight(CONTROL_HEIGHT)
        for item in PERIOD_ITEMS:
            self.combo_period.addItem(item)
        self.combo_period.setCurrentText("Months")

        self.label_labels = _caption("Labels")
        self.combo_labels = QComboBox()
        self.combo_labels.setObjectName("comboBox_chart_label_mode")
        self.combo_labels.setMinimumHeight(CONTROL_HEIGHT)
        for mode, text in LABEL_MODE_ITEMS:
            self.combo_labels.addItem(text, mode)

        self.refresh_button = _idle_button("Refresh", "refresh-cw")

        self.row1.addWidget(self.label_period)
        self.row1.addWidget(self.combo_period)
        self.row1.addWidget(self.label_labels)
        self.row1.addWidget(self.combo_labels)
        self.row1.addStretch(1)
        self.row1.addWidget(self.refresh_button)

        self.label_from = _caption("From")
        self.date_from = QDateEdit()
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from.setCalendarPopup(True)
        self.date_from.setMinimumHeight(CONTROL_HEIGHT)
        self.date_from.setDate(QDate.currentDate().addYears(-2))

        self.label_to = _caption("To")
        self.date_to = QDateEdit()
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.setCalendarPopup(True)
        self.date_to.setMinimumHeight(CONTROL_HEIGHT)
        self.date_to.setDate(QDate.currentDate())

        self.button_last_week = _idle_button("Last week", "calendar-days")
        self.button_last_month = _idle_button("Last month", "calendar")
        self.button_last_year = _idle_button("Last year", "calendar-range")
        self.button_all_time = _idle_button("All time", "infinity")
        self.button_prev_year = _idle_button("Previous year", "chevron-left")
        self.button_next_year = _idle_button("Next year", "chevron-right")

        self.label_count = _caption("Number of months")
        self.spin_count = CompactSpinBox()
        self.spin_count.setObjectName("spinBox_compare_last")
        self.spin_count.setMinimumHeight(CONTROL_HEIGHT)
        self.spin_count.setRange(1, 100000)
        self.spin_count.setValue(12)

        self.label_month = _caption("Month")
        self.combo_month = QComboBox()
        self.combo_month.setObjectName("comboBox_compare_same_months")
        self.combo_month.setMinimumHeight(CONTROL_HEIGHT)
        self._ensure_month_items()

        for widget in (
            self.label_from,
            self.date_from,
            self.label_to,
            self.date_to,
            self.button_last_week,
            self.button_last_month,
            self.button_last_year,
            self.button_all_time,
            self.button_prev_year,
            self.button_next_year,
        ):
            self.row2.addWidget(widget)
        self.row2.addStretch(1)
        self.row2.addWidget(self.label_count)
        self.row2.addWidget(self.spin_count)
        self.row2.addWidget(self.label_month)
        self.row2.addWidget(self.combo_month)

        self.frame = frame
        self._normalize_preset_labels()
        self._arrange()
        return frame

    def connect_changed(self, callback: Callable[[], None]) -> None:
        """Redraw when period, labels, dates, count, or month change."""
        self._on_changed = callback

        def _emit_changed(*_args: object) -> None:
            callback()

        if self.combo_period is not None:
            self.combo_period.currentIndexChanged.connect(_emit_changed)
        if self.combo_labels is not None:
            self.combo_labels.currentIndexChanged.connect(_emit_changed)
        if self.date_from is not None:
            self.date_from.dateChanged.connect(_emit_changed)
        if self.date_to is not None:
            self.date_to.dateChanged.connect(_emit_changed)
        if self.spin_count is not None:
            self.spin_count.valueChanged.connect(_emit_changed)
        if self.combo_month is not None:
            self.combo_month.currentIndexChanged.connect(_emit_changed)

    def connect_presets(
        self,
        *,
        last_week: Callable[[], None] | None = None,
        last_month: Callable[[], None] | None = None,
        last_year: Callable[[], None] | None = None,
        all_time: Callable[[], None] | None = None,
        prev_year: Callable[[], None] | None = None,
        next_year: Callable[[], None] | None = None,
    ) -> None:
        """Wire date and heatmap year preset buttons."""
        mapping = (
            (self.button_last_week, last_week),
            (self.button_last_month, last_month),
            (self.button_last_year, last_year),
            (self.button_all_time, all_time),
            (self.button_prev_year, prev_year),
            (self.button_next_year, next_year),
        )
        for button, handler in mapping:
            if button is not None and handler is not None:

                def _emit_preset(*_args: object, _handler: Callable[[], None] = handler) -> None:
                    _handler()

                button.clicked.connect(_emit_preset)

    def connect_refresh(self, callback: Callable[[], None]) -> None:
        """Wire the Refresh button (manual redraw / DB reload)."""
        self._on_refresh = callback

        def _emit_refresh(*_args: object) -> None:
            callback()

        if self.refresh_button is not None:
            self.refresh_button.clicked.connect(_emit_refresh)

    def count_value(self) -> int:
        """Return the compare / by-month count spin value."""
        if self.spin_count is None:
            return 12
        return int(self.spin_count.value())

    def label_mode(self) -> Literal["auto", "all", "off"]:
        """Return Auto / All / Off from the labels combo."""
        if self.combo_labels is None:
            return "auto"
        data = self.combo_labels.currentData()
        if data in {"auto", "all", "off"}:
            return data
        return "auto"

    def month_number(self) -> int:
        """Return 1-12 from the Month combo (defaults to current month)."""
        if self.combo_month is None:
            return QDate.currentDate().month()
        data = self.combo_month.currentData()
        if isinstance(data, int) and 1 <= data <= _MONTHS_IN_YEAR:
            return data
        text = self.combo_month.currentText()
        for index in range(1, _MONTHS_IN_YEAR + 1):
            if calendar.month_name[index] == text:
                return index
        return QDate.currentDate().month()

    def period_text(self) -> str:
        """Return Days / Months / Years from the period combo."""
        if self.combo_period is None:
            return "Months"
        return self.combo_period.currentText() or "Months"

    def polish(self) -> None:
        """Apply idle button chrome and caption styles."""
        for button, icon in (
            (self.button_last_week, "calendar-days"),
            (self.button_last_month, "calendar"),
            (self.button_last_year, "calendar-range"),
            (self.button_all_time, "infinity"),
            (self.refresh_button, "refresh-cw"),
            (self.button_prev_year, "chevron-left"),
            (self.button_next_year, "chevron-right"),
        ):
            if button is None:
                continue
            button.setMinimumHeight(CONTROL_HEIGHT)
            button.setStyleSheet(button_idle_qss())
            if button.icon().isNull():
                apply_lucide_button_icon(button, icon)

        for label in (
            self.label_period,
            self.label_labels,
            self.label_from,
            self.label_to,
            self.label_count,
            self.label_month,
        ):
            if isinstance(label, QLabel):
                label.setStyleSheet(muted_caption_qss())

        for control in (
            self.combo_period,
            self.combo_labels,
            self.date_from,
            self.date_to,
            self.spin_count,
            self.combo_month,
        ):
            if control is not None:
                control.setMinimumHeight(CONTROL_HEIGHT)
        self._arrange()

    def set_extra_slot(self, widget: QWidget | None) -> None:
        """Place a tracker-specific control on row 1 before the stretch."""
        if self.row1 is None:
            self.extra_slot = widget
            return
        if self.extra_slot is not None and self.row1.indexOf(self.extra_slot) >= 0:
            self.row1.removeWidget(self.extra_slot)
        self.extra_slot = widget
        if widget is None:
            self._arrange()
            return
        insert_at = self.row1.count()
        if self.refresh_button is not None:
            refresh_index = self.row1.indexOf(self.refresh_button)
            if refresh_index >= 0:
                insert_at = refresh_index
        # Prefer before the trailing stretch when present.
        for index in range(self.row1.count()):
            item = self.row1.itemAt(index)
            if item is not None and item.spacerItem() is not None:
                insert_at = index
                break
        self.row1.insertWidget(insert_at, widget)
        self._arrange()

    def set_mode(
        self,
        mode: ChartToolbarMode,
        *,
        show_count: bool = True,
        show_extra: bool | None = None,
        count_label: str | None = None,
    ) -> None:
        """Show only the slots that belong to `mode`."""
        self.mode = mode
        is_range = mode == "range"
        is_compare_last = mode == "compare_last"
        is_compare_same = mode == "compare_same"
        is_compare_years = mode == "compare_years"
        is_count = mode == "count"
        is_heatmap = mode == "heatmap"

        show_period = is_range
        show_labels = mode != "heatmap"
        show_dates = is_range
        show_presets = is_range
        show_year_nav = is_heatmap
        show_month = is_compare_same
        show_spin = (is_compare_last or is_compare_same or is_compare_years or is_count) and show_count
        if show_extra is None:
            show_extra = is_range

        if count_label is None:
            count_label = "Number of years" if is_compare_same or is_compare_years else "Number of months"
        if self.label_count is not None and count_label:
            self.label_count.setText(count_label)

        _set_visible(self.label_period, visible=show_period)
        _set_visible(self.combo_period, visible=show_period)
        _set_visible(self.label_labels, visible=show_labels)
        _set_visible(self.combo_labels, visible=show_labels)
        _set_visible(self.extra_slot, visible=show_extra)
        _set_visible(self.refresh_button, visible=True)

        _set_visible(self.label_from, visible=show_dates)
        _set_visible(self.date_from, visible=show_dates)
        _set_visible(self.label_to, visible=show_dates)
        _set_visible(self.date_to, visible=show_dates)
        _set_visible(self.button_last_week, visible=show_presets)
        _set_visible(self.button_last_month, visible=show_presets)
        _set_visible(self.button_last_year, visible=show_presets)
        _set_visible(self.button_all_time, visible=show_presets)
        _set_visible(self.button_prev_year, visible=show_year_nav)
        _set_visible(self.button_next_year, visible=show_year_nav)
        _set_visible(self.label_count, visible=show_spin)
        _set_visible(self.spin_count, visible=show_spin)
        _set_visible(self.label_month, visible=show_month)
        _set_visible(self.combo_month, visible=show_month)

    def _arrange(self) -> None:
        """Order controls as parameters, then dates, with Refresh on the right."""
        self._arrange_row(
            self.row1,
            [
                self.label_period,
                self.combo_period,
                self.label_labels,
                self.combo_labels,
                self.extra_slot,
            ],
            [self.refresh_button],
        )
        self._arrange_row(
            self.row2,
            [
                self.label_from,
                self.date_from,
                self.label_to,
                self.date_to,
                self.button_last_week,
                self.button_last_month,
                self.button_last_year,
                self.button_all_time,
                self.button_prev_year,
                self.button_next_year,
                self.label_count,
                self.spin_count,
                self.label_month,
                self.combo_month,
            ],
            [],
        )

    def _arrange_row(
        self,
        layout: QHBoxLayout | None,
        leading: list[QWidget | None],
        trailing: list[QWidget | None],
    ) -> None:
        if layout is None:
            return
        known = {id(widget) for widget in (*leading, *trailing) if widget is not None}
        unknown: list[QWidget] = []
        seen: set[int] = set()
        for index in range(layout.count()):
            item = layout.itemAt(index)
            widget = item.widget() if item is not None else None
            if widget is None or id(widget) in known or id(widget) in seen:
                continue
            unknown.append(widget)
            seen.add(id(widget))
        while layout.count():
            layout.takeAt(0)
        for widget in leading:
            if widget is not None:
                layout.addWidget(widget)
        for widget in unknown:
            layout.addWidget(widget)
        layout.addStretch(1)
        for widget in trailing:
            if widget is not None:
                layout.addWidget(widget)
        layout.setSpacing(SPACE_S)

    def _ensure_missing_controls(self, host: Any) -> None:
        if self.row1 is None or self.row2 is None:
            return

        if self.combo_labels is None:
            install_chart_label_mode_combo(host, self.row1)
            self.combo_labels = getattr(host, "comboBox_chart_label_mode", None)
            self.label_labels = getattr(host, "label_chart_label_mode", None)

        if self.refresh_button is None:
            self.refresh_button = _idle_button("Refresh", "refresh-cw")
            self.refresh_button.setObjectName("pushButton_update_chart")
            host.pushButton_update_chart = self.refresh_button
            self.row1.addWidget(self.refresh_button)
        else:
            text = self.refresh_button.text().strip().lower()
            if text in {"update chart", "update"}:
                self.refresh_button.setText("Refresh")

        if self.button_last_week is None:
            self.button_last_week = _idle_button("Last week", "calendar-days")
            self.button_last_week.setObjectName("pushButton_chart_last_week")
            host.pushButton_chart_last_week = self.button_last_week
            insert_at = 0
            if self.button_last_month is not None:
                index = self.row2.indexOf(self.button_last_month)
                if index >= 0:
                    insert_at = index
            self.row2.insertWidget(insert_at, self.button_last_week)

        if self.label_month is None and self.combo_month is not None:
            self.label_month = _caption("Month")
            self.label_month.setObjectName("label_compare_same_months")
            host.label_compare_same_months = self.label_month
            index = self.row2.indexOf(self.combo_month)
            if index >= 0:
                self.row2.insertWidget(index, self.label_month)
            else:
                self.row2.addWidget(self.label_month)

        if self.button_prev_year is None:
            self.button_prev_year = _idle_button("Previous year", "chevron-left")
            self.button_prev_year.setObjectName("pushButton_charts_heatmap_prev_year")
            host.pushButton_charts_heatmap_prev_year = self.button_prev_year
            self.row2.insertWidget(0, self.button_prev_year)
        if self.button_next_year is None:
            self.button_next_year = _idle_button("Next year", "chevron-right")
            self.button_next_year.setObjectName("pushButton_charts_heatmap_next_year")
            host.pushButton_charts_heatmap_next_year = self.button_next_year
            index = self.row2.indexOf(self.button_prev_year) + 1 if self.button_prev_year else 0
            self.row2.insertWidget(index, self.button_next_year)

    def _ensure_month_items(self) -> None:
        if self.combo_month is None:
            return
        if self.combo_month.count() == 0:
            for month_index in range(1, _MONTHS_IN_YEAR + 1):
                self.combo_month.addItem(calendar.month_name[month_index], month_index)
        elif self.combo_month.itemData(0) is None:
            # Plain month names from older .ui fills - keep text, attach 1-12 data.
            for index in range(min(_MONTHS_IN_YEAR, self.combo_month.count())):
                if self.combo_month.itemData(index) is None:
                    self.combo_month.setItemData(index, index + 1)
        current = QDate.currentDate().month()
        if self.combo_month.currentIndex() < 0:
            self.combo_month.setCurrentIndex(current - 1)

    def _normalize_preset_labels(self) -> None:
        mapping = (
            (self.button_last_week, "Last week"),
            (self.button_last_month, "Last month"),
            (self.button_last_year, "Last year"),
            (self.button_all_time, "All time"),
            (self.refresh_button, "Refresh"),
            (self.button_prev_year, "Previous year"),
            (self.button_next_year, "Next year"),
        )
        for button, text in mapping:
            if button is not None:
                button.setText(text)

        if self.label_from is not None:
            self.label_from.setText("From")
        if self.label_to is not None:
            self.label_to.setText("To")
        if self.label_period is not None:
            self.label_period.setText("Period")
        if self.label_month is not None:
            self.label_month.setText("Month")


def build_chart_type_radios(
    parent: QWidget,
    options: Sequence[tuple[str, str]],
    *,
    checked_key: str | None = None,
) -> tuple[QButtonGroup, dict[str, QRadioButton]]:
    """Create exclusive chart-type radios.

    Args:

    - `parent` (`QWidget`): Parent for the radio widgets.
    - `options` (`Sequence[tuple[str, str]]`): `(key, label)` rows.
    - `checked_key` (`str | None`): Key to check; defaults to the first option.

    Returns:

    - `tuple[QButtonGroup, dict[str, QRadioButton]]`: Group and radios by key.

    """
    button_group = QButtonGroup(parent)
    button_group.setExclusive(True)
    radios: dict[str, QRadioButton] = {}
    default_key = checked_key if checked_key is not None else (options[0][0] if options else None)
    for index, (key, label) in enumerate(options):
        radio = QRadioButton(label, parent)
        radio.setObjectName(f"radioButton_chart_type_{key}")
        button_group.addButton(radio, index)
        radios[key] = radio
        if key == default_key:
            radio.setChecked(True)
    return button_group, radios


def create_info_strip(parent: QWidget | None = None) -> QLabel:
    """Create the shared HTML info strip under the chart toolbar."""
    label = QLabel(parent)
    label.setObjectName("chartInfoStrip")
    label.setWordWrap(True)
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    label.setStyleSheet(chart_info_panel_qss())
    label.hide()
    return label


def install_chart_label_mode_combo(
    host: Any,
    layout: Any,
    *,
    replace_widget: Any | None = None,
    on_changed: Any | None = None,
    insert_index: int | None = None,
) -> QComboBox:
    """Add or reuse Labels Auto/All/Off combo on a chart toolbar layout.

    Returns the combo. Idempotent when `host.comboBox_chart_label_mode` exists.

    """
    existing = getattr(host, "comboBox_chart_label_mode", None)
    if existing is not None:
        return existing

    if replace_widget is not None:
        replace_widget.hide()
        index = layout.indexOf(replace_widget)
    elif insert_index is not None:
        index = insert_index
    else:
        index = -1

    caption = QLabel("Labels")
    caption.setStyleSheet(muted_caption_qss())
    combo = QComboBox()
    combo.setObjectName("comboBox_chart_label_mode")
    combo.setMinimumHeight(CONTROL_HEIGHT)
    for mode, text in LABEL_MODE_ITEMS:
        combo.addItem(text, mode)
    combo.setCurrentIndex(0)
    if index >= 0:
        layout.insertWidget(index, caption)
        layout.insertWidget(index + 1, combo)
    else:
        layout.addWidget(caption)
        layout.addWidget(combo)
    host.comboBox_chart_label_mode = combo
    host.label_chart_label_mode = caption
    if on_changed is not None:
        combo.currentIndexChanged.connect(on_changed)
    return combo


def move_layout_widget(layout: QVBoxLayout | QHBoxLayout, widget: QWidget, index: int) -> None:
    """Re-insert `widget` at `index` inside `layout` without destroying it."""
    current = layout.indexOf(widget)
    if current < 0:
        layout.insertWidget(index, widget)
        return
    if current == index:
        return
    layout.removeWidget(widget)
    if current < index:
        index -= 1
    layout.insertWidget(index, widget)


def polish_chart_type_group(group: Any, *, title: str = "Chart") -> None:
    """Apply the shared Chart group title and quiet Fluent chrome."""
    if group is None:
        return
    group.setTitle(title)
    quiet_group_box(group)


def _caption(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(muted_caption_qss())
    return label


def _idle_button(text: str, icon: str) -> QPushButton:
    button = make_lucide_push_button(text, icon)
    button.setMinimumHeight(CONTROL_HEIGHT)
    button.setStyleSheet(button_idle_qss())
    return button


def _set_visible(widget: QWidget | None, *, visible: bool) -> None:
    if widget is not None:
        widget.setVisible(visible)
