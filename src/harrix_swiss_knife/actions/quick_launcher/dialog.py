"""Quick launcher overlay dialog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, cast

from PySide6.QtCore import QEvent, QObject, QPoint, QSize, Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QKeyEvent, QMouseEvent, QResizeEvent
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizeGrip,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.action_hotkeys import load_hotkeys_for_action
from harrix_swiss_knife.action_title import strip_md_inline_code_markers
from harrix_swiss_knife.actions.markdown.new_markdown import OnNewMarkdown
from harrix_swiss_knife.actions.quick_launcher.settings import load_quick_launcher_markdown_in_panel
from harrix_swiss_knife.qt_action_card_grid import CARD_ICON_SIZE, configure_action_card_grid
from harrix_swiss_knife.qt_command_section import (
    apply_opaque_white,
    create_command_section,
    measure_icon_grid_height,
    style_transparent_icon_grid,
)
from harrix_swiss_knife.qt_emoji_icon import create_emoji_icon
from harrix_swiss_knife.qt_frameless_window import frameless_stay_on_top_flags, try_handle_frameless_resize_native_event
from harrix_swiss_knife.qt_markdown_choice_cards import populate_icon_choice_cards
from harrix_swiss_knife.win11_backdrop import SystemBackdrop, try_apply_system_backdrop

if TYPE_CHECKING:
    from harrix_swiss_knife.action_output_bus import ActionOutputBus
    from harrix_swiss_knife.actions.base import ActionBase

_OVERLAY_MIN_SIZE = QSize(900, 560)
_OVERLAY_DEFAULT_SIZE = QSize(1024, 720)
_WINDOW_FLAGS = frameless_stay_on_top_flags()
_DIALOG_BORDER_STYLE = "#quickLauncherDialog { background-color: #ffffff; border: 1px solid #c0c0c0;}"


class QuickLauncherDialog(QDialog):
    """Resizable always-on-top window listing quick-launcher actions."""

    _instance: ClassVar[QuickLauncherDialog | None] = None

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the quick launcher dialog."""
        super().__init__(parent)
        self._default_parent = parent
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(_WINDOW_FLAGS)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._output_bus: ActionOutputBus | None = None
        self._action_classes: list[type[ActionBase]] = []
        self._dragging = False
        self._drag_position = QPoint()

        apply_opaque_white(self)
        self.setObjectName("quickLauncherDialog")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, on=True)
        self.setStyleSheet(_DIALOG_BORDER_STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(12)

        title = QLabel("Quick launcher")
        title_font = QFont(title.font())
        title_font.setPointSize(title_font.pointSize() + 1)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setCursor(Qt.CursorShape.OpenHandCursor)

        self._close_button = QPushButton("X")
        self._close_button.setFixedSize(28, 28)
        self._close_button.setFlat(True)
        self._close_button.setToolTip("Close")
        self._close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_button.clicked.connect(self.hide)

        header_spacer = QWidget(self)
        header_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header_spacer.setCursor(Qt.CursorShape.OpenHandCursor)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(title)
        header.addWidget(header_spacer, stretch=1)
        header.addWidget(self._close_button)
        self._layout.addLayout(header)

        self._cards = QListWidget(self)
        configure_action_card_grid(self._cards)
        style_transparent_icon_grid(self._cards)
        self._cards.itemClicked.connect(self._on_item_clicked)
        self._actions_section, _, actions_layout = create_command_section(title="Actions")
        actions_layout.addWidget(self._cards)
        self._layout.addWidget(self._actions_section, stretch=1)

        self._markdown_cards = QListWidget(self)
        configure_action_card_grid(self._markdown_cards)
        style_transparent_icon_grid(self._markdown_cards)
        self._markdown_section, self._markdown_section_label, markdown_layout = create_command_section(
            title="New Markdown",
        )
        if self._markdown_section_label is not None:
            self._markdown_section_label.setCursor(Qt.CursorShape.OpenHandCursor)
        markdown_layout.addWidget(self._markdown_cards)
        self._layout.addWidget(self._markdown_section, stretch=1)

        self._hint = QLabel(self)
        self._hint.setStyleSheet("color: palette(mid);")
        self._hint.setCursor(Qt.CursorShape.OpenHandCursor)
        self._layout.addWidget(self._hint)
        self._update_hint()

        resize_row = QHBoxLayout()
        resize_row.addStretch()
        self._size_grip = QSizeGrip(self)
        resize_row.addWidget(self._size_grip, alignment=Qt.AlignmentFlag.AlignRight)
        self._layout.addLayout(resize_row)

        draggable_widgets: list[QWidget] = [title, header_spacer, self._hint]
        if self._markdown_section_label is not None:
            draggable_widgets.append(self._markdown_section_label)
        for draggable_widget in draggable_widgets:
            draggable_widget.installEventFilter(self)

        self._apply_split_layout(enabled=False)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._center_on_screen()

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
        """Hide the overlay on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
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
        """Allow edge resize for this frameless window on Windows."""
        handled = try_handle_frameless_resize_native_event(self, event_type, message)
        if handled is not None:
            return handled
        return cast("tuple[bool, int]", super().nativeEvent(event_type, message))

    def present(self) -> None:
        """Show and focus the overlay."""
        self._update_hint()
        self._retarget_to_active_modal_parent()
        width = max(self.width(), _OVERLAY_DEFAULT_SIZE.width())
        self.resize(width, _OVERLAY_DEFAULT_SIZE.height())
        self.show()
        self.raise_()
        self.activateWindow()
        QTimer.singleShot(0, self._present_after_show)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reflow icon grids when the window width changes."""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._refit_grids_for_width)

    def set_action_classes(self, action_classes: list[type[ActionBase]]) -> None:
        """Rebuild the action card grid."""
        self._action_classes = list(action_classes)
        self._cards.clear()
        for action_cls in self._action_classes:
            item = QListWidgetItem(strip_md_inline_code_markers(action_cls.title), self._cards)
            item.setData(Qt.ItemDataRole.UserRole, action_cls)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            item.setIcon(_action_icon(action_cls, CARD_ICON_SIZE))
            self._cards.addItem(item)

    @classmethod
    def toggle(
        cls,
        *,
        parent: QWidget | None,
        output_bus: ActionOutputBus | None,
        action_classes: list[type[ActionBase]],
    ) -> None:
        """Show or hide the singleton quick launcher dialog."""
        if cls._instance is None:
            cls._instance = cls(parent)
        dialog = cls._instance
        dialog.update_session(output_bus=output_bus, action_classes=action_classes)

        if dialog.isVisible():
            dialog.hide()
            return

        dialog.present()

    def update_session(
        self,
        *,
        output_bus: ActionOutputBus | None,
        action_classes: list[type[ActionBase]],
    ) -> None:
        """Refresh output bus and action list before showing."""
        self._output_bus = output_bus
        self.set_action_classes(action_classes)
        split_markdown = load_quick_launcher_markdown_in_panel()
        self._apply_split_layout(enabled=split_markdown)
        if split_markdown:
            choices, action_map = OnNewMarkdown(output_bus=output_bus).build_picker_choices()
            template_titles = {title for title, (kind, _) in action_map.items() if kind == "template"}
            self._set_markdown_choices(choices, ai_screenshot_titles=template_titles)
        else:
            self._markdown_cards.clear()
        QTimer.singleShot(0, self._fit_to_content)

    def _apply_split_layout(self, *, enabled: bool) -> None:
        """Show or hide the Markdown panel."""
        self._markdown_section.setVisible(enabled)
        configure_action_card_grid(self._cards)
        style_transparent_icon_grid(self._cards)
        if enabled:
            configure_action_card_grid(self._markdown_cards)
            style_transparent_icon_grid(self._markdown_cards)
        self._layout.setStretch(self._layout.indexOf(self._actions_section), 1)
        self._layout.setStretch(self._layout.indexOf(self._markdown_section), 1 if enabled else 0)

    def _can_start_drag_at(self, local_pos: QPoint) -> bool:
        child = self.childAt(local_pos)
        if child is None:
            return True
        return not self._is_drag_excluded_widget(child)

    def _center_on_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.availableGeometry()
        x = geometry.center().x() - self.width() // 2
        y = geometry.center().y() - self.height() // 3
        self.move(x, y)

    def _content_height_metrics(self) -> _ContentHeightMetrics:
        for grid in (self._cards, self._markdown_cards):
            grid.setMinimumHeight(0)
            grid.setMaximumHeight(16777215)

        split = self._markdown_section.isVisible()
        cards_natural = measure_icon_grid_height(self._cards)
        markdown_natural = measure_icon_grid_height(self._markdown_cards) if split else 0
        actions_chrome = _section_chrome_height(self._actions_section)
        markdown_chrome = _section_chrome_height(self._markdown_section) if split else 0
        window_chrome = _layout_vertical_chrome(self._layout, self._hint) + self._size_grip.sizeHint().height()
        spacing_total = _layout_spacing_total(self._layout, split=split) + self._layout.spacing()
        sections_chrome = actions_chrome + markdown_chrome
        grids_natural = cards_natural + markdown_natural
        content_height = window_chrome + spacing_total + sections_chrome + grids_natural
        return _ContentHeightMetrics(
            split=split,
            cards_natural=cards_natural,
            markdown_natural=markdown_natural,
            sections_chrome=sections_chrome,
            window_chrome=window_chrome,
            spacing_total=spacing_total,
            grids_natural=grids_natural,
            content_height=content_height,
        )

    def _end_drag(self) -> None:
        if self._dragging:
            self.releaseMouse()
        self._dragging = False
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def _fit_to_content(self) -> None:
        """Resize the window to fit all cards when screen height allows."""
        metrics = self._content_height_metrics()
        screen = QApplication.primaryScreen()
        screen_max_height = screen.availableGeometry().height() if screen is not None else metrics.content_height

        min_height = min(metrics.content_height, screen_max_height)
        self.setMinimumHeight(min_height)

        target_height = min_height
        available_for_grids = max(
            0,
            target_height - metrics.window_chrome - metrics.spacing_total - metrics.sections_chrome,
        )

        if metrics.grids_natural <= available_for_grids:
            _apply_card_grid_height(
                self._cards,
                natural=metrics.cards_natural,
                allocated=metrics.cards_natural,
            )
            if metrics.split:
                _apply_card_grid_height(
                    self._markdown_cards,
                    natural=metrics.markdown_natural,
                    allocated=metrics.markdown_natural,
                )
        elif metrics.split and metrics.grids_natural > 0:
            cards_allocated = max(120, int(available_for_grids * metrics.cards_natural / metrics.grids_natural))
            markdown_allocated = max(120, available_for_grids - cards_allocated)
            _apply_card_grid_height(
                self._cards,
                natural=metrics.cards_natural,
                allocated=cards_allocated,
            )
            _apply_card_grid_height(
                self._markdown_cards,
                natural=metrics.markdown_natural,
                allocated=markdown_allocated,
            )
        else:
            _apply_card_grid_height(
                self._cards,
                natural=metrics.cards_natural,
                allocated=max(120, available_for_grids),
            )

        width = max(self.width(), _OVERLAY_MIN_SIZE.width())
        self.resize(width, target_height)

    def _is_drag_excluded_widget(self, widget: QWidget) -> bool:
        if widget is self._close_button or self._close_button.isAncestorOf(widget):
            return True
        if widget is self._cards or self._cards.isAncestorOf(widget):
            return True
        if widget is self._markdown_cards or self._markdown_cards.isAncestorOf(widget):
            return True
        return widget is self._size_grip or self._size_grip.isAncestorOf(widget)

    def _move_drag(self, global_pos: QPoint) -> None:
        self.move(global_pos - self._drag_position)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        self._run_action(item)

    def _on_markdown_ai_screenshot(self, title: str) -> None:
        self._run_markdown_choice(title, ai_screenshot=True)

    def _present_after_show(self) -> None:
        self._fit_to_content()
        self._center_on_screen()
        if self._cards.count():
            self._cards.setCurrentRow(0)
            self._cards.setFocus()

    def _refit_grids_for_width(self) -> None:
        """Update card grid heights and enforce content-based minimum height."""
        if not self.isVisible():
            return

        metrics = self._content_height_metrics()
        screen = QApplication.primaryScreen()
        screen_max_height = screen.availableGeometry().height() if screen is not None else metrics.content_height
        min_height = min(metrics.content_height, screen_max_height)
        self.setMinimumHeight(min_height)

        if metrics.content_height <= screen_max_height:
            _apply_card_grid_height(
                self._cards,
                natural=metrics.cards_natural,
                allocated=metrics.cards_natural,
            )
            if metrics.split:
                _apply_card_grid_height(
                    self._markdown_cards,
                    natural=metrics.markdown_natural,
                    allocated=metrics.markdown_natural,
                )
            if self.height() < min_height:
                self.resize(self.width(), min_height)
            return

        available_for_grids = max(
            0,
            self.height() - metrics.window_chrome - metrics.spacing_total - metrics.sections_chrome,
        )
        if metrics.split and metrics.grids_natural > 0:
            cards_allocated = max(120, int(available_for_grids * metrics.cards_natural / metrics.grids_natural))
            markdown_allocated = max(120, available_for_grids - cards_allocated)
            _apply_card_grid_height(
                self._cards,
                natural=metrics.cards_natural,
                allocated=cards_allocated,
            )
            _apply_card_grid_height(
                self._markdown_cards,
                natural=metrics.markdown_natural,
                allocated=markdown_allocated,
            )
        else:
            _apply_card_grid_height(
                self._cards,
                natural=metrics.cards_natural,
                allocated=max(120, available_for_grids),
            )

    def _retarget_to_active_modal_parent(self) -> None:
        """Parent launcher to active modal dialog so it stays interactive."""
        modal_parent = QApplication.activeModalWidget()
        if modal_parent is self:
            modal_parent = None
        target_parent = modal_parent if modal_parent is not None else self._default_parent

        flags = _WINDOW_FLAGS
        if self.parentWidget() is not target_parent:
            self.setParent(target_parent, flags)
        else:
            self.setWindowFlags(flags)
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)

    def _run_action(self, item: QListWidgetItem) -> None:
        action_cls = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(action_cls, type):
            return

        self.hide()
        action = action_cls(output_bus=self._output_bus)
        action()

    def _run_markdown_choice(self, title: str, *, ai_screenshot: bool) -> None:
        self.hide()
        OnNewMarkdown(output_bus=self._output_bus).execute_picker_choice(
            title,
            ai_screenshot=ai_screenshot,
        )

    def _set_markdown_choices(
        self,
        choices: list[tuple[str, str]],
        *,
        ai_screenshot_titles: set[str] | None = None,
    ) -> None:
        populate_icon_choice_cards(
            self._markdown_cards,
            choices,
            ai_screenshot_titles=ai_screenshot_titles,
            on_select=lambda title: self._run_markdown_choice(title, ai_screenshot=False),
            on_ai_screenshot=self._on_markdown_ai_screenshot,
        )

    def _start_drag(self, global_pos: QPoint) -> None:
        self._dragging = True
        self._drag_position = global_pos - self.frameGeometry().topLeft()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.grabMouse()

    def _update_hint(self) -> None:
        # Local import avoids circular dependency: action -> context -> dialog.
        from harrix_swiss_knife.actions.quick_launcher.action import OnQuickLauncher  # noqa: PLC0415

        hint_parts = ["Click a card to run", "Drag to move", "Esc or X to close"]
        hotkeys = load_hotkeys_for_action(OnQuickLauncher.__name__)
        if hotkeys:
            hint_parts.append(f"{' / '.join(hotkeys)} to toggle")
        self._hint.setText(" · ".join(hint_parts))


@dataclass(frozen=True)
class _ContentHeightMetrics:
    split: bool
    cards_natural: int
    markdown_natural: int
    sections_chrome: int
    window_chrome: int
    spacing_total: int
    grids_natural: int
    content_height: int


def _action_icon(action_cls: type[ActionBase], size: int = CARD_ICON_SIZE) -> QIcon:
    icon_name = getattr(action_cls, "icon", "") or ""
    if ".svg" in icon_name:
        return QIcon(f":/assets/{icon_name}")
    if icon_name:
        return create_emoji_icon(icon_name, size)
    return QIcon()


def _apply_card_grid_height(
    grid: QListWidget,
    *,
    natural: int,
    allocated: int,
) -> None:
    grid.setMinimumHeight(allocated)
    grid.setMaximumHeight(allocated)
    grid.setVerticalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAsNeeded if allocated < natural else Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
    )
    if allocated >= natural:
        grid.verticalScrollBar().setRange(0, 0)
        grid.horizontalScrollBar().setRange(0, 0)


def _layout_spacing_total(layout: QVBoxLayout, *, split: bool) -> int:
    # header, actions section, [markdown section], hint, resize row
    visible_items = 4 + (1 if split else 0)
    return layout.spacing() * max(0, visible_items - 1)


def _layout_vertical_chrome(layout: QVBoxLayout, hint: QLabel) -> int:
    margins = layout.contentsMargins()
    header_layout = layout.itemAt(0).layout()
    header_height = header_layout.sizeHint().height() if header_layout is not None else 0
    return margins.top() + margins.bottom() + header_height + hint.sizeHint().height()


def _section_chrome_height(section: QFrame) -> int:
    """Height of section card chrome (margins, title, spacing) excluding the grid."""
    layout = section.layout()
    if layout is None:
        return 0
    margins = layout.contentsMargins()
    chrome = margins.top() + margins.bottom()
    if layout.count() == 0:
        return chrome
    first = layout.itemAt(0)
    widget = first.widget() if first is not None else None
    if isinstance(widget, QLabel):
        chrome += widget.sizeHint().height() + layout.spacing()
    return chrome
