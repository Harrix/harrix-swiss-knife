"""Install Fluent chrome on tracker apps and overlay dialogs.

Call `install_fluent_app_window` after `setupUi` (or equivalent layout build)
and before `install_win11_caption`. It opts the window into light/dark theme,
replaces legacy white-surface / CTA stylesheets with Fluent tokens, and
keeps lists and menus in sync when the theme changes.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QListView,
    QListWidget,
    QPushButton,
    QStatusBar,
    QWidget,
)

from harrix_swiss_knife.fluent.style import accent_button_qss, item_view_qss, push_button_qss
from harrix_swiss_knife.fluent.theme import bind_theme, css, enable_fluent_theme, mix, palette_for
from harrix_swiss_knife.fluent.tokens import CONTROL_HEIGHT
from harrix_swiss_knife.qt_flat_scrollbar import apply_flat_scrollbars

if TYPE_CHECKING:
    from harrix_swiss_knife.fluent.tokens import FluentPalette

_WHITE_SURFACE_MARK = "hsk-white-surfaces"
_CTA_MARKERS = (
    "#79b1d1",
    "#3aaf9d",
    "#4caf50",
    "button_cta_",
    "hsk-fluent-cta",
)
_PRIMARY_MARKERS = (
    "#2e86b7",
    "BUTTON_PRIMARY",
)
_PROP_BOUND = "_hskFluentAppChromeBound"


def install_fluent_app_window(window: QWidget) -> None:
    """Opt `window` into Fluent theme and restyle legacy Harrix chrome under it."""
    enable_fluent_theme(window)
    if not window.property(_PROP_BOUND):
        bind_theme(window, lambda: refresh_fluent_app_window(window))
        window.setProperty(_PROP_BOUND, True)  # noqa: FBT003
    refresh_fluent_app_window(window)


def refresh_fluent_app_window(window: QWidget) -> None:
    """Re-apply Fluent surfaces, lists, menus, and CTA buttons for the current theme."""
    palette = palette_for(window)
    _apply_fluent_surfaces(window, palette)
    _apply_fluent_list_selection(window, palette)
    _restyle_buttons(window, palette)
    apply_flat_scrollbars(window)
    window.update()


def _apply_fluent_list_selection(root: QWidget, palette: FluentPalette) -> None:
    for view in root.findChildren(QListView):
        if isinstance(view, QAbstractItemView):
            _style_item_view(view, palette)
    for view in root.findChildren(QListWidget):
        _style_item_view(view, palette)


def _apply_fluent_surfaces(window: QWidget, palette: FluentPalette) -> None:
    sheet = window.styleSheet() or ""
    if _WHITE_SURFACE_MARK in sheet or "background-color: #ffffff" in sheet.lower():
        window.setStyleSheet(_fluent_surface_qss(palette))
    else:
        window.setStyleSheet(_fluent_surface_qss(palette))
    surface = css(mix(palette.window_bg, palette.layer_alt_bg))
    for child in window.findChildren(QWidget):
        child_sheet = child.styleSheet() or ""
        if not child_sheet:
            continue
        lowered = child_sheet.lower()
        name = child.objectName()
        if name and f"#{name}" in child_sheet and "#ffffff" in lowered:
            child.setStyleSheet(
                f"QWidget#{name} {{ background-color: {surface}; border: none; }}",
            )
        elif "background-color: #ffffff" in lowered and isinstance(child, (QGroupBox, QStatusBar)):
            child.setStyleSheet("")


def _fluent_surface_qss(palette: FluentPalette) -> str:
    window = css(palette.window_bg)
    surface = css(mix(palette.window_bg, palette.layer_alt_bg))
    text = css(mix(palette.window_bg, palette.text_primary))
    secondary = css(mix(palette.window_bg, palette.text_secondary))
    divider = css(mix(palette.window_bg, palette.divider))
    hover = css(mix(palette.window_bg, palette.subtle_hover))
    popup = css(mix(palette.window_bg, palette.popup_bg))
    stroke = css(mix(palette.window_bg, palette.popup_stroke))
    return f"""
/* hsk-fluent-surfaces */
QGroupBox {{
 background-color: {surface};
 border: none;
 border-bottom: 1px solid {divider};
 border-radius: 0;
 margin-top: 0.8em;
 padding-top: 4px;
 padding-bottom: 6px;
 color: {text};
}}
QGroupBox::title {{
 subcontrol-origin: margin;
 subcontrol-position: top left;
 left: 0px;
 padding: 0;
 background-color: {surface};
 color: {text};
}}
QMenu {{
 background-color: {popup};
 border: 1px solid {stroke};
 color: {text};
}}
QMenu::item {{ color: {text}; background-color: transparent; }}
QMenu::item:selected {{ color: {text}; background-color: {hover}; }}
QMenu::item:disabled {{ color: {secondary}; }}
QStatusBar {{ background: {surface}; color: {text}; }}
QStatusBar QLabel {{ color: {text}; }}
QSplitter::handle:horizontal {{
 width: 1px;
 background: {divider};
}}
QSplitter::handle:vertical {{
 height: 1px;
 background: {divider};
}}
QMainWindow, QDialog {{ background-color: {window}; }}
"""


def _restyle_buttons(root: QWidget, palette: FluentPalette) -> None:
    accent = accent_button_qss(palette)
    secondary = push_button_qss(palette)
    for button in root.findChildren(QPushButton):
        sheet = button.styleSheet() or ""
        if not sheet:
            continue
        lowered = sheet.lower()
        if any(marker.lower() in lowered or marker in sheet for marker in _CTA_MARKERS) or any(
            marker.lower() in lowered or marker in sheet for marker in _PRIMARY_MARKERS
        ):
            button.setStyleSheet(accent)
            button.setMinimumHeight(CONTROL_HEIGHT)
        elif "background-color: #f5f5f5" in lowered or "background-color:#f5f5f5" in lowered:
            button.setStyleSheet(secondary)
            button.setMinimumHeight(CONTROL_HEIGHT)


def _style_item_view(view: QAbstractItemView, palette: FluentPalette) -> None:
    selector = view.metaObject().className()
    name = view.objectName()
    target = f"{selector}#{name}" if name else selector
    view.setStyleSheet(item_view_qss(palette, target))
