"""Frameless lightbox chrome fitted to the owner application window."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, QSize, Qt
from PySide6.QtGui import QGuiApplication, QKeyEvent, QKeySequence, QResizeEvent, QShortcut
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QWidget

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.qt_emoji_icon import CLOSE_BUTTON_EMOJI, create_emoji_icon

_BUTTON_SIZE = 44
_SWATCH_SIZE = 28
_SIDE_MARGIN = 20


class AppWindowLightboxDialog(QDialog):
    """Overlay with close, prev/next, a backdrop toggle swatch, and a caption.

    Subclasses attach a content widget and implement `show_item`.

    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        item_count: int = 0,
        current_index: int = 0,
    ) -> None:
        """Build chrome fitted to the owner window.

        Args:

        - `parent` (`QWidget | None`): Widget whose top-level window is covered.
        - `item_count` (`int`): Number of browsable items. Defaults to `0`.
        - `current_index` (`int`): Initial item index. Defaults to `0`.

        """
        owner = parent.window() if parent is not None else None
        super().__init__(owner)
        self._item_count = max(0, item_count)
        self._index = max(0, min(current_index, self._item_count - 1)) if self._item_count else 0
        self._content: QWidget | None = None

        qt_modality.set_owner_window_modal(self)
        self.setObjectName("appWindowLightbox")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        if owner is not None:
            owner.installEventFilter(self)
            self._fit_to_owner()
        else:
            screen = QGuiApplication.primaryScreen()
            if screen is not None:
                self.setGeometry(screen.availableGeometry())
            else:
                self.resize(1280, 720)

        self._close_button = self._make_button("", "Close")
        self._close_button.setIcon(create_emoji_icon(CLOSE_BUTTON_EMOJI, 22))
        self._close_button.clicked.connect(self.accept)
        self._previous_button = self._make_button("←", "Previous (Left arrow)")
        self._previous_button.clicked.connect(self.show_previous)
        self._next_button = self._make_button("→", "Next (Right arrow)")
        self._next_button.clicked.connect(self.show_next)

        self._backdrop_color = "white"
        self._backdrop_button = self._make_backdrop_toggle_button()
        self._backdrop_button.clicked.connect(self._toggle_backdrop_color)
        self._set_backdrop_color("white")

        self._previous_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        self._previous_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self._previous_shortcut.activated.connect(self.show_previous)
        self._next_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        self._next_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self._next_shortcut.activated.connect(self.show_next)

        self._caption = QLabel(self)
        self._caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._caption.setStyleSheet(
            "color: white; background: rgba(20, 20, 20, 180);border-radius: 7px; padding: 6px 12px;"
        )

    def attach_content(self, widget: QWidget) -> None:
        """Place `widget` under the overlay chrome and close on backdrop clicks."""
        self._content = widget
        backdrop_clicked = getattr(widget, "backdrop_clicked", None)
        if backdrop_clicked is not None:
            backdrop_clicked.connect(self.accept)

    def chrome_rect(self) -> QRect:
        """Return the rectangle used to place overlay controls.

        Defaults to the full dialog. Subclasses with a side panel override this
        so arrows and captions stay over the image pane.

        """
        return QRect(0, 0, self.width(), self.height())

    @property
    def current_index(self) -> int:
        """Current item index."""
        return self._index

    def empty_caption(self) -> str:
        """Caption when there are no items."""
        return "Nothing to display"

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Keep the overlay aligned with the owner window."""
        owner = self.parentWidget()
        if watched is owner and event.type() in {QEvent.Type.Resize, QEvent.Type.Move}:
            self._fit_to_owner()
        return super().eventFilter(watched, event)

    def finish_setup(self) -> None:
        """Size chrome and display the current item after content is attached."""
        self._position_controls()
        self._show_current()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle Escape and left/right navigation."""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        if event.key() == Qt.Key.Key_Left:
            self.show_previous()
            return
        if event.key() == Qt.Key.Key_Right:
            self.show_next()
            return
        super().keyPressEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Keep content and overlay controls aligned."""
        super().resizeEvent(event)
        self._position_controls()

    def set_caption(self, text: str) -> None:
        """Update the bottom caption."""
        self._caption.setText(text)

    def show_item(self, index: int) -> None:
        """Display the item at `index`. Subclasses must implement this."""
        msg = f"{type(self).__name__} must implement show_item"
        raise NotImplementedError(msg)

    def show_next(self) -> None:
        """Show the next item, wrapping at the end."""
        if self._item_count > 1:
            self._index = (self._index + 1) % self._item_count
            self._show_current()

    def show_previous(self) -> None:
        """Show the previous item, wrapping at the beginning."""
        if self._item_count > 1:
            self._index = (self._index - 1) % self._item_count
            self._show_current()

    def _fit_to_owner(self) -> None:
        owner = self.parentWidget()
        if owner is None:
            return
        if self.isWindow():
            top_left = owner.mapToGlobal(QPoint(0, 0))
            self.setGeometry(top_left.x(), top_left.y(), owner.width(), owner.height())
            return
        self.setGeometry(owner.rect())

    def _make_backdrop_toggle_button(self) -> QPushButton:
        button = QPushButton(self)
        button.setFixedSize(_SWATCH_SIZE, _SWATCH_SIZE)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setAutoDefault(False)
        button.setDefault(False)
        return button

    def _make_button(self, text: str, tooltip: str) -> QPushButton:
        button = QPushButton(text, self)
        button.setFixedSize(QSize(_BUTTON_SIZE, _BUTTON_SIZE))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setAutoDefault(False)
        button.setDefault(False)
        button.setToolTip(tooltip)
        button.setStyleSheet(
            "QPushButton { color: white; font-size: 24px; font-weight: bold;"
            "background: rgba(40, 40, 40, 125); border: 1px solid rgba(255, 255, 255, 90);"
            "border-radius: 9px; }"
            "QPushButton:hover { background: rgba(40, 40, 40, 190); }"
        )
        button.raise_()
        return button

    def _position_controls(self) -> None:
        if self._content is not None:
            self._content.setGeometry(self.rect())
        rect = self.chrome_rect()
        self._backdrop_button.move(rect.x() + _SIDE_MARGIN, rect.y() + _SIDE_MARGIN)
        self._close_button.move(rect.x() + rect.width() - _BUTTON_SIZE - _SIDE_MARGIN, rect.y() + _SIDE_MARGIN)
        center_y = rect.y() + (rect.height() - _BUTTON_SIZE) // 2
        self._previous_button.move(rect.x() + _SIDE_MARGIN, center_y)
        self._next_button.move(rect.x() + rect.width() - _BUTTON_SIZE - _SIDE_MARGIN, center_y)
        caption_width = min(640, max(240, rect.width() - 240))
        self._caption.setFixedWidth(caption_width)
        self._caption.adjustSize()
        self._caption.move(
            rect.x() + (rect.width() - caption_width) // 2,
            rect.y() + rect.height() - self._caption.height() - _SIDE_MARGIN,
        )
        for widget in (
            self._backdrop_button,
            self._close_button,
            self._previous_button,
            self._next_button,
            self._caption,
        ):
            widget.raise_()

    def _set_backdrop_color(self, color: str) -> None:
        self._backdrop_color = "black" if color == "black" else "white"
        fill = self._backdrop_color
        opposite = "white" if fill == "black" else "black"
        self.setStyleSheet(f"#appWindowLightbox {{ background-color: {fill}; }}")
        border = "#888" if opposite == "white" else "#ccc"
        radius = _SWATCH_SIZE // 2
        self._backdrop_button.setToolTip(f"Switch to {opposite} backdrop")
        self._backdrop_button.setStyleSheet(
            f"QPushButton {{ background: {opposite}; border: 1px solid {border};"
            f"border-radius: {radius}px; padding: 0; }}"
            "QPushButton:hover { border: 2px solid #2f80ed; }"
        )

    def _show_current(self) -> None:
        if self._item_count <= 0:
            self.set_caption(self.empty_caption())
            self._previous_button.hide()
            self._next_button.hide()
            return
        self.show_item(self._index)
        show_navigation = self._item_count > 1
        self._previous_button.setVisible(show_navigation)
        self._next_button.setVisible(show_navigation)
        self._position_controls()

    def _toggle_backdrop_color(self) -> None:
        self._set_backdrop_color("black" if self._backdrop_color == "white" else "white")
