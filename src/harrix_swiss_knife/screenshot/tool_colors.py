"""Per-tool screenshot colors stored in `config-temp.json`."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h
from PySide6.QtGui import QColor

from harrix_swiss_knife.paths import get_config_path_str
from harrix_swiss_knife.screenshot.annotations import AnnotationTool

_CONFIG_KEY = "screenshot_tool_colors"
_DEFAULT_COLOR = "#de2b26"
_HIGHLIGHT_COLOR = "#ffe14a"
_COLOR_TOOL_VALUES: tuple[str, ...] = (
    AnnotationTool.ARROW.value,
    AnnotationTool.RECTANGLE.value,
    AnnotationTool.ELLIPSE.value,
    AnnotationTool.LINE.value,
    AnnotationTool.PEN.value,
    AnnotationTool.TEXT.value,
    AnnotationTool.HIGHLIGHT.value,
)
COLOR_TOOLS: frozenset[AnnotationTool] = frozenset(tool for tool in AnnotationTool if tool.value in _COLOR_TOOL_VALUES)


def load_tool_colors(text_color: str) -> dict[str, str]:
    """Load each drawing tool's last color, falling back to defaults.

    `text_color` fills the text tool when `config-temp.json` has no saved text color.

    """
    colors = _default_tool_colors(text_color)
    try:
        loaded = h.dev.config_load(get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, TypeError, ValueError):
        return colors
    if not isinstance(loaded, dict):
        return colors
    raw = loaded.get(_CONFIG_KEY)
    if not isinstance(raw, dict):
        return colors
    entry: dict[str, Any] = raw
    for key in _COLOR_TOOL_VALUES:
        parsed = _normalize_color(str(entry.get(key) or ""))
        if parsed:
            colors[key] = parsed
    return colors


def save_tool_colors(colors: dict[str, str]) -> None:
    """Persist each drawing tool's color into `config-temp.json`."""
    payload: dict[str, str] = {}
    for key in _COLOR_TOOL_VALUES:
        parsed = _normalize_color(str(colors.get(key) or ""))
        if parsed:
            payload[key] = parsed
    try:
        h.dev.config_update_value(_CONFIG_KEY, payload, get_config_path_str(), is_temp=True)
    except (FileNotFoundError, OSError, TypeError, ValueError):
        return


def _default_tool_colors(text_color: str) -> dict[str, str]:
    colors = dict.fromkeys(_COLOR_TOOL_VALUES, _DEFAULT_COLOR)
    colors[AnnotationTool.HIGHLIGHT.value] = _HIGHLIGHT_COLOR
    parsed = _normalize_color(text_color)
    if parsed:
        colors[AnnotationTool.TEXT.value] = parsed
    return colors


def _normalize_color(value: str) -> str:
    text = value.strip()
    if not text or text.startswith("<"):
        return ""
    color = QColor(text)
    if not color.isValid():
        return ""
    return color.name()
