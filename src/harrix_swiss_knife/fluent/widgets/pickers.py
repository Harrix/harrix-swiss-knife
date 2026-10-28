"""Fluent date and time pickers: calendar, calendar picker, roller, roller / time / date pickers."""

from __future__ import annotations

from PySide6.QtCore import QDate, QLocale, QPoint, QSize, Qt, QTime, Signal
from PySide6.QtGui import QFont, QTextCharFormat
from PySide6.QtWidgets import (
    QCalendarWidget,
    QFrame,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.fluent.style import lucide_qss_url
from harrix_swiss_knife.fluent.theme import bind_theme, css, mix, palette_for
from harrix_swiss_knife.fluent.tokens import (
    CONTROL_HEIGHT,
    RADIUS_CONTROL,
    RADIUS_OVERLAY,
    SPACE_XS,
)
from harrix_swiss_knife.fluent.widgets.button_base import FluentPushButton
from harrix_swiss_knife.fluent.widgets.picker_base import FluentRollerPicker

_CALENDAR_SIZE = QSize(320, 300)
_CLICK_SLOP_PX = 3
_ROLLER_ROW_HEIGHT = 40
_ROLLER_VISIBLE_ROWS = 7
_ROLLER_WIDTH = 80
_HOURS = 24
_MINUTES = 60


class FluentCalendar(QCalendarWidget):
    """Month calendar with Fluent navigation chrome and a round accent selection."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a calendar."""
        super().__init__(parent)
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        self.setGridVisible(False)
        self.setLocale(QLocale(QLocale.Language.English))
        self.setFixedSize(_CALENDAR_SIZE)
        self.setObjectName("FluentCalendar")
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome and weekday/weekend text formats."""
        palette = palette_for(self)
        surface = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        previous = lucide_qss_url("chevron-left", palette.text_secondary, 14)
        following = lucide_qss_url("chevron-right", palette.text_secondary, 14)
        self.setStyleSheet(f"""
QCalendarWidget#FluentCalendar {{
    background: {css(surface)}; border: 1px solid {css(palette.popup_stroke)}; border-radius: {RADIUS_OVERLAY}px;
}}
QCalendarWidget#FluentCalendar QWidget#qt_calendar_navigationbar {{ background: transparent; padding: 4px; }}
QCalendarWidget#FluentCalendar QToolButton {{
    background: transparent; color: {css(palette.text_primary)}; border: none; border-radius: {RADIUS_CONTROL}px;
    padding: 4px 8px; font-weight: 600;
}}
QCalendarWidget#FluentCalendar QToolButton:hover {{ background: {css(palette.subtle_hover)}; }}
QCalendarWidget#FluentCalendar QToolButton::menu-indicator {{ image: none; }}
QCalendarWidget#FluentCalendar QToolButton#qt_calendar_prevmonth {{ qproperty-icon: url("{previous}"); }}
QCalendarWidget#FluentCalendar QToolButton#qt_calendar_nextmonth {{ qproperty-icon: url("{following}"); }}
QCalendarWidget#FluentCalendar QSpinBox {{ background: transparent; color: {css(palette.text_primary)}; border: none; }}
QCalendarWidget#FluentCalendar QAbstractItemView {{
    background: {css(surface)}; alternate-background-color: {css(surface)};
    color: {css(palette.text_primary)}; outline: none;
    selection-background-color: {css(palette.accent)}; selection-color: {css(palette.text_on_accent)};
}}
QCalendarWidget#FluentCalendar QAbstractItemView:disabled {{ color: {css(palette.text_disabled)}; }}
QCalendarWidget#FluentCalendar QMenu {{ background: {css(surface)}; color: {css(palette.text_primary)}; }}
""")
        normal = QTextCharFormat()
        normal.setForeground(mix(surface, palette.text_primary))
        for day in (Qt.DayOfWeek.Saturday, Qt.DayOfWeek.Sunday):
            self.setWeekdayTextFormat(day, normal)
        header = QTextCharFormat()
        header.setForeground(mix(surface, palette.text_secondary))
        header.setFontWeight(QFont.Weight.DemiBold)
        self.setHeaderTextFormat(header)
        for button in self.findChildren(QToolButton):
            button.setCursor(Qt.CursorShape.PointingHandCursor)


class FluentCalendarPicker(FluentPushButton):
    """Button that shows the chosen date and opens a `FluentCalendar` flyout."""

    date_changed = Signal(QDate)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        date: QDate | None = None,
        placeholder: str = "Pick a date",
        display_format: str = "yyyy-MM-dd",
    ) -> None:
        """Create a calendar picker (`date=None` shows the placeholder)."""
        super().__init__(placeholder, parent, icon="calendar")
        self._date = date
        self._placeholder = placeholder
        self._format = display_format
        self._popup = QFrame(
            self, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        )
        self._popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        layout = QVBoxLayout(self._popup)
        layout.setContentsMargins(0, 0, 0, 0)
        self.calendar = FluentCalendar(self._popup)
        layout.addWidget(self.calendar)
        self.calendar.clicked.connect(self._on_pick)
        self.clicked.connect(self.open_popup)
        self._sync_text()

    def date(self) -> QDate | None:
        """Return the chosen date (or `None`)."""
        return self._date

    def open_popup(self) -> None:
        """Show the calendar below the button."""
        if self._date is not None:
            self.calendar.setSelectedDate(self._date)
        self._popup.adjustSize()
        self._popup.move(self.mapToGlobal(QPoint(0, self.height() + SPACE_XS)))
        self._popup.show()

    def set_date(self, date: QDate | None) -> None:
        """Set the chosen date."""
        self._date = date
        self._sync_text()

    def _on_pick(self, date: QDate) -> None:
        self._date = date
        self._popup.hide()
        self._sync_text()
        self.date_changed.emit(date)

    def _sync_text(self) -> None:
        self.setText(self._date.toString(self._format) if self._date is not None else self._placeholder)


class FluentDatePicker(FluentRollerPicker):
    """Day, month, and year rollers."""

    date_changed = Signal(QDate)

    def __init__(self, parent: QWidget | None = None, *, date: QDate | None = None, years: range | None = None) -> None:
        """Create a date picker."""
        today = QDate.currentDate()
        self._years = years or range(today.year() - 100, today.year() + 11)
        days = [f"{day:02d}" for day in range(1, 32)]
        months = [QDate(2000, month, 1).toString("MMMM") for month in range(1, 13)]
        super().__init__(parent, columns=(days, months, [str(year) for year in self._years]), placeholder="Pick a date")
        self.rollers[1].setFixedWidth(_ROLLER_WIDTH * 2)
        self.accepted.connect(self._emit_date)
        self.set_date(date or today)

    def date(self) -> QDate | None:
        """Return the accepted date (clamped to the month length)."""
        if not self._values:
            return None
        year = int(self._values[2])
        month = self.rollers[1].current_index() + 1
        day = min(int(self._values[0]), QDate(year, month, 1).daysInMonth())
        return QDate(year, month, day)

    def format_values(self, values: list[str]) -> str:
        """Show the accepted date as ISO text."""
        self._values = values
        current = self.date()
        return current.toString("yyyy-MM-dd") if current is not None else ""

    def set_date(self, date: QDate) -> None:
        """Select `date`."""
        self.rollers[0].set_current(date.day() - 1)
        self.rollers[1].set_current(date.month() - 1)
        if date.year() in self._years:
            self.rollers[2].set_current(date.year() - self._years.start)
        self._values = [roller.current_text() for roller in self.rollers]
        current = self.date()
        if current is not None:
            self.setText(current.toString("yyyy-MM-dd"))

    def _emit_date(self, _values: list) -> None:
        current = self.date()
        if current is not None:
            self.date_changed.emit(current)


class FluentTimePicker(FluentRollerPicker):
    """Hour and minute rollers (24-hour)."""

    time_changed = Signal(QTime)

    def __init__(self, parent: QWidget | None = None, *, time: QTime | None = None, minute_step: int = 1) -> None:
        """Create a time picker."""
        hours = [f"{hour:02d}" for hour in range(_HOURS)]
        minutes = [f"{minute:02d}" for minute in range(0, _MINUTES, max(1, minute_step))]
        super().__init__(parent, columns=(hours, minutes), placeholder="Pick a time")
        self._separator = ":"
        self._minute_step = max(1, minute_step)
        self.setMinimumWidth(CONTROL_HEIGHT * 4)
        self.accepted.connect(self._emit_time)
        if time is not None:
            self.set_time(time)

    def set_time(self, time: QTime) -> None:
        """Select `time`."""
        self.rollers[0].set_current(time.hour())
        self.rollers[1].set_current(time.minute() // self._minute_step)
        self._values = [self.rollers[0].current_text(), self.rollers[1].current_text()]
        self.setText(self.format_values(self._values))

    def time(self) -> QTime | None:
        """Return the accepted time (or `None`)."""
        if not self._values:
            return None
        return QTime(int(self._values[0]), int(self._values[1]))

    def _emit_time(self, _values: list) -> None:
        current = self.time()
        if current is not None:
            self.time_changed.emit(current)
