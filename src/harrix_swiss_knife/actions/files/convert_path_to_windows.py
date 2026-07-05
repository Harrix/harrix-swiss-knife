"""Convert a forward-slash path to Windows backslash format from clipboard."""

from __future__ import annotations

from typing import Any

from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.base import ActionBase


class OnConvertPathToWindows(ActionBase):
    """Convert clipboard path with forward slashes to Windows backslash format."""

    icon = "🪟"
    title = "Convert path to Windows from clipboard"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("converting path to Windows format")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Read path from clipboard, convert slashes, and copy result back."""
        clipboard = QApplication.clipboard()
        if clipboard is None:
            self.show_toast("❌ Clipboard is not available.", duration=4000)
            return

        input_text = clipboard.text(QClipboard.Mode.Clipboard) or ""
        if not input_text.strip():
            self.show_toast("❌ Clipboard text is empty.", duration=4000)
            return

        windows_path = _to_windows_path(input_text)
        clipboard.setText(windows_path, QClipboard.Mode.Clipboard)
        self.show_toast("✅ Windows path copied to clipboard.", duration=4000)


def _to_windows_path(text: str) -> str:
    r"""Normalize path text for Windows: trim, strip quotes, replace ``/`` with ``\\``."""
    return text.strip().strip('"').strip("'").replace("/", "\\")
