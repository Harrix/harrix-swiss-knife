"""QSS builders and icon helpers that turn Fluent tokens into widget chrome.

Each builder returns a stylesheet for one widget (selectors use `objectName`
or the widget class), so applying it never restyles unrelated widgets.

"""

from __future__ import annotations

import tempfile
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap

from harrix_swiss_knife.fluent.theme import css, mix
from harrix_swiss_knife.fluent.tokens import (
    CONTROL_HEIGHT,
    CONTROL_PADDING_H,
    DATE_EDIT_DROP_WIDTH,
    ICON_SIZE,
    RADIUS_CARD,
    RADIUS_CONTROL,
    RADIUS_OVERLAY,
    SCROLLBAR_THICKNESS,
    SPACE_L,
    SPACE_S,
    SPACE_XS,
    TAB_GAP,
    TAB_INDICATOR_HEIGHT,
    FluentPalette,
)
from harrix_swiss_knife.qt_lucide_icon import create_lucide_icon

_URL_CACHE: dict[tuple[str, str, int], str] = {}


def accent_button_qss(palette: FluentPalette, selector: str = "QPushButton") -> str:
    """Return the accent (primary) button stylesheet."""
    return f"""
{selector} {{
    background-color: {css(palette.accent)};
    color: {css(palette.text_on_accent)};
    border: 1px solid {css(palette.accent)};
    border-bottom-color: {css(mix(palette.accent, QColor(0, 0, 0, 40)))};
    border-radius: {RADIUS_CONTROL}px;
    padding: 0px {CONTROL_PADDING_H}px;
    min-height: {CONTROL_HEIGHT - 2}px;
}}
{selector}:hover {{ background-color: {css(palette.accent_hover)}; border-color: {css(palette.accent_hover)}; }}
{selector}:pressed {{
    background-color: {css(palette.accent_pressed)};
    border-color: {css(palette.accent_pressed)};
    color: {css(_fade(palette.text_on_accent, 200))};
}}
{selector}:disabled {{
    background-color: {css(palette.accent_disabled)};
    border-color: {css(palette.accent_disabled)};
    color: {css(palette.text_on_accent if palette.dark else QColor(255, 255, 255))};
}}
"""


def chrome_bottom_color(palette: FluentPalette) -> QColor:
    """Return the solid color used for the status bar."""
    return _wallpaper_stops(palette)[2]


def chrome_top_color(palette: FluentPalette) -> QColor:
    """Return the solid color used for the caption and tab strip."""
    return _wallpaper_stops(palette)[0]


def combo_box_qss(palette: FluentPalette, selector: str = "QComboBox", *, height: int = CONTROL_HEIGHT) -> str:
    """Return the Fluent drop-down (combo box) stylesheet with a Lucide chevron.

    The popup list uses the same flyout fill/stroke and Settings-like item pills as
    `menu_qss` / `item_view_qss`, including `QComboBoxPrivateContainer` so Windows
    does not keep a native light frame around the dark list.

    """
    # Mix onto the field fill so the PNG is opaque and readable on control chrome.
    arrow = lucide_qss_url("chevron-down", mix(palette.control_fill, palette.text_primary), 12)
    hover = css(list_item_hover(palette))
    selected = css(list_item_selected(palette))
    popup_bg = css(palette.popup_bg)
    popup_stroke = css(palette.popup_stroke)
    ink = css(palette.text_primary)
    return f"""
{selector} {{
    background-color: {css(palette.control_fill)};
    color: {ink};
    border: 1px solid {css(palette.control_stroke)};
    border-bottom-color: {css(palette.control_stroke_bottom)};
    border-radius: {RADIUS_CONTROL}px;
    /* Keep right pad small: ::drop-down width already reserves the chevron gutter.
       Large padding-right double-counts and clips text in narrow combos (e.g. 80px RUB). */
    padding: 0px 4px 0px 8px;
    min-height: {height - 2}px;
}}
{selector}:hover {{ background-color: {css(palette.control_fill_hover)}; }}
{selector}:on {{ background-color: {css(palette.control_fill_pressed)}; }}
{selector}:disabled {{ color: {css(palette.text_disabled)}; background-color: {css(palette.control_fill_disabled)}; }}
{selector}:editable {{ background-color: {css(palette.control_fill)}; }}
{selector}::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 22px;
    border: none;
    background: transparent;
}}
{selector}::down-arrow {{ image: url("{arrow}"); width: 12px; height: 12px; }}
QComboBoxPrivateContainer {{
    background-color: {popup_bg};
    border: 1px solid {popup_stroke};
    border-radius: {RADIUS_OVERLAY}px;
    padding: 0px;
}}
{selector} QAbstractItemView {{
    background-color: {popup_bg};
    color: {ink};
    border: none;
    border-radius: {RADIUS_OVERLAY}px;
    padding: {SPACE_XS}px;
    outline: none;
    selection-background-color: {selected};
    selection-color: {ink};
}}
{selector} QAbstractItemView::item {{
    border: none;
    border-radius: {RADIUS_CONTROL}px;
    padding: 4px 8px;
    min-height: {max(20, height - 10)}px;
    color: {ink};
}}
{selector} QAbstractItemView::item:hover {{ background: {hover}; }}
{selector} QAbstractItemView::item:selected {{ background: {selected}; color: {ink}; }}
{selector} QAbstractItemView::item:selected:hover {{ background: {selected}; }}
"""


def date_edit_qss(palette: FluentPalette, *, height: int = CONTROL_HEIGHT) -> str:
    """Return a Fluent date field with a flat chevron instead of a beveled arrow."""
    arrow = lucide_qss_url("chevron-down", mix(palette.control_fill, palette.text_primary), 12)
    # Match combo: keep padding-right small. ::drop-down already reserves the chevron
    # gutter; padding-right equal to drop width leaves a dead gap before the arrow.
    drop = DATE_EDIT_DROP_WIDTH
    return f"""
{line_edit_qss(palette, "QDateEdit", height=height)}
QDateEdit {{
    padding: 0px 4px 0px 10px;
}}
QDateEdit QLineEdit {{
    background: transparent;
    border: none;
    padding: 0px;
    margin: 0px;
}}
QDateEdit::drop-down {{
    subcontrol-origin: border;
    subcontrol-position: center right;
    width: {drop}px;
    border: none;
    background: transparent;
}}
QDateEdit::down-arrow {{ image: url("{arrow}"); width: 12px; height: 12px; }}
QDateEdit::up-button, QDateEdit::down-button {{ width: 0px; height: 0px; border: none; }}
QDateEdit::drop-down:hover {{ background: {css(palette.subtle_hover)}; }}
"""


def drop_zone_qss(
    palette: FluentPalette,
    selector: str,
    *,
    selected: bool = False,
    focused: bool = False,
    padding: str = "0px",
) -> str:
    """Return a dashed drop target on a subtle layer fill (light and dark)."""
    if selected:
        border = f"2px solid {css(palette.success)}"
        fill = mix(palette.window_bg, palette.success_bg)
    elif focused:
        border = f"2px dashed {css(palette.accent)}"
        fill = mix(palette.window_bg, palette.control_fill_input_active)
    else:
        border = f"2px dashed {css(mix(palette.window_bg, palette.control_strong_stroke))}"
        fill = mix(palette.window_bg, palette.control_alt_fill)
    return f"""
{selector} {{
    border: {border};
    border-radius: {RADIUS_CARD}px;
    padding: {padding};
    background-color: {css(fill)};
    color: {css(mix(palette.window_bg, palette.text_secondary))};
}}
""".strip()


def filled_button_qss(palette: FluentPalette, fill: QColor, ink: QColor, selector: str = "QPushButton") -> str:
    """Return a Fluent solid button in `fill` with `ink` text."""
    hover = mix(fill, QColor(255, 255, 255, 48) if palette.dark else QColor(0, 0, 0, 36))
    pressed = mix(fill, QColor(0, 0, 0, 48))
    return f"""
{selector} {{
    background-color: {css(fill)};
    color: {css(ink)};
    border: 1px solid {css(fill)};
    border-bottom-color: {css(pressed)};
    border-radius: {RADIUS_CONTROL}px;
    padding: 0px {CONTROL_PADDING_H}px;
    min-height: {CONTROL_HEIGHT - 2}px;
}}
{selector}:hover {{ background-color: {css(hover)}; border-color: {css(hover)}; }}
{selector}:pressed {{ background-color: {css(pressed)}; border-color: {css(pressed)}; }}
{selector}:disabled {{
    background-color: {css(palette.accent_disabled)};
    border-color: {css(palette.accent_disabled)};
    color: {css(palette.text_disabled)};
}}
"""


def fluent_tab_bar_qss(
    palette: FluentPalette,
    selector: str = "QTabBar",
    *,
    pad_v: int = 6,
    min_height: int = 0,
    closable: bool = False,
    gap: int = TAB_GAP,
) -> str:
    """Return `tab_bar_qss` with Fluent palette colors (shared by every section tab strip)."""
    return tab_bar_qss(
        selector,
        idle=css(palette.text_secondary),
        active=css(palette.text_primary),
        accent=css(palette.accent),
        hover=css(palette.control_stroke),
        pad_v=pad_v,
        min_height=min_height,
        close_icon=lucide_qss_url("x", palette.text_secondary, 12) if closable else "",
        close_hover=css(palette.subtle_hover),
        gap=gap,
    )


def item_view_qss(
    palette: FluentPalette,
    selector: str,
    *,
    transparent: bool = True,
    compact: bool = False,
) -> str:
    """Return a list/tree/table stylesheet with Fluent rounded selection.

    Hover / selected fills are stronger than `subtle_hover` so lists read like
    Windows 11 Settings navigation (clear pill on hover and selection).

    Args:

    - `transparent` (`bool`): Use a clear view background. Defaults to `True`.
    - `compact` (`bool`): Tight row padding (Quick paste / dense lists). Defaults
      to `False` (Settings-like comfortable rows).

    """
    background = "transparent" if transparent else css(palette.card_bg)
    hover = css(list_item_hover(palette))
    selected = css(list_item_selected(palette))
    # Match `app_chrome._style_item_view` when compact so overlays stay dense.
    item_box = "padding: 1px 8px; margin: 0px;" if compact else "padding: 6px 8px; margin: 1px 4px;"
    return f"""
{selector} {{
    background: {background};
    color: {css(palette.text_primary)};
    border: none;
    outline: none;
}}
{selector}::item {{
    border-radius: {RADIUS_CONTROL}px;
    {item_box}
    color: {css(palette.text_primary)};
}}
{selector}::item:hover {{ background: {hover}; }}
{selector}::item:selected {{ background: {selected}; color: {css(palette.text_primary)}; }}
{selector}::item:selected:hover {{ background: {selected}; }}
{selector}::item:disabled {{ color: {css(palette.text_disabled)}; }}
{scroll_bar_qss(palette)}
"""


def line_edit_qss(palette: FluentPalette, selector: str = "QLineEdit", *, height: int = CONTROL_HEIGHT) -> str:
    """Return the Fluent text box stylesheet (bottom accent line on focus)."""
    return f"""
{selector} {{
    background-color: {css(palette.control_fill)};
    color: {css(palette.text_primary)};
    border: 1px solid {css(palette.control_stroke)};
    border-bottom: 1px solid {css(palette.control_strong_stroke)};
    border-radius: {RADIUS_CONTROL}px;
    padding: 0px 10px;
    min-height: {height - 2}px;
    selection-background-color: {css(palette.accent)};
    selection-color: {css(palette.text_on_accent)};
}}
{selector}:hover {{ background-color: {css(palette.control_fill_hover)}; }}
{selector}:focus {{
    background-color: {css(palette.control_fill_input_active)};
    border-bottom: 2px solid {css(palette.accent)};
}}
{selector}:disabled {{ color: {css(palette.text_disabled)}; background-color: {css(palette.control_fill_disabled)}; }}
"""


def list_item_hover(palette: FluentPalette) -> QColor:
    """Return a Win11-Settings-like hover fill (stronger than `subtle_hover`)."""
    overlay = QColor(255, 255, 255, 18) if palette.dark else QColor(0, 0, 0, 28)
    return mix(palette.window_bg, overlay)


def list_item_selected(palette: FluentPalette) -> QColor:
    """Return a Win11-Settings-like selected fill."""
    overlay = QColor(255, 255, 255, 32) if palette.dark else QColor(0, 0, 0, 42)
    return mix(palette.window_bg, overlay)


def lucide_qss_url(name: str, color: QColor, size: int = ICON_SIZE) -> str:
    """Render a Lucide glyph to a cached PNG and return a QSS `url()` path.

    Qt stylesheets on Windows ignore `file:///…` for `image:` / `border-image:`;
    a plain absolute POSIX path (`C:/…/glyph.png`) paints correctly. Translucent
    token colors keep their alpha in the PNG.

    """
    key = (name, color.name(QColor.NameFormat.HexArgb), size)
    cached = _URL_CACHE.get(key)
    if cached is not None:
        return cached
    icon = create_lucide_icon(
        name, size, color=QColor(color.red(), color.green(), color.blue()), device_pixel_ratio=2.0
    )
    source = icon.pixmap(size * 2, size * 2)
    source.setDevicePixelRatio(1.0)
    pixmap = QPixmap(source.size())
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setOpacity(color.alphaF())
    painter.drawPixmap(0, 0, source)
    painter.end()
    stem = f"hsk_fluent_{name}_{key[1].lstrip('#')}_{size}.png"
    path = Path(tempfile.gettempdir()) / stem
    if not pixmap.isNull():
        pixmap.save(str(path), "PNG")
    # No file:/// prefix — Windows QSS only loads bare absolute paths here.
    url = path.resolve().as_posix()
    _URL_CACHE[key] = url
    return url


def menu_qss(palette: FluentPalette, selector: str = "QMenu") -> str:
    """Return the Fluent context menu stylesheet.

    Icon width/padding live on `::icon` so labels sit just after the glyph.
    Inflating `::item` padding-left instead stacks on the icon column and
    leaves a wide empty gap (or, if too small, paints the icon on the text).

    """
    # Slightly denser than the old 6/24 padding and 32px icons, without the
    # ultra-tight 2px rows that felt cramped in the tray menu.
    menu_icon = 20
    hover = css(list_item_hover(palette))
    return f"""
{selector} {{
    background-color: {css(palette.popup_bg)};
    color: {css(palette.text_primary)};
    border: 1px solid {css(palette.popup_stroke)};
    border-radius: {RADIUS_OVERLAY}px;
    padding: {SPACE_XS}px;
}}
{selector}::item {{
    background: transparent;
    color: {css(palette.text_primary)};
    border-radius: {RADIUS_CONTROL}px;
    padding: {SPACE_XS}px {SPACE_L}px {SPACE_XS}px {SPACE_S}px;
    margin: 1px 0px;
}}
{selector}::item:selected {{ background: {hover}; }}
{selector}::item:disabled {{ color: {css(palette.text_disabled)}; }}
{selector}::icon {{
    width: {menu_icon}px;
    height: {menu_icon}px;
    padding-left: {SPACE_S}px;
    padding-right: {SPACE_XS}px;
}}
{selector}::separator {{ height: 1px; background: {css(palette.divider)}; margin: {SPACE_XS}px 0px; }}
"""


def push_button_qss(palette: FluentPalette, selector: str = "QPushButton") -> str:
    """Return the Fluent standard (neutral) button stylesheet."""
    return f"""
{selector} {{
    background-color: {css(palette.control_fill)};
    color: {css(palette.text_primary)};
    border: 1px solid {css(palette.control_stroke)};
    border-bottom-color: {css(palette.control_stroke_bottom)};
    border-radius: {RADIUS_CONTROL}px;
    padding: 0px {CONTROL_PADDING_H}px;
    min-height: {CONTROL_HEIGHT - 2}px;
}}
{selector}:hover {{ background-color: {css(palette.control_fill_hover)}; }}
{selector}:pressed {{
    background-color: {css(palette.control_fill_pressed)};
    color: {css(palette.text_secondary)};
    border-bottom-color: {css(palette.control_stroke)};
}}
{selector}:checked {{
    background-color: {css(palette.accent)};
    color: {css(palette.text_on_accent)};
    border-color: {css(palette.accent)};
}}
{selector}:disabled {{
    background-color: {css(palette.control_fill_disabled)};
    color: {css(palette.text_disabled)};
    border-color: {css(palette.control_stroke)};
}}
"""


def scroll_bar_qss(palette: FluentPalette) -> str:
    """Return thin rounded Fluent scrollbars without arrow buttons."""
    thumb = css(palette.scrollbar_thumb)
    hover = css(palette.scrollbar_thumb_hover)
    side = SCROLLBAR_THICKNESS
    return f"""
QScrollBar:vertical {{ background: transparent; border: none; width: {side + 4}px; margin: 2px 0px; }}
QScrollBar::handle:vertical {{
    background: {thumb}; border: none; border-radius: {side // 2}px; min-height: 32px; margin: 0px 2px;
}}
QScrollBar::handle:vertical:hover {{ background: {hover}; }}
QScrollBar:horizontal {{ background: transparent; border: none; height: {side + 4}px; margin: 0px 2px; }}
QScrollBar::handle:horizontal {{
    background: {thumb}; border: none; border-radius: {side // 2}px; min-width: 32px; margin: 2px 0px;
}}
QScrollBar::handle:horizontal:hover {{ background: {hover}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0px; height: 0px; border: none; background: none; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; border: none; }}
QAbstractScrollArea::corner {{ background: transparent; border: none; }}
"""


def semantic_button_qss(palette: FluentPalette, kind: str, selector: str = "QPushButton") -> str:
    """Return a Fluent button for `accent`, `mint`, `info`, `success`, or `danger`."""
    fill, ink = _semantic_button_colors(palette, kind)
    return filled_button_qss(palette, fill, ink, selector)


def soft_drop_zone_qss(
    palette: FluentPalette,
    selector: str,
    *,
    padding: str = "0px",
) -> str:
    """Return a compact idle drop strip: hairline stroke + soft fill (Fluent).

    Used for AI attach rows (Finance/Food): quieter than a permanent dashed card,
    but still readable as a drop target. Focus/drag keep `drop_zone_qss(focused=…)`.

    """
    stroke = mix(palette.window_bg, palette.control_stroke_bottom)
    fill = mix(palette.window_bg, palette.control_alt_fill)
    muted = mix(palette.window_bg, palette.text_secondary)
    return f"""
{selector} {{
    border: 1px solid {css(stroke)};
    border-radius: {RADIUS_CONTROL}px;
    padding: {padding};
    background-color: {css(fill)};
    color: {css(muted)};
}}
{selector} QLabel {{
    border: none;
    background: transparent;
    color: {css(muted)};
}}
""".strip()


def spin_box_qss(
    palette: FluentPalette,
    selector: str = "QAbstractSpinBox",
    *,
    height: int = CONTROL_HEIGHT,
    arrows: bool = True,
) -> str:
    """Return the Fluent number box stylesheet.

    When `arrows` is false, only the field chrome is set so a custom spin style
    (narrow stacked buttons) can keep painting its own up/down glyphs.

    """
    sheet = line_edit_qss(palette, selector, height=height)
    if not arrows:
        return sheet
    ink = mix(palette.control_fill, palette.text_primary)
    up = lucide_qss_url("chevron-up", ink, 10)
    down = lucide_qss_url("chevron-down", ink, 10)
    return f"""
{sheet}
{selector} {{ padding-right: 18px; }}
{selector}::up-button, {selector}::down-button {{
    subcontrol-origin: border;
    width: 16px;
    border: none;
    background: transparent;
    border-radius: {RADIUS_CONTROL}px;
}}
{selector}::up-button {{ subcontrol-position: top right; }}
{selector}::down-button {{ subcontrol-position: bottom right; }}
{selector}::up-button:hover, {selector}::down-button:hover {{ background: {css(palette.subtle_hover)}; }}
{selector}::up-arrow {{ image: url("{up}"); width: 10px; height: 10px; }}
{selector}::down-arrow {{ image: url("{down}"); width: 10px; height: 10px; }}
"""


def subtle_button_qss(palette: FluentPalette, selector: str = "QAbstractButton") -> str:
    """Return the transparent (subtle) button stylesheet used for icon and tool buttons."""
    return f"""
{selector} {{
    background-color: transparent;
    color: {css(palette.text_primary)};
    border: none;
    border-radius: {RADIUS_CONTROL}px;
    padding: 4px 8px;
}}
{selector}:hover {{ background-color: {css(palette.subtle_hover)}; }}
{selector}:pressed {{ background-color: {css(palette.subtle_pressed)}; color: {css(palette.text_secondary)}; }}
{selector}:checked {{ background-color: {css(palette.subtle_hover)}; color: {css(palette.accent_text)}; }}
{selector}:disabled {{ color: {css(palette.text_disabled)}; }}
"""


def tab_bar_qss(
    selector: str = "QTabBar",
    *,
    idle: str,
    active: str,
    accent: str,
    hover: str = "transparent",
    pad_v: int = 6,
    min_height: int = 0,
    close_icon: str = "",
    close_hover: str = "transparent",
    gap: int = TAB_GAP,
) -> str:
    """Return Fluent Tabs chrome: plain text tabs, accent underline under the selected one.

    Colors are CSS strings so the caption can pass its own (non-Fluent) hex colors.
    `selector` is the tab bar selector, e.g. `QTabWidget#pages > QTabBar`. The top
    padding includes the indicator height so the label stays vertically centered.
    `min_height` is the content (label) height. `gap` is the space between tabs.

    """
    height = f" min-height: {min_height}px;" if min_height else ""
    side = max(0, gap // 2)
    close = (
        f"""
{selector}::close-button {{
    image: url("{close_icon}"); subcontrol-position: right; border-radius: {RADIUS_CONTROL}px;
    width: 16px; height: 16px; padding: 2px; margin-left: {SPACE_XS}px;
}}
{selector}::close-button:hover {{ background: {close_hover}; }}
"""
        if close_icon
        else ""
    )
    return f"""
{selector} {{ background: transparent; border: none; }}
{selector}::tab {{
    background: transparent;
    color: {idle};
    border: none;
    border-bottom: {TAB_INDICATOR_HEIGHT}px solid transparent;
    border-radius: 0px;
    margin: 0px {side}px;
    padding: {pad_v + TAB_INDICATOR_HEIGHT}px {SPACE_XS // 2}px {pad_v}px;{height}
}}
{selector}::tab:first {{ margin-left: 0px; }}
{selector}::tab:hover:!selected {{ color: {active}; border-bottom-color: {hover}; }}
{selector}::tab:selected {{ color: {active}; font-weight: 600; border-bottom-color: {accent}; }}
{selector}::tab:disabled {{ color: {idle}; }}
{close}"""


def text_edit_qss(palette: FluentPalette, selector: str = "QPlainTextEdit") -> str:
    """Return the Fluent multi-line text box stylesheet."""
    return f"""
{selector} {{
    background-color: {css(palette.control_fill)};
    color: {css(palette.text_primary)};
    border: 1px solid {css(palette.control_stroke)};
    border-bottom: 1px solid {css(palette.control_strong_stroke)};
    border-radius: {RADIUS_CONTROL}px;
    padding: 4px 6px;
    selection-background-color: {css(palette.accent)};
    selection-color: {css(palette.text_on_accent)};
}}
{selector}:focus {{
    background-color: {css(palette.control_fill_input_active)};
    border-bottom: 2px solid {css(palette.accent)};
}}
{scroll_bar_qss(palette)}
"""


def themed_icon(name: str, palette: FluentPalette, color: QColor | None = None, size: int = ICON_SIZE) -> QIcon:
    """Return a Lucide icon in a text token color, flattened onto the window background.

    Args:

    - `name` (`str`): Lucide icon ID.
    - `palette` (`FluentPalette`): Active palette.
    - `color` (`QColor | None`): Token color; defaults to `palette.text_primary`.
    - `size` (`int`): Logical icon size. Defaults to `ICON_SIZE`.

    """
    token = color if color is not None else palette.text_primary
    return create_lucide_icon(name, size, color=mix(palette.window_bg, token))


def tooltip_qss(palette: FluentPalette) -> str:
    """Return the Fluent tooltip stylesheet."""
    return f"""
QToolTip {{
    background-color: {css(palette.popup_bg)};
    color: {css(palette.text_primary)};
    border: 1px solid {css(palette.popup_stroke)};
    border-radius: {RADIUS_CONTROL}px;
    padding: 4px 8px;
}}
"""


def wallpaper_fill(palette: FluentPalette) -> str:
    """Return the qfluent-style gradient value (no selector)."""
    top, mid, bottom = _wallpaper_stops(palette)
    return (
        f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {top.name()}, stop:0.45 {mid.name()}, stop:1 {bottom.name()})"
    )


def wallpaper_qss(palette: FluentPalette) -> str:
    """Return the soft window gradient used behind Fluent app content."""
    return f"QMainWindow, QDialog {{ background: {wallpaper_fill(palette)}; }}"


def _fade(color: QColor, alpha: int) -> QColor:
    faded = QColor(color)
    faded.setAlpha(alpha)
    return faded


def _semantic_button_colors(palette: FluentPalette, kind: str) -> tuple[QColor, QColor]:
    """Return `(fill, text)` for a named Fluent button role."""
    white = QColor("#ffffff")
    black = QColor("#0d0d0d")
    if kind == "mint":
        return (QColor("#3dbea8") if palette.dark else QColor("#0f8a78"), black if palette.dark else white)
    if kind == "info":
        return (QColor("#8ec3dc") if palette.dark else QColor("#4f93b5"), black if palette.dark else white)
    if kind == "success":
        return (QColor(palette.success), black if palette.dark else white)
    if kind == "danger":
        return (QColor(palette.critical), black if palette.dark else white)
    return (QColor(palette.accent), QColor(palette.text_on_accent))


def _wallpaper_stops(palette: FluentPalette) -> tuple[QColor, QColor, QColor]:
    """Return the top, middle, and bottom colors of the window gradient."""
    if palette.dark:
        return (QColor("#2c2638"), QColor("#1e2633"), QColor("#171b22"))
    return (QColor("#f7f2f5"), QColor("#f3f6f8"), QColor("#e8eef3"))
