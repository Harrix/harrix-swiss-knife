"""Tests for clickable http(s) links in action result text."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.actions.common.result_html import ResultTextBrowser, plain_text_to_result_html


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        return QApplication([])
    if not isinstance(app, QApplication):
        msg = "QApplication.instance() returned a non-QApplication object."
        raise TypeError(msg)
    return app


def test_plain_text_to_result_html_linkifies_https() -> None:
    html = plain_text_to_result_html(
        "success: Upgraded uv! https://github.com/astral-sh/uv/releases/tag/0.12.17",
    )
    assert 'href="https://github.com/astral-sh/uv/releases/tag/0.12.17"' in html
    assert ">https://github.com/astral-sh/uv/releases/tag/0.12.17</a>" in html
    assert "success: Upgraded uv!" in html


def test_plain_text_to_result_html_escapes_markup() -> None:
    html = plain_text_to_result_html("a < b & c")
    assert "&lt;" in html
    assert "&amp;" in html
    assert "<a " not in html


def test_plain_text_to_result_html_keeps_trailing_punct_outside_link() -> None:
    html = plain_text_to_result_html("see https://example.com.")
    assert 'href="https://example.com"' in html
    assert ">https://example.com</a>." in html


def test_result_browser_plain_text_roundtrip_and_plain_clipboard(
    qapp: QApplication,  # noqa: ARG001
) -> None:
    text = (
        "=== uv self update ===\n"
        "success: Upgraded uv from v0.12.10 to v0.12.17! "
        "https://github.com/astral-sh/uv/releases/tag/0.12.17"
    )
    browser = ResultTextBrowser()
    browser.set_plain_result(text)
    assert browser.toPlainText() == text
    assert browser.openExternalLinks()
    html = browser.toHtml()
    assert "https://github.com/astral-sh/uv/releases/tag/0.12.17" in html
    assert "<a " in html.lower() or "href=" in html.lower()

    browser.selectAll()
    mime = browser.createMimeDataFromSelection()
    assert mime.text() == text
    assert mime.html() == ""
    formats = {str(fmt) for fmt in mime.formats()}
    assert "text/html" not in formats


def test_result_browser_link_style_is_blue_underline(qapp: QApplication) -> None:  # noqa: ARG001
    browser = ResultTextBrowser()
    sheet = browser.document().defaultStyleSheet()
    assert "#0563C1" in sheet
    assert "underline" in sheet
    assert browser.textInteractionFlags() & Qt.TextInteractionFlag.LinksAccessibleByMouse
