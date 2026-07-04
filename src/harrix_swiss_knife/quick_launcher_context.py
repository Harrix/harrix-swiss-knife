"""Shared quick launcher wiring for tray startup and the OnQuickLauncher action."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.quick_launcher_dialog import QuickLauncherDialog
from harrix_swiss_knife.quick_launcher_registry import collect_quick_launcher_actions

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import QWidget

    from harrix_swiss_knife.action_output_bus import ActionOutputBus
    from harrix_swiss_knife.actions.base import ActionBase
    from harrix_swiss_knife.global_hotkey import GlobalHotkeyManager


class QuickLauncherContext:
    """Holds quick launcher dependencies for menu action and global hotkey."""

    def __init__(
        self,
        *,
        output_bus: ActionOutputBus | None,
        hotkey_manager: GlobalHotkeyManager | None,
        menu_structure_provider: Callable[[], list[Any]],
        parent: QWidget | None = None,
    ) -> None:
        """Store dependencies used by the tray action and global hotkey handler."""
        self.output_bus = output_bus
        self.hotkey_manager = hotkey_manager
        self._menu_structure_provider = menu_structure_provider
        self.parent = parent

    def action_classes(self) -> list[type[ActionBase]]:
        """Return quick-launcher action classes from the current menu structure."""
        return collect_quick_launcher_actions(self._menu_structure_provider())

    def toggle(self) -> None:
        """Toggle the quick launcher overlay."""
        QuickLauncherDialog.toggle(
            parent=self.parent,
            output_bus=self.output_bus,
            action_classes=self.action_classes(),
        )


def get_quick_launcher_context() -> QuickLauncherContext | None:
    """Return the process-wide quick launcher context, if initialized."""
    return _context


def set_quick_launcher_context(context: QuickLauncherContext | None) -> None:
    """Set the process-wide quick launcher context."""
    global _context  # noqa: PLW0603
    _context = context


_context: QuickLauncherContext | None = None
