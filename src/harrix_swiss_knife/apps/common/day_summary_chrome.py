"""Shared type roles for Finance / Fitness / Food day summaries in column 1.

Uses the Fluent type ramp (`TYPE_*` relative to the app body font) so sizes
track DPI and the user scale. Values stay plain labels or rich text; chrome
does not add cards, frames, or decorative fills.

Logical-px targets at the default 14px body: caption ~14, today ~28,
yesterday ~20, unit/secondary ~16–18.

"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QLabel, QSizePolicy, QWidget

from harrix_swiss_knife.apps.common.ui_chrome import muted_caption_qss
from harrix_swiss_knife.fluent.theme import css, fluent_font, mix, palette_for
from harrix_swiss_knife.fluent.tokens import (
    SPACE_XS,
    TYPE_BODY,
    TYPE_BODY_LARGE,
    TYPE_SUBTITLE,
    TYPE_TITLE,
)

# Caption / today primary / yesterday / drink-or-unit line (scales of body).
_CAPTION_SCALE = TYPE_BODY
_TODAY_VALUE_SCALE = TYPE_TITLE
_YESTERDAY_VALUE_SCALE = TYPE_SUBTITLE
_TODAY_SECONDARY_SCALE = TYPE_BODY_LARGE
_YESTERDAY_SECONDARY_SCALE = TYPE_BODY


def apply_day_summary_caption(label: QLabel) -> None:
    """Style a period caption (Today / Yesterday) smaller than the value."""
    label.setFont(fluent_font(_summary_base_font(label), _CAPTION_SCALE))
    label.setStyleSheet(muted_caption_qss())
    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)


def apply_day_summary_value(label: QLabel, *, today: bool = True) -> None:
    """Style a numeric day-summary value; today is the primary emphasis."""
    scale = _TODAY_VALUE_SCALE if today else _YESTERDAY_VALUE_SCALE
    label.setFont(fluent_font(_summary_base_font(label), scale, weight=QFont.Weight.DemiBold))
    palette = palette_for(label)
    color = css(mix(palette.window_bg, palette.text_primary))
    label.setStyleSheet(f"color: {color}; border: none; background: transparent;")
    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    metrics = label.fontMetrics()
    label.setMinimumHeight(max(label.minimumHeight(), metrics.height() + SPACE_XS))


def apply_food_day_summary_label(
    label: QLabel,
    calories: float,
    drinks_weight: int,
    *,
    today: bool,
) -> None:
    """Paint kcal (primary) and drink volume (secondary) with units bound to values."""
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    # Font/min-height from the value role; HTML colors and sizes carry the hierarchy.
    apply_day_summary_value(label, today=today)
    label.setText(format_food_day_summary_html(label, calories, drinks_weight, today=today))


def format_food_day_summary_html(
    widget: QWidget,
    calories: float,
    drinks_weight: int,
    *,
    today: bool,
) -> str:
    """Return rich text: large kcal line, then drinks; nbsp keeps units with numbers."""
    drinks_liters = drinks_weight / 1000 if drinks_weight else 0.0
    base = _summary_base_font(widget)
    kcal_font = fluent_font(
        base,
        _TODAY_VALUE_SCALE if today else _YESTERDAY_VALUE_SCALE,
        weight=QFont.Weight.DemiBold,
    )
    drink_font = fluent_font(
        base,
        _TODAY_SECONDARY_SCALE if today else _YESTERDAY_SECONDARY_SCALE,
        weight=QFont.Weight.DemiBold,
    )
    palette = palette_for(widget)
    primary = css(mix(palette.window_bg, palette.text_primary))
    # Secondary line stays readable (not disabled); slightly quieter than kcal.
    secondary = css(mix(palette.window_bg, palette.text_secondary))
    kcal_text = f"{calories:.1f}&nbsp;kcal"
    drink_text = f"{drinks_liters:.1f}&nbsp;L"
    return (
        f'<div style="color:{primary}; font-size:{_font_size_css(kcal_font)}; '
        f'font-weight:600;">{kcal_text}</div>'
        f'<div style="color:{secondary}; font-size:{_font_size_css(drink_font)}; '
        f'font-weight:600; margin-top:2px;">{drink_text}</div>'
    )


def _font_size_css(font: QFont) -> str:
    if font.pointSizeF() > 0:
        return f"{font.pointSizeF():.2f}pt"
    if font.pixelSize() > 0:
        return f"{font.pixelSize()}px"
    return "14pt"


def _summary_base_font(widget: QWidget) -> QFont:
    """Return the app body font so repeated polish does not compound scales."""
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return QFont(app.font())
    return QFont(widget.font())
