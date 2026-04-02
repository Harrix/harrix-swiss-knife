"""QMessageBox helpers with a Copy button for clipboard export."""

from __future__ import annotations

import weakref

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QAbstractButton, QMessageBox, QWidget

_copy_button_for_box: weakref.WeakKeyDictionary[QMessageBox, QAbstractButton] = weakref.WeakKeyDictionary()


def add_copy_button(box: QMessageBox) -> QAbstractButton:
    """Add a Copy button; on click, copy ``clipboard_text_from_box`` to the clipboard."""
    copy_btn = box.addButton("Copy", QMessageBox.ButtonRole.ActionRole)

    def on_clicked(button: QAbstractButton) -> None:
        if button is copy_btn:
            QGuiApplication.clipboard().setText(clipboard_text_from_box(box))

    box.buttonClicked.connect(on_clicked)
    return copy_btn


def clipboard_text_from_box(box: QMessageBox) -> str:
    """Build plain text for the clipboard from the dialog fields."""
    parts: list[str] = []
    title = box.windowTitle().strip()
    if title:
        parts.append(title)
    body = box.text().strip()
    if body:
        parts.append(body)
    detail = box.detailedText().strip()
    if detail:
        parts.append(detail)
    return "\n\n".join(parts)


def critical(parent: QWidget | None, title: str, text: str) -> QMessageBox.StandardButton:
    """Like ``QMessageBox.critical`` with a Copy button."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Critical)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    prepare_box(box)
    return exec_with_copy_retry(box)


def exec_with_copy_retry(box: QMessageBox) -> QMessageBox.StandardButton:
    """Run ``box`` until the user clicks a standard button (not Copy)."""
    prepare_box(box)
    copy_btn = _copy_button_for_box[box]
    while True:
        box.exec()
        clicked = box.clickedButton()
        if clicked is copy_btn:
            continue
        if clicked is None:
            return QMessageBox.StandardButton.Cancel
        sb = box.standardButton(clicked)
        return QMessageBox.StandardButton(sb)


def information(parent: QWidget | None, title: str, text: str) -> QMessageBox.StandardButton:
    """Like ``QMessageBox.information`` with a Copy button."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Information)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    prepare_box(box)
    return exec_with_copy_retry(box)


def prepare_box(box: QMessageBox) -> None:
    """Ensure ``box`` has a Copy button (idempotent)."""
    if box in _copy_button_for_box:
        return
    _copy_button_for_box[box] = add_copy_button(box)


def question(
    parent: QWidget | None,
    title: str,
    text: str,
    buttons: QMessageBox.StandardButton,
    default_button: QMessageBox.StandardButton,
) -> QMessageBox.StandardButton:
    """Like ``QMessageBox.question`` with a Copy button."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(buttons)
    box.setDefaultButton(default_button)
    prepare_box(box)
    return exec_with_copy_retry(box)


def warning(parent: QWidget | None, title: str, text: str) -> QMessageBox.StandardButton:
    """Like ``QMessageBox.warning`` with a Copy button."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Warning)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    prepare_box(box)
    return exec_with_copy_retry(box)
