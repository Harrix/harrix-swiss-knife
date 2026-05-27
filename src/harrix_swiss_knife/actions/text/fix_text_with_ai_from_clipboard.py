"""Fix text with AI (BotHub) from clipboard and copy result back."""

from __future__ import annotations

from typing import Any

from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.integrations.bothub import build_text_fix_prompt, fix_text_sync
from harrix_swiss_knife.integrations.bothub_client import BotHubApiError


class OnFixTextWithAIFromClipboard(ActionBase):
    """Fix clipboard text with BotHub and put corrected text back to clipboard."""

    icon = "🤖"
    title = "Fix text with AI from clipboard"
    bold_title = False
    cli_available = False

    @ActionBase.handle_exceptions("fixing clipboard text with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Read clipboard text, call BotHub, and copy fixed text to clipboard."""
        clipboard = QApplication.clipboard()
        if clipboard is None:
            self.show_toast("❌ Clipboard is not available.", duration=4000)
            return

        input_text = clipboard.text(QClipboard.Mode.Clipboard) or ""
        if not input_text.strip():
            self.show_toast("❌ Clipboard text is empty.", duration=4000)
            return

        try:
            build_text_fix_prompt(input_text, self.config)
        except ValueError as exc:
            self.show_toast(f"❌ {exc!s}", duration=6000)
            return

        def work() -> str:
            try:
                return fix_text_sync(input_text, self.config)
            except BotHubApiError as exc:
                raise RuntimeError(str(exc)) from exc

        def on_done(result: object) -> None:
            if not isinstance(result, str) or not result.strip():
                self.show_toast("❌ BotHub error: empty response.", duration=6000)
                return

            clipboard.setText(result, QClipboard.Mode.Clipboard)
            self.show_toast("✅ Fixed text copied to clipboard.", duration=4000)

        self.start_thread(work, on_done, "Requesting BotHub…")
