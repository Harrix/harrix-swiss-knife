"""Quick launcher overlay and hotkey capture dialogs."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QKeyEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from harrix_swiss_knife.global_hotkey import hotkey_string_from_event
from harrix_swiss_knife.qt_emoji_icon import create_emoji_icon
from harrix_swiss_knife.win11_backdrop import SystemBackdrop, try_apply_system_backdrop

if TYPE_CHECKING:
    from harrix_swiss_knife.action_output_bus import ActionOutputBus
    from harrix_swiss_knife.actions.base import ActionBase

_CARD_ICON_SIZE = 64
_CARD_SPACING = 16
_OVERLAY_MIN_SIZE = QSize(900, 560)
_OVERLAY_DEFAULT_SIZE = QSize(1024, 720)


class HotkeyCaptureDialog(QDialog):
    """Capture a keyboard shortcut for the quick launcher global hotkey."""

    hotkey_captured = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the hotkey capture dialog."""
        super().__init__(parent)
        self.setWindowTitle("Quick launcher hotkey")
        self.setModal(True)
        self.setMinimumWidth(420)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Press the key combination for the quick launcher.\n"
                "It will work globally while Harrix Swiss Knife is running in the tray.",
            ),
        )
        self._preview = QLabel("Waiting for keys…")
        preview_font = QFont(self._preview.font())
        preview_font.setPointSize(preview_font.pointSize() + 2)
        preview_font.setBold(True)
        self._preview.setFont(preview_font)
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._preview)

        buttons = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        save_button = QPushButton("Save")
        save_button.setDefault(True)
        save_button.clicked.connect(self._save)
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)
        layout.addLayout(buttons)

        self._captured_hotkey = ""

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Capture modifier + key and preview the portable hotkey string."""
        key = event.key()
        if key in {Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter}:
            super().keyPressEvent(event)
            return

        modifiers = event.modifiers() & Qt.KeyboardModifier.KeyboardModifierMask
        if key in {
            Qt.Key.Key_Control,
            Qt.Key.Key_Shift,
            Qt.Key.Key_Alt,
            Qt.Key.Key_Meta,
            Qt.Key.Key_AltGr,
        }:
            self._preview.setText("Press a key with modifiers (Ctrl, Alt, Shift, Win)…")
            event.accept()
            return

        if modifiers == Qt.KeyboardModifier.NoModifier:
            self._preview.setText("Add at least one modifier (Ctrl, Alt, Shift, or Win)…")
            event.accept()
            return

        self._captured_hotkey = hotkey_string_from_event(key, modifiers)
        self._preview.setText(self._captured_hotkey)
        event.accept()

    def _save(self) -> None:
        if not self._captured_hotkey.strip():
            self._preview.setText("Press a key combination first.")
            return
        self.hotkey_captured.emit(self._captured_hotkey)
        self.accept()


class QuickLauncherDialog(QDialog):
    """Always-on-top overlay listing quick-launcher actions."""

    _instance: ClassVar[QuickLauncherDialog | None] = None

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the quick launcher overlay dialog."""
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=False)
        self.setMinimumSize(_OVERLAY_MIN_SIZE)
        self.resize(_OVERLAY_DEFAULT_SIZE)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)

        self._output_bus: ActionOutputBus | None = None
        self._action_classes: list[type[ActionBase]] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Quick launcher")
        title_font = QFont(title.font())
        title_font.setPointSize(title_font.pointSize() + 1)
        title_font.setBold(True)
        title.setFont(title_font)

        close_button = QPushButton("X")
        close_button.setFixedSize(28, 28)
        close_button.setFlat(True)
        close_button.setToolTip("Close")
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.clicked.connect(self.hide)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_button)
        layout.addLayout(header)

        self._cards = QListWidget(self)
        _configure_action_card_grid(self._cards)
        self._cards.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._cards, stretch=1)

        hint = QLabel("Click a card to run · Esc or X to close")
        hint.setStyleSheet("color: palette(mid);")
        layout.addWidget(hint)

        self._center_on_screen()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Hide the overlay on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
            return
        super().keyPressEvent(event)

    def present(self) -> None:
        """Center, show, and focus the overlay."""
        self.resize(_OVERLAY_DEFAULT_SIZE)
        self._center_on_screen()
        self.show()
        self.raise_()
        self.activateWindow()
        if self._cards.count():
            self._cards.setCurrentRow(0)
            self._cards.setFocus()

    def set_action_classes(self, action_classes: list[type[ActionBase]]) -> None:
        """Rebuild the action card grid."""
        self._action_classes = list(action_classes)
        self._cards.clear()
        for action_cls in self._action_classes:
            item = QListWidgetItem(action_cls.title, self._cards)
            item.setData(Qt.ItemDataRole.UserRole, action_cls)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            item.setIcon(_action_icon(action_cls, _CARD_ICON_SIZE))
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

    def _center_on_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.availableGeometry()
        x = geometry.center().x() - self.width() // 2
        y = geometry.center().y() - self.height() // 3
        self.move(x, y)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        self._run_action(item)

    def _run_action(self, item: QListWidgetItem) -> None:
        action_cls = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(action_cls, type):
            return

        self.hide()
        action = action_cls(output_bus=self._output_bus)
        action()


def _action_icon(action_cls: type[ActionBase], size: int = _CARD_ICON_SIZE) -> QIcon:
    icon_name = getattr(action_cls, "icon", "") or ""
    if ".svg" in icon_name:
        return QIcon(f":/assets/{icon_name}")
    if icon_name:
        return create_emoji_icon(icon_name, size)
    return QIcon()


def _configure_action_card_grid(list_widget: QListWidget) -> None:
    """Apply the same icon-card layout used by New Markdown command picker."""
    list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    list_widget.setMinimumHeight(_OVERLAY_DEFAULT_SIZE.height() - 140)
    list_widget.setViewMode(QListWidget.ViewMode.IconMode)
    list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
    list_widget.setMovement(QListWidget.Movement.Static)
    list_widget.setSpacing(_CARD_SPACING)
    list_widget.setIconSize(QSize(_CARD_ICON_SIZE, _CARD_ICON_SIZE))
    list_widget.setWordWrap(True)
    list_widget.setUniformItemSizes(False)
    list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    list_widget.setFrameShape(QListWidget.Shape.NoFrame)
