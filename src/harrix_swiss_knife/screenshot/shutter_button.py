"""Shutter controls for region capture: embeddable panel and arrange-mode dialog."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from PySide6.QtCore import QEvent, QObject, QPoint, QSize, Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.qt_emoji_icon import create_emoji_icon
from harrix_swiss_knife.qt_flow_layout import FlowLayout
from harrix_swiss_knife.qt_frameless_window import frameless_stay_on_top_flags
from harrix_swiss_knife.screenshot.toolbar_style import (
    TOOLBAR_BUTTON_GAP,
    TOOLBAR_BUTTON_SIZE,
    TOOLBAR_BUTTON_STYLE,
    TOOLBAR_EDGE_MARGIN,
    TOOLBAR_ICON_SIZE,
)
from harrix_swiss_knife.screenshot.window_visibility import (
    claim_screenshot_keyboard,
    mark_screenshot_ui,
    release_screenshot_keyboard,
)

if TYPE_CHECKING:
    from PySide6.QtCore import QRect
    from PySide6.QtGui import QHideEvent, QKeyEvent, QShowEvent

_HINT_GAP = 8
_HINT_WIDTH = 220
_ARRANGE_EMOJI = "🪟"
_CAMERA_EMOJI = "📷"
_ADJUST_EMOJI = "✥"
_GUIDES_EMOJI = "📐"
_KEEP_WINDOWS_EMOJI = "👁️"
_CLIPBOARD_EMOJI = "📋"
_CLOSE_EMOJI = "❌"
_EDIT_KEYS_TEXT = "←↑↓→ move 1 px\nShift+arrows 10 px\nCtrl+arrows resize\nDouble-click W/H to type\nEnter confirm"

ShutterMode = Literal["selection", "arrange"]

_HINT_STYLE = """
QLabel {
    color: #222;
    background-color: #F5F5F7;
    border: 1px solid #E5E5E8;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 11pt;
}
"""


class ArrangeModeDialog(QDialog):
    """Small frameless stay-on-top dialog shown while the user arranges the desktop.

    Runs via `exec()` so it becomes the newest application-modal window and
    receives input above any concealed dialogs. Camera click accepts (back to
    region selection), close or Escape rejects (cancel capture).

    """

    def __init__(self) -> None:
        """Create the arrange-mode controls dialog."""
        super().__init__(None)
        mark_screenshot_ui(self)
        self.setWindowFlags(frameless_stay_on_top_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        panel = ShutterPanel(self)
        panel.set_mode("arrange")
        panel.triggered.connect(self.accept)
        panel.cancelled.connect(self.reject)
        panel.geometry_changed.connect(self._fit_panel)
        self._panel = panel
        self._fit_panel()

    def event(self, event: QEvent) -> bool:
        """Accept Escape as a shortcut override so it is not stolen by other Windows.

        Args:

        - `event` (`QEvent`): The event being delivered to the dialog.

        """
        key = getattr(event, "key", None)
        if event.type() == QEvent.Type.ShortcutOverride and callable(key) and key() == Qt.Key.Key_Escape:
            event.accept()
            return True
        return super().event(event)

    def hideEvent(self, event: QHideEvent) -> None:  # noqa: N802
        """Release the keyboard grab when arrange mode is closed."""
        release_screenshot_keyboard(self)
        super().hideEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Escape cancels the screenshot capture."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Take keyboard focus so Escape cancels capture in arrange mode."""
        super().showEvent(event)
        claim_screenshot_keyboard(self)

    def _fit_panel(self) -> None:
        """Keep the dialog size matched to the panel (grows when a hint is shown)."""
        self._panel.apply_available_width(_primary_available_width())
        self.setFixedSize(self._panel.sizeHint())
        self._position_on_primary_screen()

    def _position_on_primary_screen(self) -> None:
        """Place the controls at the top center of the primary screen."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.x() + (geo.width() - self.width()) // 2
        y = geo.y() + TOOLBAR_EDGE_MARGIN
        self.move(x, y)


class ShutterPanel(QWidget):
    """Top-centered toolbar with mode and close buttons, embeddable as a child.

    Being a regular child widget (not a separate native window) guarantees that
    clicks reach the buttons even when the application has modal dialogs in
    `exec()` — the parent (overlay or arrange dialog) owns the modal input.

    Hover captions are drawn as an in-panel label (not `QToolTip`), so they stay
    visible above the stay-on-top screenshot overlay.

    Buttons are square (`TOOLBAR_BUTTON_SIZE` px) and wrap to additional rows when
    the available width is too narrow. Checkable tools use the accent fill when
    selected.

    In selection mode extra checkable buttons enable “adjust region” (the next
    selection stays editable until Enter), composition guides (thin frame,
    thirds, diagonal, size, and angle), keeping app Windows visible in the
    grab, and clipboard-only (skip the preview window). Pass
    `capture_options=False` for screen recording to keep only Arrange, Guides,
    and Cancel.

    """

    adjust_toggled = Signal(bool)
    cancelled = Signal()
    geometry_changed = Signal()
    guides_toggled = Signal(bool)
    clipboard_toggled = Signal(bool)
    keep_windows_toggled = Signal(bool)
    triggered = Signal()

    def __init__(self, parent: QWidget | None = None, *, capture_options: bool = True) -> None:
        """Create the shutter panel with arrange/adjust/close controls.

        Args:

        - `parent` (`QWidget | None`): Parent widget.
        - `capture_options` (`bool`): When `False` (screen recording), hide Adjust /
          Keep Windows / Clipboard — only Arrange, Guides, and Cancel remain.

        """
        super().__init__(parent)
        self._capture_options = capture_options
        self._available_width = _primary_available_width()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(_HINT_GAP)

        self._buttons_host = QWidget(self)
        self._buttons_layout = FlowLayout(
            self._buttons_host,
            margin=0,
            h_spacing=TOOLBAR_BUTTON_GAP,
            v_spacing=TOOLBAR_BUTTON_GAP,
            alignment=Qt.AlignmentFlag.AlignHCenter,
        )

        self._mode_button = self._make_emoji_button(_ARRANGE_EMOJI, "Arrange desktop")
        self._mode_button.clicked.connect(self.triggered.emit)
        self._buttons_layout.addWidget(self._mode_button)

        self._adjust_button = self._make_emoji_button(
            _ADJUST_EMOJI,
            "Adjust region after select (Enter confirms)",
        )
        self._adjust_button.setCheckable(True)
        self._adjust_button.toggled.connect(self.adjust_toggled.emit)
        self._buttons_layout.addWidget(self._adjust_button)

        self._guides_button = self._make_emoji_button(
            _GUIDES_EMOJI,
            "Composition guides: thirds, diagonal, size, and angle",
        )
        self._guides_button.setCheckable(True)
        self._guides_button.toggled.connect(self.guides_toggled.emit)
        self._buttons_layout.addWidget(self._guides_button)

        self._keep_windows_button = self._make_emoji_button(
            _KEEP_WINDOWS_EMOJI,
            "Keep app Windows visible in the screenshot",
        )
        self._keep_windows_button.setCheckable(True)
        self._keep_windows_button.toggled.connect(self.keep_windows_toggled.emit)
        self._buttons_layout.addWidget(self._keep_windows_button)

        self._clipboard_button = self._make_emoji_button(
            _CLIPBOARD_EMOJI,
            "Clipboard only (skip preview)",
        )
        self._clipboard_button.setCheckable(True)
        self._clipboard_button.toggled.connect(self.clipboard_toggled.emit)
        self._buttons_layout.addWidget(self._clipboard_button)

        self._close_button = self._make_emoji_button(
            _CLOSE_EMOJI,
            "Cancel" if not capture_options else "Cancel screenshot",
        )
        self._close_button.clicked.connect(self.cancelled.emit)
        self._buttons_layout.addWidget(self._close_button)

        root.addWidget(self._buttons_host)

        self._hint_label = QLabel(self)
        self._hint_label.setStyleSheet(_HINT_STYLE)
        self._hint_label.setWordWrap(True)
        self._hint_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self._hint_label.hide()
        root.addWidget(self._hint_label, 0, Qt.AlignmentFlag.AlignHCenter)

        self._edit_keys_label = QLabel(self)
        self._edit_keys_label.setStyleSheet(_HINT_STYLE)
        self._edit_keys_label.setWordWrap(True)
        self._edit_keys_label.setText(_EDIT_KEYS_TEXT)
        self._edit_keys_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._edit_keys_label.hide()
        root.addWidget(self._edit_keys_label, 0, Qt.AlignmentFlag.AlignHCenter)

        self._mode: ShutterMode = "selection"
        self._hovered_button: QPushButton | None = None
        self._apply_capture_option_visibility()
        self._update_size()

    @property
    def adjust_mode(self) -> bool:
        """Whether the next selection should stay editable until confirmed."""
        return self._mode == "selection" and self._adjust_button.isChecked()

    def apply_available_width(self, width: int) -> None:
        """Constrain the toolbar width so buttons wrap on narrow screens."""
        clamped = max(TOOLBAR_BUTTON_SIZE, width)
        if clamped == self._available_width:
            return
        self._available_width = clamped
        self._update_size()

    @property
    def clipboard_only(self) -> bool:
        """Whether capture should skip the preview and only copy to the clipboard."""
        return self._mode == "selection" and self._clipboard_button.isChecked()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Show an in-panel caption while the pointer is over a shutter button."""
        if isinstance(watched, QPushButton):
            if event.type() == QEvent.Type.Enter:
                self._hovered_button = watched
                self._show_hint(str(watched.property("hover_hint") or watched.toolTip()))
            elif event.type() == QEvent.Type.Leave and self._hovered_button is watched:
                self._hovered_button = None
                self._hide_hint()
        return super().eventFilter(watched, event)

    @property
    def guides_mode(self) -> bool:
        """Whether the selection frame shows composition guides and measurements."""
        return self._mode == "selection" and self._guides_button.isChecked()

    @property
    def keep_windows(self) -> bool:
        """Whether application Windows should stay visible in the next grab."""
        return self._mode == "selection" and self._keep_windows_button.isChecked()

    def set_adjust_mode(self, *, enabled: bool) -> None:
        """Set the adjust-region button without requiring a user click."""
        self._adjust_button.setChecked(enabled)

    def set_clipboard_only(self, *, enabled: bool) -> None:
        """Set the clipboard-only button without requiring a user click."""
        self._clipboard_button.setChecked(enabled)

    def set_edit_keys_visible(self, *, visible: bool) -> None:
        """Show or hide arrow/Shift/Ctrl hints under the shutter buttons."""
        if visible == self._edit_keys_label.isVisible():
            return
        self._edit_keys_label.setVisible(visible)
        self._update_size()

    def set_guides_mode(self, *, enabled: bool) -> None:
        """Set the composition-guides button without requiring a user click."""
        self._guides_button.setChecked(enabled)

    def set_keep_windows(self, *, enabled: bool) -> None:
        """Set the keep-Windows button without emitting `keep_windows_toggled`."""
        blocked = self._keep_windows_button.blockSignals(True)  # noqa: FBT003
        try:
            self._keep_windows_button.setChecked(enabled)
        finally:
            self._keep_windows_button.blockSignals(blocked)

    def set_mode(self, mode: ShutterMode) -> None:
        """Update the mode button emoji for selection vs desktop-arrangement."""
        self._mode = mode
        if mode == "selection":
            # In region selection, click leaves capture to arrange other Windows.
            self._mode_button.setIcon(create_emoji_icon(_ARRANGE_EMOJI, TOOLBAR_ICON_SIZE))
            self._mode_button.setToolTip("Arrange desktop")
            self._mode_button.setProperty("hover_hint", "Arrange desktop")
            self._guides_button.show()
            self._apply_capture_option_visibility()
        else:
            # In arrange mode, click returns to region capture.
            self._mode_button.setIcon(create_emoji_icon(_CAMERA_EMOJI, TOOLBAR_ICON_SIZE))
            self._mode_button.setToolTip("Capture region" if self._capture_options else "Select region")
            self._mode_button.setProperty(
                "hover_hint",
                "Capture region" if self._capture_options else "Select region",
            )
            self._adjust_button.hide()
            self._adjust_button.setChecked(False)
            self._guides_button.hide()
            self._guides_button.setChecked(False)
            self._keep_windows_button.hide()
            self._clipboard_button.hide()
            self.set_edit_keys_visible(visible=False)
        if self._hovered_button is self._mode_button:
            self._show_hint(str(self._mode_button.property("hover_hint") or ""))
        self._update_size()

    def _apply_capture_option_visibility(self) -> None:
        show = self._capture_options and self._mode == "selection"
        self._adjust_button.setVisible(show)
        self._keep_windows_button.setVisible(show)
        self._clipboard_button.setVisible(show)
        if not show:
            self._adjust_button.setChecked(False)
            self._keep_windows_button.setChecked(False)
            self._clipboard_button.setChecked(False)
            self.set_edit_keys_visible(visible=False)

    def _hide_hint(self) -> None:
        if not self._hint_label.isVisible():
            return
        self._hint_label.hide()
        self._hint_label.clear()
        self._update_size()

    def _make_emoji_button(self, emoji: str, tooltip: str) -> QPushButton:
        button = QPushButton(self._buttons_host)
        button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
        button.setIcon(create_emoji_icon(emoji, TOOLBAR_ICON_SIZE))
        button.setIconSize(QSize(TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip(tooltip)
        button.setProperty("hover_hint", tooltip)
        button.setStyleSheet(TOOLBAR_BUTTON_STYLE)
        button.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
        button.installEventFilter(self)
        return button

    def _show_hint(self, text: str) -> None:
        if not text:
            self._hide_hint()
            return
        self._hint_label.setText(text)
        self._hint_label.show()
        self._update_size()

    def _update_size(self) -> None:
        visible_count = sum(
            1
            for button in (
                self._mode_button,
                self._adjust_button,
                self._guides_button,
                self._keep_windows_button,
                self._clipboard_button,
                self._close_button,
            )
            if not button.isHidden()
        )
        ideal_width = (
            TOOLBAR_BUTTON_SIZE * visible_count + TOOLBAR_BUTTON_GAP * max(0, visible_count - 1)
            if visible_count
            else TOOLBAR_BUTTON_SIZE
        )
        width = min(ideal_width, self._available_width)
        width = max(width, TOOLBAR_BUTTON_SIZE)

        buttons_height = self._buttons_layout.heightForWidth(width)
        self._buttons_host.setFixedSize(width, max(TOOLBAR_BUTTON_SIZE, buttons_height))

        extra_height = 0
        content_width = width
        if self._hint_label.isVisible():
            hint_w = min(max(width, _HINT_WIDTH), self._available_width)
            self._hint_label.setFixedWidth(hint_w)
            hint_h = self._hint_label.sizeHint().height()
            extra_height += _HINT_GAP + hint_h
            content_width = max(content_width, hint_w)
        if self._edit_keys_label.isVisible():
            keys_w = min(max(width, _HINT_WIDTH), self._available_width)
            self._edit_keys_label.setFixedWidth(keys_w)
            keys_h = self._edit_keys_label.sizeHint().height()
            extra_height += _HINT_GAP + keys_h
            content_width = max(content_width, keys_w)

        new_width = content_width
        new_height = self._buttons_host.height() + extra_height
        if self.width() == new_width and self.height() == new_height:
            return
        self.setFixedSize(new_width, new_height)
        self.geometry_changed.emit()


def position_panel_at_top_center(panel: ShutterPanel, overlay_geometry: QRect) -> None:
    """Place an embedded panel at the top center of the primary screen.

    Args:

    - `panel` (`ShutterPanel`): Panel that is a child of the fullscreen overlay.
    - `overlay_geometry` (`QRect`): Overlay geometry in global (virtual desktop) coordinates.

    """
    screen = QApplication.primaryScreen()
    if screen is None:
        return
    geo = screen.availableGeometry()
    panel.apply_available_width(max(TOOLBAR_BUTTON_SIZE, geo.width() - 2 * TOOLBAR_EDGE_MARGIN))
    parent = panel.parentWidget()
    origin = parent.mapToGlobal(QPoint(0, 0)) if parent is not None else overlay_geometry.topLeft()
    x = geo.x() - origin.x() + (geo.width() - panel.width()) // 2
    y = geo.y() - origin.y() + TOOLBAR_EDGE_MARGIN
    panel.move(x, y)
    panel.raise_()


def _primary_available_width() -> int:
    screen = QApplication.primaryScreen()
    if screen is None:
        return 480
    return max(TOOLBAR_BUTTON_SIZE, screen.availableGeometry().width() - 2 * TOOLBAR_EDGE_MARGIN)
