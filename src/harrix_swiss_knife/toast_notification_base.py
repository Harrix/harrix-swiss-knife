"""Toast notification implementation for PySide6 applications.

This module provides a base class for creating toast-style notifications
that can be displayed temporarily on screen with customizable messages.

"""

from __future__ import annotations

import itertools
from html import escape
from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QEventLoop, QObject, QPoint, QRect, QSize, Qt
from PySide6.QtGui import QCloseEvent, QColor, QIcon, QMouseEvent, QPainter, QPaintEvent, QPixmap, QShowEvent
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from PySide6.QtGui import QResizeEvent

_COLLAPSE_SYMBOL = "\u2212"
_EXPAND_SYMBOL = "\u25a1"

DEFAULT_ACTION_BUTTON_SIDE = 24
COMPACT_ACTION_BUTTON_SIDE = 18
ACTION_BUTTON_GAP = 4
ACTION_BUTTON_MARGIN_DEFAULT = 8
ACTION_BUTTON_MARGIN_COMPACT = 4
ACTION_BUTTON_TEXT_GAP = 10
LABEL_PAD_TOP_DEFAULT = 16
LABEL_PAD_BOTTOM_DEFAULT = 15
LABEL_PAD_LEFT_DEFAULT = 24
LABEL_PAD_TOP_COMPACT = 10
LABEL_PAD_BOTTOM_COMPACT = 8
LABEL_PAD_LEFT_COMPACT = 14
CANCEL_HINT_FONT_SIZE = "10pt"
CANCEL_HINT_FONT_SIZE_COMPACT = "8pt"

STACK_GAP = 8
SCREEN_MARGIN = 20
TOAST_BG = QColor(40, 40, 40, 230)
TOAST_RADIUS_DEFAULT = 10
TOAST_RADIUS_COMPACT = 8

DEFAULT_ACTION_BUTTON_STYLE = (
    "QPushButton {"
    "background-color: transparent;"
    "border: none;"
    "padding: 0px;"
    "margin: 0px;"
    "}"
    "QPushButton:hover {"
    "background-color: rgba(255, 255, 255, 40);"
    "border-radius: 4px;"
    "}"
)

COMPACT_ACTION_BUTTON_STYLE = (
    "QPushButton {"
    "background-color: transparent;"
    "border: none;"
    "padding: 0px;"
    "margin: 0px;"
    "}"
    "QPushButton:hover {"
    "background-color: rgba(255, 255, 255, 40);"
    "border-radius: 3px;"
    "}"
)

_stack_seq = itertools.count()
_active_toasts: set[ToastNotificationBase] = set()


class ToastNotificationBase(QDialog):
    """Base class for toast notifications.

    This class provides a foundation for creating toast-style notification dialogs
    that appear temporarily on screen. It creates a semi-transparent, frameless
    dialog with a message displayed in the center.

    Attributes:

    - `message` (`str`): The text to be displayed in the notification.
    - `label` (`QLabel`): The label widget that displays the message.

    """

    def __init__(self, message: str, parent: QWidget | None = None) -> None:
        """Initialize the toast notification with the specified message and parent widget.

        Args:

        - `message` (`str`): The message to display in the toast notification.
        - `parent` (`QWidget | None`): The parent widget of the notification. Defaults to `None`.

        """
        super().__init__(parent)

        # Window settings
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Message display
        self.message = message
        self.label = QLabel(self.message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Clicks must reach the dialog so dragging and double-click pin work.
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._apply_default_style()

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Dragging tracking variables
        self.dragging = False
        self.drag_position = QPoint()
        self._user_moved = False

        # Pinned state (bottom-right near system tray)
        self._is_pinned = False
        self.stack_order = next(_stack_seq)

        # Enable mouse tracking for drag operations
        self.setMouseTracking(True)

        # Set cursor to indicate draggable window
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        self._collapse_button = QPushButton(self)
        self._collapse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._collapse_button.setFlat(True)
        self._collapse_button.setStyleSheet(DEFAULT_ACTION_BUTTON_STYLE)
        self._apply_collapse_button_icon(compact=False)
        self._collapse_button.setToolTip("Collapse")
        self._collapse_button.clicked.connect(self._toggle_pinned)
        self._position_collapse_button()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Unregister from the stack and restack remaining toasts of the same pin group."""
        was_pinned = self.is_pinned
        _active_toasts.discard(self)
        super().closeEvent(event)
        self.restack_group(pinned=was_pinned)

    @property
    def is_pinned(self) -> bool:
        """Whether the toast uses the compact bottom-right layout."""
        return self._is_pinned

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Toggle pinned (compact, bottom-right) and expanded (large, centered) layout.

        First double-click pins the notification near the system tray with compact styling.
        A second double-click restores the default size and centers it on the primary screen.

        Args:

        - `event` (`QMouseEvent`): The mouse event triggering the double-click action.

        """
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self._toggle_pinned()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle the mouse move event to update the position of the notification during dragging.

        Args:

        - `event` (`QMouseEvent`): The mouse event triggering the move action.

        """
        if event.buttons() & Qt.MouseButton.LeftButton and self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            self._user_moved = True
            event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle the mouse press event to initiate dragging of the notification.

        Args:

        - `event` (`QMouseEvent`): The mouse event triggering the press action.

        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)  # Change cursor to indicate active dragging
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Handle the mouse release event to conclude the dragging of the notification.

        Args:

        - `event` (`QMouseEvent`): The mouse event triggering the release action.

        """
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)  # Restore cursor to indicate draggable state
            event.accept()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Fill the frameless window so Windows layered blits keep the dark plate."""
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(TOAST_BG)
        radius = TOAST_RADIUS_COMPACT if self._is_pinned else TOAST_RADIUS_DEFAULT
        painter.drawRoundedRect(self.rect(), radius, radius)

    def present(self, *, activate: bool = True, pinned: bool | None = None) -> None:
        """Size, position via the toast stack, and show on top.

        Args:

        - `activate` (`bool`): When `True`, steal window focus. Defaults to `True`.
        - `pinned` (`bool | None`): When set, show collapsed (`True`) or expanded (`False`)
          before the first paint. Defaults to `None` (keep the current layout).

        """
        if pinned is not None:
            self._is_pinned = pinned
            if pinned:
                self._apply_compact_style()
            else:
                self._apply_default_style()
        self.adjustSize()
        self.show()
        self.raise_()
        if activate:
            self.activateWindow()
        self._position_collapse_button()

    def pump_events(self) -> None:
        """Process queued Qt events while keeping this toast clickable and draggable.

        Use during long UI-thread work instead of
        `QApplication.processEvents(ExcludeUserInputEvents)`, which updates the
        toast text but drops mouse input.

        """
        process_events_allowing_widget(self)

    def reposition_action_buttons(self) -> None:
        """Place collapse (and subclass) action buttons after a move or resize."""
        self._position_collapse_button()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reposition the collapse button when the toast is resized."""
        super().resizeEvent(event)
        self._position_collapse_button()

    @classmethod
    def restack_group(cls, *, pinned: bool) -> None:
        """Reposition all visible toasts in the given pin group."""
        toasts = cls.stack_members(pinned=pinned)
        if not toasts:
            return

        screen = QApplication.primaryScreen()
        if screen is None:
            return

        area = screen.availableGeometry()
        for toast in toasts:
            toast.adjustSize()

        points = compute_toast_stack_positions(
            [toast.size() for toast in toasts],
            area=area,
            pinned=pinned,
        )
        for toast, point in zip(toasts, points, strict=True):
            toast.move(point)
            toast.reposition_action_buttons()

        toasts[-1].raise_()

    def set_pinned(self, *, pinned: bool) -> None:
        """Switch between compact (pinned) and expanded layout."""
        if self._is_pinned == pinned:
            return
        self._user_moved = False
        self._is_pinned = pinned
        if pinned:
            self._apply_compact_style()
        else:
            self._apply_default_style()
        self.adjustSize()
        self.restack_group(pinned=False)
        self.restack_group(pinned=True)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Register in the active stack and restack the pin group."""
        super().showEvent(event)
        _active_toasts.add(self)
        self.restack_group(pinned=self.is_pinned)

    @classmethod
    def stack_members(cls, *, pinned: bool) -> list[ToastNotificationBase]:
        """Return visible toasts in a pin group that still follow automatic stacking."""
        return [
            toast
            for toast in sorted(_active_toasts, key=lambda item: item.stack_order)
            if toast.isVisible() and toast.is_pinned == pinned and not toast.user_moved
        ]

    @property
    def user_moved(self) -> bool:
        """Whether the user dragged this toast away from the automatic stack."""
        return self._user_moved

    def _action_button_margin(self) -> int:
        """Return the inset of corner action buttons from the label edges."""
        return action_button_edge_margin(compact=self._is_pinned)

    def _action_button_side(self) -> int:
        """Return the action-button side length for the current pin state."""
        return COMPACT_ACTION_BUTTON_SIDE if self._is_pinned else DEFAULT_ACTION_BUTTON_SIDE

    def _apply_collapse_button_icon(self, *, compact: bool) -> None:
        side = COMPACT_ACTION_BUTTON_SIDE if compact else DEFAULT_ACTION_BUTTON_SIDE
        symbol = _EXPAND_SYMBOL if self._is_pinned else _COLLAPSE_SYMBOL
        self._collapse_button.setFixedSize(side, side)
        self._collapse_button.setIconSize(QSize(side, side))
        self._collapse_button.setIcon(make_action_icon(side, symbol))
        self._collapse_button.setToolTip("Expand" if self._is_pinned else "Collapse")

    def _apply_compact_style(self) -> None:
        """Apply compact styling with reduced font size for pinned notifications."""
        self.label.setStyleSheet(
            "background-color: transparent;"
            "color: white;"
            f"padding: {toast_label_padding(compact=True)};"
            "border-radius: 8px;"
            "font-size: 10pt;"
            "font-weight: bold;",
        )
        if hasattr(self, "_collapse_button"):
            self._collapse_button.setStyleSheet(COMPACT_ACTION_BUTTON_STYLE)
            self._apply_collapse_button_icon(compact=True)
            self._position_collapse_button()

    def _apply_default_style(self) -> None:
        """Apply default styling for expanded, centered notifications."""
        self.label.setStyleSheet(
            "background-color: transparent;"
            "color: white;"
            f"padding: {toast_label_padding(compact=False)};"
            "border-radius: 10px;"
            "font-size: 16pt;"
            "font-weight: bold;",
        )
        if hasattr(self, "_collapse_button"):
            self._collapse_button.setStyleSheet(DEFAULT_ACTION_BUTTON_STYLE)
            self._apply_collapse_button_icon(compact=False)
            self._position_collapse_button()

    def _position_collapse_button(self) -> None:
        """Place the collapse button near the top-right of the message label."""
        if not hasattr(self, "_collapse_button"):
            return
        label_geom = self.label.geometry()
        side = self._action_button_side()
        margin = self._action_button_margin()
        right_offset = self._trailing_controls_width()
        self._collapse_button.move(
            label_geom.x() + label_geom.width() - side - margin - right_offset,
            label_geom.y() + margin,
        )
        self._collapse_button.raise_()

    def _toggle_pinned(self) -> None:
        """Toggle between pinned compact layout and expanded centered layout."""
        self.set_pinned(pinned=not self._is_pinned)

    def _trailing_controls_width(self) -> int:
        """Width reserved to the right of the collapse button for subclass controls."""
        return 0


class _AllowWidgetInputFilter(QObject):
    """Block user input except for one widget tree (typically a toast)."""

    def __init__(self, root: QWidget) -> None:
        super().__init__(root)
        self._root = root

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Swallow user input that is not aimed at the allowed widget."""
        if event.type() not in _USER_INPUT_EVENT_TYPES:
            return False
        return not event_targets_widget(watched, self._root)


def action_button_edge_margin(*, compact: bool) -> int:
    """Return the inset of corner action buttons from the toast label edges."""
    return ACTION_BUTTON_MARGIN_COMPACT if compact else ACTION_BUTTON_MARGIN_DEFAULT


def compute_toast_stack_positions(
    sizes: list[QSize],
    *,
    area: QRect,
    pinned: bool,
    gap: int = STACK_GAP,
    margin: int = SCREEN_MARGIN,
) -> list[QPoint]:
    """Return top-left points for toasts ordered oldest → newest.

    Newest sits at the home anchor (screen center, or bottom-right when pinned).
    Older toasts stack upward with `gap` when they fit above the available top
    margin; otherwise they share the home position (overlap).

    """
    if not sizes:
        return []

    points: list[QPoint] = [QPoint() for _ in sizes]
    newest_index = len(sizes) - 1
    newest_home = _toast_home_point(area, sizes[newest_index], pinned=pinned, margin=margin)
    points[newest_index] = newest_home
    stack_top = newest_home.y()

    for index in range(newest_index - 1, -1, -1):
        size = sizes[index]
        home = _toast_home_point(area, size, pinned=pinned, margin=margin)
        proposed_y = stack_top - gap - size.height()
        if proposed_y >= area.y() + margin:
            points[index] = QPoint(home.x(), proposed_y)
            stack_top = proposed_y
        else:
            points[index] = home

    return points


def event_targets_widget(watched: QObject, root: QWidget) -> bool:
    """Return whether `watched` belongs to `root` or its native window."""
    root_window = root.windowHandle()
    current: QObject | None = watched
    while current is not None:
        if current is root or current is root_window:
            return True
        current = current.parent()
    return False


def format_toast_cancel_hint_html(body: str, hint: str, *, compact: bool = False) -> str:
    """Return rich text with `hint` on a smaller line under `body`.

    Args:

    - `body` (`str`): Main toast lines, separated by newlines.
    - `hint` (`str`): Cancel hint such as `Press Esc to cancel`.
    - `compact` (`bool`): Use the compact hint size. Defaults to `False`.

    Returns:

    - `str`: HTML for a `QLabel` with `RichText` format.

    """
    size = CANCEL_HINT_FONT_SIZE_COMPACT if compact else CANCEL_HINT_FONT_SIZE
    lines = "<br>".join(escape(part) for part in body.split("\n"))
    return f'{lines}<br><span style="font-size: {size}; font-weight: normal;">{escape(hint)}</span>'


def make_action_icon(side: int, symbol: str) -> QIcon:
    """Render a centered action symbol for the given button side length."""
    pixmap = QPixmap(side, side)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    font = painter.font()
    font.setPixelSize(max(10, int(side * 0.72)))
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor(255, 255, 255, 200))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, symbol)
    painter.end()
    return QIcon(pixmap)


def process_events_allowing_widget(widget: QWidget | None) -> None:
    """Pump the event loop so `widget` stays interactive during long UI-thread work.

    The rest of the UI still receives paint and timer events, but mouse and
    keyboard input is delivered only to `widget` and its descendants. That keeps
    a toast draggable without letting the owner window re-enter catalog load
    handlers.

    """
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        return
    if widget is None:
        app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
        return
    event_filter = _AllowWidgetInputFilter(widget)
    app.installEventFilter(event_filter)
    try:
        app.processEvents()
    finally:
        app.removeEventFilter(event_filter)


def toast_action_buttons_reserved_width(*, compact: bool, extra_buttons: int = 1) -> int:
    """Return right-side space reserved for collapse plus extra action buttons.

    Args:

    - `compact` (`bool`): Pinned compact layout.
    - `extra_buttons` (`int`): Buttons to the right of collapse, typically close.
      Defaults to `1`.

    Returns:

    - `int`: Width in pixels from the label's right edge to the text content.

    """
    side = COMPACT_ACTION_BUTTON_SIDE if compact else DEFAULT_ACTION_BUTTON_SIDE
    count = 1 + max(0, extra_buttons)
    return (
        action_button_edge_margin(compact=compact)
        + count * side
        + (count - 1) * ACTION_BUTTON_GAP
        + ACTION_BUTTON_TEXT_GAP
    )


def toast_label_padding(*, compact: bool, bottom: int | None = None) -> str:
    """Return CSS padding that keeps toast text clear of corner action buttons.

    Args:

    - `compact` (`bool`): Pinned compact layout.
    - `bottom` (`int | None`): Override bottom padding. Defaults to the layout default.

    Returns:

    - `str`: CSS padding such as `16px 70px 15px 24px`.

    """
    if compact:
        top = LABEL_PAD_TOP_COMPACT
        left = LABEL_PAD_LEFT_COMPACT
        bottom_px = LABEL_PAD_BOTTOM_COMPACT if bottom is None else bottom
    else:
        top = LABEL_PAD_TOP_DEFAULT
        left = LABEL_PAD_LEFT_DEFAULT
        bottom_px = LABEL_PAD_BOTTOM_DEFAULT if bottom is None else bottom
    right = toast_action_buttons_reserved_width(compact=compact)
    return f"{top}px {right}px {bottom_px}px {left}px"


def _toast_home_point(area: QRect, size: QSize, *, pinned: bool, margin: int) -> QPoint:
    if pinned:
        return QPoint(
            area.x() + area.width() - size.width() - margin,
            area.y() + area.height() - size.height() - margin,
        )
    return QPoint(
        area.x() + (area.width() - size.width()) // 2,
        area.y() + (area.height() - size.height()) // 2,
    )


_USER_INPUT_EVENT_TYPES = frozenset(
    {
        QEvent.Type.MouseButtonPress,
        QEvent.Type.MouseButtonRelease,
        QEvent.Type.MouseButtonDblClick,
        QEvent.Type.MouseMove,
        QEvent.Type.NonClientAreaMouseButtonPress,
        QEvent.Type.NonClientAreaMouseButtonRelease,
        QEvent.Type.NonClientAreaMouseButtonDblClick,
        QEvent.Type.NonClientAreaMouseMove,
        QEvent.Type.Wheel,
        QEvent.Type.KeyPress,
        QEvent.Type.KeyRelease,
        QEvent.Type.Shortcut,
        QEvent.Type.ShortcutOverride,
        QEvent.Type.ContextMenu,
        QEvent.Type.HoverEnter,
        QEvent.Type.HoverLeave,
        QEvent.Type.HoverMove,
        QEvent.Type.Enter,
        QEvent.Type.Leave,
        QEvent.Type.FocusIn,
        QEvent.Type.DragEnter,
        QEvent.Type.DragMove,
        QEvent.Type.Drop,
    },
)
