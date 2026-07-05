"""Shared result-dialog actions for text AI features."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton

from harrix_swiss_knife.qt_emoji_icon import make_emoji_push_button

if TYPE_CHECKING:
    from collections.abc import Callable

RERUN_DIALOG_CODE = 2
REWRITE_DIALOG_CODE = 3
REMOVE_PARAGRAPHS_DIALOG_CODE = 4

RERUN_BUTTON_LABEL = "Run again"
RERUN_BUTTON_EMOJI = "🔄"
REWRITE_BUTTON_LABEL = "Rewrite with AI…"
REWRITE_BUTTON_EMOJI = "✍️"
REMOVE_PARAGRAPHS_BUTTON_LABEL = "To single line"
REMOVE_PARAGRAPHS_BUTTON_EMOJI = "↪️"
COPY_BUTTON_LABEL = "Copy to Clipboard"
COPY_BUTTON_EMOJI = "📋"
OK_BUTTON_LABEL = "OK"
OK_BUTTON_EMOJI = "✅"
CANCEL_BUTTON_EMOJI = "❌"


def add_copy_button(button_layout: QHBoxLayout, click_handler: Callable[[], None]) -> QPushButton:
    """Add a copy-to-clipboard button with an emoji icon."""
    copy_button = make_emoji_push_button(COPY_BUTTON_LABEL, COPY_BUTTON_EMOJI)
    copy_button.clicked.connect(click_handler)
    button_layout.addWidget(copy_button)
    return copy_button


def add_ok_button(dialog: QDialog, button_layout: QHBoxLayout) -> QPushButton:
    """Add an OK button with an emoji icon."""
    ok_button = make_emoji_push_button(OK_BUTTON_LABEL, OK_BUTTON_EMOJI)
    ok_button.clicked.connect(dialog.accept)
    button_layout.addWidget(ok_button)
    return ok_button


def append_result_action_buttons(
    dialog: QDialog,
    button_layout: QHBoxLayout,
    *,
    rerun_button: bool = False,
    rewrite_button: bool = False,
    remove_paragraphs_button: bool = False,
) -> None:
    """Add optional rerun/rewrite/remove-paragraphs buttons that close the dialog with custom codes."""
    if rerun_button:
        rerun_btn = make_emoji_push_button(RERUN_BUTTON_LABEL, RERUN_BUTTON_EMOJI)
        rerun_btn.clicked.connect(lambda: dialog.done(RERUN_DIALOG_CODE))
        button_layout.addWidget(rerun_btn)

    if rewrite_button:
        rewrite_btn = make_emoji_push_button(REWRITE_BUTTON_LABEL, REWRITE_BUTTON_EMOJI)
        rewrite_btn.clicked.connect(lambda: dialog.done(REWRITE_DIALOG_CODE))
        button_layout.addWidget(rewrite_btn)

    if remove_paragraphs_button:
        remove_paragraphs_btn = make_emoji_push_button(
            REMOVE_PARAGRAPHS_BUTTON_LABEL,
            REMOVE_PARAGRAPHS_BUTTON_EMOJI,
        )
        remove_paragraphs_btn.clicked.connect(lambda: dialog.done(REMOVE_PARAGRAPHS_DIALOG_CODE))
        button_layout.addWidget(remove_paragraphs_btn)


def collapse_text_to_single_line(text: str) -> str:
    """Replace line breaks and paragraph gaps with single spaces."""
    return re.sub(r"\s+", " ", text).strip()


def resolve_text_result_dialog_action(
    action_code: int,
    current_text: str,
    *,
    on_rerun: Callable[[], None] | None = None,
    on_rewrite: Callable[[], None] | None = None,
) -> str | None:
    """Handle custom dialog codes. Return updated text to continue the loop, or None to stop."""
    if action_code == RERUN_DIALOG_CODE:
        if on_rerun is not None:
            on_rerun()
        return None
    if action_code == REWRITE_DIALOG_CODE:
        if on_rewrite is not None:
            on_rewrite()
        return None
    if action_code == REMOVE_PARAGRAPHS_DIALOG_CODE:
        return collapse_text_to_single_line(current_text)
    return None
