---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `ui_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `action_card_selection_qss`](#-function-action_card_selection_qss)
- [🔧 Function `apply_readable_selection_palette`](#-function-apply_readable_selection_palette)
- [🔧 Function `apply_soft_form_spin_fills`](#-function-apply_soft_form_spin_fills)
- [🔧 Function `apply_soft_item_selection`](#-function-apply_soft_item_selection)
- [🔧 Function `apply_soft_list_selection_chrome`](#-function-apply_soft_list_selection_chrome)
- [🔧 Function `apply_white_surface_palette`](#-function-apply_white_surface_palette)
- [🔧 Function `button_content_colors`](#-function-button_content_colors)
- [🔧 Function `button_cta_cyan_qss`](#-function-button_cta_cyan_qss)
- [🔧 Function `button_cta_green_qss`](#-function-button_cta_green_qss)
- [🔧 Function `button_cta_mint_qss`](#-function-button_cta_mint_qss)
- [🔧 Function `button_danger_qss`](#-function-button_danger_qss)
- [🔧 Function `button_fill_from_stylesheet`](#-function-button_fill_from_stylesheet)
- [🔧 Function `button_fill_is_ordinary`](#-function-button_fill_is_ordinary)
- [🔧 Function `button_icon_color_for_bg`](#-function-button_icon_color_for_bg)
- [🔧 Function `button_idle_qss`](#-function-button_idle_qss)
- [🔧 Function `button_lucide_color_from_stylesheet`](#-function-button_lucide_color_from_stylesheet)
- [🔧 Function `button_primary_qss`](#-function-button_primary_qss)
- [🔧 Function `button_secondary_qss`](#-function-button_secondary_qss)
- [🔧 Function `button_success_qss`](#-function-button_success_qss)
- [🔧 Function `button_text_color_from_stylesheet`](#-function-button_text_color_from_stylesheet)
- [🔧 Function `drop_zone_qss`](#-function-drop_zone_qss)
- [🔧 Function `list_view_item_selection_qss`](#-function-list_view_item_selection_qss)
- [🔧 Function `list_view_panel_qss`](#-function-list_view_panel_qss)
- [🔧 Function `media_preview_plate_qss`](#-function-media_preview_plate_qss)
- [🔧 Function `media_preview_popup_frame_qss`](#-function-media_preview_popup_frame_qss)
- [🔧 Function `muted_caption_qss`](#-function-muted_caption_qss)
- [🔧 Function `nearest_codestyle_color`](#-function-nearest_codestyle_color)
- [🔧 Function `normalize_hex_color`](#-function-normalize_hex_color)
- [🔧 Function `record_caption_stop_qss`](#-function-record_caption_stop_qss)
- [🔧 Function `relative_luminance`](#-function-relative_luminance)
- [🔧 Function `selection_chrome_colors`](#-function-selection_chrome_colors)
- [🔧 Function `snippet_list_selection_qss`](#-function-snippet_list_selection_qss)
- [🔧 Function `soft_field_qss`](#-function-soft_field_qss)
- [🔧 Function `solid_button_qss`](#-function-solid_button_qss)

</details>

## 🔧 Function `action_card_selection_qss`

```python
def action_card_selection_qss() -> str
```

Return selection / hover QSS for Quick launcher action cards.

<details>
<summary>Code:</summary>

```python
def action_card_selection_qss() -> str:
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
```

</details>

## 🔧 Function `apply_readable_selection_palette`

```python
def apply_readable_selection_palette(view: QAbstractItemView) -> None
```

Keep selected-item text readable on soft selection fills (not system invert).

<details>
<summary>Code:</summary>

```python
def apply_readable_selection_palette(view: QAbstractItemView) -> None:
    fill, _hover, _border, text = selection_chrome_colors()
    palette = view.palette()
    highlight = QColor(fill) if fill.startswith("#") else _qcolor_from_css(fill)
    ink = QColor(text) if text.startswith("#") else _qcolor_from_css(text)
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive, QPalette.ColorGroup.Disabled):
        palette.setColor(group, QPalette.ColorRole.Highlight, highlight)
        palette.setColor(group, QPalette.ColorRole.HighlightedText, ink)
    view.setPalette(palette)
```

</details>

## 🔧 Function `apply_soft_form_spin_fills`

```python
def apply_soft_form_spin_fills(host: object, names: tuple[str, ...]) -> None
```

Apply [`soft_field_qss`](#-function-soft_field_qss) to named spin boxes on a tracker main window.

<details>
<summary>Code:</summary>

```python
def apply_soft_form_spin_fills(host: object, names: tuple[str, ...]) -> None:
    for name in names:
        control = getattr(host, name, None)
        if control is None:
            continue
        control.setStyleSheet(soft_field_qss(type(control).__name__))
```

</details>

## 🔧 Function `apply_soft_item_selection`

```python
def apply_soft_item_selection(view: QAbstractItemView) -> None
```

Append soft selected / hover rules to a list view or list widget.

<details>
<summary>Code:</summary>

```python
def apply_soft_item_selection(view: QAbstractItemView) -> None:
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
```

</details>

## 🔧 Function `apply_soft_list_selection_chrome`

```python
def apply_soft_list_selection_chrome(root: QWidget) -> None
```

Apply soft selection chrome to every `QListView` under [`root`](../habits/habit_comments.g.md#%EF%B8%8F-method-root).

<details>
<summary>Code:</summary>

```python
def apply_soft_list_selection_chrome(root: QWidget) -> None:
    for view in root.findChildren(QListView):
        apply_soft_item_selection(view)
```

</details>

## 🔧 Function `apply_white_surface_palette`

```python
def apply_white_surface_palette(widget: QWidget) -> None
```

Paint `widget` with the shared white surface (dialogs / panels).

Sets `Window` / `Base` / `AlternateBase` to `SURFACE` so modal forms are not
system gray. Idempotent.

<details>
<summary>Code:</summary>

```python
def apply_white_surface_palette(widget: QWidget) -> None:
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
```

</details>

## 🔧 Function `button_content_colors`

```python
def button_content_colors(bg_hex: str) -> tuple[str, str]
```

Return `(text_hex, icon_hex)` for a solid fill.

Accent fills use the same stroke for text and Lucide icons. Low-chroma gray
fills are ordinary chrome: dark text, but callers keep semantic icons.

<details>
<summary>Code:</summary>

```python
def button_content_colors(bg_hex: str) -> tuple[str, str]:
    if button_fill_is_ordinary(bg_hex):
        return BUTTON_SECONDARY_FG, BUTTON_ON_LIGHT_FG
    if relative_luminance(bg_hex) < _BUTTON_DARK_LUMINANCE_MAX:
        return BUTTON_ON_DARK_FG, BUTTON_ON_DARK_FG
    return BUTTON_ON_LIGHT_FG, BUTTON_ON_LIGHT_FG
```

</details>

## 🔧 Function `button_cta_cyan_qss`

```python
def button_cta_cyan_qss(*, radius: int = PANEL_RADIUS) -> str
```

Brand accent CTA fill (legacy cyan name). `radius` kept for callers.

<details>
<summary>Code:</summary>

```python
def button_cta_cyan_qss(*, radius: int = PANEL_RADIUS) -> str:
    del radius
    return _fluent_cta_button_qss()
```

</details>

## 🔧 Function `button_cta_green_qss`

```python
def button_cta_green_qss(*, radius: int = PANEL_RADIUS) -> str
```

Brand accent CTA fill (legacy green name). `radius` kept for callers.

<details>
<summary>Code:</summary>

```python
def button_cta_green_qss(*, radius: int = PANEL_RADIUS) -> str:
    del radius
    return _fluent_cta_button_qss()
```

</details>

## 🔧 Function `button_cta_mint_qss`

```python
def button_cta_mint_qss(*, radius: int = PANEL_RADIUS) -> str
```

Brand accent CTA fill (legacy mint name). `radius` kept for callers.

<details>
<summary>Code:</summary>

```python
def button_cta_mint_qss(*, radius: int = PANEL_RADIUS) -> str:
    del radius
    return _fluent_cta_button_qss()
```

</details>

## 🔧 Function `button_danger_qss`

```python
def button_danger_qss(*, radius: int = PANEL_RADIUS) -> str
```

Return solid danger `QPushButton` stylesheet (site `$h-danger`).

<details>
<summary>Code:</summary>

```python
def button_danger_qss(*, radius: int = PANEL_RADIUS) -> str:
    return solid_button_qss(
        BUTTON_DANGER_BG,
        hover=BUTTON_DANGER_HOVER,
        pressed="#8f342f",
        radius=radius,
    )
```

</details>

## 🔧 Function `button_fill_from_stylesheet`

```python
def button_fill_from_stylesheet(stylesheet: str | None) -> str | None
```

Parse the first `background-color` from a button stylesheet, if any.

<details>
<summary>Code:</summary>

```python
def button_fill_from_stylesheet(stylesheet: str | None) -> str | None:
    if not stylesheet:
        return None
    match = _BG_COLOR_RE.search(stylesheet)
    if match is None:
        return None
    return normalize_hex_color(match.group(1))
```

</details>

## 🔧 Function `button_fill_is_ordinary`

```python
def button_fill_is_ordinary(bg_hex: str) -> bool
```

Return whether `bg_hex` is a low-chroma gray (semantic icons stay).

<details>
<summary>Code:</summary>

```python
def button_fill_is_ordinary(bg_hex: str) -> bool:
    rgb = _parse_rgb(bg_hex)
    if rgb is None:
        return True
    return _chroma(rgb) < _ORDINARY_FILL_CHROMA_MAX and relative_luminance(bg_hex) > _ORDINARY_FILL_LUMINANCE_MIN
```

</details>

## 🔧 Function `button_icon_color_for_bg`

```python
def button_icon_color_for_bg(bg_hex: str | None) -> str | None
```

Return a forced Lucide stroke for a fill, or `None` for semantic colors.

<details>
<summary>Code:</summary>

```python
def button_icon_color_for_bg(bg_hex: str | None) -> str | None:
    if bg_hex is None or button_fill_is_ordinary(bg_hex):
        return None
    return button_content_colors(bg_hex)[1]
```

</details>

## 🔧 Function `button_idle_qss`

```python
def button_idle_qss(*, radius: int = PANEL_RADIUS) -> str
```

Return idle `QPushButton` chrome (Cancel / Copy / filter / Add row).

Tracker layout polish often runs after Fluent app chrome and on theme change.
Hard white plates stay wrong in dark mode, so idle buttons follow the active
Fluent secondary control fill whenever a theme is available.

<details>
<summary>Code:</summary>

```python
def button_idle_qss(*, radius: int = PANEL_RADIUS) -> str:
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
```

</details>

## 🔧 Function `button_lucide_color_from_stylesheet`

```python
def button_lucide_color_from_stylesheet(stylesheet: str | None) -> str | None
```

Return Lucide stroke matching accent button text, or `None` for semantic.

Fluent CTA QSS uses `rgba(...)` fills; ordinary gray/white chrome keeps
CodeStyle semantic icon colors.

<details>
<summary>Code:</summary>

```python
def button_lucide_color_from_stylesheet(stylesheet: str | None) -> str | None:
    fill = button_fill_from_stylesheet(stylesheet)
    if fill is None or button_fill_is_ordinary(fill):
        return None
    text = button_text_color_from_stylesheet(stylesheet)
    if text is not None:
        return text
    return button_content_colors(fill)[1]
```

</details>

## 🔧 Function `button_primary_qss`

```python
def button_primary_qss(*, radius: int = PANEL_RADIUS) -> str
```

Return solid primary `QPushButton` stylesheet (site `.button.is-primary`).

<details>
<summary>Code:</summary>

```python
def button_primary_qss(*, radius: int = PANEL_RADIUS) -> str:
    return solid_button_qss(
        BUTTON_PRIMARY_BG,
        hover=BUTTON_PRIMARY_HOVER,
        pressed=BUTTON_PRIMARY_HOVER,
        radius=radius,
    )
```

</details>

## 🔧 Function `button_secondary_qss`

```python
def button_secondary_qss(*, radius: int = PANEL_RADIUS) -> str
```

Return light secondary `QPushButton` stylesheet (site `.button.is-light`).

<details>
<summary>Code:</summary>

```python
def button_secondary_qss(*, radius: int = PANEL_RADIUS) -> str:
    return solid_button_qss(
        BUTTON_SECONDARY_BG,
        hover=BUTTON_SECONDARY_HOVER,
        pressed=BUTTON_SECONDARY_PRESSED,
        border=BUTTON_SECONDARY_BORDER,
        radius=radius,
    )
```

</details>

## 🔧 Function `button_success_qss`

```python
def button_success_qss(*, radius: int = PANEL_RADIUS) -> str
```

Return solid success `QPushButton` stylesheet (site `$h-success`).

<details>
<summary>Code:</summary>

```python
def button_success_qss(*, radius: int = PANEL_RADIUS) -> str:
    return solid_button_qss(
        BUTTON_SUCCESS_BG,
        hover=BUTTON_SUCCESS_HOVER,
        pressed="#2e7d4f",
        radius=radius,
    )
```

</details>

## 🔧 Function `button_text_color_from_stylesheet`

```python
def button_text_color_from_stylesheet(stylesheet: str | None) -> str | None
```

Parse the first idle `color:` from a button stylesheet, if any.

<details>
<summary>Code:</summary>

```python
def button_text_color_from_stylesheet(stylesheet: str | None) -> str | None:
    if not stylesheet:
        return None
    match = _FG_COLOR_RE.search(stylesheet)
    if match is None:
        return None
    return normalize_hex_color(match.group(1))
```

</details>

## 🔧 Function `drop_zone_qss`

```python
def drop_zone_qss(*, selected: bool = False, focused: bool = False, padding: str = '20px', radius: int = 5, selector: str = 'QLabel') -> str
```

Return drop-zone QSS (surface in light, Fluent card fill in dark).

<details>
<summary>Code:</summary>

```python
def drop_zone_qss(
    *,
    selected: bool = False,
    focused: bool = False,
    padding: str = "20px",
    radius: int = 5,
    selector: str = "QLabel",
) -> str:
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
```

</details>

## 🔧 Function `list_view_item_selection_qss`

```python
def list_view_item_selection_qss(*, with_row_separators: bool = False) -> str
```

Return QSS for `QListView::item` selected / hover states.

Args:

- `with_row_separators` (`bool`): When `True`, keep a light bottom border
  between rows (finance / food / fitness filter lists).

Returns:

- `str`: Stylesheet fragment for list items (does not set the outer list border).

<details>
<summary>Code:</summary>

```python
def list_view_item_selection_qss(*, with_row_separators: bool = False) -> str:
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
```

</details>

## 🔧 Function `list_view_panel_qss`

```python
def list_view_panel_qss(*, border_color: str, with_row_separators: bool = True) -> str
```

Return a full `QListView` stylesheet with branded border and soft selection.

Args:

- `border_color` (`str`): Outer list border color (app accent).
- `with_row_separators` (`bool`): Whether items draw a bottom hairline.

Returns:

- `str`: Complete stylesheet string for a filter / option list.

<details>
<summary>Code:</summary>

```python
def list_view_panel_qss(*, border_color: str, with_row_separators: bool = True) -> str:
    return f"""
QListView {{
    border: 2px solid {border_color};
    border-radius: {PANEL_RADIUS}px;
    background-color: {SURFACE};
    outline: none;
}}
{list_view_item_selection_qss(with_row_separators=with_row_separators)}
""".strip()
```

</details>

## 🔧 Function `media_preview_plate_qss`

```python
def media_preview_plate_qss(*, selector: str = 'QLabel') -> str
```

Return AVIF preview plate QSS (white in light, soft card gray in dark).

<details>
<summary>Code:</summary>

```python
def media_preview_plate_qss(*, selector: str = "QLabel") -> str:
    plate = SURFACE
    with contextlib.suppress(Exception):
        from harrix_swiss_knife.fluent.theme import FluentTheme, css, mix  # noqa: PLC0415

        palette = FluentTheme.instance().palette()
        if palette.dark:
            plate = css(mix(palette.window_bg, palette.card_bg))
    return f"{selector} {{ background-color: {plate}; border: none; }}"
```

</details>

## 🔧 Function `media_preview_popup_frame_qss`

```python
def media_preview_popup_frame_qss() -> str
```

Return themed QSS for the exercise hover-preview popup frame.

<details>
<summary>Code:</summary>

```python
def media_preview_popup_frame_qss() -> str:
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
```

</details>

## 🔧 Function `muted_caption_qss`

```python
def muted_caption_qss(*, bold: bool = True, extra: str = '') -> str
```

Return theme-aware muted caption QSS (`MUTED_TEXT` in light).

<details>
<summary>Code:</summary>

```python
def muted_caption_qss(*, bold: bool = True, extra: str = "") -> str:
    _surface, _hairline, _input_border, muted = _surface_chrome_colors()
    weight = "600" if bold else "400"
    suffix = f" {extra}" if extra and not extra.startswith(" ") else extra
    return f"color: {muted}; font-weight: {weight};{suffix}"
```

</details>

## 🔧 Function `nearest_codestyle_color`

```python
def nearest_codestyle_color(hex_color: str, *, palette: Iterable[str] = CODESTYLE_PALETTE) -> str
```

Map any hex to the nearest CodeStyle brand color (HSL-weighted).

<details>
<summary>Code:</summary>

```python
def nearest_codestyle_color(
    hex_color: str,
    *,
    palette: Iterable[str] = CODESTYLE_PALETTE,
) -> str:
    rgb = _parse_rgb(hex_color)
    if rgb is None:
        return BUTTON_PRIMARY_BG
    best = min(palette, key=lambda candidate: _color_distance(rgb, _parse_rgb(candidate) or rgb))
    return best.lower() if best.startswith("#") else best
```

</details>

## 🔧 Function `normalize_hex_color`

```python
def normalize_hex_color(value: str) -> str | None
```

Normalize `#rgb` / `#rrggbb` / `rgb()` / `rgba()` / named colors to `#rrggbb`.

<details>
<summary>Code:</summary>

```python
def normalize_hex_color(value: str) -> str | None:
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
```

</details>

## 🔧 Function `record_caption_stop_qss`

```python
def record_caption_stop_qss() -> str
```

Return theme-aware QSS for the recording stop-state caption.

<details>
<summary>Code:</summary>

```python
def record_caption_stop_qss() -> str:
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
```

</details>

## 🔧 Function `relative_luminance`

```python
def relative_luminance(hex_color: str) -> float
```

WCAG relative luminance of `hex_color` in `0..1`.

<details>
<summary>Code:</summary>

```python
def relative_luminance(hex_color: str) -> float:
    rgb = _parse_rgb(hex_color)
    if rgb is None:
        return 1.0

    def channel(value: int) -> float:
        c = value / 255.0
        return c / 12.92 if c <= _WCAG_LINEAR_CHANNEL_CUTOFF else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)
```

</details>

## 🔧 Function `selection_chrome_colors`

```python
def selection_chrome_colors() -> tuple[str, str, str, str]
```

Return `(fill, hover, border, text)` for soft list/card selection.

Light mode keeps the shared soft-blue tokens. Dark mode uses Fluent list
selection fills so tiles are not bright white islands.

<details>
<summary>Code:</summary>

```python
def selection_chrome_colors() -> tuple[str, str, str, str]:
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
```

</details>

## 🔧 Function `snippet_list_selection_qss`

```python
def snippet_list_selection_qss() -> str
```

Return selection QSS for Quick paste snippet list.

<details>
<summary>Code:</summary>

```python
def snippet_list_selection_qss() -> str:
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
```

</details>

## 🔧 Function `soft_field_qss`

```python
def soft_field_qss(selector: str = 'QWidget') -> str
```

Return theme-aware fill for highlighted form fields (spin boxes, etc.).

<details>
<summary>Code:</summary>

```python
def soft_field_qss(selector: str = "QWidget") -> str:
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
```

</details>

## 🔧 Function `solid_button_qss`

```python
def solid_button_qss(bg: str, *, hover: str | None = None, pressed: str | None = None, border: str | None = None, radius: int = PANEL_RADIUS) -> str
```

Solid fill button QSS with contrast text and native-like padding.

Border matches the fill (no contrasting outline) unless `border` is set.

<details>
<summary>Code:</summary>

```python
def solid_button_qss(
    bg: str,
    *,
    hover: str | None = None,
    pressed: str | None = None,
    border: str | None = None,
    radius: int = PANEL_RADIUS,
) -> str:
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
```

</details>
