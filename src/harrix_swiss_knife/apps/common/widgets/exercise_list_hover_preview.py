"""Hover preview popup for exercise icons in list and table views."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QEvent, QObject, QPoint, QSize, Qt, QTimer
from PySide6.QtGui import QCursor, QGuiApplication, QMouseEvent
from PySide6.QtWidgets import QAbstractItemView, QFrame, QLabel, QVBoxLayout
from shiboken6 import isValid

from harrix_swiss_knife.apps.common.avif_manager import AvifLabelKey
from harrix_swiss_knife.apps.common.delegates.name_local_list_delegate import NameLocalListDelegate

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import QWidget

    from harrix_swiss_knife.apps.common.avif_manager import AvifManager

_HOVER_DELAY_MS = 450
_PREVIEW_EDGE = 280
_CURSOR_OFFSET = QPoint(18, 18)


class ExerciseListHoverPreview(QObject):
    """Show an enlarged animated AVIF preview after dwelling on an exercise icon."""

    def __init__(
        self,
        list_view: QAbstractItemView,
        *,
        get_avif_manager: Callable[[], AvifManager | None],
        preview_size: QSize | None = None,
        parent: QObject | None = None,
        exercise_at: Callable[[QPoint], str | None] | None = None,
    ) -> None:
        """Attach hover tracking to `list_view`.

        Args:

        - `list_view` (`QAbstractItemView`): Exercise list or other view with icons.
        - `get_avif_manager` (`Callable`): Returns the current `AvifManager` (may be `None`).
        - `preview_size` (`QSize | None`): Popup size. Defaults to `_PREVIEW_EDGE` square.
        - `parent` (`QObject | None`): Qt parent. Prefer a longer-lived owner than `list_view`.
        - `exercise_at` (`Callable | None`): Viewport-position resolver. Defaults to list-icon hit-test.

        """
        # Prefer an owner that outlives the list (e.g. main window) so teardown is ordered.
        super().__init__(parent if parent is not None else list_view)
        self._get_avif_manager = get_avif_manager
        self._preview_size = preview_size or QSize(_PREVIEW_EDGE, _PREVIEW_EDGE)
        self._pending_exercise: str | None = None
        self._shown_exercise: str | None = None
        self._detached = False
        self._targets: list[_HoverTarget] = []

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._show_preview)

        self._popup = QFrame(
            None,
            Qt.WindowType.ToolTip
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self._popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=True)
        self._popup.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        self._popup.setStyleSheet(
            """
            QFrame {
                background: white;
                border: 1px solid #bdbdbd;
                border-radius: 6px;
            }
            """
        )
        popup_layout = QVBoxLayout(self._popup)
        popup_layout.setContentsMargins(4, 4, 4, 4)
        self._label = QLabel(self._popup)
        self._label.setFixedSize(self._preview_size)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet("background-color: white; border: none;")
        popup_layout.addWidget(self._label)

        resolver = exercise_at if exercise_at is not None else (lambda pos: exercise_at_list_icon(list_view, pos))
        self.add_view(list_view, resolver)

    def add_view(
        self,
        view: QAbstractItemView,
        exercise_at: Callable[[QPoint], str | None],
    ) -> None:
        """Track icon hover on another view that shares this popup.

        Args:

        - `view` (`QAbstractItemView`): Extra list or table to watch.
        - `exercise_at` (`Callable[[QPoint], str | None]`): Viewport-position resolver.

        """
        if self._detached:
            return
        viewport = view.viewport()
        view.setMouseTracking(True)
        viewport.setMouseTracking(True)
        viewport.installEventFilter(self)
        view.installEventFilter(self)
        view.destroyed.connect(self.detach)
        viewport.destroyed.connect(self.detach)
        for scroll in (view.verticalScrollBar(), view.horizontalScrollBar()):
            if scroll is not None:
                scroll.valueChanged.connect(self.hide_preview)
        self._targets.append(_HoverTarget(view, viewport, exercise_at))

    def detach(self, *_args: object) -> None:
        """Remove filters and hide popup; safe during widget teardown."""
        if self._detached:
            return
        self._detached = True
        self._timer.stop()
        self._pending_exercise = None
        self._shown_exercise = None
        self._stop_animation()
        if isValid(self._popup):
            self._popup.hide()
            self._popup.close()

        for target in self._targets:
            if isValid(target.viewport):
                target.viewport.removeEventFilter(self)
            if isValid(target.view):
                target.view.removeEventFilter(self)
        self._targets.clear()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Track icon hover, dwell delay, click hide, and leave/scroll hide."""
        if self._detached or not self._any_view_alive():
            return False

        target = self._target_for(obj)
        if target is None:
            return False

        event_type = event.type()
        viewport = target.viewport if isValid(target.viewport) else None

        if viewport is not None and obj is viewport and event_type == QEvent.Type.MouseButtonPress:
            # Avoid racing a decode with the click that selects the exercise.
            self.hide_preview()
            return False

        if viewport is not None and obj is viewport and event_type == QEvent.Type.MouseMove:
            self._on_mouse_move(target, cast("QMouseEvent", event).position().toPoint())
            return False

        if viewport is not None and obj is viewport and event_type in {QEvent.Type.Leave, QEvent.Type.Wheel}:
            self.hide_preview()
            return False

        if obj is target.view and event_type == QEvent.Type.Leave:
            self.hide_preview()
            return False

        return super().eventFilter(obj, event)

    def hide_preview(self) -> None:
        """Stop animation and hide the popup."""
        if self._detached:
            return
        self._timer.stop()
        self._pending_exercise = None
        self._shown_exercise = None
        self._stop_animation()
        if isValid(self._popup):
            self._popup.hide()

    def _any_view_alive(self) -> bool:
        return any(target.is_alive() for target in self._targets)

    def _move_popup_to_cursor(self) -> None:
        if not isValid(self._popup):
            return
        global_pos = QCursor.pos() + _CURSOR_OFFSET
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            popup_size = self._popup.sizeHint()
            x = min(global_pos.x(), available.right() - popup_size.width())
            y = min(global_pos.y(), available.bottom() - popup_size.height())
            x = max(x, available.left())
            y = max(y, available.top())
            global_pos = QPoint(x, y)
        self._popup.move(global_pos)

    def _on_mouse_move(self, target: _HoverTarget, pos: QPoint) -> None:
        if not target.is_alive():
            if not self._any_view_alive():
                self.detach()
            return

        exercise = target.exercise_at(pos)
        if exercise is None:
            self.hide_preview()
            return

        if exercise == self._shown_exercise and isValid(self._popup) and self._popup.isVisible():
            self._move_popup_to_cursor()
            return

        if exercise == self._pending_exercise and self._timer.isActive():
            return

        self._timer.stop()
        self._stop_animation()
        if isValid(self._popup):
            self._popup.hide()
        self._shown_exercise = None
        self._pending_exercise = exercise
        self._timer.start(_HOVER_DELAY_MS)

    def _show_preview(self) -> None:
        if self._detached or not self._any_view_alive():
            return
        exercise = self._pending_exercise
        manager = self._get_avif_manager()
        if not exercise or manager is None or not isValid(self._popup) or not isValid(self._label):
            return
        avif_path = manager.get_exercise_avif_path(exercise)
        if avif_path is None:
            return

        self._label.setFixedSize(self._preview_size)
        manager.load_exercise_avif(exercise, self._label, AvifLabelKey.LIST_HOVER)
        pixmap = self._label.pixmap()
        if pixmap is None or pixmap.isNull():
            self._stop_animation()
            return

        self._popup.adjustSize()
        self._move_popup_to_cursor()
        self._popup.show()
        self._shown_exercise = exercise

    def _stop_animation(self) -> None:
        manager = self._get_avif_manager()
        if manager is not None:
            manager.stop_animation(AvifLabelKey.LIST_HOVER)
        if isValid(self._label):
            self._label.clear()

    def _target_for(self, obj: QObject) -> _HoverTarget | None:
        for target in self._targets:
            if obj is target.viewport or obj is target.view:
                return target
        return None


class _HoverTarget:
    """One tracked item view and its viewport-position resolver."""

    def __init__(
        self,
        view: QAbstractItemView,
        viewport: QWidget,
        exercise_at: Callable[[QPoint], str | None],
    ) -> None:
        """Store one view, its viewport, and the hover resolver."""
        self.view = view
        self.viewport = viewport
        self.exercise_at = exercise_at

    def is_alive(self) -> bool:
        """Return whether the view and viewport are still valid Qt objects."""
        return isValid(self.view) and isValid(self.viewport)


def exercise_at_list_icon(list_view: QAbstractItemView, pos: QPoint) -> str | None:
    """Return the exercise name when `pos` is over a list-row icon.

    Args:

    - `list_view` (`QAbstractItemView`): List whose icons use `NameLocalListDelegate`.
    - `pos` (`QPoint`): Pointer position in viewport coordinates.

    Returns:

    - `str | None`: Exercise name from `UserRole`, or `None` when not on an icon.

    """
    if not isValid(list_view):
        return None
    index = list_view.indexAt(pos)
    if not index.isValid():
        return None

    exercise = index.data(Qt.ItemDataRole.UserRole)
    if not exercise:
        return None

    icon = index.data(Qt.ItemDataRole.DecorationRole)
    if icon is None or (hasattr(icon, "isNull") and icon.isNull()):
        return None

    item_rect = list_view.visualRect(index)
    icon_rect = NameLocalListDelegate.list_decoration_rect(
        item_rect,
        list_view.iconSize(),
        has_icon=True,
    )
    if not icon_rect.contains(pos):
        return None

    name = str(exercise).strip()
    return name or None


def exercise_at_table_image(
    table_view: QAbstractItemView,
    pos: QPoint,
    *,
    image_column: int = 0,
    name_column: int = 1,
) -> str | None:
    """Return the exercise name when `pos` is over a table image cell with an icon.

    Args:

    - `table_view` (`QAbstractItemView`): Table whose image and name columns are used.
    - `pos` (`QPoint`): Pointer position in viewport coordinates.
    - `image_column` (`int`): Column with the exercise icon. Defaults to `0`.
    - `name_column` (`int`): Column with the exercise name. Defaults to `1`.

    Returns:

    - `str | None`: Exercise name, or `None` when the pointer is not on an image.

    """
    index = table_view.indexAt(pos)
    if not index.isValid() or index.column() != image_column:
        return None

    icon = index.data(Qt.ItemDataRole.DecorationRole)
    if icon is None or (hasattr(icon, "isNull") and icon.isNull()):
        return None

    if not table_view.visualRect(index).contains(pos):
        return None

    name = index.sibling(index.row(), name_column).data(Qt.ItemDataRole.DisplayRole)
    text = str(name).strip() if name else ""
    return text or None
