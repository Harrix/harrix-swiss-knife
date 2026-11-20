"""Unified-diff viewer: JetBrains Mono and add / delete / hunk highlighting."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat
from PySide6.QtWidgets import QPlainTextEdit, QWidget

from harrix_swiss_knife.fluent.theme import palette_for
from harrix_swiss_knife.fluent.widgets.inputs import FluentPlainTextEdit
from harrix_swiss_knife.qt_app_font import apply_mono_font

if TYPE_CHECKING:
    from PySide6.QtGui import QTextDocument

_META_PREFIXES = ("diff ", "index ", "+++", "---", "Binary ", "new file", "deleted file", "rename ")


class GitDiffEdit(FluentPlainTextEdit):
    """Read-only diff with JetBrains Mono and GitHub Desktop-style line colors."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a diff view."""
        super().__init__(parent)
        apply_mono_font(self)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self._highlighter = _GitDiffHighlighter(self.document(), self)

    def refresh_theme(self) -> None:
        """Re-apply chrome and diff colors."""
        super().refresh_theme()
        self._highlighter.rehighlight()


class _GitDiffHighlighter(QSyntaxHighlighter):
    def __init__(self, document: QTextDocument, host: GitDiffEdit) -> None:
        super().__init__(document)
        self._host = host

    def highlightBlock(self, text: str) -> None:  # noqa: N802
        """Color one diff line."""
        kind = diff_line_kind(text)
        if kind == "context":
            return
        palette = palette_for(self._host)
        fmt = QTextCharFormat()
        if kind == "add":
            fmt.setBackground(palette.success_bg)
            fmt.setForeground(palette.success)
        elif kind == "delete":
            fmt.setBackground(palette.critical_bg)
            fmt.setForeground(palette.critical)
        elif kind == "hunk":
            fmt.setBackground(palette.caution_bg)
            fmt.setForeground(palette.caution)
        else:
            fmt.setForeground(palette.text_secondary)
        self.setFormat(0, len(text), fmt)


def diff_line_kind(line: str) -> str:
    """Return `meta`, `add`, `delete`, `hunk`, or `context` for one diff line."""
    if line.startswith(_META_PREFIXES):
        return "meta"
    if line.startswith("+"):
        return "add"
    if line.startswith("-"):
        return "delete"
    if line.startswith("@@"):
        return "hunk"
    return "context"
