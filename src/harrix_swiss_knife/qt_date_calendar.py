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


class SoftCalendarWidget(QCalendarWidget):
    """Month grid with Ant-like chrome around Qt native day table."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build restyled navigation, native day grid, and Today footer."""
        super().__init__(parent)
        self._hover_date: QDate | None = None
        self._grid_view: QTableView | None = None
        self._painted_cells: list[tuple[QRect, QDate]] = []

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

        self._title = QLabel(self)
        title_font = QFont(self._title.font())
        title_font.setBold(True)
        self._title.setFont(title_font)
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(f"color: {SELECTION_TEXT}; background: transparent;")

        self._prev_year = self._nav_button("chevrons-left", "Previous year")
        self._prev_month = self._nav_button("chevron-left", "Previous month")
        self._next_month = self._nav_button("chevron-right", "Next month")
        self._next_year = self._nav_button("chevrons-right", "Next year")
        self._prev_year.clicked.connect(lambda: self._shift_page(years=-1))
        self._prev_month.clicked.connect(lambda: self._shift_page(months=-1))
        self._next_month.clicked.connect(lambda: self._shift_page(months=1))
        self._next_year.clicked.connect(lambda: self._shift_page(years=1))

        header = QWidget(self)
        header.setObjectName("hskCalendarHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 8, 8, 8)
        header_layout.setSpacing(2)
        header_layout.addWidget(self._prev_year)
        header_layout.addWidget(self._prev_month)
        header_layout.addWidget(self._title, stretch=1)
        header_layout.addWidget(self._next_month)
        header_layout.addWidget(self._next_year)

        header_line = _hairline(self)
        self._weekdays = self._build_weekdays()
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
            SoftCalendarWidget QWidget#hskCalendarWeekdays {{
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
        self._tune_grid()
        self._install_hover_tracking()
        parent = self.parentWidget()
        if parent is not None and parent.objectName() == "qt_datetimedit_calendar":
            parent.setFixedSize(self.minimumSizeHint())
        self.setFixedSize(self.minimumSizeHint())

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the fixed Ant-like popup size."""
        return QSize(_POPUP_WIDTH, self._popup_height())

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

    def _on_page_changed(self, *_args: object) -> None:
        self._hover_date = None
        self._refresh_title()
        self._tune_grid()

    def _on_selection_changed(self) -> None:
        self._tune_grid()
        view = self._grid_view
        if view is not None:
            view.viewport().update()

    def _popup_height(self) -> int:
        # header + separators + weekday row + 6 week rows + Today footer
        return 44 + 1 + _WEEKDAY_ROW_HEIGHT + (_CELL_SIZE * _WEEK_ROWS) + 1 + 36

    def _refresh_title(self, *_args: object) -> None:
        page = QDate(self.yearShown(), self.monthShown(), 1)
        self._title.setText(_UI_LOCALE.toString(page, "MMM yyyy"))

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

    def _shift_page(self, *, months: int = 0, years: int = 0) -> None:
        page = QDate(self.yearShown(), self.monthShown(), 1).addMonths(months).addYears(years)
        self.setCurrentPage(page.year(), page.month())

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
