"""Fix text with AI (BotHub) while preserving code spans/blocks."""

from __future__ import annotations

from typing import Any

from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.integrations.bothub_client import BotHubApiError
from harrix_swiss_knife.services.text_fix_bothub import (
    PROMPT_MISSING_MSG,
    build_text_fix_prompt,
    fix_text_sync,
)


class OnFixTextWithAI(ActionBase):
    """Send text to BotHub and return corrected text (no changes in `...` / code blocks)."""

    icon = "🤖"
    title = "Fix text with AI"
    bold_title = False
    cli_available = False

    @ActionBase.handle_exceptions("fixing text with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Collect text, call BotHub, and show corrected output."""
        cli_sync = bool(kwargs.get("cli_sync", False))

        input_text = self.dialogs.get_text_textarea(
            "Fix text with AI",
            "Paste text to fix (punctuation, typos, style).\nCode in backticks must remain unchanged.",
        )
        if input_text is None:
            return

        try:
            build_text_fix_prompt(input_text, self.config)
        except ValueError as exc:
            msg = str(exc)
            if msg == PROMPT_MISSING_MSG:
                message_box.warning(None, "Prompt", msg)
            else:
                message_box.critical(None, "BotHub API Key", msg)
            return

        if cli_sync:
            try:
                result = fix_text_sync(input_text, self.config)
            except BotHubApiError as exc:
                message_box.critical(None, "BotHub Error", str(exc))
                return

            if not result.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return

            QApplication.clipboard().setText(result, QClipboard.Mode.Clipboard)
            self.show_text_multiline(result, title="Fixed text (copied to clipboard)")
            return

        def work() -> str:
            try:
                return fix_text_sync(input_text, self.config)
            except BotHubApiError as exc:
                raise RuntimeError(str(exc)) from exc

        def on_done(result: object) -> None:
            if not isinstance(result, str) or not result.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return
            self.text_to_clipboard(result)
            self.show_text_multiline(result, title="Fixed text (copied to clipboard)")

        self.start_thread(work, on_done, "Requesting BotHub…")
