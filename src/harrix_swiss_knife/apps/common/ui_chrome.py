"""Shared selection, buttons, and list chrome for tracker apps and overlays.

Soft-blue and neutrals match Harrix-HTML-Template (`$h-*` in `_variables.scss`).
See `.cursor/design-tokens.md` for the cross-repo table.

"""

from __future__ import annotations

import colorsys
import re
from typing import TYPE_CHECKING

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QAbstractItemView, QListView, QListWidget, QWidget

if TYPE_CHECKING:
    from collections.abc import Iterable

# Soft blue selection (site `$h-soft-*` / `$h-primary`).
SELECTION_BG = "#e8f4fc"
SELECTION_BORDER = "#2e86b7"
SELECTION_HOVER = "#f3f8fb"
SELECTION_TEXT = "#1a1a1a"
# Text on soft-blue chips / status labels (site `$h-brand-ink`).
BRAND_INK = "#1a5f7a"
# Secondary labels — avoid palette(mid), which is nearly white on some light themes.
MUTED_TEXT = "#5c6370"
SURFACE = "#ffffff"

# Neutrals (site `$h-border` / `$h-hairline` / `$h-separator`).
INPUT_BORDER = "#dbdbdb"
HAIRLINE = "#f0f0f0"
SEPARATOR = "#e0e0e0"
INPUT_RADIUS = 6
PANEL_RADIUS = 4

# Solid primary / secondary / semantic buttons (site Bulma `.is-primary` / light).
BUTTON_PRIMARY_BG = SELECTION_BORDER
BUTTON_PRIMARY_BORDER = SELECTION_BORDER
BUTTON_PRIMARY_FG = "#ffffff"
BUTTON_PRIMARY_HOVER = BRAND_INK
BUTTON_SECONDARY_BG = "#f5f5f5"
BUTTON_SECONDARY_HOVER = "#ececec"
BUTTON_SECONDARY_PRESSED = "#e2e2e2"
BUTTON_SECONDARY_BORDER = INPUT_BORDER
BUTTON_SECONDARY_FG = SELECTION_TEXT
BUTTON_SUCCESS_BG = "#4caf50"
BUTTON_SUCCESS_HOVER = "#35965f"
BUTTON_DANGER_BG = "#cc584c"
BUTTON_DANGER_HOVER = "#ad403b"
# App CTAs restored from pre-unify soft fills → nearest CodeStyle brand hex.
BUTTON_CTA_CYAN_BG = "#79b1d1"  # was Material soft blue `#e3f2fd`
BUTTON_CTA_CYAN_HOVER = "#2e86b7"
BUTTON_CTA_GREEN_BG = "#4caf50"  # was soft green / lightgreen
BUTTON_CTA_GREEN_HOVER = "#35965f"
BUTTON_CTA_MINT_BG = "#3aaf9d"  # was finance mint `#C1ECDD`
BUTTON_CTA_MINT_HOVER = "#038387"
# Text / icon on solid fills (CodeStyle white-on-fill + dark ink).
BUTTON_ON_DARK_FG = "#ffffff"
BUTTON_ON_DARK_ICON = "#f4f4f4"
BUTTON_ON_LIGHT_FG = "#122a3a"
# Shared metrics for solid and secondary `QPushButton` chrome.
BUTTON_PADDING = "5px 14px"
BUTTON_MIN_HEIGHT_PX = 28
# Contrast / “ordinary gray” thresholds for solid fills.
_BUTTON_DARK_LUMINANCE_MAX = 0.55
_ORDINARY_FILL_CHROMA_MAX = 18
_ORDINARY_FILL_LUMINANCE_MIN = 0.45
_WCAG_LINEAR_CHANNEL_CUTOFF = 0.03928
_HSL_SATURATION_CHROMA_MIN = 0.08

# Harrix CodeStyle vector palette (style__vector-images.md).
CODESTYLE_PALETTE: tuple[str, ...] = (
    "#ffffff",
    "#f4f4f4",
    "#e9e9e9",
    "#dddddd",
    "#bbbbbb",
    "#999999",
    "#444444",
    "#607785",
    "#7193ad",
    "#36434f",
    "#122a3a",
    "#121e28",
    "#79b1d1",
    "#2e86b7",
    "#038387",
    "#3aaf9d",
    "#de2b26",
    "#cc584c",
    "#f84d18",
    "#ad403b",
    "#eec646",
    "#ffdd7a",
    "#ffa000",
    "#df7148",
    "#4caf50",
    "#35965f",
    "#ffcc80",
    "#e3b877",
    "#ddc4b0",
    "#e0ac7e",
    "#a18267",
    "#66442b",
)

_BG_COLOR_RE = re.compile(
    r"background-color\s*:\s*(#[0-9a-fA-F]{3,8}|\b[a-zA-Z]+\b)",
    re.IGNORECASE,
)

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
    margin: 0px;
    padding: 2px;
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


def apply_white_surface_palette(widget: QWidget) -> None:
    """Paint `widget` with the shared white surface (dialogs / panels).

    Sets `Window` / `Base` / `AlternateBase` to `SURFACE` so modal forms are not
    system gray. Idempotent.

    """
    white = QColor(SURFACE)
    palette = widget.palette()
    changed = False
    for role in (
        QPalette.ColorRole.Window,
        QPalette.ColorRole.Base,
        QPalette.ColorRole.AlternateBase,
    ):
        if palette.color(role) != white:
            palette.setColor(role, white)
            changed = True
    if changed:
        widget.setPalette(palette)
    if not widget.autoFillBackground():
        widget.setAutoFillBackground(True)


def button_content_colors(bg_hex: str) -> tuple[str, str]:
    """Return `(text_hex, icon_hex)` for a solid fill.

    Dark / saturated fills use white text and near-white icons. Light fills use
    dark ink for both. Low-chroma gray fills are treated as ordinary chrome:
    dark text, but callers should keep semantic (colored) icons.

    """
    if button_fill_is_ordinary(bg_hex):
        return BUTTON_SECONDARY_FG, BUTTON_ON_LIGHT_FG
    if relative_luminance(bg_hex) < _BUTTON_DARK_LUMINANCE_MAX:
        return BUTTON_ON_DARK_FG, BUTTON_ON_DARK_ICON
    return BUTTON_ON_LIGHT_FG, BUTTON_ON_LIGHT_FG


def button_cta_cyan_qss(*, radius: int = PANEL_RADIUS) -> str:
    """Soft-blue app CTA fill (`#e3f2fd` → nearest brand `#79b1d1`)."""
    return solid_button_qss(
        BUTTON_CTA_CYAN_BG,
        hover=BUTTON_CTA_CYAN_HOVER,
        pressed=BUTTON_PRIMARY_HOVER,
        radius=radius,
    )


def button_cta_green_qss(*, radius: int = PANEL_RADIUS) -> str:
    """Soft-green app CTA fill (lightgreen / `#e8f5e9` → `#4caf50`)."""
    return solid_button_qss(
        BUTTON_CTA_GREEN_BG,
        hover=BUTTON_CTA_GREEN_HOVER,
        pressed="#2e7d4f",
        radius=radius,
    )


def button_cta_mint_qss(*, radius: int = PANEL_RADIUS) -> str:
    """Finance mint CTA fill (`#C1ECDD` → nearest brand `#3aaf9d`)."""
    return solid_button_qss(
        BUTTON_CTA_MINT_BG,
        hover=BUTTON_CTA_MINT_HOVER,
        pressed="#026a6d",
        radius=radius,
    )


def button_danger_qss(*, radius: int = PANEL_RADIUS) -> str:
    """Return solid danger `QPushButton` stylesheet (site `$h-danger`)."""
    return solid_button_qss(
        BUTTON_DANGER_BG,
        hover=BUTTON_DANGER_HOVER,
        pressed="#8f342f",
        radius=radius,
    )


def button_fill_from_stylesheet(stylesheet: str | None) -> str | None:
    """Parse the first `background-color` from a button stylesheet, if any."""
    if not stylesheet:
        return None
    match = _BG_COLOR_RE.search(stylesheet)
    if match is None:
        return None
    return normalize_hex_color(match.group(1))


def button_fill_is_ordinary(bg_hex: str) -> bool:
    """Return whether `bg_hex` is a low-chroma gray (semantic icons stay)."""
    rgb = _parse_rgb(bg_hex)
    if rgb is None:
        return True
    return _chroma(rgb) < _ORDINARY_FILL_CHROMA_MAX and relative_luminance(bg_hex) > _ORDINARY_FILL_LUMINANCE_MIN


def button_icon_color_for_bg(bg_hex: str | None) -> str | None:
    """Return a forced Lucide stroke for a fill, or `None` for semantic colors."""
    if bg_hex is None or button_fill_is_ordinary(bg_hex):
        return None
    return button_content_colors(bg_hex)[1]


def button_idle_qss(*, radius: int = PANEL_RADIUS) -> str:
    """Return white outlined idle `QPushButton` chrome (Cancel / Copy / Add row)."""
    return solid_button_qss(
        SURFACE,
        hover=SELECTION_HOVER,
        pressed=BUTTON_SECONDARY_HOVER,
        border=INPUT_BORDER,
        radius=radius,
    )


def button_primary_qss(*, radius: int = PANEL_RADIUS) -> str:
    """Return solid primary `QPushButton` stylesheet (site `.button.is-primary`)."""
    return solid_button_qss(
        BUTTON_PRIMARY_BG,
        hover=BUTTON_PRIMARY_HOVER,
        pressed=BUTTON_PRIMARY_HOVER,
        radius=radius,
    )


def button_secondary_qss(*, radius: int = PANEL_RADIUS) -> str:
    """Return light secondary `QPushButton` stylesheet (site `.button.is-light`)."""
    return solid_button_qss(
        BUTTON_SECONDARY_BG,
        hover=BUTTON_SECONDARY_HOVER,
        pressed=BUTTON_SECONDARY_PRESSED,
        border=BUTTON_SECONDARY_BORDER,
        radius=radius,
    )


def button_success_qss(*, radius: int = PANEL_RADIUS) -> str:
    """Return solid success `QPushButton` stylesheet (site `$h-success`)."""
    return solid_button_qss(
        BUTTON_SUCCESS_BG,
        hover=BUTTON_SUCCESS_HOVER,
        pressed="#2e7d4f",
        radius=radius,
    )


def drop_zone_qss(
    *,
    selected: bool = False,
    focused: bool = False,
    padding: str = "20px",
    radius: int = 5,
    selector: str = "QLabel",
) -> str:
    """Return white drop-zone QSS (replaces legacy gray `#f9f9f9` panels)."""
    if selected:
        border = f"2px solid {BUTTON_SUCCESS_BG}"
        background = SELECTION_HOVER
    elif focused:
        border = f"2px dashed {MUTED_TEXT}"
        background = HAIRLINE
    else:
        border = f"2px dashed {INPUT_BORDER}"
        background = SURFACE
    return f"""
{selector} {{
    border: {border};
    border-radius: {radius}px;
    padding: {padding};
    background-color: {background};
}}
""".strip()


def list_view_item_selection_qss(*, with_row_separators: bool = False) -> str:
    """Return QSS for `QListView::item` selected / hover states.

    Args:

    - `with_row_separators` (`bool`): When `True`, keep a light bottom border
      between rows (finance / food / fitness filter lists).

    Returns:

    - `str`: Stylesheet fragment for list items (does not set the outer list border).

    """
    separator = f"border-bottom: 1px solid {SEPARATOR};" if with_row_separators else ""
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
    border-radius: {PANEL_RADIUS}px;
    background-color: {SURFACE};
    outline: none;
}}
{list_view_item_selection_qss(with_row_separators=with_row_separators)}
""".strip()


def nearest_codestyle_color(
    hex_color: str,
    *,
    palette: Iterable[str] = CODESTYLE_PALETTE,
) -> str:
    """Map any hex to the nearest CodeStyle brand color (HSL-weighted)."""
    rgb = _parse_rgb(hex_color)
    if rgb is None:
        return BUTTON_PRIMARY_BG
    best = min(palette, key=lambda candidate: _color_distance(rgb, _parse_rgb(candidate) or rgb))
    return best.lower() if best.startswith("#") else best


def normalize_hex_color(value: str) -> str | None:
    """Normalize `#rgb` / `#rrggbb` / named Qt colors used in stylesheets."""
    text = value.strip()
    if not text:
        return None
    color = QColor(text)
    if not color.isValid():
        return None
    return color.name(QColor.NameFormat.HexRgb)


def relative_luminance(hex_color: str) -> float:
    """WCAG relative luminance of `hex_color` in `0..1`."""
    rgb = _parse_rgb(hex_color)
    if rgb is None:
        return 1.0

    def channel(value: int) -> float:
        c = value / 255.0
        return c / 12.92 if c <= _WCAG_LINEAR_CHANNEL_CUTOFF else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


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


def soft_field_qss(selector: str = "QWidget") -> str:
    """Return soft-blue fill for highlighted form fields (spin boxes, etc.)."""
    return f"""
{selector} {{
    background-color: {SELECTION_BG};
}}
""".strip()


def solid_button_qss(
    bg: str,
    *,
    hover: str | None = None,
    pressed: str | None = None,
    border: str | None = None,
    radius: int = PANEL_RADIUS,
) -> str:
    """Solid fill button QSS with contrast text and native-like padding.

    Border matches the fill (no contrasting outline) unless `border` is set.

    """
    fg, _icon = button_content_colors(bg)
    hover_bg = hover or bg
    pressed_bg = pressed or hover_bg
    border_color = border or bg
    hover_border = border or hover_bg
    pressed_border = border or pressed_bg
    hover_fg, _ = button_content_colors(hover_bg)
    pressed_fg, _ = button_content_colors(pressed_bg)
    return f"""
QPushButton {{
    background-color: {bg};
    color: {fg};
    border: 1px solid {border_color};
    border-radius: {radius}px;
    padding: {BUTTON_PADDING};
    min-height: {BUTTON_MIN_HEIGHT_PX}px;
}}
QPushButton:hover {{
    background-color: {hover_bg};
    color: {hover_fg};
    border-color: {hover_border};
}}
QPushButton:pressed {{
    background-color: {pressed_bg};
    color: {pressed_fg};
    border-color: {pressed_border};
}}
""".strip()


def _chroma(rgb: tuple[int, int, int]) -> int:
    return max(rgb) - min(rgb)


def _color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    ha, la, sa = colorsys.rgb_to_hls(*(c / 255 for c in a))
    hb, lb, sb = colorsys.rgb_to_hls(*(c / 255 for c in b))
    dh = min(abs(ha - hb), 1 - abs(ha - hb))
    weight_h = 3.0 if sa > _HSL_SATURATION_CHROMA_MIN and sb > _HSL_SATURATION_CHROMA_MIN else 0.5
    return (weight_h * dh) ** 2 + (la - lb) ** 2 + (sa - sb) ** 2


def _parse_rgb(hex_color: str | None) -> tuple[int, int, int] | None:
    if not hex_color:
        return None
    normalized = normalize_hex_color(hex_color)
    if normalized is None:
        return None
    value = normalized.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
