"""Turn action result text into HTML with clickable http(s) links."""

from __future__ import annotations

import html
import re

from PySide6.QtCore import QMimeData
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTextBrowser, QWidget

_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_TRAILING_PUNCT = frozenset(".,;:!?)]}'\"")
_LINK_STYLE = "a { color: #0563C1; text-decoration: underline; }"


class ResultTextBrowser(QTextBrowser):
    """Read-only result view: clickable links, clipboard selections stay plain text."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a result browser that opens http(s) links in the default browser."""
        super().__init__(parent)
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)
        self.setOpenLinks(True)
        self.setUndoRedoEnabled(False)
        font = QFont()
        font.setPointSize(9)
        self.setFont(font)
        self.document().setDefaultFont(font)
        self.document().setDefaultStyleSheet(_LINK_STYLE)

    def createMimeDataFromSelection(self) -> QMimeData:  # noqa: N802
        """Copy the selected characters only, without HTML link markup."""
        mime = QMimeData()
        mime.setText(self.textCursor().selectedText().replace("\u2029", "\n"))
        return mime

    def set_plain_result(self, text: str) -> None:
        """Show `text` with auto-linked URLs."""
        self.setHtml(plain_text_to_result_html(text))


def plain_text_to_result_html(text: str) -> str:
    """Escape `text` and wrap http(s) URLs in blue underlined anchors.

    Trailing sentence punctuation is kept outside the link. The visible URL text
    stays the same as in the log so `QTextBrowser.toPlainText()` matches `text`.

    """
    chunks: list[str] = []
    pos = 0
    for match in _URL_RE.finditer(text):
        url, trailing = _split_trailing_url_punct(match.group())
        chunks.append(html.escape(text[pos : match.start()]))
        if url:
            escaped = html.escape(url, quote=True)
            chunks.append(f'<a href="{escaped}">{html.escape(url)}</a>')
        chunks.append(html.escape(trailing))
        pos = match.end()
    chunks.append(html.escape(text[pos:]))
    body = "".join(chunks)
    return f"<html><head><meta charset='utf-8'></head><body style='white-space:pre-wrap;margin:0;'>{body}</body></html>"


def _split_trailing_url_punct(url: str) -> tuple[str, str]:
    """Split trailing punctuation that is not part of the URL."""
    end = len(url)
    while end > 0 and url[end - 1] in _TRAILING_PUNCT:
        end -= 1
    if end == 0:
        return url, ""
    return url[:end], url[end:]
