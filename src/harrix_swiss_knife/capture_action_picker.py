"""Picker dialog for screenshot / record actions after a capture hotkey long-press."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QEvent, QEventLoop, QObject, QPoint, QSize, Qt, QTimer
from PySide6.QtGui import QFont, QKeyEvent, QMouseEvent, QResizeEvent
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizeGrip,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.action_title import strip_md_inline_code_markers
from harrix_swiss_knife.actions.common.dialog_geometry import center_widget_on_available_screen
from harrix_swiss_knife.actions.images.record_region import OnRecordRegion
from harrix_swiss_knife.actions.images.screenshot_region import OnScreenshotRegion
from harrix_swiss_knife.actions.images.screenshot_region_clipboard import OnScreenshotRegionClipboard
from harrix_swiss_knife.actions.images.screenshot_region_keep_windows import OnScreenshotRegionKeepWindows
from harrix_swiss_knife.actions.images.screenshot_region_translate import OnScreenshotRegionTranslate
from harrix_swiss_knife.cli_menu import show_action_class_context_menu
from harrix_swiss_knife.fluent.app_chrome import install_fluent_app_window, prepare_fluent_app_window
from harrix_swiss_knife.fluent.theme import bind_theme, css, mix, palette_for
from harrix_swiss_knife.fluent.tokens import (
    COMMAND_CARD_MIN_SCALE,
    ICON_TILE_HEIGHT,
    ICON_TILE_ICON_SIZE,
    ICON_TILE_WIDTH,
    SPACE_L,
    SPACE_M,
)
from harrix_swiss_knife.fluent.widgets.cards import FluentIconTileCard
from harrix_swiss_knife.fluent.widgets.text import SubtitleLabel
from harrix_swiss_knife.fluent.widgets.views import FluentCardGrid
from harrix_swiss_knife.installer.icon_assets import apply_window_icon
from harrix_swiss_knife.qt_action_icon import create_action_icon
from harrix_swiss_knife.qt_command_section import grow_qfont
from harrix_swiss_knife.qt_frameless_window import frameless_stay_on_top_flags, try_handle_frameless_resize_native_event
from harrix_swiss_knife.qt_lucide_icon import CLOSE_BUTTON_ICON, apply_lucide_button_icon
from harrix_swiss_knife.win11_caption import (
    CAPTION_BUTTON_HEIGHT,
    OVERLAY_CAPTION_PROPERTY,
    install_win11_caption,
    refresh_win11_caption,
    try_handle_win11_caption_native_event,
)

if TYPE_CHECKING:
    from harrix_swiss_knife.actions.common.base import ActionBase

CAPTURE_PICKER_ACTIONS: tuple[type[ActionBase], ...] = (
    OnScreenshotRegion,
    OnScreenshotRegionClipboard,
    OnScreenshotRegionKeepWindows,
    OnScreenshotRegionTranslate,
    OnRecordRegion,
)

_OVERLAY_MIN_SIZE = QSize(640, 280)
_OVERLAY_DEFAULT_SIZE = QSize(720, 360)


class CaptureActionPickerDialog(QDialog):
    """Frameless Quick-Launcher-style picker for screenshot / record actions."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the picker with Fluent command cards like OnQuickLauncher."""
        super().__init__(parent)
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(_overlay_window_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        apply_window_icon(self)
        prepare_fluent_app_window(self)

        self._selected: str | None = None
        self._dragging = False
        self._drag_position = QPoint()
        self._win11_caption = False
        self._close_button: QPushButton | None = None
        self._selected_card: FluentIconTileCard | None = None

        self.setObjectName("captureActionPickerDialog")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setProperty(OVERLAY_CAPTION_PROPERTY, True)  # noqa: FBT003

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        content = QWidget(self)
        content.setObjectName("captureActionPickerContent")
        content.setAutoFillBackground(False)
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(SPACE_L, SPACE_M, SPACE_L, SPACE_L)
        self._content_layout.setSpacing(SPACE_M)

        self._win11_caption = install_win11_caption(self)
        if not self._win11_caption:
            self._build_fallback_header()

        self._actions_title = SubtitleLabel("Actions", content)
        self._actions_title.setCursor(Qt.CursorShape.OpenHandCursor)
        self._content_layout.addWidget(self._actions_title)

        self._actions_grid = FluentCardGrid(
            content,
            base_width=ICON_TILE_WIDTH,
            min_scale=COMMAND_CARD_MIN_SCALE,
        )
        self._content_layout.addWidget(self._actions_grid)

        self._hint = QLabel("Hold a capture hotkey to open · Esc to close")
        self._hint.setCursor(Qt.CursorShape.OpenHandCursor)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.addWidget(self._hint, stretch=1)
        self._size_grip = QSizeGrip(self)
        footer.addWidget(self._size_grip, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self._content_layout.addLayout(footer)

        self._layout.addWidget(content, stretch=1)

        for draggable_widget in (self._hint, self._actions_title):
            draggable_widget.installEventFilter(self)

        self._populate_cards()
        install_fluent_app_window(self)
        bind_theme(self, self._refresh_overlay_theme)
        self._refresh_overlay_theme()
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._prepare_geometry_before_show()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Start window drag from passive header and hint widgets."""
        if isinstance(watched, QWidget) and self._is_drag_excluded_widget(watched):
            return False

        if (
            event.type() == QEvent.Type.MouseButtonPress
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._start_drag(event.globalPosition().toPoint())
            return True

        if (
            event.type() == QEvent.Type.MouseMove
            and isinstance(event, QMouseEvent)
            and event.buttons() & Qt.MouseButton.LeftButton
            and self._dragging
        ):
            self._move_drag(event.globalPosition().toPoint())
            return True

        if (
            event.type() == QEvent.Type.MouseButtonRelease
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.LeftButton
            and self._dragging
        ):
            self._end_drag()
            return True

        return False

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Close the picker on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Move the overlay while dragging from dialog margins."""
        if event.buttons() & Qt.MouseButton.LeftButton and self._dragging:
            self._move_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start dragging from dialog margins and background."""
        if event.button() == Qt.MouseButton.LeftButton and self._can_start_drag_at(event.position().toPoint()):
            self._start_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Stop dragging the overlay."""
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._end_drag()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def nativeEvent(self, event_type, message) -> tuple[bool, int]:  # noqa: ANN001, N802
        """Allow caption drag and edge resize for this frameless window on Windows."""
        caption = try_handle_win11_caption_native_event(self, event_type, message)
        if caption is not None:
            return caption
        handled = try_handle_frameless_resize_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Refit the card grid height when the window width changes."""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._refit_grid_for_width)

    def selected_action_name(self) -> str | None:
        """Return the action class name chosen by the user."""
        return self._selected

    def _accept_action(self, action_cls: type[ActionBase]) -> None:
        self._selected = action_cls.__name__
        self.accept()

    def _build_fallback_header(self) -> None:
        title = QLabel("Capture")
        title_font = QFont(title.font())
        grow_qfont(title_font)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setCursor(Qt.CursorShape.OpenHandCursor)

        self._close_button = QPushButton("")
        self._close_button.setFixedSize(CAPTION_BUTTON_HEIGHT, CAPTION_BUTTON_HEIGHT)
        self._close_button.setFlat(True)
        self._close_button.setToolTip("Close")
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_lucide_button_icon(self._close_button, CLOSE_BUTTON_ICON, icon_size=18)
        self._close_button.clicked.connect(self.reject)

        header_spacer = QWidget(self)
        header_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header_spacer.setCursor(Qt.CursorShape.OpenHandCursor)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(title)
        header.addWidget(header_spacer, stretch=1)
        header.addWidget(self._close_button)
        self._content_layout.addLayout(header)

        for draggable_widget in (title, header_spacer):
            draggable_widget.installEventFilter(self)

    def _can_start_drag_at(self, local_pos: QPoint) -> bool:
        child = self.childAt(local_pos)
        if child is None:
            return True
        return not self._is_drag_excluded_widget(child)

    def _end_drag(self) -> None:
        self._dragging = False
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def _fit_to_content(self) -> None:
        margins = self._content_layout.contentsMargins()
        grid_width = max(1, self.width() - margins.left() - margins.right())
        natural = max(ICON_TILE_HEIGHT, self._actions_grid.flow_layout().heightForWidth(grid_width))
        title_h = self._actions_title.sizeHint().height()
        footer_h = max(self._hint.sizeHint().height(), self._size_grip.sizeHint().height())
        chrome = margins.top() + margins.bottom() + title_h + footer_h + self._content_layout.spacing() * 2
        if self._win11_caption:
            chrome += CAPTION_BUTTON_HEIGHT
        elif self._content_layout.count() > 0:
            header_item = self._content_layout.itemAt(0)
            header_layout = header_item.layout() if header_item is not None else None
            if header_layout is not None:
                chrome += header_layout.sizeHint().height() + self._content_layout.spacing()
        height = max(_OVERLAY_MIN_SIZE.height(), chrome + natural)
        width = max(self.width(), _OVERLAY_DEFAULT_SIZE.width())
        self.setMinimumHeight(min(height, _OVERLAY_MIN_SIZE.height()))
        self.resize(width, height)
        center_widget_on_available_screen(self)
        cards = [card for card in self._actions_grid.cards() if isinstance(card, FluentIconTileCard)]
        if cards:
            self._select_card(cards[0])
            cards[0].setFocus(Qt.FocusReason.OtherFocusReason)

    def _is_drag_excluded_widget(self, widget: QWidget) -> bool:
        if widget is self._actions_grid or self._actions_grid.isAncestorOf(widget):
            return True
        if self._close_button is not None and (widget is self._close_button or self._close_button.isAncestorOf(widget)):
            return True
        caption = self.findChild(QWidget, "captionBar")
        if caption is not None and (widget is caption or caption.isAncestorOf(widget)):
            return True
        return widget is self._size_grip or self._size_grip.isAncestorOf(widget)

    def _move_drag(self, global_pos: QPoint) -> None:
        self.move(global_pos - self._drag_position)

    def _on_card_clicked(self, action_cls: type[ActionBase], card: FluentIconTileCard) -> None:
        self._select_card(card)
        self._accept_action(action_cls)

    def _populate_cards(self) -> None:
        self._actions_grid.clear()
        for action_cls in CAPTURE_PICKER_ACTIONS:
            title = strip_md_inline_code_markers(action_cls.title)
            icon = create_action_icon(action_cls, ICON_TILE_ICON_SIZE)
            card = FluentIconTileCard(
                title,
                icon=icon if not icon.isNull() else None,
                user_data=action_cls,
            )
            card.clicked.connect(lambda listed=action_cls, host=card: self._on_card_clicked(listed, host))
            card.context_menu_requested.connect(
                lambda global_pos, listed=action_cls, host=card: show_action_class_context_menu(
                    parent=self,
                    global_pos=global_pos,
                    action_cls=listed,
                    host_widget=host,
                ),
            )
            self._actions_grid.add_card(card)

    def _prepare_geometry_before_show(self) -> None:
        width = max(self.width(), _OVERLAY_DEFAULT_SIZE.width())
        self.resize(width, max(self.height(), _OVERLAY_MIN_SIZE.height()))
        self.move(-10_000, -10_000)
        self.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
        try:
            self.show()
            self._fit_to_content()
            QApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
            self.hide()
        finally:
            self.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=False)

    def _refit_grid_for_width(self) -> None:
        if not self.isVisible():
            return
        self._fit_to_content()

    def _refresh_overlay_theme(self) -> None:
        palette = palette_for(self)
        border = css(mix(palette.window_bg, palette.popup_stroke))
        window = css(palette.window_bg)
        muted = css(mix(palette.window_bg, palette.text_secondary))
        self.setStyleSheet(
            f"#captureActionPickerDialog {{ background-color: {window}; border: 1px solid {border}; }}"
            "#captureActionPickerContent { background: transparent; }",
        )
        self._hint.setStyleSheet(f"color: {muted};")
        refresh_win11_caption(self)

    def _select_card(self, card: FluentIconTileCard) -> None:
        previous = self._selected_card
        if previous is not None and previous is not card:
            previous.set_selected(selected=False)
        card.set_selected(selected=True)
        self._selected_card = card

    def _start_drag(self, global_pos: QPoint) -> None:
        self._dragging = True
        self._drag_position = global_pos - self.frameGeometry().topLeft()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)


def choose_capture_hotkey_action(*, parent: QWidget | None = None) -> str | None:
    """Show the capture-action picker and return the selected class name, or `None`."""
    dialog = CaptureActionPickerDialog(parent)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.selected_action_name()


def _overlay_window_flags() -> Qt.WindowType:
    return (
        frameless_stay_on_top_flags()
        | Qt.WindowType.WindowSystemMenuHint
        | Qt.WindowType.WindowMinimizeButtonHint
        | Qt.WindowType.WindowMaximizeButtonHint
        | Qt.WindowType.WindowCloseButtonHint
    )
