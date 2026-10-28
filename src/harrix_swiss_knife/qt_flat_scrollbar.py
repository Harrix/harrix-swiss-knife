"""Flat QScrollBar rules for widgets that already use a stylesheet.

A stylesheet on `QListView` / `QTableView` / `QScrollArea` makes Qt drop
Windows 11 native scrollbar drawing and fall back to classic beveled bars.
Append these rules so those widgets keep a modern flat look matching Quick paste.
Inside Fluent-themed Windows the rules follow the light / dark Fluent palette.

"""

from __future__ import annotations

import re

from PySide6.QtWidgets import QAbstractScrollArea, QWidget

from harrix_swiss_knife.fluent.style import scroll_bar_qss
from harrix_swiss_knife.fluent.theme import bind_theme, is_fluent_themed, palette_for

_FLUENT_BEGIN = "/* hsk-fluent-scrollbars */"
_FLUENT_END = "/* /hsk-fluent-scrollbars */"
_FLUENT_BLOCK = re.compile(re.escape(_FLUENT_BEGIN) + r".*?" + re.escape(_FLUENT_END), re.DOTALL)
_FLUENT_BOUND_PROP = "_hskFluentScrollbarsBound"

FLAT_SCROLLBAR_STYLE = """
QScrollBar:vertical {
    background: transparent;
    border: none;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #d1d5db;
    border: none;
    border-radius: 5px;
    min-height: 32px;
    margin: 2px 1px;
}
QScrollBar::handle:vertical:hover {
    background: #9ca3af;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
    width: 0;
    border: none;
    background: none;
}
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
    border: none;
}
QScrollBar::up-arrow:vertical,
QScrollBar::down-arrow:vertical {
    width: 0;
    height: 0;
    background: none;
    border: none;
}
QScrollBar:horizontal {
    background: transparent;
    border: none;
    height: 10px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #d1d5db;
    border: none;
    border-radius: 5px;
    min-width: 32px;
    margin: 1px 2px;
}
QScrollBar::handle:horizontal:hover {
    background: #9ca3af;
}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    height: 0;
    width: 0;
    border: none;
    background: none;
}
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: none;
    border: none;
}
QScrollBar::left-arrow:horizontal,
QScrollBar::right-arrow:horizontal {
    width: 0;
    height: 0;
    background: none;
    border: none;
}
QAbstractScrollArea::corner {
    background: #ffffff;
    border: none;
}
""".strip()


def apply_flat_scrollbars(root: QWidget) -> None:
    """Append flat scrollbar rules to every scroll area under `root`.

    Covers item views, `QScrollArea`, and text edits — including widgets with
    no stylesheet yet, so parent window stylesheets cannot leave classic bars.
    In Fluent-themed Windows the rules use the current Fluent palette and are
    re-applied on theme change.

    """
    if is_fluent_themed(root):
        _apply_fluent_scrollbars(root)
        if not root.property(_FLUENT_BOUND_PROP):
            root.setProperty(_FLUENT_BOUND_PROP, True)  # noqa: FBT003
            bind_theme(root, lambda: _apply_fluent_scrollbars(root))
        return
    for widget in root.findChildren(QAbstractScrollArea):
        sheet = widget.styleSheet().strip()
        updated = with_flat_scrollbars(sheet)
        if updated != sheet:
            widget.setStyleSheet(updated)


def apply_flat_scrollbars_to_styled_item_views(root: QWidget) -> None:
    """Apply flat scrollbars under `root` (alias kept for older call sites)."""
    apply_flat_scrollbars(root)


def with_flat_scrollbars(style: str) -> str:
    """Return `style` with flat scrollbar rules appended (once)."""
    sheet = style.strip()
    if "QScrollBar:vertical" in sheet:
        return sheet
    if not sheet:
        return FLAT_SCROLLBAR_STYLE
    return f"{sheet}\n{FLAT_SCROLLBAR_STYLE}"


def _apply_fluent_scrollbars(root: QWidget) -> None:
    block = f"{_FLUENT_BEGIN}\n{scroll_bar_qss(palette_for(root)).strip()}\n{_FLUENT_END}"
    for widget in root.findChildren(QAbstractScrollArea):
        base = _FLUENT_BLOCK.sub("", widget.styleSheet()).strip()
        if "QScrollBar:vertical" in base:
            continue
        updated = f"{base}\n{block}" if base else block
        if updated != widget.styleSheet():
            widget.setStyleSheet(updated)
