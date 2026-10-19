"""Superscript and subscript glyphs for the Quick paste Scripts tab."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget

from harrix_swiss_knife.apps.common.ui_chrome import MUTED_TEXT, button_primary_qss, button_secondary_qss
from harrix_swiss_knife.qt_app_font import style_overlay_line_edit
from harrix_swiss_knife.qt_flow_layout import FlowLayout

if TYPE_CHECKING:
    from collections.abc import Callable

# Unicode superscripts and subscripts (Latin-1 supplement, U+2070 block, modifier letters).
# Pairs are `(glyph, base)` so the tooltip names the plain character.
SUPERSCRIPT_GLYPHS: tuple[tuple[str, str], ...] = (
    ("⁰", "0"),
    ("¹", "1"),
    ("²", "2"),
    ("³", "3"),
    ("⁴", "4"),
    ("⁵", "5"),
    ("⁶", "6"),
    ("⁷", "7"),
    ("⁸", "8"),
    ("⁹", "9"),
    ("⁺", "+"),
    ("⁻", "-"),
    ("⁼", "="),
    ("⁽", "("),
    ("⁾", ")"),
    ("ᵃ", "a"),
    ("ᵇ", "b"),
    ("ᶜ", "c"),
    ("ᵈ", "d"),
    ("ᵉ", "e"),
    ("ᶠ", "f"),
    ("ᵍ", "g"),
    ("ʰ", "h"),
    ("ⁱ", "i"),
    ("ʲ", "j"),
    ("ᵏ", "k"),
    ("ˡ", "l"),
    ("ᵐ", "m"),
    ("ⁿ", "n"),
    ("ᵒ", "o"),
    ("ᵖ", "p"),
    ("ʳ", "r"),
    ("ˢ", "s"),
    ("ᵗ", "t"),
    ("ᵘ", "u"),
    ("ᵛ", "v"),
    ("ʷ", "w"),
    ("ˣ", "x"),
    ("ʸ", "y"),
    ("ᶻ", "z"),
    ("ᴬ", "A"),
    ("ᴮ", "B"),
    ("ᴰ", "D"),
    ("ᴱ", "E"),
    ("ᴳ", "G"),
    ("ᴴ", "H"),
    ("ᴵ", "I"),
    ("ᴶ", "J"),
    ("ᴷ", "K"),
    ("ᴸ", "L"),
    ("ᴹ", "M"),
    ("ᴺ", "N"),
    ("ᴼ", "O"),
    ("ᴾ", "P"),
    ("ᴿ", "R"),
    ("ᵀ", "T"),
    ("ᵁ", "U"),
    ("ⱽ", "V"),
    ("ᵂ", "W"),
)
SUBSCRIPT_GLYPHS: tuple[tuple[str, str], ...] = (
    ("₀", "0"),
    ("₁", "1"),
    ("₂", "2"),
    ("₃", "3"),
    ("₄", "4"),
    ("₅", "5"),
    ("₆", "6"),
    ("₇", "7"),
    ("₈", "8"),
    ("₉", "9"),
    ("₊", "+"),
    ("₋", "-"),
    ("₌", "="),
    ("₍", "("),
    ("₎", ")"),
    ("ₐ", "a"),
    ("ₑ", "e"),
    ("ₕ", "h"),
    ("ᵢ", "i"),
    ("ⱼ", "j"),
    ("ₖ", "k"),
    ("ₗ", "l"),
    ("ₘ", "m"),
    ("ₙ", "n"),
    ("ₒ", "o"),
    ("ₚ", "p"),
    ("ᵣ", "r"),
    ("ₛ", "s"),
    ("ₜ", "t"),
    ("ᵤ", "u"),
    ("ᵥ", "v"),
    ("ₓ", "x"),
)
SCRIPT_SECTIONS: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = (
    ("Superscript", SUPERSCRIPT_GLYPHS),
    ("Subscript", SUBSCRIPT_GLYPHS),
)

_GLYPH_POINT_DELTA = 4
_FLOW_SPACING = 6


class ScriptsPanel(QWidget):
    """Compose a superscript or subscript string, then paste it with Add."""

    add_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the composer and the glyph buttons."""
        super().__init__(parent)
        self._edit = QLineEdit(self)
        self._edit.setPlaceholderText("Click characters, then Add")
        self._edit.setClearButtonEnabled(True)
        style_overlay_line_edit(self._edit)
        self._edit.returnPressed.connect(self._emit_add)

        self._add_button = QPushButton("Add", self)
        self._add_button.setObjectName("scriptsAddButton")
        self._add_button.setAutoDefault(False)
        self._add_button.setDefault(False)
        self._add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._add_button.setStyleSheet(button_primary_qss())
        self._add_button.clicked.connect(self._emit_add)

        composer = QHBoxLayout()
        composer.setContentsMargins(0, 0, 0, 0)
        composer.addWidget(self._edit, stretch=1)
        composer.addWidget(self._add_button)

        sections = QWidget(self)
        sections_layout = QVBoxLayout(sections)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(8)
        for title, glyphs in SCRIPT_SECTIONS:
            sections_layout.addWidget(_section_label(title, sections))
            sections_layout.addWidget(_glyph_flow(glyphs, title, self._append_glyph, sections))
        sections_layout.addStretch(1)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(sections)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.addLayout(composer)
        layout.addWidget(scroll, stretch=1)

    def append_glyph(self, char: str) -> None:
        """Insert `char` at the composer caret."""
        self._append_glyph(char)

    def clear(self) -> None:
        """Empty the composer."""
        self._edit.clear()

    def composed_text(self) -> str:
        """Return the characters collected in the composer."""
        return self._edit.text()

    def focus_composer(self) -> None:
        """Move keyboard focus to the composer."""
        self._edit.setFocus()

    def _append_glyph(self, char: str) -> None:
        """Insert `char` at the composer caret and keep the caret there."""
        edit = self._edit
        pos = edit.cursorPosition()
        text = edit.text()
        edit.setText(text[:pos] + char + text[pos:])
        edit.setCursorPosition(pos + len(char))
        edit.setFocus()

    def _emit_add(self) -> None:
        """Ask the overlay to paste the composer text."""
        text = self._edit.text()
        if not text:
            return
        self.add_requested.emit(text)


def _glyph_button(glyph: str, base: str, section: str, on_click: Callable[[str], None]) -> QPushButton:
    """Return a button that inserts `glyph` and names `base` in the tooltip."""
    button = QPushButton(glyph)
    button.setAutoDefault(False)
    button.setDefault(False)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setToolTip(f"{section} {base}")
    button.setStyleSheet(button_secondary_qss())
    font = button.font()
    if font.pointSize() > 0:
        font.setPointSize(font.pointSize() + _GLYPH_POINT_DELTA)
        button.setFont(font)
    button.clicked.connect(lambda _checked=False, char=glyph: on_click(char))
    return button


def _glyph_flow(
    glyphs: tuple[tuple[str, str], ...],
    section: str,
    on_click: Callable[[str], None],
    parent: QWidget,
) -> QWidget:
    """Return a wrapping row of glyph buttons for `section`."""
    host = QWidget(parent)
    flow = FlowLayout(host, margin=0, h_spacing=_FLOW_SPACING, v_spacing=_FLOW_SPACING)
    for glyph, base in glyphs:
        flow.addWidget(_glyph_button(glyph, base, section, on_click))
    return host


def _section_label(title: str, parent: QWidget) -> QLabel:
    """Return a muted heading for one glyph section."""
    label = QLabel(title, parent)
    label.setStyleSheet(f"color: {MUTED_TEXT};")
    return label
