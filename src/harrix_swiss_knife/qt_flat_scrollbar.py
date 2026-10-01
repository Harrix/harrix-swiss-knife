"""Flat QScrollBar rules for widgets that already use a stylesheet.

A stylesheet on `QListView` / `QTableView` / `QScrollArea` makes Qt drop
Windows 11 native scrollbar drawing and fall back to classic beveled bars.
Append these rules so those widgets keep a modern flat look matching Quick paste.

"""

from __future__ import annotations

from PySide6.QtWidgets import QAbstractScrollArea, QWidget

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

    """
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
