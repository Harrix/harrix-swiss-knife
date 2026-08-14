"""Custom Qt widgets for the habits dashboard (Habitify-like UI)."""

from __future__ import annotations

import calendar
from typing import TYPE_CHECKING

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.habits.habit_emojis import default_habit_emoji

if TYPE_CHECKING:
    from collections.abc import Sequence

    from PySide6.QtGui import QMouseEvent, QPaintEvent


# Design tokens from the Habitify-like screenshot TZ
COLOR_PRIMARY = QColor("#3B82F6")
COLOR_TRACK = QColor("#E5E7EB")
COLOR_BG_MUTED = QColor("#F3F4F6")
COLOR_TEXT = QColor("#111827")
COLOR_SUCCESS = QColor("#22C55E")
COLOR_RATE = QColor("#F97316")
COLOR_STREAK = QColor("#EF4444")
MONTHS_IN_YEAR = 12

HABIT_ICON_COLORS: tuple[QColor, ...] = (
    QColor("#FCE7F3"),  # pink
    QColor("#FFEDD5"),  # orange
    QColor("#CCFBF1"),  # teal
    QColor("#DBEAFE"),  # blue
    QColor("#EDE9FE"),  # violet
    QColor("#DCFCE7"),  # green
    QColor("#FEF3C7"),  # amber
    QColor("#E0E7FF"),  # indigo
)


class CheckCircle(QWidget):
    """Clickable day check-in circle (done = blue with checkmark)."""

    clicked = Signal()

    def __init__(self, parent: QWidget | None = None, *, size: int = 22) -> None:  # noqa: D107
        super().__init__(parent)
        self._done = False
        self._size = size
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Toggle check-in")

    def is_done(self) -> bool:
        """Return whether the day is marked completed."""
        return self._done

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Emit clicked on left press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Draw filled check circle or empty gray circle."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        margin = 1.0
        rect = QRectF(margin, margin, self.width() - 2 * margin, self.height() - 2 * margin)

        if self._done:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(COLOR_PRIMARY)
            painter.drawEllipse(rect)

            pen = QPen(QColor("white"), max(1.8, self._size * 0.1))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            # Simple checkmark
            x0 = rect.left() + rect.width() * 0.28
            y0 = rect.top() + rect.height() * 0.52
            x1 = rect.left() + rect.width() * 0.42
            y1 = rect.top() + rect.height() * 0.68
            x2 = rect.left() + rect.width() * 0.72
            y2 = rect.top() + rect.height() * 0.32
            painter.drawLine(QPointF(x0, y0), QPointF(x1, y1))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        else:
            painter.setPen(QPen(COLOR_TRACK, 1.5))
            painter.setBrush(COLOR_BG_MUTED)
            painter.drawEllipse(rect)

    def set_done(self, *, done: bool) -> None:
        """Set completed state."""
        self._done = done
        self.update()


class HabitIconBadge(QWidget):
    """Circular colored badge with a glyph for a habit."""

    def __init__(self, parent: QWidget | None = None, *, size: int = 40) -> None:  # noqa: D107
        super().__init__(parent)
        self._bg = HABIT_ICON_COLORS[0]
        self._glyph = "★"
        self._size = size
        self.setFixedSize(size, size)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Draw colored circle and centered glyph."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._bg)
        painter.drawEllipse(0, 0, self.width(), self.height())

        painter.setPen(COLOR_TEXT)
        font = QFont(self.font())
        font.setPointSize(max(10, int(self._size * 0.35)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._glyph)

    def set_habit(self, habit_id: int, glyph: str | None = None) -> None:
        """Style badge from habit ID and optional stored emoji/glyph."""
        self._bg = habit_accent_color(habit_id)
        self._glyph = glyph or habit_glyph(habit_id)
        self.update()


class HabitRow(QFrame):
    """Selectable habit list row with week check circles."""

    selected = Signal(int)
    day_toggled = Signal(int, int)  # habit_id, day_index 0..6

    def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._habit_id = -1
        self._selected = False
        self.setObjectName("habitRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(64)
        self._apply_style()

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 8, 12, 8)
        root.setSpacing(12)

        self._icon = HabitIconBadge(size=40)
        root.addWidget(self._icon)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self._name_label = QLabel("")
        self._name_label.setStyleSheet("color: #111827; font-size: 14px; font-weight: 700;")
        self._meta_label = QLabel("")
        self._meta_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        text_col.addWidget(self._name_label)
        text_col.addWidget(self._meta_label)
        root.addLayout(text_col, 1)

        self._checks_layout = QHBoxLayout()
        self._checks_layout.setSpacing(6)
        self._checks: list[CheckCircle] = []
        for day_index in range(7):
            circle = CheckCircle(size=22)
            circle.clicked.connect(lambda idx=day_index: self._on_day_clicked(idx))
            self._checks.append(circle)
            self._checks_layout.addWidget(circle)
        root.addLayout(self._checks_layout)

    def habit_id(self) -> int:
        """Return bound habit ID."""
        return self._habit_id

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Select this habit when clicking the row (not only circles)."""
        if event.button() == Qt.MouseButton.LeftButton and self._habit_id >= 0:
            self.selected.emit(self._habit_id)
        super().mousePressEvent(event)

    def set_habit_data(
        self,
        habit_id: int,
        name: str,
        total_days: int,
        streak_days: int,
        week_done: Sequence[bool],
        *,
        selected: bool,
        emoji: str = "",
    ) -> None:
        """Populate row content."""
        self._habit_id = habit_id
        self._selected = selected
        self._icon.set_habit(habit_id, emoji or None)
        self._name_label.setText(name)
        self._meta_label.setText(f"⚡ {total_days} Days   🔥 {streak_days} Days")
        for i, circle in enumerate(self._checks):
            done = week_done[i] if i < len(week_done) else False
            circle.set_done(done=done)
        self._apply_style()

    def _apply_style(self) -> None:
        border = COLOR_PRIMARY.name() if self._selected else "transparent"
        bg = "#EFF6FF" if self._selected else "#FFFFFF"
        self.setStyleSheet(
            f"""
            QFrame#habitRow {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 10px;
            }}
            """
        )

    def _on_day_clicked(self, day_index: int) -> None:
        if self._habit_id >= 0:
            self.day_toggled.emit(self._habit_id, day_index)


class MonthCalendarGrid(QWidget):
    """Month grid of check circles with weekday headers."""

    day_toggled = Signal(str)  # YYYY-MM-DD
    month_changed = Signal(int, int)  # year, month

    def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._year = 0
        self._month = 0
        self._done_dates: set[str] = set()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        header = QHBoxLayout()
        self._prev_btn = QPushButton("←")
        self._next_btn = QPushButton("→")
        for btn in (self._prev_btn, self._next_btn):
            btn.setFixedSize(34, 34)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                """
                QPushButton {
                    background: #F9FAFB;
                    border: 1px solid #D1D5DB;
                    border-radius: 8px;
                    color: #374151;
                    font-size: 18px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: #EFF6FF;
                    border-color: #93C5FD;
                    color: #1D4ED8;
                }
                """
            )
        self._prev_btn.setToolTip("Previous month")
        self._next_btn.setToolTip("Next month")
        self._title = QLabel("")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont(self._title.font())
        title_font.setPointSize(12)
        title_font.setBold(True)
        self._title.setFont(title_font)
        self._title.setStyleSheet("color: #111827;")
        header.addWidget(self._prev_btn)
        header.addWidget(self._title, 1)
        header.addWidget(self._next_btn)
        root.addLayout(header)

        self._prev_btn.clicked.connect(self._on_prev)
        self._next_btn.clicked.connect(self._on_next)

        weekdays = QHBoxLayout()
        for name in ("M", "T", "W", "T", "F", "S", "S"):
            lab = QLabel(name)
            lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
            weekday_font = QFont(lab.font())
            weekday_font.setPointSize(9)
            weekday_font.setBold(True)
            lab.setFont(weekday_font)
            lab.setStyleSheet("color: #6B7280;")
            weekdays.addWidget(lab, 1)
        root.addLayout(weekdays)

        self._grid = QGridLayout()
        self._grid.setHorizontalSpacing(4)
        self._grid.setVerticalSpacing(6)
        for column in range(7):
            self._grid.setColumnStretch(column, 1)
        root.addLayout(self._grid)
        self._day_cells: list[tuple[CheckCircle | None, QLabel, str | None]] = []

    def set_month(self, year: int, month: int, done_dates: set[str]) -> None:
        """Rebuild grid for year/month with completed dates as ``YYYY-MM-DD``."""
        self._year = year
        self._month = month
        self._done_dates = set(done_dates)
        self._title.setText(f"{_month_short(month)} {year}")
        self._rebuild_grid()

    def _clear_grid(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._day_cells.clear()

    def _on_next(self) -> None:
        year, month = self._year, self._month + 1
        if month > MONTHS_IN_YEAR:
            month = 1
            year += 1
        self.month_changed.emit(year, month)

    def _on_prev(self) -> None:
        year, month = self._year, self._month - 1
        if month < 1:
            month = MONTHS_IN_YEAR
            year -= 1
        self.month_changed.emit(year, month)

    def _rebuild_grid(self) -> None:
        self._clear_grid()

        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        weeks = cal.monthdayscalendar(self._year, self._month)
        for row_index, week in enumerate(weeks):
            self._grid.setRowStretch(row_index, 1)
            for column_index, day in enumerate(week):
                cell = QWidget()
                cell.setMinimumHeight(48)
                cell_layout = QVBoxLayout(cell)
                cell_layout.setContentsMargins(0, 0, 0, 0)
                cell_layout.setSpacing(2)
                cell_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                if day == 0:
                    self._grid.addWidget(cell, row_index, column_index)
                    continue

                date_str = f"{self._year:04d}-{self._month:02d}-{day:02d}"
                circle = CheckCircle(size=26)
                circle.set_done(done=date_str in self._done_dates)
                circle.clicked.connect(lambda d=date_str: self.day_toggled.emit(d))
                day_label = QLabel(str(day))
                day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                day_label.setFixedHeight(18)
                day_font = QFont(day_label.font())
                day_font.setPointSize(10)
                day_font.setWeight(QFont.Weight.DemiBold)
                day_label.setFont(day_font)
                day_label.setStyleSheet("color: #4B5563;")
                cell_layout.addWidget(circle, 0, Qt.AlignmentFlag.AlignHCenter)
                cell_layout.addWidget(day_label)
                self._grid.addWidget(cell, row_index, column_index)
                self._day_cells.append((circle, day_label, date_str))


class ProgressRing(QWidget):
    """Circular progress ring showing a 0.0-1.0 completion ratio."""

    def __init__(self, parent: QWidget | None = None, *, size: int = 36) -> None:  # noqa: D107
        super().__init__(parent)
        self._ratio = 0.0
        self._ring_size = size
        self.setFixedSize(size, size)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Draw track ring and progress arc."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen_width = max(3.0, self._ring_size * 0.12)
        margin = pen_width / 2 + 1
        rect = QRectF(margin, margin, self.width() - 2 * margin, self.height() - 2 * margin)

        track_pen = QPen(COLOR_TRACK, pen_width)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawEllipse(rect)

        if self._ratio <= 0:
            return

        progress_pen = QPen(COLOR_PRIMARY, pen_width)
        progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(progress_pen)
        # Qt arcs: 0° at 3 o'clock, counter-clockwise; start at 12 o'clock
        start_angle = 90 * 16
        span_angle = -int(360 * 16 * self._ratio)
        painter.drawArc(rect, start_angle, span_angle)

    def set_ratio(self, ratio: float) -> None:
        """Update completion ratio in ``[0, 1]`` and repaint."""
        self._ratio = max(0.0, min(1.0, ratio))
        self.update()


class StatCard(QFrame):
    """Small metric card: icon, label, value."""

    def __init__(  # noqa: D107
        self,
        title: str,
        icon_text: str,
        icon_color: QColor,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("habitStatCard")
        self.setStyleSheet(
            """
            QFrame#habitStatCard {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
            }
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        top = QHBoxLayout()
        top.setSpacing(6)
        icon = QLabel(icon_text)
        icon.setStyleSheet(f"color: {icon_color.name()}; font-size: 14px; font-weight: 700;")
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        title_label.setWordWrap(True)
        top.addWidget(icon, 0, Qt.AlignmentFlag.AlignTop)
        top.addWidget(title_label, 1)
        layout.addLayout(top)

        self._value_label = QLabel("-")
        self._value_label.setStyleSheet("color: #111827; font-size: 18px; font-weight: 700;")
        layout.addWidget(self._value_label)

    def set_value(self, text: str) -> None:
        """Update the large value text."""
        self._value_label.setText(text)


class WeekDayHeader(QWidget):
    """One day column in the week progress bar: label + progress ring."""

    def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._label = QLabel("-")
        self._label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._label.setStyleSheet("color: #6B7280; font-size: 11px;")
        self._ring = ProgressRing(size=34)
        layout.addWidget(self._label)
        layout.addWidget(self._ring, 0, Qt.AlignmentFlag.AlignHCenter)

    def set_day(self, caption: str, ratio: float, *, is_today: bool) -> None:
        """Update caption, ring, and today highlight."""
        self._label.setText(caption)
        self._ring.set_ratio(ratio)
        if is_today:
            self._label.setStyleSheet("color: #2563EB; font-size: 11px; font-weight: 700;")
        else:
            self._label.setStyleSheet("color: #6B7280; font-size: 11px;")


def habit_accent_color(habit_id: int) -> QColor:
    """Return a soft background color for a habit icon."""
    return HABIT_ICON_COLORS[habit_id % len(HABIT_ICON_COLORS)]


def habit_glyph(habit_id: int) -> str:
    """Return a simple glyph for a habit icon."""
    return default_habit_emoji(habit_id)


def weekday_short(weekday: int) -> str:
    """Return short weekday name for ``date.weekday()`` (Mon=0)."""
    names = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    return names[weekday % 7]


def _month_short(month: int) -> str:
    names = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    if 1 <= month <= MONTHS_IN_YEAR:
        return names[month - 1]
    return str(month)
