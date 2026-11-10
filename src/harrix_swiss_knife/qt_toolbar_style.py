"""Shared toolbar button size and stylesheet (light plate / soft checked)."""

from __future__ import annotations

from harrix_swiss_knife.apps.common.ui_chrome import (
    BUTTON_SECONDARY_BG,
    BUTTON_SECONDARY_BORDER,
    BUTTON_SECONDARY_HOVER,
    BUTTON_SECONDARY_PRESSED,
    SELECTION_BG,
    SELECTION_BORDER,
    SELECTION_HOVER,
    selection_chrome_colors,
)

TOOLBAR_BUTTON_SIZE = 40
TOOLBAR_TOGGLE_WIDTH = 64
TOOLBAR_BUTTON_GAP = 6
TOOLBAR_ICON_SIZE = 24
TOOLBAR_EDGE_MARGIN = 12
TOOLBAR_BORDER_RADIUS = 6
TOOLBAR_TOGGLE_RADIUS = TOOLBAR_BUTTON_SIZE // 2


def toolbar_button_style() -> str:
    """Return toolbar button QSS; checked fill follows soft selection chrome."""
    fill, hover, border, _text = selection_chrome_colors()
    secondary_bg, secondary_hover, secondary_pressed, secondary_border = _toolbar_secondary_colors()
    return f"""
QPushButton, QToolButton {{
    background-color: {secondary_bg};
    border: 1px solid {secondary_border};
    border-radius: {TOOLBAR_BORDER_RADIUS}px;
    padding: 0px;
    margin: 0px;
}}
QPushButton:hover, QToolButton:hover {{
    background-color: {secondary_hover};
    border-color: {secondary_border};
}}
QPushButton:pressed, QToolButton:pressed {{
    background-color: {secondary_pressed};
    border-color: {secondary_border};
}}
QPushButton:checked, QToolButton:checked {{
    background-color: {fill};
    border: 1px solid {border};
}}
QPushButton:checked:hover, QToolButton:checked:hover {{
    background-color: {hover};
    border-color: {border};
}}
"""


def toolbar_toggle_style() -> str:
    """Return pill toggle QSS with themed on/off fills."""
    fill, hover, border, _text = selection_chrome_colors()
    secondary_bg, secondary_hover, secondary_pressed, secondary_border = _toolbar_secondary_colors()
    return f"""
QPushButton {{
    background-color: {secondary_bg};
    border: 1px solid {secondary_border};
    border-radius: {TOOLBAR_TOGGLE_RADIUS}px;
    padding: 0px;
    margin: 0px;
}}
QPushButton:hover {{
    background-color: {secondary_hover};
    border-color: {secondary_border};
}}
QPushButton:pressed {{
    background-color: {secondary_pressed};
    border-color: {secondary_border};
}}
QPushButton:checked {{
    background-color: {fill};
    border: 1px solid {border};
}}
QPushButton:checked:hover {{
    background-color: {hover};
    border-color: {border};
}}
"""


def _toolbar_secondary_colors() -> tuple[str, str, str, str]:
    """Return `(bg, hover, pressed, border)` for idle toolbar plates."""
    try:
        from harrix_swiss_knife.fluent.theme import FluentTheme, css, mix  # noqa: PLC0415

        palette = FluentTheme.instance().palette()
        if palette.dark:
            return (
                css(mix(palette.window_bg, palette.control_fill)),
                css(mix(palette.window_bg, palette.control_fill_hover)),
                css(mix(palette.window_bg, palette.control_fill_pressed)),
                css(mix(palette.window_bg, palette.control_stroke)),
            )
    except Exception:
        pass
    return BUTTON_SECONDARY_BG, BUTTON_SECONDARY_HOVER, BUTTON_SECONDARY_PRESSED, BUTTON_SECONDARY_BORDER


# Backward-compatible module constants (evaluated at import; prefer the functions).
TOOLBAR_BUTTON_STYLE = f"""
QPushButton, QToolButton {{
    background-color: {BUTTON_SECONDARY_BG};
    border: 1px solid {BUTTON_SECONDARY_BORDER};
    border-radius: {TOOLBAR_BORDER_RADIUS}px;
    padding: 0px;
    margin: 0px;
}}
QPushButton:hover, QToolButton:hover {{
    background-color: {BUTTON_SECONDARY_HOVER};
    border-color: {BUTTON_SECONDARY_BORDER};
}}
QPushButton:pressed, QToolButton:pressed {{
    background-color: {BUTTON_SECONDARY_PRESSED};
    border-color: {BUTTON_SECONDARY_BORDER};
}}
QPushButton:checked, QToolButton:checked {{
    background-color: {SELECTION_BG};
    border: 1px solid {SELECTION_BORDER};
}}
QPushButton:checked:hover, QToolButton:checked:hover {{
    background-color: {SELECTION_HOVER};
    border-color: {SELECTION_BORDER};
}}
"""

TOOLBAR_TOGGLE_STYLE = f"""
QPushButton {{
    background-color: {BUTTON_SECONDARY_BG};
    border: 1px solid {BUTTON_SECONDARY_BORDER};
    border-radius: {TOOLBAR_TOGGLE_RADIUS}px;
    padding: 0px;
    margin: 0px;
}}
QPushButton:hover {{
    background-color: {BUTTON_SECONDARY_HOVER};
    border-color: {BUTTON_SECONDARY_BORDER};
}}
QPushButton:pressed {{
    background-color: {BUTTON_SECONDARY_PRESSED};
    border-color: {BUTTON_SECONDARY_BORDER};
}}
QPushButton:checked {{
    background-color: {SELECTION_BG};
    border: 1px solid {SELECTION_BORDER};
}}
QPushButton:checked:hover {{
    background-color: {SELECTION_HOVER};
    border-color: {SELECTION_BORDER};
}}
"""
