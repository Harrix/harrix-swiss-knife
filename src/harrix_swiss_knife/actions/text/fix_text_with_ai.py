"""Fix text with AI (BotHub) while preserving code spans/blocks."""

from __future__ import annotations

from typing import Any

from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.actions.text_result_dialog import RERUN_DIALOG_CODE
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.integrations.bothub import (
    PROMPT_MISSING_MSG,
    build_text_fix_prompt,
    fix_text_sync,
    run_bothub_request,
)
from harrix_swiss_knife.integrations.bothub_client import BotHubApiError


class OnFixTextWithAI(ActionBase):
    """Send text to BotHub and return corrected text (no changes in `...` / code blocks)."""

    icon = "🤖"
    title = "Fix text with AI…"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("fixing text with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Collect text, call BotHub, and show corrected output."""
        self._run(initial_text=kwargs.get("initial_text"), cli_sync=bool(kwargs.get("cli_sync", False)))

    def _run(self, *, initial_text: str | None = None, cli_sync: bool = False) -> None:
        if initial_text is None:
            input_text = self.dialogs.get_text_textarea(
                "Fix text with AI",
                "Paste text to fix (punctuation, typos, style).\nCode in backticks must remain unchanged.",
            )
            if input_text is None:
                return
        else:
            input_text = initial_text

        try:
            prompt_text = build_text_fix_prompt(input_text, self.config)
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
            dialog_result = self.show_text_multiline(
                result,
                title="Fixed text (copied to clipboard)",
                rerun_button=True,
            )
            if isinstance(dialog_result, tuple):
                _, action_code = dialog_result
                if action_code == RERUN_DIALOG_CODE:
                    self._run(initial_text=result, cli_sync=True)
            return

        def on_success(response_text: str) -> None:
            if not response_text.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return
            self.text_to_clipboard(response_text)
            _, action_code = self.dialogs.show_text_diff_side_by_side(
                input_text,
                response_text,
                title="Fixed text diff (Before/After)",
                rerun_button=True,
            )
            if action_code == RERUN_DIALOG_CODE:
                self._run(initial_text=response_text)

        def on_error(message: str) -> None:
            message_box.critical(None, "BotHub Error", message)

        run_bothub_request(
            None,
            self.config,
            prompt_text,
            on_success,
            on_error=on_error,
        )
