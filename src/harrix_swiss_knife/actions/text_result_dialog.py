"""Shared result-dialog actions for text AI features."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton

RERUN_DIALOG_CODE = 2
REWRITE_DIALOG_CODE = 3

RERUN_BUTTON_LABEL = "Run again"
REWRITE_BUTTON_LABEL = "Rewrite with AI…"


def append_result_action_buttons(
    dialog: QDialog,
    button_layout: QHBoxLayout,
    *,
    rerun_button: bool = False,
    rewrite_button: bool = False,
) -> None:
    """Add optional rerun/rewrite buttons that close the dialog with custom result codes."""
    if rerun_button:
        rerun_btn = QPushButton(RERUN_BUTTON_LABEL)
        rerun_btn.clicked.connect(lambda: dialog.done(RERUN_DIALOG_CODE))
        button_layout.addWidget(rerun_btn)

    if rewrite_button:
        rewrite_btn = QPushButton(REWRITE_BUTTON_LABEL)
        rewrite_btn.clicked.connect(lambda: dialog.done(REWRITE_DIALOG_CODE))
        button_layout.addWidget(rewrite_btn)
