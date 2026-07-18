"""QMessageBox helpers with a Copy button for clipboard export."""

from __future__ import annotations

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QAbstractButton, QMessageBox, QWidget

_COPY_BUTTON_ATTR = "_harrix_copy_button_added"


def add_copy_button(box: QMessageBox) -> QAbstractButton:
    """Add a Copy button; on click, copy `clipboard_text_from_box` to the clipboard."""
    copy_btn = box.addButton("Copy", QMessageBox.ButtonRole.ActionRole)
    copy_btn.clicked.disconnect()

    def _copy_box_text() -> None:
        QGuiApplication.clipboard().setText(clipboard_text_from_box(box))

    copy_btn.clicked.connect(_copy_box_text)
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
    """Like `QMessageBox.critical` with a Copy button."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Critical)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    prepare_box(box)
    return _exec_box(box)


def information(
    parent: QWidget | None,
    title: str,
    text: str,
    *,
    stylesheet: str | None = None,
) -> QMessageBox.StandardButton:
    """Like `QMessageBox.information` with a Copy button."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Information)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    if stylesheet:
        box.setStyleSheet(stylesheet)
    prepare_box(box)
    return _exec_box(box)


def prepare_box(box: QMessageBox) -> None:
    """Ensure `box` has a Copy button (idempotent)."""
    if getattr(box, _COPY_BUTTON_ATTR, False):
        return
    add_copy_button(box)
    setattr(box, _COPY_BUTTON_ATTR, True)


def question(
    parent: QWidget | None,
    title: str,
    text: str,
    buttons: QMessageBox.StandardButton,
    default_button: QMessageBox.StandardButton,
) -> QMessageBox.StandardButton:
    """Like `QMessageBox.question` with a Copy button."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(buttons)
    box.setDefaultButton(default_button)
    prepare_box(box)
    return _exec_box(box)


def warning(parent: QWidget | None, title: str, text: str) -> QMessageBox.StandardButton:
    """Like `QMessageBox.warning` with a Copy button."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Warning)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    prepare_box(box)
    return _exec_box(box)


def _exec_box(box: QMessageBox) -> QMessageBox.StandardButton:
    """Run `box` until the user clicks a standard button."""
    result_code = box.exec()
    clicked = box.clickedButton()
    if clicked is None or result_code == QMessageBox.DialogCode.Rejected:
        return QMessageBox.StandardButton.Cancel
    sb = box.standardButton(clicked)
    return QMessageBox.StandardButton(sb)
