"""Shared light-plate toolbar button size and stylesheet."""

from __future__ import annotations

from harrix_swiss_knife.apps.common.ui_chrome import SELECTION_BG, SELECTION_BORDER, SELECTION_HOVER

TOOLBAR_BUTTON_SIZE = 40
TOOLBAR_TOGGLE_WIDTH = 64
TOOLBAR_BUTTON_GAP = 6
TOOLBAR_ICON_SIZE = 24
TOOLBAR_EDGE_MARGIN = 12
TOOLBAR_BORDER_RADIUS = 6
TOOLBAR_TOGGLE_RADIUS = TOOLBAR_BUTTON_SIZE // 2

# Default: light plate. Checked/selected: soft blue fill (Icons selection chrome).
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
    background-color: {SELECTION_BG};
    border: 1px solid {SELECTION_BORDER};
}}
QPushButton:checked:hover, QToolButton:checked:hover {{
    background-color: {SELECTION_HOVER};
    border-color: {SELECTION_BORDER};
}}
"""

# Pill toggles: round ends + soft on/off fill (screenshot shutter tools).
TOOLBAR_TOGGLE_STYLE = f"""
QPushButton {{
    background-color: #F5F5F7;
    border: 1px solid #E5E5E8;
    border-radius: {TOOLBAR_TOGGLE_RADIUS}px;
    padding: 0px;
    margin: 0px;
}}
QPushButton:hover {{
    background-color: #ECECEF;
    border-color: #D8D8DC;
}}
QPushButton:pressed {{
    background-color: #E2E2E6;
    border-color: #C8C8CC;
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
