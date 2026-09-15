"""Picker dialog for screenshot / record actions after a capture hotkey long-press."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QVBoxLayout,
)

from harrix_swiss_knife.action_title import strip_md_inline_code_markers
from harrix_swiss_knife.actions.common.dialog_geometry import (
    center_widget_on_available_screen,
    fit_widget_height,
    icon_grid_content_height,
)
from harrix_swiss_knife.actions.images.record_region import OnRecordRegion
from harrix_swiss_knife.actions.images.screenshot_region import OnScreenshotRegion
from harrix_swiss_knife.actions.images.screenshot_region_clipboard import OnScreenshotRegionClipboard
from harrix_swiss_knife.actions.images.screenshot_region_translate import OnScreenshotRegionTranslate
from harrix_swiss_knife.qt_action_icon import resolve_ui_icon_spec
from harrix_swiss_knife.qt_command_section import create_command_section
from harrix_swiss_knife.qt_described_choice_cards import (
    add_described_action_card,
    configure_described_choice_card_grid,
    sync_described_choice_card_grid,
)
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_dialog_buttons
from harrix_swiss_knife.win11_backdrop import SystemBackdrop, try_apply_system_backdrop

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

    from harrix_swiss_knife.actions.common.base import ActionBase

CAPTURE_PICKER_ACTIONS: tuple[type[ActionBase], ...] = (
    OnScreenshotRegion,
    OnScreenshotRegionClipboard,
    OnScreenshotRegionTranslate,
    OnRecordRegion,
)


def choose_capture_hotkey_action(*, parent: QWidget | None = None) -> str | None:
    """Show the capture-action picker and return the selected class name, or `None`."""
    dialog = CaptureActionPickerDialog(parent)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.selected_action_name()


class CaptureActionPickerDialog(QDialog):
    """Modal list of screenshot / record actions for a long-pressed capture hotkey."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the picker with described choice cards for each capture action."""
        super().__init__(parent)
        self.setWindowTitle("Capture")
        self.setModal(True)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, on=True)
        try_apply_system_backdrop(self, backdrop=SystemBackdrop.MICA)
        self.resize(720, 420)

        self._selected: str | None = None
        self._list = QListWidget(self)
        configure_described_choice_card_grid(self._list)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        hint = QLabel("Choose a capture action")
        hint.setWordWrap(True)
        root.addWidget(hint)

        section, _, section_layout = create_command_section(title="Actions")
        for action_cls in CAPTURE_PICKER_ACTIONS:
            add_described_action_card(
                self._list,
                icon=resolve_ui_icon_spec(action_cls),
                title=strip_md_inline_code_markers(action_cls.title),
                description=action_cls.resolve_description(),
                user_data=action_cls.__name__,
                on_select=lambda name=action_cls.__name__: self._accept_action(name),
            )
        sync_described_choice_card_grid(self._list)
        fit_widget_height(self._list, icon_grid_content_height(self._list), maximum=360)
        section_layout.addWidget(self._list)
        root.addWidget(section, stretch=1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        apply_lucide_dialog_buttons(buttons)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        center_widget_on_available_screen(self)

    def selected_action_name(self) -> str | None:
        """Return the action class name chosen by the user."""
        return self._selected

    def _accept_action(self, action_name: str) -> None:
        self._selected = action_name
        self.accept()
