"""Shared result-dialog actions for text AI features."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton

if TYPE_CHECKING:
    from collections.abc import Callable

RERUN_DIALOG_CODE = 2
REWRITE_DIALOG_CODE = 3
REMOVE_PARAGRAPHS_DIALOG_CODE = 4

RERUN_BUTTON_LABEL = "Run again"
REWRITE_BUTTON_LABEL = "Rewrite with AI…"
REMOVE_PARAGRAPHS_BUTTON_LABEL = "To single line"


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
        rerun_btn = QPushButton(RERUN_BUTTON_LABEL)
        rerun_btn.clicked.connect(lambda: dialog.done(RERUN_DIALOG_CODE))
        button_layout.addWidget(rerun_btn)

    if rewrite_button:
        rewrite_btn = QPushButton(REWRITE_BUTTON_LABEL)
        rewrite_btn.clicked.connect(lambda: dialog.done(REWRITE_DIALOG_CODE))
        button_layout.addWidget(rewrite_btn)

    if remove_paragraphs_button:
        remove_paragraphs_btn = QPushButton(REMOVE_PARAGRAPHS_BUTTON_LABEL)
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
