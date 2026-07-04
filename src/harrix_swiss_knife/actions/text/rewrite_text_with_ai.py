"""Rewrite text with AI (BotHub) for deep literary editing while preserving code spans/blocks."""

from __future__ import annotations

from typing import Any

from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.integrations.bothub import run_bothub_request
from harrix_swiss_knife.integrations.bothub.text_rewrite import (
    PROMPT_MISSING_MSG,
    build_text_rewrite_prompt,
    rewrite_text_sync,
)
from harrix_swiss_knife.integrations.bothub_client import BotHubApiError


class OnRewriteTextWithAI(ActionBase):
    """Send text to BotHub and return deeply rewritten text (no changes in `...` / code blocks)."""

    icon = "✍️"
    title = "Rewrite text with AI…"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("rewriting text with AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Collect text, call BotHub, and show rewritten output."""
        cli_sync = bool(kwargs.get("cli_sync", False))

        input_text = self.dialogs.get_text_textarea(
            "Rewrite text with AI",
            "Paste text for deep rewrite (grammar, style, sentence flow).\nCode in backticks must remain unchanged.",
        )
        if input_text is None:
            return

        try:
            prompt_text = build_text_rewrite_prompt(input_text, self.config)
        except ValueError as exc:
            msg = str(exc)
            if msg == PROMPT_MISSING_MSG:
                message_box.warning(None, "Prompt", msg)
            else:
                message_box.critical(None, "BotHub API Key", msg)
            return

        if cli_sync:
            try:
                result = rewrite_text_sync(input_text, self.config)
            except BotHubApiError as exc:
                message_box.critical(None, "BotHub Error", str(exc))
                return

            if not result.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return

            QApplication.clipboard().setText(result, QClipboard.Mode.Clipboard)
            self.show_text_multiline(result, title="Rewritten text (copied to clipboard)")
            return

        def on_success(response_text: str) -> None:
            if not response_text.strip():
                message_box.critical(None, "BotHub Error", "Empty response from BotHub.")
                return
            self.text_to_clipboard(response_text)
            self.dialogs.show_text_diff_side_by_side(
                input_text,
                response_text,
                title="Rewritten text diff (Before/After)",
            )

        def on_error(message: str) -> None:
            message_box.critical(None, "BotHub Error", message)

        run_bothub_request(
            None,
            self.config,
            prompt_text,
            on_success,
            on_error=on_error,
        )
