"""Open the quick launcher overlay (global hotkey on Windows)."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h
from PySide6.QtWidgets import QMessageBox

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.paths import get_config_path_str
from harrix_swiss_knife.quick_launcher_context import get_quick_launcher_context
from harrix_swiss_knife.quick_launcher_dialog import HotkeyCaptureDialog


class OnQuickLauncher(ActionBase):
    """Show quick launcher overlay; configure global hotkey on first run (Windows)."""

    icon = "⚡"
    title = "Quick launcher…"
    bold_title = False
    cli_available = False

    @ActionBase.handle_exceptions("opening quick launcher")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Configure hotkey if needed, then toggle the quick launcher overlay."""
        context = get_quick_launcher_context()
        if context is None:
            message_box.critical(None, "Quick launcher", "Quick launcher is not initialized.")
            return

        hotkey = str(self.config.get("quick_launcher_hotkey") or "").strip()
        if not hotkey:
            dialog = HotkeyCaptureDialog()
            captured: dict[str, str] = {"value": ""}

            def on_captured(value: str) -> None:
                captured["value"] = value

            dialog.hotkey_captured.connect(on_captured)
            if dialog.exec() != dialog.DialogCode.Accepted or not captured["value"].strip():
                return

            hotkey = captured["value"].strip()
            h.dev.config_update_value("quick_launcher_hotkey", hotkey, get_config_path_str())
            self.config["quick_launcher_hotkey"] = hotkey

            if context.hotkey_manager is not None and not context.hotkey_manager.register(hotkey):
                QMessageBox.warning(
                    None,
                    "Quick launcher hotkey",
                    "Could not register the hotkey. Choose another combination from the tray menu.",
                )

        elif context.hotkey_manager is not None and not context.hotkey_manager.registered_hotkey:
            context.hotkey_manager.register(hotkey)

        context.toggle()
