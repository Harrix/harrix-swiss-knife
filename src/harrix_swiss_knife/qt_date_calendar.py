"""Ant Design-inspired calendar popup for `QDateEdit`.

Keeps Qt's native month grid (so columns stay aligned) and restyles the
navigation chrome, selection painting, and Today footer. Uses Harrix soft-blue
tokens for accents.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, QEvent, QLocale, QObject, QPoint, QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QCalendarWidget,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSpinBox,
    QStyleFactory,
    QTableView,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.common.ui_chrome import (
    MUTED_TEXT,
    SELECTION_BG,
    SELECTION_BORDER,
    SELECTION_HOVER,
    SELECTION_TEXT,
)
from harrix_swiss_knife.qt_lucide_icon import create_lucide_icon

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtGui import QShowEvent

_PROP_APPLIED = "hskDateCalendar"
_NAV_ICON_SIZE = 16
_CELL_SIZE = 36
_WEEKDAY_ROW_HEIGHT = 28
_WEEK_ROWS = 6
_WEEK_COLUMNS = 7
_POPUP_WIDTH = 294  # 7 * 36 + side padding
_DAY_OUTSIDE = "#bfbfbf"
_PANEL_BORDER = "#e8e8e8"
_HEADER_SEP = "#f0f0f0"
_UI_LOCALE = QLocale(QLocale.Language.English)
_YEAR_PANEL_COLUMNS = 3
_YEAR_PANEL_ROWS = 4
_DECADE_LENGTH = 10
_PANEL_DAY = "day"
_PANEL_MONTH_PICK = "month_pick"
_PANEL_YEAR = "year"
_MONTHS_IN_YEAR = 12


class SoftCalendarWidget(QCalendarWidget):
    """Month grid with Ant-like chrome around Qt native day table."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build restyled navigation, native day grid, and Today footer."""
        super().__init__(parent)
        self._hover_date: QDate | None = None
        self._grid_view: QTableView | None = None
        self._painted_cells: list[tuple[QRect, QDate]] = []
        self._panel_mode = _PANEL_DAY
        self._decade_start = decade_start(QDate.currentDate().year())
        self._month_pick_year = QDate.currentDate().year()
        self._year_buttons: list[QPushButton] = []
        self._month_buttons: list[QPushButton] = []

        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        # Own weekday labels — QHeaderView collapses/overlaps after selection on Windows.
        self.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.NoHorizontalHeader)
        self.setGridVisible(False)
        self.setFirstDayOfWeek(Qt.DayOfWeek.Sunday)
        self.setLocale(_UI_LOCALE)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        fusion = QStyleFactory.create("Fusion")
        if fusion is not None:
            self.setStyle(fusion)

        self.setNavigationBarVisible(False)
        self._detach_default_nav_bar()

        title_font = QFont(self.font())
        title_font.setBold(True)
        self._title_month = QPushButton(self)
        self._title_month.setObjectName("hskCalendarMonth")
        self._title_month.setCursor(Qt.CursorShape.PointingHandCursor)
        self._title_month.setFlat(True)
        self._title_month.setFont(title_font)
        self._title_month.setStyleSheet(_title_chip_qss("hskCalendarMonth"))
        self._title_month.setToolTip("Choose month")
        self._title_month.clicked.connect(self._on_title_month_clicked)

        self._title_year = QPushButton(self)
        self._title_year.setObjectName("hskCalendarYear")
        self._title_year.setCursor(Qt.CursorShape.PointingHandCursor)
        self._title_year.setFlat(True)
        self._title_year.setFont(title_font)
        self._title_year.setStyleSheet(_title_chip_qss("hskCalendarYear"))
        self._title_year.clicked.connect(self._on_title_year_clicked)
        self._title = self._title_year

        self._prev_year = self._nav_button("chevrons-left", "Previous year")
        self._prev_month = self._nav_button("chevron-left", "Previous month")
        self._next_month = self._nav_button("chevron-right", "Next month")
        self._next_year = self._nav_button("chevrons-right", "Next year")
        self._prev_year.clicked.connect(self._on_prev_jump)
        self._prev_month.clicked.connect(lambda: self._shift_page(months=-1))
        self._next_month.clicked.connect(lambda: self._shift_page(months=1))
        self._next_year.clicked.connect(self._on_next_jump)

        header = QWidget(self)
        header.setObjectName("hskCalendarHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 8, 8, 8)
        header_layout.setSpacing(2)
        title_row = QWidget(self)
        title_row.setObjectName("hskCalendarTitle")
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        title_layout.addStretch(1)
        title_layout.addWidget(self._title_month)
        title_layout.addWidget(self._title_year)
        title_layout.addStretch(1)

        header_layout.addWidget(self._prev_year)
        header_layout.addWidget(self._prev_month)
        header_layout.addWidget(title_row, stretch=1)
        header_layout.addWidget(self._next_month)
        header_layout.addWidget(self._next_year)

        header_line = _hairline(self)
        self._weekdays = self._build_weekdays()
        self._month_panel = self._build_month_panel()
        self._year_panel = self._build_year_panel()
        footer_line = _hairline(self)

        self._today_button = QPushButton("Today", self)
        self._today_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._today_button.setFlat(True)
        self._today_button.setStyleSheet(
            f"QPushButton {{ color: {SELECTION_BORDER}; border: none; background: transparent;"
            " padding: 8px 12px; font-weight: 500; }"
            f"QPushButton:hover {{ color: {SELECTION_TEXT}; background: {SELECTION_HOVER}; }}"
        )
        self._today_button.clicked.connect(self._go_today)

        footer = QWidget(self)
        footer.setObjectName("hskCalendarFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self._today_button)
        footer_layout.addStretch(1)

        root = self.layout()
        if isinstance(root, QVBoxLayout):
            root.setContentsMargins(8, 0, 8, 0)
            root.setSpacing(0)
            root.insertWidget(0, header)
            root.insertWidget(1, header_line)
            root.insertWidget(2, self._weekdays)
            root.insertWidget(3, self._month_panel)
            root.insertWidget(4, self._year_panel)
            root.addWidget(footer_line)
            root.addWidget(footer)

        self.setStyleSheet(
            f"""
            SoftCalendarWidget {{
                background: #ffffff;
                border: 1px solid {_PANEL_BORDER};
                border-radius: 8px;
            }}
            SoftCalendarWidget QWidget#hskCalendarHeader,
            SoftCalendarWidget QWidget#hskCalendarFooter,
            SoftCalendarWidget QWidget#hskCalendarWeekdays,
            SoftCalendarWidget QWidget#hskCalendarYearPanel,
            SoftCalendarWidget QWidget#hskCalendarMonthPanel,
            SoftCalendarWidget QWidget#hskCalendarTitle {{
                background: #ffffff;
                border: none;
            }}
            SoftCalendarWidget QAbstractItemView {{
                background: #ffffff;
                outline: none;
                border: none;
                selection-background-color: transparent;
                selection-color: {SELECTION_TEXT};
            }}
            """.strip()
        )

        self._month_panel.hide()
        self._year_panel.hide()
        self.setMinimumSize(_POPUP_WIDTH, self._popup_height())
        self.currentPageChanged.connect(self._on_page_changed)
        self.selectionChanged.connect(self._on_selection_changed)
        self._refresh_title()
        self._tune_grid()
        self._install_hover_tracking()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Track hovered day cells for soft-blue hover fill."""
        view = self._grid_view
        viewport = view.viewport() if view is not None else None
        if view is not None and watched is viewport:
            event_type = event.type()
            if event_type == QEvent.Type.Paint:
                self._painted_cells = []
            elif event_type == QEvent.Type.MouseMove and isinstance(event, QMouseEvent):
                pos = viewport.mapFromGlobal(event.globalPosition().toPoint())
                self._set_hover_date(self._date_at_viewport_pos(pos))
            elif event_type == QEvent.Type.Leave:
                self._set_hover_date(None)
        return super().eventFilter(watched, event)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Keep the QDateEdit popup wide enough for seven day columns."""
        return QSize(_POPUP_WIDTH, self._popup_height())

    def paintCell(self, painter: QPainter, rect: QRect, date: QDate) -> None:  # noqa: N802
        """Draw Ant-like day cells: hover, outline selection, soft today, muted outsiders."""
        self._painted_cells.append((QRect(rect), date))
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.fillRect(rect, QColor("#ffffff"))

        selected = date == self.selectedDate()
        today = date == QDate.currentDate()
        hovered = self._hover_date is not None and date == self._hover_date
        in_month = date.month() == self.monthShown() and date.year() == self.yearShown()
        cell = rect.adjusted(3, 3, -3, -3)

        if selected:
            painter.setPen(QPen(QColor(SELECTION_BORDER), 1.5))
            painter.setBrush(QColor("#ffffff"))
            painter.drawRoundedRect(cell, 4, 4)
            text_color = QColor(SELECTION_TEXT)
        elif today:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(SELECTION_BG))
            painter.drawRoundedRect(cell, 4, 4)
            text_color = QColor(SELECTION_BORDER)
        elif hovered:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(SELECTION_HOVER))
            painter.drawRoundedRect(cell, 4, 4)
            text_color = QColor(SELECTION_TEXT if in_month else _DAY_OUTSIDE)
        elif in_month:
            text_color = QColor(SELECTION_TEXT)
        else:
            text_color = QColor(_DAY_OUTSIDE)

        painter.setPen(text_color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(date.day()))
        painter.restore()

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Re-apply equal column metrics when the popup opens."""
        super().showEvent(event)
        self._show_day_panel()
        self._tune_grid()
        self._install_hover_tracking()
        parent = self.parentWidget()
        if parent is not None and parent.objectName() == "qt_datetimedit_calendar":
            parent.setFixedSize(self.minimumSizeHint())
        self.setFixedSize(self.minimumSizeHint())

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the fixed Ant-like popup size."""
        return QSize(_POPUP_WIDTH, self._popup_height())

    def _build_choice_grid(self, object_name: str, on_clicked: Callable[[], None]) -> tuple[QWidget, list[QPushButton]]:
        panel = QWidget(self)
        panel.setObjectName(object_name)
        panel.setFixedHeight(_WEEKDAY_ROW_HEIGHT + _CELL_SIZE * _WEEK_ROWS)
        grid = QGridLayout(panel)
        grid.setContentsMargins(8, 12, 8, 12)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(12)
        buttons: list[QPushButton] = []
        for index in range(_YEAR_PANEL_ROWS * _YEAR_PANEL_COLUMNS):
            button = QPushButton(panel)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFlat(True)
            button.setMinimumHeight(40)
            row, column = divmod(index, _YEAR_PANEL_COLUMNS)
            grid.addWidget(button, row, column)
            button.clicked.connect(on_clicked)
            buttons.append(button)
        return panel, buttons

    def _build_month_panel(self) -> QWidget:
        panel, self._month_buttons = self._build_choice_grid("hskCalendarMonthPanel", self._on_month_button_clicked)
        return panel

    def _build_weekdays(self) -> QWidget:
        row = QWidget(self)
        row.setObjectName("hskCalendarWeekdays")
        row.setFixedHeight(_WEEKDAY_ROW_HEIGHT)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 4, 0, 2)
        layout.setSpacing(0)
        first = Qt.DayOfWeek.Sunday.value
        for offset in range(_WEEK_COLUMNS):
            day = ((first - 1 + offset) % _WEEK_COLUMNS) + 1
            label = QLabel(_UI_LOCALE.dayName(day, QLocale.FormatType.ShortFormat))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(f"color: {MUTED_TEXT}; background: transparent; border: none;")
            layout.addWidget(label, stretch=1)
        return row

    def _build_year_panel(self) -> QWidget:
        panel, self._year_buttons = self._build_choice_grid("hskCalendarYearPanel", self._on_year_button_clicked)
        return panel

    def _date_at(self, row: int, column: int) -> QDate | None:
        if row < 0 or column < 0 or row >= _WEEK_ROWS or column >= _WEEK_COLUMNS:
            return None
        first = QDate(self.yearShown(), self.monthShown(), 1)
        start_dow = self.firstDayOfWeek().value
        offset = (first.dayOfWeek() - start_dow) % _WEEK_COLUMNS
        return first.addDays(row * _WEEK_COLUMNS + column - offset)

    def _date_at_viewport_pos(self, pos: QPoint) -> QDate | None:
        for cell_rect, date in self._painted_cells:
            if cell_rect.contains(pos):
                return date
        view = self._grid_view
        if view is None:
            return None
        index = view.indexAt(pos)
        if not index.isValid():
            return None
        return self._date_at(index.row(), index.column())

    def _detach_default_nav_bar(self) -> None:
        nav = self.findChild(QWidget, "qt_calendar_navigationbar")
        if nav is None:
            return
        root = self.layout()
        if isinstance(root, QVBoxLayout):
            root.removeWidget(nav)
        nav.hide()
        nav.setParent(self)
        for spin in nav.findChildren(QSpinBox):
            spin.setEnabled(False)

    def _go_today(self) -> None:
        today = QDate.currentDate()
        self.setCurrentPage(today.year(), today.month())
        self.setSelectedDate(today)
        self._show_day_panel()
        self.activated.emit(today)

    def _install_hover_tracking(self) -> None:
        view = self.findChild(QTableView, "qt_calendar_calendarview")
        if view is None:
            return
        if self._grid_view is not None and self._grid_view is not view:
            old_viewport = self._grid_view.viewport()
            if old_viewport is not None:
                old_viewport.removeEventFilter(self)
        self._grid_view = view
        view.setMouseTracking(True)
        viewport = view.viewport()
        if viewport is not None:
            viewport.setMouseTracking(True)
            viewport.installEventFilter(self)

    def _nav_button(self, icon_name: str, tooltip: str) -> QToolButton:
        button = QToolButton(self)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setAutoRaise(True)
        button.setToolTip(tooltip)
        button.setIcon(create_lucide_icon(icon_name, _NAV_ICON_SIZE, color=MUTED_TEXT))
        button.setIconSize(QSize(_NAV_ICON_SIZE, _NAV_ICON_SIZE))
        button.setFixedSize(28, 28)
        button.setStyleSheet(
            "QToolButton { border: none; border-radius: 4px; background: transparent; padding: 4px; }"
            f"QToolButton:hover {{ background: {SELECTION_HOVER}; }}"
        )
        return button

    def _on_month_button_clicked(self) -> None:
        button = self.sender()
        if not isinstance(button, QPushButton):
            return
        month = button.property("hskMonth")
        if not isinstance(month, int):
            return
        self.setCurrentPage(self._month_pick_year, month)
        self._show_day_panel()

    def _on_next_jump(self) -> None:
        if self._panel_mode == _PANEL_YEAR:
            self._shift_decade(1)
            return
        if self._panel_mode == _PANEL_MONTH_PICK:
            self._shift_month_pick_year(1)
            return
        self._shift_page(years=1)

    def _on_page_changed(self, *_args: object) -> None:
        self._hover_date = None
        self._refresh_title()
        self._tune_grid()

    def _on_prev_jump(self) -> None:
        if self._panel_mode == _PANEL_YEAR:
            self._shift_decade(-1)
            return
        if self._panel_mode == _PANEL_MONTH_PICK:
            self._shift_month_pick_year(-1)
            return
        self._shift_page(years=-1)

    def _on_selection_changed(self) -> None:
        self._tune_grid()
        view = self._grid_view
        if view is not None:
            view.viewport().update()

    def _on_title_month_clicked(self) -> None:
        if self._panel_mode == _PANEL_DAY:
            self._show_month_pick_panel()

    def _on_title_year_clicked(self) -> None:
        if self._panel_mode == _PANEL_YEAR:
            self._show_day_panel()
            return
        self._show_year_panel()

    def _on_year_button_clicked(self) -> None:
        button = self.sender()
        if not isinstance(button, QPushButton):
            return
        year = button.property("hskYear")
        if not isinstance(year, int):
            return
        self.setCurrentPage(year, self.monthShown())
        self._show_month_pick_panel()

    def _popup_height(self) -> int:
        # header + separators + weekday row + 6 week rows + Today footer
        return 44 + 1 + _WEEKDAY_ROW_HEIGHT + (_CELL_SIZE * _WEEK_ROWS) + 1 + 36

    def _rebuild_month_cells(self) -> None:
        today = QDate.currentDate()
        for month in range(1, _MONTHS_IN_YEAR + 1):
            button = self._month_buttons[month - 1]
            label = _UI_LOCALE.toString(QDate(2000, month, 1), "MMM")
            selected = month == self.monthShown() and self._month_pick_year == self.yearShown()
            is_current = month == today.month() and self._month_pick_year == today.year()
            button.setText(label)
            button.setProperty("hskMonth", month)
            button.setStyleSheet(_year_cell_qss(muted=False, selected=selected, current=is_current))

    def _rebuild_year_cells(self) -> None:
        _start, years = decade_panel_years(self._decade_start)
        selected_year = self.yearShown()
        current_year = QDate.currentDate().year()
        for button, year in zip(self._year_buttons, years, strict=True):
            muted = year < self._decade_start or year >= self._decade_start + _DECADE_LENGTH
            selected = year == selected_year
            is_current = year == current_year
            button.setText(str(year))
            button.setProperty("hskYear", year)
            button.setStyleSheet(_year_cell_qss(muted=muted, selected=selected, current=is_current))

    def _refresh_title(self, *_args: object) -> None:
        page = QDate(self.yearShown(), self.monthShown(), 1)
        if self._panel_mode == _PANEL_YEAR:
            start, _years = decade_panel_years(self._decade_start)
            self._title_month.hide()
            self._title_year.setText(f"{start}-{start + _DECADE_LENGTH - 1}")
            self._title_year.setToolTip("")
            self._title_year.setCursor(Qt.CursorShape.ArrowCursor)
            return
        if self._panel_mode == _PANEL_MONTH_PICK:
            self._title_month.hide()
            self._title_year.setText(str(self._month_pick_year))
            self._title_year.setToolTip("Choose year")
            self._title_year.setCursor(Qt.CursorShape.PointingHandCursor)
            return
        self._title_month.show()
        self._title_month.setText(_UI_LOCALE.toString(page, "MMM"))
        self._title_year.setText(_UI_LOCALE.toString(page, "yyyy"))
        self._title_year.setToolTip("Choose year")
        self._title_year.setCursor(Qt.CursorShape.PointingHandCursor)

    def _set_hover_date(self, date: QDate | None) -> None:
        if date == self._hover_date:
            return
        self._hover_date = date
        view = self._grid_view
        if view is None:
            return
        viewport = view.viewport()
        if viewport is not None:
            # Full viewport update is cheap for a 7x6 grid and avoids stale cells.
            viewport.update()

    def _shift_decade(self, steps: int) -> None:
        self._decade_start += steps * _DECADE_LENGTH
        self._rebuild_year_cells()
        self._refresh_title()

    def _shift_month_pick_year(self, steps: int) -> None:
        self._month_pick_year += steps
        self._rebuild_month_cells()
        self._refresh_title()

    def _shift_page(self, *, months: int = 0, years: int = 0) -> None:
        page = QDate(self.yearShown(), self.monthShown(), 1).addMonths(months).addYears(years)
        self.setCurrentPage(page.year(), page.month())

    def _show_day_grid(self, *, visible: bool) -> None:
        self._weekdays.setVisible(visible)
        view = self.findChild(QTableView, "qt_calendar_calendarview")
        if view is not None:
            view.setVisible(visible)
        self._prev_month.setVisible(visible)
        self._next_month.setVisible(visible)

    def _show_day_panel(self) -> None:
        self._panel_mode = _PANEL_DAY
        self._month_panel.hide()
        self._year_panel.hide()
        self._show_day_grid(visible=True)
        self._prev_year.setToolTip("Previous year")
        self._next_year.setToolTip("Next year")
        self._refresh_title()
        self._tune_grid()

    def _show_month_pick_panel(self) -> None:
        self._panel_mode = _PANEL_MONTH_PICK
        self._month_pick_year = self.yearShown()
        self._year_panel.hide()
        self._show_day_grid(visible=False)
        self._month_panel.show()
        self._prev_year.setToolTip("Previous year")
        self._next_year.setToolTip("Next year")
        self._rebuild_month_cells()
        self._refresh_title()

    def _show_year_panel(self) -> None:
        year = self._month_pick_year if self._panel_mode == _PANEL_MONTH_PICK else self.yearShown()
        self._panel_mode = _PANEL_YEAR
        self._decade_start = decade_start(year)
        self._month_panel.hide()
        self._show_day_grid(visible=False)
        self._year_panel.show()
        self._prev_year.setToolTip("Previous decade")
        self._next_year.setToolTip("Next decade")
        self._rebuild_year_cells()
        self._refresh_title()

    def _tune_grid(self) -> None:
        view = self.findChild(QTableView, "qt_calendar_calendarview")
        if view is None:
            return
        self._grid_view = view
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        header = view.horizontalHeader()
        vheader = view.verticalHeader()
        if header is not None:
            header.hide()
            header.setMinimumHeight(0)
            header.setMaximumHeight(0)
            header.setFixedHeight(0)
        if vheader is not None:
            vheader.hide()
            vheader.setMinimumSectionSize(_CELL_SIZE)
            vheader.setDefaultSectionSize(_CELL_SIZE)
            vheader.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
            for row in range(_WEEK_ROWS):
                vheader.resizeSection(row, _CELL_SIZE)
        # Stretch columns across the content width (popup margins are on the outer layout).
        h_header = view.horizontalHeader()
        if h_header is not None:
            h_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            h_header.setMinimumSectionSize(_CELL_SIZE)
            h_header.setDefaultSectionSize(_CELL_SIZE)
        view.setViewportMargins(0, 0, 0, 0)
        view.updateGeometries()
        view.setFixedHeight(_CELL_SIZE * _WEEK_ROWS)


class _DateEditCalendarFilter(QObject):
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if isinstance(watched, QDateEdit) and event.type() in {
            QEvent.Type.Show,
            QEvent.Type.Polish,
            QEvent.Type.WinIdChange,
        }:
            apply_date_calendar_popup(watched)
        return super().eventFilter(watched, event)


def apply_date_calendar_popup(date_edit: QDateEdit) -> None:
    """Replace the popup calendar on `date_edit` with the soft Ant-like widget."""
    if date_edit.property(_PROP_APPLIED) is True:
        return
    if not date_edit.calendarPopup():
        return
    calendar = SoftCalendarWidget(date_edit)
    date_edit.setCalendarWidget(calendar)
    date_edit.setProperty(_PROP_APPLIED, True)  # noqa: FBT003
    popup = calendar.parentWidget()
    if popup is not None and popup.objectName() == "qt_datetimedit_calendar":
        popup.setMinimumSize(calendar.minimumSizeHint())


def decade_panel_years(year: int) -> tuple[int, list[int]]:
    """Return `(decade_start, twelve years)` for an Ant-like year panel."""
    start = decade_start(year)
    years = [start - 1, *range(start, start + _DECADE_LENGTH), start + _DECADE_LENGTH]
    return start, years


def decade_start(year: int) -> int:
    """Return the first year of the decade that contains `year`."""
    return year - (year % _DECADE_LENGTH)


def install_date_calendar_popups(app: QApplication) -> None:
    """Style every `QDateEdit` calendar popup that uses `setCalendarPopup(True)`."""
    if app.property("_hskDateCalendarFilter") is not None:
        return
    filtr = _DateEditCalendarFilter(app)
    app.installEventFilter(filtr)
    app.setProperty("_hskDateCalendarFilter", filtr)
    for widget in app.allWidgets():
        if isinstance(widget, QDateEdit):
            apply_date_calendar_popup(widget)


def _hairline(parent: QWidget) -> QFrame:
    line = QFrame(parent)
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFixedHeight(1)
    line.setStyleSheet(f"background-color: {_HEADER_SEP}; border: none; color: {_HEADER_SEP};")
    return line


def _title_chip_qss(object_name: str) -> str:
    """Return hover chip styles for the month or year header button."""
    return (
        f"QPushButton#{object_name} {{ color: {SELECTION_TEXT}; background: transparent;"
        " border: none; border-radius: 4px; padding: 2px 6px; font-weight: 700; }"
        f"QPushButton#{object_name}:hover {{ background: {SELECTION_HOVER}; color: {SELECTION_BORDER}; }}"
    )


def _year_cell_qss(*, muted: bool, selected: bool, current: bool) -> str:
    color = _DAY_OUTSIDE if muted else SELECTION_TEXT
    background = "transparent"
    border = "1px solid transparent"
    if selected:
        border = f"1px solid {SELECTION_BORDER}"
        background = "#ffffff"
    elif current:
        background = SELECTION_BG
        color = SELECTION_BORDER
    return (
        "QPushButton {"
        f" color: {color}; background: {background}; border: {border};"
        " border-radius: 4px; padding: 8px 4px; font-size: 13px;"
        "}"
        f"QPushButton:hover {{ background: {SELECTION_HOVER}; color: {SELECTION_TEXT}; }}"
    )
