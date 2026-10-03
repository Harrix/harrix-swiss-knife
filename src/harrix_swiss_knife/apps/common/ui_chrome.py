"""Shared selection and list chrome for tracker apps and overlays.

Soft-blue tokens match Icons tiles/chips and Harrix-HTML-Template brand
(`$h-primary` / `$h-soft-bg` / `$h-soft-hover` / `$h-brand-ink`).

"""

from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QAbstractItemView, QListView, QListWidget, QWidget

# Soft blue selection (matches Icons tiles / chips; site `$h-soft-*`).
SELECTION_BG = "#e8f4fc"
SELECTION_BORDER = "#2e86b7"
SELECTION_HOVER = "#f3f8fb"
SELECTION_TEXT = "#1a1a1a"
# Text on soft-blue chips / status labels (site `$h-brand-ink`).
BRAND_INK = "#1a5f7a"
# Secondary labels — avoid palette(mid), which is nearly white on some light themes.
MUTED_TEXT = "#5c6370"

# Compact chip / filter control.
CHIP_BG = "#f0f4f8"
CHIP_BORDER = "#d0d7de"
CHIP_HOVER = "#e4ebf2"
CHIP_CHECKED_BG = SELECTION_BG
CHIP_CHECKED_BORDER = SELECTION_BORDER

_LIST_ITEM_SELECTION_QSS = f"""
QListView::item {{
    border-radius: 6px;
}}
QListView::item:selected {{
    background-color: {SELECTION_BG};
    color: {SELECTION_TEXT};
    border: 1px solid {SELECTION_BORDER};
}}
QListView::item:hover:!selected {{
    background-color: {SELECTION_HOVER};
}}
""".strip()

_LIST_WIDGET_ITEM_SELECTION_QSS = f"""
QListWidget::item {{
    border-radius: 6px;
}}
QListWidget::item:selected {{
    background-color: {SELECTION_BG};
    color: {SELECTION_TEXT};
    border: 1px solid {SELECTION_BORDER};
}}
QListWidget::item:hover:!selected {{
    background-color: {SELECTION_HOVER};
}}
""".strip()


def action_card_selection_qss() -> str:
    """Return selection / hover QSS for Quick launcher action cards."""
    return f"""
QListWidget {{
    outline: none;
    background: transparent;
    border: none;
}}
QListWidget::item {{
    margin: 4px;
    padding: 0px;
    border-radius: 8px;
    border: 1px solid transparent;
    background: transparent;
    color: {SELECTION_TEXT};
}}
QListWidget::item:hover:!selected {{
    background: {SELECTION_HOVER};
    border-color: {CHIP_BORDER};
}}
QListWidget::item:selected {{
    background: {SELECTION_BG};
    border: 1px solid {SELECTION_BORDER};
    color: {SELECTION_TEXT};
}}
""".strip()


def apply_readable_selection_palette(view: QAbstractItemView) -> None:
    """Keep selected-item text dark on soft blue highlights (not system white)."""
    palette = view.palette()
    text = QColor(SELECTION_TEXT)
    highlight = QColor(SELECTION_BG)
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive, QPalette.ColorGroup.Disabled):
        palette.setColor(group, QPalette.ColorRole.Highlight, highlight)
        palette.setColor(group, QPalette.ColorRole.HighlightedText, text)
    view.setPalette(palette)


def apply_soft_item_selection(view: QAbstractItemView) -> None:
    """Append soft blue selected / hover rules to a list view or list widget."""
    existing = (view.styleSheet() or "").rstrip()
    fragment = _LIST_WIDGET_ITEM_SELECTION_QSS if isinstance(view, QListWidget) else _LIST_ITEM_SELECTION_QSS
    view.setStyleSheet(f"{existing}\n{fragment}" if existing else fragment)
    apply_readable_selection_palette(view)


def apply_soft_list_selection_chrome(root: QWidget) -> None:
    """Apply soft selection chrome to every `QListView` under `root`."""
    for view in root.findChildren(QListView):
        apply_soft_item_selection(view)


def list_view_item_selection_qss(*, with_row_separators: bool = False) -> str:
    """Return QSS for `QListView::item` selected / hover states.

    Args:

    - `with_row_separators` (`bool`): When `True`, keep a light bottom border
      between rows (finance / food / fitness filter lists).

    Returns:

    - `str`: Stylesheet fragment for list items (does not set the outer list border).

    """
    separator = "border-bottom: 1px solid #e0e0e0;" if with_row_separators else ""
    return f"""
QListView::item {{
    padding: 4px 6px;
    border-radius: 6px;
    {separator}
}}
QListView::item:selected {{
    background-color: {SELECTION_BG};
    color: {SELECTION_TEXT};
    border: 1px solid {SELECTION_BORDER};
}}
QListView::item:hover:!selected {{
    background-color: {SELECTION_HOVER};
}}
""".strip()


def list_view_panel_qss(*, border_color: str, with_row_separators: bool = True) -> str:
    """Return a full `QListView` stylesheet with branded border and soft selection.

    Args:

    - `border_color` (`str`): Outer list border color (app accent).
    - `with_row_separators` (`bool`): Whether items draw a bottom hairline.

    Returns:

    - `str`: Complete stylesheet string for a filter / option list.

    """
    return f"""
QListView {{
    border: 2px solid {border_color};
    border-radius: 4px;
    background-color: white;
    outline: none;
}}
{list_view_item_selection_qss(with_row_separators=with_row_separators)}
""".strip()


def snippet_list_selection_qss() -> str:
    """Return selection QSS for Quick paste snippet list."""
    return f"""
QListWidget {{
    outline: none;
    show-decoration-selected: 0;
}}
QListWidget::item {{
    border: none;
    border-radius: 6px;
    color: palette(text);
}}
QListWidget::item:hover,
QListWidget::item:selected,
QListWidget::item:selected:active,
QListWidget::item:selected:!active,
QListWidget::item:selected:hover {{
    background-color: {SELECTION_BG};
    color: {SELECTION_TEXT};
    border: 1px solid {SELECTION_BORDER};
    border-radius: 6px;
}}
""".strip()
