"""`QSyntaxHighlighter` wavy red underlines for document-based editors."""

from __future__ import annotations

from PySide6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat, QTextDocument

from harrix_swiss_knife.spellcheck.engine import SpellEngine, get_spell_engine
from harrix_swiss_knife.spellcheck.tokenize import iter_word_spans

_MISS_FORMAT = QTextCharFormat()
_MISS_FORMAT.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
_MISS_FORMAT.setUnderlineColor(QColor(220, 50, 47))


class SpellHighlighter(QSyntaxHighlighter):
    """Highlight misspelled words with a red wave underline."""

    def __init__(self, document: QTextDocument, engine: SpellEngine | None = None) -> None:
        """Attach to `document` using `engine` (default: process-wide)."""
        super().__init__(document)
        self._engine = engine if engine is not None else get_spell_engine()
        self._enabled = True

    def set_enabled(self, *, enabled: bool) -> None:
        """Enable or disable highlighting and rehighlight when turning on."""
        self._enabled = enabled
        if enabled:
            self.rehighlight()
        else:
            self.setDocument(self.document())

    def rehighlight_all(self) -> None:
        """Force a full rehighlight (e.g. after adding a user word)."""
        self.rehighlight()

    def highlightBlock(self, text: str) -> None:  # noqa: N802
        """Underline misspelled tokens in the current block."""
        if not self._enabled or not text:
            return
        engine = self._engine
        for start, end, word in iter_word_spans(text):
            if not engine.lookup(word):
                self.setFormat(start, end - start, _MISS_FORMAT)
