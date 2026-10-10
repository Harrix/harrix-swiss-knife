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
- [🔧 Function `button_primary_qss`](#-function-button_primary_qss)
- [🔧 Function `button_secondary_qss`](#-function-button_secondary_qss)
- [🔧 Function `button_success_qss`](#-function-button_success_qss)
- [🔧 Function `drop_zone_qss`](#-function-drop_zone_qss)
- [🔧 Function `list_view_item_selection_qss`](#-function-list_view_item_selection_qss)
- [🔧 Function `list_view_panel_qss`](#-function-list_view_panel_qss)
- [🔧 Function `nearest_codestyle_color`](#-function-nearest_codestyle_color)
- [🔧 Function `normalize_hex_color`](#-function-normalize_hex_color)
- [🔧 Function `relative_luminance`](#-function-relative_luminance)
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
```

</details>

## 🔧 Function `apply_readable_selection_palette`

```python
def apply_readable_selection_palette(view: QAbstractItemView) -> None
```

Keep selected-item text dark on soft blue highlights (not system white).

<details>
<summary>Code:</summary>

```python
def apply_readable_selection_palette(view: QAbstractItemView) -> None:
    palette = view.palette()
    text = QColor(SELECTION_TEXT)
    highlight = QColor(SELECTION_BG)
    for group in (QPalette.ColorGroup.Active, QPalette.ColorGroup.Inactive, QPalette.ColorGroup.Disabled):
        palette.setColor(group, QPalette.ColorRole.Highlight, highlight)
        palette.setColor(group, QPalette.ColorRole.HighlightedText, text)
    view.setPalette(palette)
```

</details>

## 🔧 Function `apply_soft_item_selection`

```python
def apply_soft_item_selection(view: QAbstractItemView) -> None
```

Append soft blue selected / hover rules to a list view or list widget.

<details>
<summary>Code:</summary>

```python
def apply_soft_item_selection(view: QAbstractItemView) -> None:
    existing = (view.styleSheet() or "").rstrip()
    fragment = _LIST_WIDGET_ITEM_SELECTION_QSS if isinstance(view, QListWidget) else _LIST_ITEM_SELECTION_QSS
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

Dark / saturated fills use white text and near-white icons. Light fills use
dark ink for both. Low-chroma gray fills are treated as ordinary chrome:
dark text, but callers should keep semantic (colored) icons.

<details>
<summary>Code:</summary>

```python
def button_content_colors(bg_hex: str) -> tuple[str, str]:
    if button_fill_is_ordinary(bg_hex):
        return BUTTON_SECONDARY_FG, BUTTON_ON_LIGHT_FG
    if relative_luminance(bg_hex) < _BUTTON_DARK_LUMINANCE_MAX:
        return BUTTON_ON_DARK_FG, BUTTON_ON_DARK_ICON
    return BUTTON_ON_LIGHT_FG, BUTTON_ON_LIGHT_FG
```

</details>

## 🔧 Function `button_cta_cyan_qss`

```python
def button_cta_cyan_qss(*, radius: int = PANEL_RADIUS) -> str
```

Soft-blue app CTA fill (`#e3f2fd` → nearest brand `#79b1d1`).

<details>
<summary>Code:</summary>

```python
def button_cta_cyan_qss(*, radius: int = PANEL_RADIUS) -> str:
    return solid_button_qss(
        BUTTON_CTA_CYAN_BG,
        hover=BUTTON_CTA_CYAN_HOVER,
        pressed=BUTTON_PRIMARY_HOVER,
        radius=radius,
    )
```

</details>

## 🔧 Function `button_cta_green_qss`

```python
def button_cta_green_qss(*, radius: int = PANEL_RADIUS) -> str
```

Soft-green app CTA fill (lightgreen / `#e8f5e9` → `#4caf50`).

<details>
<summary>Code:</summary>

```python
def button_cta_green_qss(*, radius: int = PANEL_RADIUS) -> str:
    return solid_button_qss(
        BUTTON_CTA_GREEN_BG,
        hover=BUTTON_CTA_GREEN_HOVER,
        pressed="#2e7d4f",
        radius=radius,
    )
```

</details>

## 🔧 Function `button_cta_mint_qss`

```python
def button_cta_mint_qss(*, radius: int = PANEL_RADIUS) -> str
```

Finance mint CTA fill (`#C1ECDD` → nearest brand `#3aaf9d`).

<details>
<summary>Code:</summary>

```python
def button_cta_mint_qss(*, radius: int = PANEL_RADIUS) -> str:
    return solid_button_qss(
        BUTTON_CTA_MINT_BG,
        hover=BUTTON_CTA_MINT_HOVER,
        pressed="#026a6d",
        radius=radius,
    )
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

Return white outlined idle `QPushButton` chrome (Cancel / Copy / Add row).

<details>
<summary>Code:</summary>

```python
def button_idle_qss(*, radius: int = PANEL_RADIUS) -> str:
    return solid_button_qss(
        SURFACE,
        hover=SELECTION_HOVER,
        pressed=BUTTON_SECONDARY_HOVER,
        border=INPUT_BORDER,
        radius=radius,
    )
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

## 🔧 Function `drop_zone_qss`

```python
def drop_zone_qss(*, selected: bool = False, focused: bool = False, padding: str = '20px', radius: int = 5, selector: str = 'QLabel') -> str
```

Return white drop-zone QSS (replaces legacy gray `#f9f9f9` panels).

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

Normalize `#rgb` / `#rrggbb` / named Qt colors used in stylesheets.

<details>
<summary>Code:</summary>

```python
def normalize_hex_color(value: str) -> str | None:
    text = value.strip()
    if not text:
        return None
    color = QColor(text)
    if not color.isValid():
        return None
    return color.name(QColor.NameFormat.HexRgb)
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

Return soft-blue fill for highlighted form fields (spin boxes, etc.).

<details>
<summary>Code:</summary>

```python
def soft_field_qss(selector: str = "QWidget") -> str:
    return f"""
{selector} {{
    background-color: {SELECTION_BG};
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
