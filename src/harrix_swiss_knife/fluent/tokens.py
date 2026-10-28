"""Fluent Design color tokens and shared metrics for light and dark themes.

Values follow the Windows 11 (WinUI 3) theme resources: layered window,
card and control fills with translucent strokes, and the default system
accent. Metrics are the only sizes Fluent widgets use for radii, spacing,
control heights, and the type ramp.

"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor


@dataclass(frozen=True, slots=True)
class FluentPalette:
    """One complete set of Fluent color tokens (light or dark)."""

    dark: bool
    window_bg: QColor
    layer_bg: QColor
    layer_alt_bg: QColor
    layer_stroke: QColor
    card_bg: QColor
    card_bg_hover: QColor
    card_bg_pressed: QColor
    card_stroke: QColor
    divider: QColor
    text_primary: QColor
    text_secondary: QColor
    text_tertiary: QColor
    text_disabled: QColor
    accent: QColor
    accent_hover: QColor
    accent_pressed: QColor
    accent_disabled: QColor
    accent_text: QColor
    text_on_accent: QColor
    control_fill: QColor
    control_fill_hover: QColor
    control_fill_pressed: QColor
    control_fill_disabled: QColor
    control_fill_input_active: QColor
    control_alt_fill: QColor
    control_stroke: QColor
    control_stroke_bottom: QColor
    control_strong_stroke: QColor
    control_strong_fill: QColor
    subtle_hover: QColor
    subtle_pressed: QColor
    popup_bg: QColor
    popup_stroke: QColor
    smoke: QColor
    solid_bg: QColor
    solid_secondary_bg: QColor
    solid_tertiary_bg: QColor
    solid_quarternary_bg: QColor
    success: QColor
    caution: QColor
    critical: QColor
    neutral: QColor
    success_bg: QColor
    caution_bg: QColor
    critical_bg: QColor
    neutral_bg: QColor
    focus_stroke_outer: QColor
    focus_stroke_inner: QColor
    shadow: QColor
    scrollbar_thumb: QColor
    scrollbar_thumb_hover: QColor


def _c(value: str) -> QColor:
    """Parse `#RRGGBB` or `#AARRGGBB` into a `QColor`."""
    return QColor(value)


LIGHT_PALETTE = FluentPalette(
    dark=False,
    window_bg=_c("#f3f3f3"),
    layer_bg=_c("#80ffffff"),
    layer_alt_bg=_c("#ffffffff"),
    layer_stroke=_c("#0f000000"),
    card_bg=_c("#b3ffffff"),
    card_bg_hover=_c("#80f9f9f9"),
    card_bg_pressed=_c("#4df9f9f9"),
    card_stroke=_c("#0f000000"),
    divider=_c("#14000000"),
    text_primary=_c("#e4000000"),
    text_secondary=_c("#9e000000"),
    text_tertiary=_c("#72000000"),
    text_disabled=_c("#5c000000"),
    accent=_c("#005fb8"),
    accent_hover=_c("#e6005fb8"),
    accent_pressed=_c("#cc005fb8"),
    accent_disabled=_c("#37000000"),
    accent_text=_c("#005fb8"),
    text_on_accent=_c("#ffffff"),
    control_fill=_c("#b3ffffff"),
    control_fill_hover=_c("#80f9f9f9"),
    control_fill_pressed=_c("#4df9f9f9"),
    control_fill_disabled=_c("#4df9f9f9"),
    control_fill_input_active=_c("#ffffff"),
    control_alt_fill=_c("#06000000"),
    control_stroke=_c("#0f000000"),
    control_stroke_bottom=_c("#29000000"),
    control_strong_stroke=_c("#72000000"),
    control_strong_fill=_c("#72000000"),
    subtle_hover=_c("#09000000"),
    subtle_pressed=_c("#06000000"),
    popup_bg=_c("#f9f9f9"),
    popup_stroke=_c("#e5e5e5"),
    smoke=_c("#4d000000"),
    solid_bg=_c("#f3f3f3"),
    solid_secondary_bg=_c("#eeeeee"),
    solid_tertiary_bg=_c("#f9f9f9"),
    solid_quarternary_bg=_c("#ffffff"),
    success=_c("#0f7b0f"),
    caution=_c("#9d5d00"),
    critical=_c("#c42b1c"),
    neutral=_c("#8a8a8a"),
    success_bg=_c("#dff6dd"),
    caution_bg=_c("#fff4ce"),
    critical_bg=_c("#fde7e9"),
    neutral_bg=_c("#f6f6f6"),
    focus_stroke_outer=_c("#e4000000"),
    focus_stroke_inner=_c("#b3ffffff"),
    shadow=_c("#24000000"),
    scrollbar_thumb=_c("#72000000"),
    scrollbar_thumb_hover=_c("#9e000000"),
)

DARK_PALETTE = FluentPalette(
    dark=True,
    window_bg=_c("#202020"),
    layer_bg=_c("#4c3a3a3a"),
    layer_alt_bg=_c("#0effffff"),
    layer_stroke=_c("#19000000"),
    card_bg=_c("#0dffffff"),
    card_bg_hover=_c("#15ffffff"),
    card_bg_pressed=_c("#08ffffff"),
    card_stroke=_c("#19000000"),
    divider=_c("#15ffffff"),
    text_primary=_c("#ffffff"),
    text_secondary=_c("#c5ffffff"),
    text_tertiary=_c("#87ffffff"),
    text_disabled=_c("#5dffffff"),
    accent=_c("#60cdff"),
    accent_hover=_c("#e660cdff"),
    accent_pressed=_c("#cc60cdff"),
    accent_disabled=_c("#28ffffff"),
    accent_text=_c("#99ebff"),
    text_on_accent=_c("#000000"),
    control_fill=_c("#0fffffff"),
    control_fill_hover=_c("#15ffffff"),
    control_fill_pressed=_c("#08ffffff"),
    control_fill_disabled=_c("#0bffffff"),
    control_fill_input_active=_c("#b31e1e1e"),
    control_alt_fill=_c("#19000000"),
    control_stroke=_c("#12ffffff"),
    control_stroke_bottom=_c("#18ffffff"),
    control_strong_stroke=_c("#8bffffff"),
    control_strong_fill=_c("#8bffffff"),
    subtle_hover=_c("#0fffffff"),
    subtle_pressed=_c("#0affffff"),
    popup_bg=_c("#2c2c2c"),
    popup_stroke=_c("#3a3a3a"),
    smoke=_c("#4d000000"),
    solid_bg=_c("#202020"),
    solid_secondary_bg=_c("#1c1c1c"),
    solid_tertiary_bg=_c("#282828"),
    solid_quarternary_bg=_c("#2c2c2c"),
    success=_c("#6ccb5f"),
    caution=_c("#fce100"),
    critical=_c("#ff99a4"),
    neutral=_c("#9d9d9d"),
    success_bg=_c("#393d1b"),
    caution_bg=_c("#433519"),
    critical_bg=_c("#442726"),
    neutral_bg=_c("#2e2e2e"),
    focus_stroke_outer=_c("#ffffff"),
    focus_stroke_inner=_c("#b3000000"),
    shadow=_c("#50000000"),
    scrollbar_thumb=_c("#87ffffff"),
    scrollbar_thumb_hover=_c("#c5ffffff"),
)

# Corner radii (WinUI `ControlCornerRadius` / `OverlayCornerRadius`).
RADIUS_SMALL = 2
RADIUS_CONTROL = 4
RADIUS_CARD = 8
RADIUS_OVERLAY = 8

# Spacing ramp (multiples of 4).
SPACE_XXS = 2
SPACE_XS = 4
SPACE_S = 8
SPACE_M = 12
SPACE_L = 16
SPACE_XL = 24
SPACE_XXL = 36

# Control metrics.
CONTROL_HEIGHT = 32
CONTROL_HEIGHT_COMPACT = 24
CONTROL_PADDING_H = 12
ICON_SIZE = 16
ICON_SIZE_LARGE = 24
CARD_ICON_SIZE = 40
NAV_ITEM_HEIGHT = 36
NAV_INDICATOR_WIDTH = 3
NAV_INDICATOR_HEIGHT = 16
TOGGLE_SWITCH_WIDTH = 40
TOGGLE_SWITCH_HEIGHT = 20
SCROLLBAR_THICKNESS = 6
SCROLLBAR_THICKNESS_HOVER = 8

# Command / setting card metrics.
COMMAND_CARD_WIDTH = 320
COMMAND_CARD_HEIGHT = 88
CARD_GRID_SPACING = SPACE_S

# Type ramp relative to the application body font (WinUI: Caption 12, Body 14,
# Subtitle 20, Title 28, Title Large 40, Display 68 px).
TYPE_CAPTION = 12 / 14
TYPE_BODY = 1.0
TYPE_BODY_LARGE = 18 / 14
TYPE_SUBTITLE = 20 / 14
TYPE_TITLE = 28 / 14
TYPE_TITLE_LARGE = 40 / 14
TYPE_DISPLAY = 68 / 14

# Animation durations (ms).
ANIMATION_FAST = 83
ANIMATION_NORMAL = 167
ANIMATION_SLOW = 250
