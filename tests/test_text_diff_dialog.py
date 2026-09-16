"""Tests for side-by-side text diff copy buttons."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSize
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QVBoxLayout

from harrix_swiss_knife.actions.common.text_diff_dialog import build_text_diff_side_by_side
from harrix_swiss_knife.actions.common.text_result_dialog import (
    COPY_BUTTON_LABEL,
    COPY_TRANSLATION_BUTTON_LABEL,
)


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_copy_before_and_copy_translation_buttons(qapp: QApplication) -> None:  # noqa: ARG001
    toasts: list[str] = []
    dialog = QDialog()
    layout = QVBoxLayout(dialog)
    build_text_diff_side_by_side(
        "Hello world",
        "Привет мир",
        QSize(800, 600),
        toasts.append,
        before_label="Original",
        after_label="Translation",
        highlight_changes=False,
        copy_before=True,
        copy_after_button=True,
    )(dialog, layout)

    buttons = {button.text(): button for button in dialog.findChildren(QPushButton)}
    assert COPY_BUTTON_LABEL in buttons
    assert COPY_TRANSLATION_BUTTON_LABEL in buttons

    clipboard = QGuiApplication.clipboard()
    buttons[COPY_BUTTON_LABEL].click()
    assert clipboard.text() == "Hello world"
    assert toasts[-1] == "Copied to Clipboard"

    buttons[COPY_TRANSLATION_BUTTON_LABEL].click()
    assert clipboard.text() == "Привет мир"
    assert toasts[-1] == "Translation copied to Clipboard"

    dialog.close()
