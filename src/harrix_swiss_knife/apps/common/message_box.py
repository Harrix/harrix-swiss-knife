"""QMessageBox helpers with a Copy button for clipboard export."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication, QPalette
from PySide6.QtWidgets import QAbstractButton, QLabel, QMessageBox, QWidget

from harrix_swiss_knife import qt_modality
from harrix_swiss_knife.fluent.style import accent_button_qss, push_button_qss
from harrix_swiss_knife.fluent.theme import bind_theme, is_fluent_themed, mix, palette_for, to_qpalette
from harrix_swiss_knife.qt_lucide_icon import (
    style_accept_button,
    style_cancel_button,
    style_delete_button,
)

if TYPE_CHECKING:
    from harrix_swiss_knife.fluent.tokens import FluentPalette

_COPY_BUTTON_ATTR = "_harrix_copy_button_added"
_CLIPBOARD_TEXT_ATTR = "_harrix_clipboard_text"
_PRIMARY_ROLES = (
    QMessageBox.ButtonRole.AcceptRole,
    QMessageBox.ButtonRole.YesRole,
    QMessageBox.ButtonRole.ApplyRole,
)
# Qt rich text ignores QSS for <a>; only palette + inline style= are reliable.
_ANCHOR_OPEN_RE = re.compile(r"<a\b([^>]*)>", re.IGNORECASE)
_ANCHOR_STYLE_RE = re.compile(r"""\sstyle\s*=\s*(['"]).*?\1""", re.IGNORECASE | re.DOTALL)


def add_copy_button(box: QMessageBox) -> QAbstractButton:
    """Add a Copy button; on click, copy `clipboard_text_from_box` to the clipboard."""
    copy_btn = box.addButton("Copy", QMessageBox.ButtonRole.ActionRole)
    copy_btn.clicked.disconnect()

    def _copy_box_text() -> None:
        QGuiApplication.clipboard().setText(clipboard_text_from_box(box))

    copy_btn.clicked.connect(_copy_box_text)
    return copy_btn


def ask_retry(
    parent: QWidget | None,
    title: str,
    text: str,
    *,
    critical: bool = False,
) -> bool:
    """Ask whether to resend a failed or cancelled AI request.

    Args:

    - `parent` (`QWidget | None`): Parent for modality.
    - `title` (`str`): Dialog title.
    - `text` (`str`): Explanation (error message or cancel note).
    - `critical` (`bool`): When `True`, use a critical icon. Defaults to `False`.

    Returns:

    - `bool`: `True` when the user chose Retry.

    """
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Critical if critical else QMessageBox.Icon.Warning)
    box.setWindowTitle(title)
    box.setText(text)
    retry_button = box.addButton("Retry", QMessageBox.ButtonRole.AcceptRole)
    box.addButton("Close", QMessageBox.ButtonRole.RejectRole)
    box.setDefaultButton(retry_button)
    prepare_box(box)
    qt_modality.set_owner_window_modal(box)
    box.exec()
    return box.clickedButton() is retry_button


def clipboard_text_from_box(box: QMessageBox) -> str:
    """Build plain text for the clipboard from the dialog fields."""
    custom = getattr(box, _CLIPBOARD_TEXT_ATTR, None)
    if isinstance(custom, str) and custom.strip():
        return custom

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


def colorize_html_links(html: str, color: QColor | str) -> str:
    """Return `html` with inline `style="color:…"` on every `<a>` tag.

    Qt's rich-text engine ignores style sheets for anchors inside `QLabel` /
    `QMessageBox`, so palette alone is not enough on Windows dark chrome.

    """
    hex_color = QColor(color).name(QColor.NameFormat.HexRgb)

    def _inject(match: re.Match[str]) -> str:
        attrs = match.group(1)
        cleaned = _ANCHOR_STYLE_RE.sub("", attrs)
        return f'<a{cleaned} style="color:{hex_color}">'

    return _ANCHOR_OPEN_RE.sub(_inject, html)


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
    rich_text: bool = False,
    clipboard_text: str | None = None,
) -> QMessageBox.StandardButton:
    """Like `QMessageBox.information` with a Copy button.

    Args:

    - `rich_text` (`bool`): When `True`, interpret `text` as HTML rich text
      (so links are clickable). Defaults to `False`.
    - `clipboard_text` (`str | None`): Plain text for the Copy button when
      `text` is HTML. Defaults to `None` (copy from dialog fields).

    """
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Information)
    box.setWindowTitle(title)
    if rich_text:
        box.setTextFormat(Qt.TextFormat.RichText)
        if is_fluent_themed(parent):
            palette = palette_for(parent)
            text = colorize_html_links(text, mix(palette.window_bg, palette.accent_text))
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    if stylesheet:
        box.setStyleSheet(stylesheet)
    if clipboard_text is not None:
        setattr(box, _CLIPBOARD_TEXT_ATTR, clipboard_text)
    prepare_box(box)
    return _exec_box(box)


def prepare_box(box: QMessageBox) -> None:
    """Ensure `box` has a Copy button and matching accept / delete / idle chrome."""
    if not getattr(box, _COPY_BUTTON_ATTR, False):
        add_copy_button(box)
        setattr(box, _COPY_BUTTON_ATTR, True)
    if is_fluent_themed(box):
        bind_theme(box, lambda: _style_fluent_box(box))
        _style_fluent_box(box)
        return
    for button in box.buttons():
        role = box.buttonRole(button)
        if role in _PRIMARY_ROLES:
            style_accept_button(button)
        elif role == QMessageBox.ButtonRole.DestructiveRole:
            style_delete_button(button)
        else:
            style_cancel_button(button)


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
    # Prefer WindowModal so sibling apps in the same process stay interactive.
    qt_modality.set_owner_window_modal(box)
    result_code = box.exec()
    clicked = box.clickedButton()
    if clicked is None or result_code == QMessageBox.DialogCode.Rejected:
        return QMessageBox.StandardButton.Cancel
    sb = box.standardButton(clicked)
    return QMessageBox.StandardButton(sb)


def _style_fluent_box(box: QMessageBox) -> None:
    """Apply Fluent button chrome and readable rich-text link colors."""
    palette = palette_for(box)
    box.setPalette(to_qpalette(palette, box.palette()))
    _apply_fluent_link_colors(box, palette)
    primary = accent_button_qss(palette)
    standard = push_button_qss(palette)
    for button in box.buttons():
        role = box.buttonRole(button)
        button.setStyleSheet(primary if role in _PRIMARY_ROLES else standard)


def _apply_fluent_link_colors(box: QMessageBox, palette: FluentPalette) -> None:
    """Paint `<a href>` via palette + inline HTML color (QSS cannot style rich text)."""
    link = mix(palette.window_bg, palette.accent_text)
    text = mix(palette.window_bg, palette.text_primary)
    hex_link = link.name(QColor.NameFormat.HexRgb)
    body = box.text()
    if "<a" in body.casefold():
        colored_body = colorize_html_links(body, hex_link)
        if colored_body != body:
            box.setTextFormat(Qt.TextFormat.RichText)
            box.setText(colored_body)
    informative = box.informativeText()
    if "<a" in informative.casefold():
        colored_info = colorize_html_links(informative, hex_link)
        if colored_info != informative:
            box.setInformativeText(colored_info)
    for label in box.findChildren(QLabel):
        qp = label.palette()
        for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive):
            qp.setColor(group, QPalette.ColorRole.Link, link)
            qp.setColor(group, QPalette.ColorRole.LinkVisited, link)
            qp.setColor(group, QPalette.ColorRole.WindowText, text)
            qp.setColor(group, QPalette.ColorRole.Text, text)
        label.setPalette(qp)
        raw = label.text()
        if "<a" not in raw.casefold():
            continue
        colored = colorize_html_links(raw, hex_link)
        if colored != raw:
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setText(colored)
