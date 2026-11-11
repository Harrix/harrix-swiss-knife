"""Shared selection, buttons, and list chrome for tracker apps and overlays.

Soft-blue and neutrals match Harrix-HTML-Template (`$h-*` in `_variables.scss`).
See `.cursor/design-tokens.md` for the cross-repo table.

"""

from __future__ import annotations

import colorsys
import contextlib
import re
from typing import TYPE_CHECKING

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QAbstractItemView, QListView, QListWidget, QWidget

if TYPE_CHECKING:
    from collections.abc import Iterable

# Soft blue selection (site `$h-soft-*` / `$h-primary`).
SELECTION_BG = "#eaf1f8"
SELECTION_BORDER = "#3a78bc"
SELECTION_HOVER = "#f3f7fb"
SELECTION_TEXT = "#1a1a1a"
# Text on soft-blue chips / status labels (site `$h-brand-ink`).
BRAND_INK = "#2a5687"
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
# Tracker Add / primary CTAs use brand accent (aliases kept for call-site names).
BUTTON_CTA_CYAN_BG = BUTTON_PRIMARY_BG
BUTTON_CTA_CYAN_HOVER = BUTTON_PRIMARY_HOVER
BUTTON_CTA_GREEN_BG = BUTTON_PRIMARY_BG
BUTTON_CTA_GREEN_HOVER = BUTTON_PRIMARY_HOVER
BUTTON_CTA_MINT_BG = BUTTON_PRIMARY_BG
BUTTON_CTA_MINT_HOVER = BUTTON_PRIMARY_HOVER
# Text / icon on solid fills (CodeStyle white-on-fill + dark ink).
BUTTON_ON_DARK_FG = "#ffffff"
BUTTON_ON_DARK_ICON = "#f4f4f4"
BUTTON_ON_LIGHT_FG = "#122a3a"
# Shared metrics for solid and secondary `QPushButton` chrome.
BUTTON_PADDING = "0px 14px"
BUTTON_MIN_HEIGHT_PX = 32
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
    "#3a78bc",
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

# Hex, rgb/rgba (Fluent `css()`), or named Qt colors in button QSS.
_CSS_COLOR = r"(?:#[0-9a-fA-F]{3,8}|rgba?\([^)]+\)|\b[a-zA-Z]+\b)"
_BG_COLOR_RE = re.compile(rf"background-color\s*:\s*({_CSS_COLOR})", re.IGNORECASE)
# Idle `color:` only — skip `border-color` / `background-color` / `selection-color`.
_FG_COLOR_RE = re.compile(rf"(?<![-\w])color\s*:\s*({_CSS_COLOR})", re.IGNORECASE)
_RGBA_RE = re.compile(
    r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)",
    re.IGNORECASE,
)

# Compact chip / filter control.
CHIP_BG = "#f0f4f8"
CHIP_BORDER = "#d0d7de"
CHIP_HOVER = "#e4ebf2"
CHIP_CHECKED_BG = SELECTION_BG
CHIP_CHECKED_BORDER = SELECTION_BORDER


def action_card_selection_qss() -> str:
    """Return selection / hover QSS for Quick launcher action cards."""
    fill, hover, border, text = selection_chrome_colors()
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
    color: {text};
}}
QListWidget::item:hover:!selected {{
    background: {hover};
    border-color: {CHIP_BORDER};
}}
QListWidget::item:selected {{
    background: {fill};
    border: 1px solid {border};
    color: {text};
}}
""".strip()


def apply_readable_selection_palette(view: QAbstractItemView) -> None:
    """Keep selected-item text readable on soft selection fills (not system invert)."""
    fill, _hover, _border, text = selection_chrome_colors()
    palette = view.palette()
    highlight = QColor(fill) if fill.startswith("#") else _qcolor_from_css(fill)
    ink = QColor(text) if text.startswith("#") else _qcolor_from_css(text)
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive, QPalette.ColorGroup.Disabled):
        palette.setColor(group, QPalette.ColorRole.Highlight, highlight)
        palette.setColor(group, QPalette.ColorRole.HighlightedText, ink)
    view.setPalette(palette)


def apply_soft_form_spin_fills(host: object, names: tuple[str, ...]) -> None:
    """Apply `soft_field_qss` to named spin boxes on a tracker main window."""
    for name in names:
        control = getattr(host, name, None)
        if control is None:
            continue
        control.setStyleSheet(soft_field_qss(type(control).__name__))


def apply_soft_item_selection(view: QAbstractItemView) -> None:
    """Append soft selected / hover rules to a list view or list widget."""
    existing = (view.styleSheet() or "").rstrip()
    fill, hover, border, text = selection_chrome_colors()
    selector = "QListWidget" if isinstance(view, QListWidget) else "QListView"
    fragment = f"""
{selector}::item {{
    border-radius: 6px;
}}
{selector}::item:selected {{
    background-color: {fill};
    color: {text};
    border: 1px solid {border};
}}
{selector}::item:hover:!selected {{
    background-color: {hover};
}}
""".strip()
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

    Accent fills use the same stroke for text and Lucide icons. Low-chroma gray
    fills are ordinary chrome: dark text, but callers keep semantic icons.

    """
    if button_fill_is_ordinary(bg_hex):
        return BUTTON_SECONDARY_FG, BUTTON_ON_LIGHT_FG
    if relative_luminance(bg_hex) < _BUTTON_DARK_LUMINANCE_MAX:
        return BUTTON_ON_DARK_FG, BUTTON_ON_DARK_FG
    return BUTTON_ON_LIGHT_FG, BUTTON_ON_LIGHT_FG


def button_cta_cyan_qss(*, radius: int = PANEL_RADIUS) -> str:
    """Brand accent CTA fill (legacy cyan name). `radius` kept for callers."""
    del radius
    return _fluent_cta_button_qss()


def button_cta_green_qss(*, radius: int = PANEL_RADIUS) -> str:
    """Brand accent CTA fill (legacy green name). `radius` kept for callers."""
    del radius
    return _fluent_cta_button_qss()


def button_cta_mint_qss(*, radius: int = PANEL_RADIUS) -> str:
    """Brand accent CTA fill (legacy mint name). `radius` kept for callers."""
    del radius
    return _fluent_cta_button_qss()


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
    """Return idle `QPushButton` chrome (Cancel / Copy / filter / Add row).

    Tracker layout polish often runs after Fluent app chrome and on theme change.
    Hard white plates stay wrong in dark mode, so idle buttons follow the active
    Fluent secondary control fill whenever a theme is available.

    """
    try:
        from harrix_swiss_knife.fluent.style import push_button_qss  # noqa: PLC0415
        from harrix_swiss_knife.fluent.theme import FluentTheme  # noqa: PLC0415

        return push_button_qss(FluentTheme.instance().palette())
    except Exception:
        return solid_button_qss(
            SURFACE,
            hover=SELECTION_HOVER,
            pressed=BUTTON_SECONDARY_HOVER,
            border=INPUT_BORDER,
            radius=radius,
        )


def button_lucide_color_from_stylesheet(stylesheet: str | None) -> str | None:
    """Return Lucide stroke matching accent button text, or `None` for semantic.

    Fluent CTA QSS uses `rgba(...)` fills; ordinary gray/white chrome keeps
    CodeStyle semantic icon colors.

    """
    fill = button_fill_from_stylesheet(stylesheet)
    if fill is None or button_fill_is_ordinary(fill):
        return None
    text = button_text_color_from_stylesheet(stylesheet)
    if text is not None:
        return text
    return button_content_colors(fill)[1]


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


def button_text_color_from_stylesheet(stylesheet: str | None) -> str | None:
    """Parse the first idle `color:` from a button stylesheet, if any."""
    if not stylesheet:
        return None
    match = _FG_COLOR_RE.search(stylesheet)
    if match is None:
        return None
    return normalize_hex_color(match.group(1))


def drop_zone_qss(
    *,
    selected: bool = False,
    focused: bool = False,
    padding: str = "20px",
    radius: int = 5,
    selector: str = "QLabel",
) -> str:
    """Return drop-zone QSS (surface in light, Fluent card fill in dark)."""
    surface, hairline, input_border, muted = _surface_chrome_colors()
    _fill, hover, _border, _text = selection_chrome_colors()
    if selected:
        border = f"2px solid {BUTTON_SUCCESS_BG}"
        background = hover
    elif focused:
        border = f"2px dashed {muted}"
        background = hairline
    else:
        border = f"2px dashed {input_border}"
        background = surface
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


def media_preview_plate_qss(*, selector: str = "QLabel") -> str:
    """Return AVIF preview plate QSS (white in light, soft card gray in dark)."""
    plate = SURFACE
    with contextlib.suppress(Exception):
        from harrix_swiss_knife.fluent.theme import FluentTheme, css, mix  # noqa: PLC0415

        palette = FluentTheme.instance().palette()
        if palette.dark:
            plate = css(mix(palette.window_bg, palette.card_bg))
    return f"{selector} {{ background-color: {plate}; border: none; }}"


def media_preview_popup_frame_qss() -> str:
    """Return themed QSS for the exercise hover-preview popup frame."""
    plate = SURFACE
    border = INPUT_BORDER
    with contextlib.suppress(Exception):
        from harrix_swiss_knife.fluent.theme import FluentTheme, css, mix  # noqa: PLC0415

        palette = FluentTheme.instance().palette()
        plate = css(mix(palette.window_bg, palette.card_bg)) if palette.dark else SURFACE
        border = css(mix(palette.window_bg, palette.control_stroke))
    return f"""
QFrame {{
    background-color: {plate};
    border: 1px solid {border};
    border-radius: 6px;
}}
""".strip()


def muted_caption_qss(*, bold: bool = True, extra: str = "") -> str:
    """Return theme-aware muted caption QSS (`MUTED_TEXT` in light)."""
    _surface, _hairline, _input_border, muted = _surface_chrome_colors()
    weight = "600" if bold else "400"
    suffix = f" {extra}" if extra and not extra.startswith(" ") else extra
    return f"color: {muted}; font-weight: {weight};{suffix}"


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
    """Normalize `#rgb` / `#rrggbb` / `rgb()` / `rgba()` / named colors to `#rrggbb`."""
    text = value.strip()
    if not text:
        return None
    match = _RGBA_RE.fullmatch(text)
    if match is not None:
        red, green, blue = int(match.group(1)), int(match.group(2)), int(match.group(3))
        alpha = 255
        if match.group(4) is not None:
            raw = float(match.group(4))
            # Fluent `css()` uses 0-255; CSS rgba often uses 0-1.
            alpha = round(raw) if raw > 1.0 else round(raw * 255)
        color = QColor(red, green, blue, max(0, min(255, alpha)))
    else:
        color = QColor(text)
    if not color.isValid():
        return None
    return color.name(QColor.NameFormat.HexRgb)


def record_caption_stop_qss() -> str:
    """Return theme-aware QSS for the recording stop-state caption."""
    base = "#1a1a1a"
    hover = "#333333"
    with contextlib.suppress(Exception):
        from harrix_swiss_knife.fluent.theme import FluentTheme, css, mix  # noqa: PLC0415

        palette = FluentTheme.instance().palette()
        base = css(mix(palette.window_bg, palette.text_primary))
        hover = css(mix(palette.window_bg, palette.text_secondary))
    return f"""
    QLabel {{
        color: {base};
    }}
    QLabel:hover {{
        color: {hover};
    }}
""".strip()


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


def selection_chrome_colors() -> tuple[str, str, str, str]:
    """Return `(fill, hover, border, text)` for soft list/card selection.

    Light mode keeps the shared soft-blue tokens. Dark mode uses Fluent list
    selection fills so tiles are not bright white islands.

    """
    with contextlib.suppress(Exception):
        from harrix_swiss_knife.fluent.style import list_item_hover, list_item_selected  # noqa: PLC0415
        from harrix_swiss_knife.fluent.theme import FluentTheme, css, mix  # noqa: PLC0415

        palette = FluentTheme.instance().palette()
        if palette.dark:
            return (
                css(list_item_selected(palette)),
                css(list_item_hover(palette)),
                css(mix(palette.window_bg, palette.accent)),
                css(mix(palette.window_bg, palette.text_primary)),
            )
    return SELECTION_BG, SELECTION_HOVER, SELECTION_BORDER, SELECTION_TEXT


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
    """Return theme-aware fill for highlighted form fields (spin boxes, etc.)."""
    fill = SELECTION_BG
    with contextlib.suppress(Exception):
        from harrix_swiss_knife.fluent.theme import FluentTheme, css, mix  # noqa: PLC0415

        palette = FluentTheme.instance().palette()
        if palette.dark:
            fill = css(mix(palette.window_bg, palette.control_fill_input_active))
        else:
            fill, _, _, _ = selection_chrome_colors()
    return f"""
{selector} {{
    background-color: {fill};
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


def _fluent_cta_button_qss() -> str:
    """Return Fluent accent button QSS tagged for theme refresh."""
    return _fluent_role_button_qss("accent")


def _fluent_role_button_qss(kind: str) -> str:
    """Return a theme-aware solid button tagged so app chrome keeps its role."""
    from harrix_swiss_knife.fluent.style import semantic_button_qss  # noqa: PLC0415
    from harrix_swiss_knife.fluent.theme import FluentTheme  # noqa: PLC0415

    return f"/* hsk-fluent-{kind} */\n{semantic_button_qss(FluentTheme.instance().palette(), kind)}"


def _parse_rgb(hex_color: str | None) -> tuple[int, int, int] | None:
    if not hex_color:
        return None
    normalized = normalize_hex_color(hex_color)
    if normalized is None:
        return None
    value = normalized.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _qcolor_from_css(value: str) -> QColor:
    """Parse `#RRGGBB` or `rgba(r, g, b, a)` into a `QColor`."""
    text = value.strip()
    if text.startswith("#"):
        return QColor(text)
    match = re.fullmatch(
        r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+(?:\.\d+)?)\s*\)",
        text,
        flags=re.IGNORECASE,
    )
    if match is None:
        return QColor(SELECTION_TEXT)
    red, green, blue, alpha = match.groups()
    color = QColor(int(red), int(green), int(blue))
    alpha_f = float(alpha)
    color.setAlpha(int(alpha_f * 255) if alpha_f <= 1.0 else int(alpha_f))
    return color


def _surface_chrome_colors() -> tuple[str, str, str, str]:
    """Return `(surface, hairline, input_border, muted_text)` for panels/captions."""
    with contextlib.suppress(Exception):
        from harrix_swiss_knife.fluent.theme import FluentTheme, css, mix  # noqa: PLC0415

        palette = FluentTheme.instance().palette()
        if palette.dark:
            return (
                css(mix(palette.window_bg, palette.card_bg)),
                css(mix(palette.window_bg, palette.divider)),
                css(mix(palette.window_bg, palette.control_stroke)),
                css(mix(palette.window_bg, palette.text_secondary)),
            )
    return SURFACE, HAIRLINE, INPUT_BORDER, MUTED_TEXT
