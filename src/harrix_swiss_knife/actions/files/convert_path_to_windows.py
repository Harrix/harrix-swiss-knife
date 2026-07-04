"""Convert a forward-slash path to Windows backslash format."""

from __future__ import annotations

from typing import Any

from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.base import ActionBase


class OnConvertPathToWindows(ActionBase):
    """Convert a path with forward slashes to Windows backslash format."""

    icon = "🪟"
    title = "Convert path to Windows"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("converting path to Windows format")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Show path dialog, convert slashes, and copy result to clipboard."""
        clipboard = QApplication.clipboard()
        default_path = ""
        if clipboard is not None:
            default_path = clipboard.text(QClipboard.Mode.Clipboard) or ""

        path = self.dialogs.get_text_input("Convert path to Windows", "Enter path:", default_path)
        if path is None:
            return

        windows_path = _to_windows_path(path)
        self.text_to_clipboard(windows_path)
        self.add_line(windows_path)
        self.show_result()


def _to_windows_path(text: str) -> str:
    """Normalize path text for Windows: trim, strip quotes, replace ``/`` with ``\\``."""
    return text.strip().strip('"').strip("'").replace("/", "\\")
