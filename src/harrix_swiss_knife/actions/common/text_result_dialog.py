"""Shared result-dialog actions for text AI features."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harrix_swiss_knife.qt_lucide_icon import (
    COPY_BUTTON_ICON,
    OK_BUTTON_ICON,
    SAVE_BUTTON_ICON,
    make_lucide_push_button,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton

RERUN_DIALOG_CODE = 2
REWRITE_DIALOG_CODE = 3
TRANSLATE_DIALOG_CODE = 4

RERUN_BUTTON_LABEL = "Run again"
RERUN_BUTTON_ICON = "refresh-cw"
FIX_AGAIN_BUTTON_LABEL = "Fix again"
FIX_AGAIN_BUTTON_ICON = "astroid"
REWRITE_AGAIN_BUTTON_LABEL = "Rewrite again"
REWRITE_AGAIN_BUTTON_ICON = "square-pen"
REWRITE_BUTTON_LABEL = "Rewrite with AI…"
REWRITE_BUTTON_ICON = "square-pen"
TRANSLATE_BUTTON_LABEL = "Translate"
TRANSLATE_BUTTON_ICON = "languages"
REMOVE_PARAGRAPHS_BUTTON_LABEL = "To single line"
REMOVE_PARAGRAPHS_BUTTON_ICON = "text-wrap"
COPY_BUTTON_LABEL = "Copy to Clipboard"
SAVE_MARKDOWN_BUTTON_LABEL = "Save Markdown"
OPEN_FOLDER_BUTTON_LABEL = "Open folder"
OPEN_FOLDER_BUTTON_ICON = "folder-open"
OK_BUTTON_LABEL = "OK"
CANCEL_BUTTON_LABEL = "Cancel"


def add_copy_button(button_layout: QHBoxLayout, click_handler: Callable[[], None]) -> QPushButton:
    """Add a copy-to-clipboard button with a Lucide icon."""
    copy_button = make_lucide_push_button(COPY_BUTTON_LABEL, COPY_BUTTON_ICON)
    copy_button.clicked.connect(click_handler)
    button_layout.addWidget(copy_button)
    return copy_button


def add_ok_button(
    dialog: QDialog,
    button_layout: QHBoxLayout,
    *,
    label: str = OK_BUTTON_LABEL,
    icon: str = OK_BUTTON_ICON,
) -> QPushButton:
    """Add a dismiss/confirm button with a Lucide icon.

    Callers that pair this with a separate Apply-style action should pass
    `Cancel` so the dismiss button is not mistaken for confirmation.

    """
    ok_button = make_lucide_push_button(label, icon)
    ok_button.clicked.connect(dialog.accept)
    button_layout.addWidget(ok_button)
    return ok_button


def add_open_folder_button(button_layout: QHBoxLayout, click_handler: Callable[[], None]) -> QPushButton:
    """Add an open-folder button with a Lucide icon."""
    open_folder_button = make_lucide_push_button(OPEN_FOLDER_BUTTON_LABEL, OPEN_FOLDER_BUTTON_ICON)
    open_folder_button.clicked.connect(click_handler)
    button_layout.addWidget(open_folder_button)
    return open_folder_button


def add_save_markdown_button(button_layout: QHBoxLayout, click_handler: Callable[[], None]) -> QPushButton:
    """Add a save-markdown button with a Lucide icon."""
    save_button = make_lucide_push_button(SAVE_MARKDOWN_BUTTON_LABEL, SAVE_BUTTON_ICON)
    save_button.clicked.connect(click_handler)
    button_layout.addWidget(save_button)
    return save_button


def append_result_action_buttons(
    dialog: QDialog,
    button_layout: QHBoxLayout,
    *,
    rerun_button: bool = False,
    rerun_button_label: str = RERUN_BUTTON_LABEL,
    rerun_button_icon: str = RERUN_BUTTON_ICON,
    rewrite_button: bool = False,
    translate_button: bool = False,
    remove_paragraphs_button: bool = False,
    on_remove_paragraphs: Callable[[], None] | None = None,
    remove_paragraphs_source_text: str = "",
) -> QPushButton | None:
    """Add optional rerun/rewrite/translate buttons and in-place remove-paragraphs action.

    The "To single line" button is created only when requested and the source text
    has more than one line after trimming.

    """
    if rerun_button:
        rerun_btn = make_lucide_push_button(rerun_button_label, rerun_button_icon)
        rerun_btn.clicked.connect(lambda: dialog.done(RERUN_DIALOG_CODE))
        button_layout.addWidget(rerun_btn)

    if rewrite_button:
        rewrite_btn = make_lucide_push_button(REWRITE_BUTTON_LABEL, REWRITE_BUTTON_ICON)
        rewrite_btn.clicked.connect(lambda: dialog.done(REWRITE_DIALOG_CODE))
        button_layout.addWidget(rewrite_btn)

    if translate_button:
        translate_btn = make_lucide_push_button(TRANSLATE_BUTTON_LABEL, TRANSLATE_BUTTON_ICON)
        translate_btn.setToolTip("Translate into the local language from config")
        translate_btn.clicked.connect(lambda: dialog.done(TRANSLATE_DIALOG_CODE))
        button_layout.addWidget(translate_btn)

    if not remove_paragraphs_button or on_remove_paragraphs is None:
        return None
    if not is_multiline_text(remove_paragraphs_source_text):
        return None

    remove_paragraphs_btn = make_lucide_push_button(
        REMOVE_PARAGRAPHS_BUTTON_LABEL,
        REMOVE_PARAGRAPHS_BUTTON_ICON,
    )
    remove_paragraphs_btn.clicked.connect(on_remove_paragraphs)
    button_layout.addWidget(remove_paragraphs_btn)
    return remove_paragraphs_btn


def collapse_text_to_single_line(text: str) -> str:
    """Replace line breaks and paragraph gaps with single spaces."""
    return re.sub(r"\s+", " ", text).strip()


def is_multiline_text(text: str) -> bool:
    """Return `True` when trimmed `text` contains more than one line.

    A trailing newline alone does not count as a second line.

    """
    return len(text.strip().splitlines()) > 1


def resolve_text_result_dialog_action(
    action_code: int,
    _current_text: str,
    *,
    on_rerun: Callable[[], None] | None = None,
    on_rewrite: Callable[[], None] | None = None,
    on_translate: Callable[[], None] | None = None,
) -> str | None:
    """Handle custom dialog codes. Always returns `None` after optional callbacks."""
    if action_code == RERUN_DIALOG_CODE:
        if on_rerun is not None:
            on_rerun()
        return None
    if action_code == REWRITE_DIALOG_CODE:
        if on_rewrite is not None:
            on_rewrite()
        return None
    if action_code == TRANSLATE_DIALOG_CODE:
        if on_translate is not None:
            on_translate()
        return None
    return None
