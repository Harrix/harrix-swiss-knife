"""Hover picker for dashboard habit-day circles."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, cast

from PySide6.QtCore import QEvent, QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QCursor, QFont, QGuiApplication, QIntValidator, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.apps.habits.dashboard_widgets import (
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_TEXT,
    COLOR_TRACK,
    habit_day_state,
    paint_habit_day_circle,
    weekday_short,
)

if TYPE_CHECKING:
    from datetime import date

    from PySide6.QtGui import QEnterEvent, QMouseEvent, QPaintEvent

    from harrix_swiss_knife.apps.habits.dashboard_widgets import CheckCircle

HabitDayChoice = int | None | Literal["number"]

_SHOW_DELAY_MS = 180
_HIDE_DELAY_MS = 280
_TRIANGLE_HEIGHT = 8
_TRIANGLE_HALF_WIDTH = 7
_OPTION_CIRCLE_SIZE = 26
_PANEL_MARGIN = 8
_PANEL_EDGE_TO_TRIANGLE = 4
_CHOICE_SPACING = 8
_ANCHOR_GAP = 2
_NUMBER_PREVIEW_VALUE = 2
_NUMBER_MIN = -999999
_NUMBER_MAX = 999999
_DEFAULT_NUMBER = 2
_CHOICE_CAPTION_HEIGHT = 12
_DATE_COLUMN_HEIGHT = _OPTION_CIRCLE_SIZE + 4 + _CHOICE_CAPTION_HEIGHT
_DATE_LINE_HEIGHT = 14
_WEEKDAY_LINE_HEIGHT = 12


class DayChoiceCircle(QWidget):
    """Picker option drawn as a dashboard-style day circle."""

    selected = Signal(object)

    def __init__(self, choice: HabitDayChoice, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._choice = choice
        self.setFixedSize(_OPTION_CIRCLE_SIZE, _OPTION_CIRCLE_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def choice(self) -> HabitDayChoice:
        """Return the value this option represents."""
        return self._choice

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Emit the option when clicked."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit(self._choice)
        super().mousePressEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Draw the option circle."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        margin = 1.0
        rect = QRectF(margin, margin, self.width() - 2 * margin, self.height() - 2 * margin)
        if self._choice == "number":
            paint_habit_day_circle(painter, rect, _NUMBER_PREVIEW_VALUE, font=self.font(), text="#")
            return
        paint_habit_day_circle(painter, rect, self._choice, font=self.font())


class HabitDayPickerPopup(QWidget):
    """Speech-bubble picker shown above a dashboard day circle."""

    _hide_timer: QTimer | None = None
    _instance: HabitDayPickerPopup | None = None
    _pending: CheckCircle | None = None
    _show_timer: QTimer | None = None

    def __init__(self) -> None:  # noqa: D107
        super().__init__(None)
        self._anchor: CheckCircle | None = None
        self._choices: list[HabitDayChoice] = []
        self._triangle_on_top = False
        self._triangle_x = 0.0

        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=True)
        self.setMouseTracking(True)

        self._root_layout = QVBoxLayout(self)
        self._set_panel_margins(triangle_on_top=False)
        self._root_layout.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self._date_column = _PickerDateColumn()
        self._date_column.hide()
        self._choices_page = QWidget()
        self._choices_page.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self._choices_layout = QHBoxLayout(self._choices_page)
        self._choices_layout.setContentsMargins(0, 0, 0, 0)
        self._choices_layout.setSpacing(_CHOICE_SPACING)
        self._choices_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._choices_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self._stepper = HabitNumberStepper()
        self._stepper.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self._stepper.confirmed.connect(self._on_number_confirmed)
        self._stepper.cancelled.connect(self.hide_active)
        self._stepper.hide()
        self._content_row = QHBoxLayout()
        self._content_row.setContentsMargins(0, 0, 0, 0)
        self._content_row.setSpacing(_CHOICE_SPACING)
        self._content_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self._content_row.addWidget(self._date_column, 0, Qt.AlignmentFlag.AlignVCenter)
        self._content_row.addWidget(self._choices_page, 0, Qt.AlignmentFlag.AlignCenter)
        self._root_layout.addLayout(self._content_row)
        self._reposition_timer = QTimer(self)
        self._reposition_timer.setSingleShot(True)
        self._reposition_timer.timeout.connect(self._update_geometry)

    def attach(self, circle: CheckCircle) -> None:
        """Rebuild choices for ``circle`` and point the bubble at it."""
        if self._anchor is not None and self._anchor is not circle:
            self._anchor.destroyed.disconnect(self._on_anchor_destroyed)
        if self._anchor is not circle:
            circle.destroyed.connect(self._on_anchor_destroyed)
        self._anchor = circle
        self._choices = habit_day_choices(allows_number=circle.allows_number())
        self._update_date_labels()
        self._rebuild_choices()
        self.show_choices_page()
        self._update_geometry()
        self._schedule_geometry_update()

    def cancel_reposition(self) -> None:
        """Cancel a pending geometry pass after hide."""
        self._reposition_timer.stop()

    def choices(self) -> list[HabitDayChoice]:
        """Return the choices currently offered in the picker."""
        return list(self._choices)

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Keep the picker open while the pointer is over it."""
        self.request_keep()
        super().enterEvent(event)

    @classmethod
    def hide_active(cls) -> None:
        """Hide the open picker immediately."""
        cls._cancel_timers()
        cls._set_pending(None)
        if cls._instance is not None:
            cls._instance.cancel_reposition()
            cls._instance.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=True)
            cls._instance.hide()
            cls._instance.show_choices_page()

    def is_attached_to(self, circle: CheckCircle) -> bool:
        """Return whether the picker is currently bound to ``circle``."""
        return self._anchor is circle

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        """Hide after the pointer leaves the picker."""
        self.request_hide()
        super().leaveEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Draw the rounded bubble and the pointer triangle."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = self._bubble_path()
        shadow = QPainterPath(path)
        shadow.translate(0, 1)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(17, 24, 39, 28))
        painter.drawPath(shadow)
        painter.setPen(QPen(COLOR_TRACK, 1))
        painter.setBrush(QColor("white"))
        painter.drawPath(path)

    def refresh_geometry(self) -> None:
        """Place the bubble above the attached circle after it is shown."""
        self._update_geometry()
        self._schedule_geometry_update()

    @classmethod
    def request_hide(cls) -> None:
        """Hide the picker after a short delay."""
        cls._ensure_timers()
        if cls._show_timer is not None:
            cls._show_timer.stop()
        cls._set_pending(None)
        if cls._hide_timer is not None:
            cls._hide_timer.start(_HIDE_DELAY_MS)

    @classmethod
    def request_keep(cls) -> None:
        """Cancel a pending hide while the pointer stays on the picker."""
        if cls._hide_timer is not None:
            cls._hide_timer.stop()

    @classmethod
    def request_show(cls, circle: CheckCircle) -> None:
        """Show or retarget the picker for ``circle``."""
        if not cls._should_show_for(circle):
            return
        cls._ensure_timers()
        if cls._hide_timer is not None:
            cls._hide_timer.stop()
        if cls._instance is not None and cls._instance.isVisible() and cls._instance.is_attached_to(circle):
            return
        if cls._instance is not None and cls._instance.isVisible():
            cls._instance.attach(circle)
            return
        cls._set_pending(circle)
        if cls._show_timer is not None:
            cls._show_timer.start(_SHOW_DELAY_MS)

    def show_choices_page(self) -> None:
        """Show the day-state circles instead of the number stepper."""
        self._show_page(self._choices_page)

    @classmethod
    def show_for(cls, circle: CheckCircle) -> HabitDayPickerPopup:
        """Show the picker immediately. Intended for tests and direct calls."""
        cls._cancel_timers()
        if cls._instance is None:
            cls._instance = cls()
        cls._instance.attach(circle)
        cls._instance.show()
        cls._instance.raise_()
        cls._instance.refresh_geometry()
        return cls._instance

    def _anchor_edges(self) -> tuple[int, int, int]:
        """Return global center X, top, and bottom of the hovered circle."""
        if self._anchor is None:
            return (0, 0, 0)
        top_left = self._anchor.mapToGlobal(self._anchor.rect().topLeft())
        return (
            top_left.x() + self._anchor.width() // 2,
            top_left.y(),
            top_left.y() + self._anchor.height(),
        )

    def _apply_choice(self, choice: object) -> None:
        typed = cast("HabitDayChoice", choice)
        if typed == "number":
            self._show_number_stepper()
            return
        if self._anchor is not None:
            self._anchor.value_set.emit(typed)
        self.hide_active()

    def _bubble_path(self) -> QPainterPath:
        width = float(self.width())
        height = float(self.height())
        radius = 12.0
        triangle_h = float(_TRIANGLE_HEIGHT)
        half = float(_TRIANGLE_HALF_WIDTH)
        tip_x = min(max(self._triangle_x, radius + half), width - radius - half)

        if self._triangle_on_top:
            body = QRectF(0.5, triangle_h, width - 1.0, height - triangle_h - 0.5)
            tip = QPointF(tip_x, 1.0)
            left = QPointF(tip_x - half, triangle_h + 1.0)
            right = QPointF(tip_x + half, triangle_h + 1.0)
        else:
            body = QRectF(0.5, 0.5, width - 1.0, height - triangle_h - 0.5)
            tip = QPointF(tip_x, height - 1.0)
            left = QPointF(tip_x - half, height - triangle_h - 1.0)
            right = QPointF(tip_x + half, height - triangle_h - 1.0)

        path = QPainterPath()
        path.addRoundedRect(body, radius, radius)
        triangle = QPainterPath()
        triangle.moveTo(left)
        triangle.lineTo(tip)
        triangle.lineTo(right)
        triangle.closeSubpath()
        return path.united(triangle)

    @classmethod
    def _cancel_timers(cls) -> None:
        if cls._show_timer is not None:
            cls._show_timer.stop()
        if cls._hide_timer is not None:
            cls._hide_timer.stop()

    def _clear_layout(self, layout: QLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            child = item.layout()
            if child is not None:
                self._clear_layout(child)

    @classmethod
    def _ensure_timers(cls) -> None:
        if cls._show_timer is None:
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(cls._on_show_timeout)
            cls._show_timer = timer
        if cls._hide_timer is None:
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(cls.hide_active)
            cls._hide_timer = timer

    def _fit_to_content(self) -> None:
        """Shrink the bubble to the visible page instead of the hidden stepper."""
        self._choices_page.adjustSize()
        self._stepper.adjustSize()
        self.updateGeometry()
        self.adjustSize()

    def _on_anchor_destroyed(self) -> None:
        self._anchor = None
        self.hide_active()

    def _on_comment_clicked(self) -> None:
        if self._anchor is not None:
            self._anchor.comment_requested.emit()
        self.hide_active()

    def _on_number_confirmed(self, value: int) -> None:
        if self._anchor is not None:
            self._anchor.value_set.emit(value)
        self.hide_active()

    @classmethod
    def _on_pending_destroyed(cls) -> None:
        cls._pending = None
        if cls._show_timer is not None:
            cls._show_timer.stop()

    @classmethod
    def _on_show_timeout(cls) -> None:
        circle = cls._pending
        cls._set_pending(None)
        if circle is None or not cls._should_show_for(circle):
            return
        cls.show_for(circle)

    @classmethod
    def _set_pending(cls, circle: CheckCircle | None) -> None:
        previous = cls._pending
        if previous is circle:
            return
        if previous is not None:
            try:
                previous.destroyed.disconnect(cls._on_pending_destroyed)
            except (RuntimeError, TypeError):
                pass
        cls._pending = circle
        if circle is not None:
            circle.destroyed.connect(cls._on_pending_destroyed)

    @classmethod
    def _should_show_for(cls, circle: CheckCircle) -> bool:
        """Return whether the pointer is really over an editable circle with no popup."""
        if not circle.is_editable() or not circle.isVisible():
            return False
        if QApplication.activePopupWidget() is not None:
            return False
        if QGuiApplication.mouseButtons() & Qt.MouseButton.RightButton:
            return False
        return pointer_is_over_widget(circle)

    def _rebuild_choices(self) -> None:
        self._clear_layout(self._choices_layout)
        for choice in self._choices:
            column = QVBoxLayout()
            column.setContentsMargins(0, 0, 0, 0)
            column.setSpacing(4)
            column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            circle = DayChoiceCircle(choice)
            circle.selected.connect(self._apply_choice)
            caption = QLabel(habit_day_choice_caption(choice))
            caption.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            caption.setStyleSheet("color: #6B7280; font-size: 9px;")
            column.addWidget(circle, 0, Qt.AlignmentFlag.AlignHCenter)
            column.addWidget(caption, 0, Qt.AlignmentFlag.AlignHCenter)
            self._choices_layout.addLayout(column)
        comment_column = QVBoxLayout()
        comment_column.setContentsMargins(0, 0, 0, 0)
        comment_column.setSpacing(4)
        comment_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        comment_button = QPushButton("💬")
        comment_button.setFixedSize(_OPTION_CIRCLE_SIZE, _OPTION_CIRCLE_SIZE)
        comment_button.setCursor(Qt.CursorShape.PointingHandCursor)
        comment_button.setToolTip("Comment")
        comment_button.setStyleSheet(
            """
            QPushButton {
                background: #FFFBEB;
                border: 1px solid #F59E0B;
                border-radius: 13px;
                font-size: 13px;
            }
            QPushButton:hover { background: #FEF3C7; }
            """
        )
        comment_button.clicked.connect(self._on_comment_clicked)
        comment_caption = QLabel("Note")
        comment_caption.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        comment_caption.setStyleSheet("color: #6B7280; font-size: 9px;")
        comment_column.addWidget(comment_button, 0, Qt.AlignmentFlag.AlignHCenter)
        comment_column.addWidget(comment_caption, 0, Qt.AlignmentFlag.AlignHCenter)
        self._choices_layout.addLayout(comment_column)

    def _schedule_geometry_update(self) -> None:
        """Reposition after Qt finishes layout of the just-shown bubble."""
        self._reposition_timer.start(0)

    def _set_panel_margins(self, *, triangle_on_top: bool) -> None:
        extra = _TRIANGLE_HEIGHT
        if triangle_on_top:
            self._root_layout.setContentsMargins(
                _PANEL_MARGIN,
                _PANEL_MARGIN + extra,
                _PANEL_MARGIN,
                _PANEL_EDGE_TO_TRIANGLE,
            )
            return
        self._root_layout.setContentsMargins(
            _PANEL_MARGIN,
            _PANEL_MARGIN,
            _PANEL_MARGIN,
            _PANEL_EDGE_TO_TRIANGLE + extra,
        )

    def _show_number_stepper(self) -> None:
        current = self._anchor.value() if self._anchor is not None else None
        initial = current if current is not None and habit_day_state(current) == "number" else _DEFAULT_NUMBER
        self._stepper.set_value(initial)
        self._show_page(self._stepper)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.adjustSize()
        self._update_geometry()
        self.activateWindow()

    def _show_page(self, page: QWidget) -> None:
        """Show ``page`` and keep only that page in the layout."""
        for child in (self._choices_page, self._stepper):
            if child is page:
                continue
            child.hide()
            self._content_row.removeWidget(child)
        if self._content_row.indexOf(page) < 0:
            self._content_row.addWidget(page, 0, Qt.AlignmentFlag.AlignCenter)
        page.show()
        self._fit_to_content()

    def _update_date_labels(self) -> None:
        day = self._anchor.day() if self._anchor is not None else None
        if day is None:
            self._date_column.hide()
            return
        self._date_column.set_day(day)
        self._date_column.show()

    def _update_geometry(self) -> None:
        if self._anchor is None:
            return
        self._fit_to_content()
        center_x, circle_top, circle_bottom = self._anchor_edges()
        screen = QGuiApplication.screenAt(self._anchor.mapToGlobal(self._anchor.rect().center()))
        if screen is None:
            screen = QGuiApplication.primaryScreen()
        area = screen.availableGeometry() if screen is not None else self.rect()
        width, height = self._window_size()
        x = center_x - width // 2
        x = max(area.left() + 4, min(x, area.right() - width - 4))
        y_above = circle_top - height - _ANCHOR_GAP
        self._triangle_on_top = y_above < area.top() + 4
        self._set_panel_margins(triangle_on_top=self._triangle_on_top)
        self._fit_to_content()
        width, height = self._window_size()
        x = center_x - width // 2
        x = max(area.left() + 4, min(x, area.right() - width - 4))
        y = circle_bottom + _ANCHOR_GAP if self._triangle_on_top else circle_top - height - _ANCHOR_GAP
        self.setGeometry(x, y, width, height)
        self._triangle_x = float(center_x - x)
        self.update()

    def _window_size(self) -> tuple[int, int]:
        """Return the bubble size from the current page, not a stale window size."""
        hint = self.sizeHint()
        width = hint.width() if hint.isValid() and hint.width() > 0 else self.width()
        height = hint.height() if hint.isValid() and hint.height() > 0 else self.height()
        return (width, height)


class HabitNumberStepper(QWidget):
    """Compact plus/minus editor for a numeric habit value."""

    cancelled = Signal()
    confirmed = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._value = _DEFAULT_NUMBER

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(8)
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._minus = _RoundStepButton("-", COLOR_TRACK, COLOR_TEXT)
        self._plus = _RoundStepButton("+", COLOR_SUCCESS, QColor("white"))
        self._edit = QLineEdit()
        self._edit.setValidator(QIntValidator(_NUMBER_MIN, _NUMBER_MAX, self._edit))
        self._edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._edit.setFixedSize(72, 32)
        self._edit.setStyleSheet(
            """
            QLineEdit {
                background: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                color: #111827;
                font-size: 16px;
                font-weight: 700;
            }
            """
        )
        self._minus.clicked.connect(self._on_minus)
        self._plus.clicked.connect(self._on_plus)
        self._edit.returnPressed.connect(self._on_confirm)
        row.addWidget(self._minus)
        row.addWidget(self._edit)
        row.addWidget(self._plus)
        root.addLayout(row)

        self._set_btn = QPushButton("Set")
        self._set_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._set_btn.setFixedHeight(28)
        self._set_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {COLOR_PRIMARY.name()};
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 12px;
                font-weight: 700;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: #2563EB;
            }}
            """
        )
        self._set_btn.clicked.connect(self._on_confirm)
        root.addWidget(self._set_btn, 0, Qt.AlignmentFlag.AlignHCenter)

    def set_value(self, value: int) -> None:
        """Show ``value`` in the editor."""
        self._value = max(_NUMBER_MIN, min(_NUMBER_MAX, value))
        self._edit.setText(str(self._value))
        self._edit.setFocus()
        self._edit.selectAll()

    def _on_confirm(self) -> None:
        text = self._edit.text().strip()
        if not text:
            self.cancelled.emit()
            return
        try:
            value = int(text)
        except ValueError:
            return
        self.confirmed.emit(max(_NUMBER_MIN, min(_NUMBER_MAX, value)))

    def _on_minus(self) -> None:
        self.set_value(self._read_value() - 1)

    def _on_plus(self) -> None:
        self.set_value(self._read_value() + 1)

    def _read_value(self) -> int:
        try:
            return int(self._edit.text().strip())
        except ValueError:
            return self._value


class _PickerDateColumn(QWidget):
    """Compact ``30.08`` / ``Sun`` stack for the hover picker."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(_DATE_COLUMN_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._date_label = QLabel()
        self._date_label.setObjectName("pickerDateLabel")
        self._date_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._date_label.setFixedHeight(_DATE_LINE_HEIGHT)
        self._date_label.setStyleSheet("color: #111827; font-size: 11px; font-weight: 700;")
        self._weekday_label = QLabel()
        self._weekday_label.setObjectName("pickerWeekdayLabel")
        self._weekday_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._weekday_label.setFixedHeight(_WEEKDAY_LINE_HEIGHT)
        self._weekday_label.setStyleSheet("color: #6B7280; font-size: 9px;")
        layout.addStretch(1)
        layout.addWidget(self._date_label, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._weekday_label, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)

    def set_day(self, day: date) -> None:
        """Show ``DD.MM`` and the short weekday for ``day``."""
        date_text, weekday_text = habit_picker_date_parts(day)
        self._date_label.setText(date_text)
        self._weekday_label.setText(weekday_text)


class _RoundStepButton(QWidget):
    """Circular plus/minus control for the number stepper."""

    clicked = Signal()

    def __init__(self, glyph: str, fill: QColor, ink: QColor, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._glyph = glyph
        self._fill = fill
        self._ink = ink
        self.setFixedSize(28, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Emit clicked on left press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Draw a filled circle with a centered glyph."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._fill)
        painter.drawEllipse(1, 1, self.width() - 2, self.height() - 2)
        painter.setPen(self._ink)
        font = QFont(self.font())
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect(), int(Qt.AlignmentFlag.AlignCenter), self._glyph)


def habit_day_choice_caption(choice: HabitDayChoice) -> str:
    """Return a short label for a picker choice."""
    if choice is None:
        return "No record"
    if choice == "number":
        return "Number"
    if choice == 0:
        return "Not done"
    if choice == 1:
        return "Done"
    return "Number"


def habit_day_choices(*, allows_number: bool) -> list[HabitDayChoice]:
    """Return every day state the picker can set.

    Boolean habits get No record, Not done, and Done. Counted habits also get Number.

    """
    choices: list[HabitDayChoice] = [None, 0, 1]
    if allows_number:
        choices.append("number")
    return choices


def habit_picker_date_parts(day: date) -> tuple[str, str]:
    """Return compact ``DD.MM`` and English weekday for the hover picker."""
    return (f"{day.day:02d}.{day.month:02d}", weekday_short(day.weekday()))


def pointer_is_over_widget(widget: QWidget) -> bool:
    """Return whether the cursor is inside ``widget`` in local coordinates."""
    return widget.rect().contains(widget.mapFromGlobal(QCursor.pos()))
