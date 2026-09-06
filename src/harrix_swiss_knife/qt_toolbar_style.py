"""Shared light-plate toolbar button size and stylesheet."""

from __future__ import annotations

TOOLBAR_BUTTON_SIZE = 40
TOOLBAR_BUTTON_GAP = 6
TOOLBAR_ICON_SIZE = 22
TOOLBAR_EDGE_MARGIN = 12
TOOLBAR_BORDER_RADIUS = 6

# Default: light plate. Checked/selected: accent fill + matching border.
TOOLBAR_BUTTON_STYLE = f"""
QPushButton, QToolButton {{
    background-color: #F5F5F7;
    border: 1px solid #E5E5E8;
    border-radius: {TOOLBAR_BORDER_RADIUS}px;
    padding: 0px;
    margin: 0px;
}}
QPushButton:hover, QToolButton:hover {{
    background-color: #ECECEF;
    border-color: #D8D8DC;
}}
QPushButton:pressed, QToolButton:pressed {{
    background-color: #E2E2E6;
    border-color: #C8C8CC;
}}
QPushButton:checked, QToolButton:checked {{
    background-color: #0072CA;
    border: 1px solid #0072CA;
}}
QPushButton:checked:hover, QToolButton:checked:hover {{
    background-color: #0060AB;
    border-color: #0060AB;
}}
"""
