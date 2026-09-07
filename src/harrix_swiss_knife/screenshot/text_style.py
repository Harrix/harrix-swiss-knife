"""Screenshot text annotation style helpers and `config-temp.json` persistence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import harrix_pylib as h
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QFont, QFontDatabase, QFontMetricsF

from harrix_swiss_knife.paths import get_config_path_str
from harrix_swiss_knife.qt_app_font import MONO_FONT_FAMILY, load_jetbrains_mono_fonts
from harrix_swiss_knife.screenshot.annotations import AnnotationStyle

TextAlign = Literal["left", "center", "right"]

_CONFIG_KEY = "screenshot_text"
_FALLBACK_FAMILY = "Arial"
_DEFAULT_SIZE = 26.0
_DEFAULT_COLOR = "#de2b26"
_SIZE_CHOICES: tuple[float, ...] = (
    8,
    9,
    10,
    11,
    12,
    14,
    16,
    18,
    20,
    22,
    24,
    26,
    28,
    32,
    36,
    48,
    72,
)


@dataclass(slots=True)
class ScreenshotTextSettings:
    """Persisted defaults for the screenshot text tool."""

    font_family: str = ""
    font_size: float = _DEFAULT_SIZE
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikeout: bool = False
    align: TextAlign = "left"
    background_fill: bool = False
    color: str = _DEFAULT_COLOR


def default_text_font_family() -> str:
    """Return JetBrains Mono when bundled/available, otherwise Arial."""
    from PySide6.QtWidgets import QApplication  # noqa: PLC0415

    if QApplication.instance() is None:
        return MONO_FONT_FAMILY
    load_jetbrains_mono_fonts()
    families = set(QFontDatabase.families())
    if MONO_FONT_FAMILY in families:
        return MONO_FONT_FAMILY
    if _FALLBACK_FAMILY in families:
        return _FALLBACK_FAMILY
    return QFont().defaultFamily() or _FALLBACK_FAMILY


def font_size_choices() -> tuple[float, ...]:
    """Return common point sizes for the text toolbar."""
    return _SIZE_CHOICES


def load_screenshot_text_settings() -> ScreenshotTextSettings:
    """Load text-tool defaults from `config-temp.json`."""
    raw: dict[str, Any] = {}
    try:
        loaded = h.dev.config_load(get_config_path_str(), is_temp=True)
        if isinstance(loaded, dict):
            entry = loaded.get(_CONFIG_KEY)
            if isinstance(entry, dict):
                raw = entry
    except (FileNotFoundError, OSError, TypeError, ValueError):
        raw = {}
    family = str(raw.get("font_family") or "").strip() or default_text_font_family()
    try:
        size = float(raw.get("font_size", _DEFAULT_SIZE))
    except (TypeError, ValueError):
        size = _DEFAULT_SIZE
    size = max(6.0, min(200.0, size))
    align_raw = str(raw.get("align", "left")).strip().lower()
    align: TextAlign = align_raw if align_raw in {"left", "center", "right"} else "left"
    color = str(raw.get("color") or _DEFAULT_COLOR).strip()
    if not QColor(color).isValid():
        color = _DEFAULT_COLOR
    return ScreenshotTextSettings(
        font_family=family,
        font_size=size,
        bold=bool(raw.get("bold", False)),
        italic=bool(raw.get("italic", False)),
        underline=bool(raw.get("underline", False)),
        strikeout=bool(raw.get("strikeout", False)),
        align=align,
        background_fill=bool(raw.get("background_fill", False)),
        color=color,
    )


def save_screenshot_text_settings(settings: ScreenshotTextSettings) -> None:
    """Persist text-tool defaults into `config-temp.json`."""
    payload = {
        "font_family": settings.font_family,
        "font_size": settings.font_size,
        "bold": settings.bold,
        "italic": settings.italic,
        "underline": settings.underline,
        "strikeout": settings.strikeout,
        "align": settings.align,
        "background_fill": settings.background_fill,
        "color": settings.color,
    }
    h.dev.config_update_value(_CONFIG_KEY, payload, get_config_path_str(), is_temp=True)


def settings_to_annotation_style(settings: ScreenshotTextSettings) -> AnnotationStyle:
    """Build an `AnnotationStyle` from persisted text settings."""
    return AnnotationStyle(
        color=QColor(settings.color),
        width=3.0,
        font_family=settings.font_family or default_text_font_family(),
        font_size=settings.font_size,
        bold=settings.bold,
        italic=settings.italic,
        underline=settings.underline,
        strikeout=settings.strikeout,
        align=settings.align,
        background_fill=settings.background_fill,
    )


def annotation_style_to_settings(style: AnnotationStyle) -> ScreenshotTextSettings:
    """Snapshot text fields from `style` for the toolbar / config."""
    align: TextAlign = style.align if style.align in {"left", "center", "right"} else "left"
    return ScreenshotTextSettings(
        font_family=style.font_family or default_text_font_family(),
        font_size=max(6.0, style.font_size),
        bold=style.bold,
        italic=style.italic,
        underline=style.underline,
        strikeout=style.strikeout,
        align=align,
        background_fill=style.background_fill,
        color=style.color.name() if style.color.isValid() else _DEFAULT_COLOR,
    )


def annotation_qfont(style: AnnotationStyle) -> QFont:
    """Build the QFont used to paint/edit a text annotation."""
    family = style.font_family.strip() if style.font_family else ""
    if not family:
        family = default_text_font_family()
    font = QFont(family)
    font.setPointSizeF(max(6.0, style.font_size))
    font.setBold(style.bold)
    font.setItalic(style.italic)
    font.setUnderline(style.underline)
    font.setStrikeOut(style.strikeout)
    return font


def default_text_box_points(origin: QPointF, style: AnnotationStyle) -> list[QPointF]:
    """Return a default `[topLeft, bottomRight]` text box at `origin`."""
    metrics = QFontMetricsF(annotation_qfont(style))
    width = max(metrics.averageCharWidth() * 14.0, 140.0)
    height = max(metrics.height() * 2.8, 48.0)
    return [QPointF(origin), QPointF(origin.x() + width, origin.y() + height)]


def available_text_font_families() -> list[str]:
    """Return UI font list with JetBrains Mono / Arial preferred at the top."""
    from PySide6.QtWidgets import QApplication  # noqa: PLC0415

    if QApplication.instance() is None:
        return [MONO_FONT_FAMILY, _FALLBACK_FAMILY]
    load_jetbrains_mono_fonts()
    families = sorted(QFontDatabase.families(), key=str.casefold)
    preferred = [name for name in (MONO_FONT_FAMILY, _FALLBACK_FAMILY) if name in families]
    rest = [name for name in families if name not in preferred]
    return [*preferred, *rest]


def copy_annotation_style(style: AnnotationStyle) -> AnnotationStyle:
    """Return a deep-enough copy of `style`."""
    return AnnotationStyle(
        color=QColor(style.color),
        width=style.width,
        font_family=style.font_family,
        font_size=style.font_size,
        bold=style.bold,
        italic=style.italic,
        underline=style.underline,
        strikeout=style.strikeout,
        align=style.align,
        background_fill=style.background_fill,
    )
