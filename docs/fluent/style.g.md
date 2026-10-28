---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `style.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `accent_button_qss`](#-function-accent_button_qss)
- [🔧 Function `combo_box_qss`](#-function-combo_box_qss)
- [🔧 Function `item_view_qss`](#-function-item_view_qss)
- [🔧 Function `line_edit_qss`](#-function-line_edit_qss)
- [🔧 Function `lucide_qss_url`](#-function-lucide_qss_url)
- [🔧 Function `menu_qss`](#-function-menu_qss)
- [🔧 Function `push_button_qss`](#-function-push_button_qss)
- [🔧 Function `scroll_bar_qss`](#-function-scroll_bar_qss)
- [🔧 Function `spin_box_qss`](#-function-spin_box_qss)
- [🔧 Function `subtle_button_qss`](#-function-subtle_button_qss)
- [🔧 Function `text_edit_qss`](#-function-text_edit_qss)
- [🔧 Function `themed_icon`](#-function-themed_icon)
- [🔧 Function `tooltip_qss`](#-function-tooltip_qss)

</details>

## 🔧 Function `accent_button_qss`

```python
def accent_button_qss(palette: FluentPalette, selector: str = 'QPushButton') -> str
```

Return the accent (primary) button stylesheet.

<details>
<summary>Code:</summary>

```python
def accent_button_qss(palette: FluentPalette, selector: str = "QPushButton") -> str:
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
```

</details>

## 🔧 Function `combo_box_qss`

```python
def combo_box_qss(palette: FluentPalette, selector: str = 'QComboBox', *, height: int = CONTROL_HEIGHT) -> str
```

Return the Fluent drop-down (combo box) stylesheet with a Lucide chevron.

<details>
<summary>Code:</summary>

```python
def combo_box_qss(palette: FluentPalette, selector: str = "QComboBox", *, height: int = CONTROL_HEIGHT) -> str:
    arrow = lucide_qss_url("chevron-down", palette.text_secondary, 12)
    return f"""
{selector} {{
    background-color: {css(palette.control_fill)};
    color: {css(palette.text_primary)};
    border: 1px solid {css(palette.control_stroke)};
    border-bottom-color: {css(palette.control_stroke_bottom)};
    border-radius: {RADIUS_CONTROL}px;
    padding: 0px 28px 0px 10px;
    min-height: {height - 2}px;
}}
{selector}:hover {{ background-color: {css(palette.control_fill_hover)}; }}
{selector}:on {{ background-color: {css(palette.control_fill_pressed)}; }}
{selector}:disabled {{ color: {css(palette.text_disabled)}; background-color: {css(palette.control_fill_disabled)}; }}
{selector}:editable {{ background-color: {css(palette.control_fill)}; }}
{selector}::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 28px;
    border: none;
    background: transparent;
}}
{selector}::down-arrow {{ image: url("{arrow}"); width: 12px; height: 12px; }}
{selector} QAbstractItemView {{
    background-color: {css(palette.popup_bg)};
    color: {css(palette.text_primary)};
    border: 1px solid {css(palette.popup_stroke)};
    border-radius: {RADIUS_OVERLAY}px;
    padding: {SPACE_XS}px;
    outline: none;
    selection-background-color: {css(palette.subtle_hover)};
    selection-color: {css(palette.text_primary)};
}}
"""
```

</details>

## 🔧 Function `item_view_qss`

```python
def item_view_qss(palette: FluentPalette, selector: str, *, transparent: bool = True) -> str
```

Return a list/tree/table stylesheet with Fluent rounded selection.

<details>
<summary>Code:</summary>

```python
def item_view_qss(palette: FluentPalette, selector: str, *, transparent: bool = True) -> str:
    background = "transparent" if transparent else css(palette.card_bg)
    return f"""
{selector} {{
    background: {background};
    color: {css(palette.text_primary)};
    border: none;
    outline: none;
}}
{selector}::item {{
    border-radius: {RADIUS_CONTROL}px;
    padding: 6px 8px;
    margin: 1px 4px;
    color: {css(palette.text_primary)};
}}
{selector}::item:hover {{ background: {css(palette.subtle_hover)}; }}
{selector}::item:selected {{ background: {css(palette.subtle_hover)}; color: {css(palette.text_primary)}; }}
{selector}::item:selected:hover {{ background: {css(palette.subtle_pressed)}; }}
{selector}::item:disabled {{ color: {css(palette.text_disabled)}; }}
{scroll_bar_qss(palette)}
"""
```

</details>

## 🔧 Function `line_edit_qss`

```python
def line_edit_qss(palette: FluentPalette, selector: str = 'QLineEdit', *, height: int = CONTROL_HEIGHT) -> str
```

Return the Fluent text box stylesheet (bottom accent line on focus).

<details>
<summary>Code:</summary>

```python
def line_edit_qss(palette: FluentPalette, selector: str = "QLineEdit", *, height: int = CONTROL_HEIGHT) -> str:
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
```

</details>

## 🔧 Function `lucide_qss_url`

```python
def lucide_qss_url(name: str, color: QColor, size: int = ICON_SIZE) -> str
```

Render a Lucide glyph to a cached PNG and return a QSS-ready file URL.

Translucent token colors keep their alpha in the PNG.

<details>
<summary>Code:</summary>

```python
def lucide_qss_url(name: str, color: QColor, size: int = ICON_SIZE) -> str:
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
    url = path.resolve().as_posix()
    _URL_CACHE[key] = url
    return url
```

</details>

## 🔧 Function `menu_qss`

```python
def menu_qss(palette: FluentPalette, selector: str = 'QMenu') -> str
```

Return the Fluent context menu stylesheet.

<details>
<summary>Code:</summary>

```python
def menu_qss(palette: FluentPalette, selector: str = "QMenu") -> str:
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
    padding: 6px 24px 6px 12px;
    margin: 1px 0px;
}}
{selector}::item:selected {{ background: {css(palette.subtle_hover)}; }}
{selector}::item:disabled {{ color: {css(palette.text_disabled)}; }}
{selector}::icon {{ padding-left: 8px; }}
{selector}::separator {{ height: 1px; background: {css(palette.divider)}; margin: 4px 0px; }}
"""
```

</details>

## 🔧 Function `push_button_qss`

```python
def push_button_qss(palette: FluentPalette, selector: str = 'QPushButton') -> str
```

Return the Fluent standard (neutral) button stylesheet.

<details>
<summary>Code:</summary>

```python
def push_button_qss(palette: FluentPalette, selector: str = "QPushButton") -> str:
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
```

</details>

## 🔧 Function `scroll_bar_qss`

```python
def scroll_bar_qss(palette: FluentPalette) -> str
```

Return thin rounded Fluent scrollbars without arrow buttons.

<details>
<summary>Code:</summary>

```python
def scroll_bar_qss(palette: FluentPalette) -> str:
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
```

</details>

## 🔧 Function `spin_box_qss`

```python
def spin_box_qss(palette: FluentPalette, selector: str = 'QAbstractSpinBox') -> str
```

Return the Fluent number box stylesheet with Lucide up/down glyphs.

<details>
<summary>Code:</summary>

```python
def spin_box_qss(palette: FluentPalette, selector: str = "QAbstractSpinBox") -> str:
    up = lucide_qss_url("chevron-up", palette.text_secondary, 10)
    down = lucide_qss_url("chevron-down", palette.text_secondary, 10)
    return f"""
{line_edit_qss(palette, selector)}
{selector} {{ padding-right: 24px; }}
{selector}::up-button, {selector}::down-button {{
    subcontrol-origin: border;
    width: 22px;
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
```

</details>

## 🔧 Function `subtle_button_qss`

```python
def subtle_button_qss(palette: FluentPalette, selector: str = 'QAbstractButton') -> str
```

Return the transparent (subtle) button stylesheet used for icon and tool buttons.

<details>
<summary>Code:</summary>

```python
def subtle_button_qss(palette: FluentPalette, selector: str = "QAbstractButton") -> str:
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
```

</details>

## 🔧 Function `text_edit_qss`

```python
def text_edit_qss(palette: FluentPalette, selector: str = 'QPlainTextEdit') -> str
```

Return the Fluent multi-line text box stylesheet.

<details>
<summary>Code:</summary>

```python
def text_edit_qss(palette: FluentPalette, selector: str = "QPlainTextEdit") -> str:
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
```

</details>

## 🔧 Function `themed_icon`

```python
def themed_icon(name: str, palette: FluentPalette, color: QColor | None = None, size: int = ICON_SIZE) -> QIcon
```

Return a Lucide icon in a text token color, flattened onto the window background.

Args:

- `name` (`str`): Lucide icon ID.
- [`palette`](theme.g.md#%EF%B8%8F-method-palette) ([`FluentPalette`](tokens.g.md#%EF%B8%8F-class-fluentpalette)): Active palette.
- [`color`](widgets/dialogs.g.md#%EF%B8%8F-method-color) (`QColor | None`): Token color; defaults to `palette.text_primary`.
- [`size`](../apps/icons/lightbox_cache.g.md#%EF%B8%8F-method-size-property) (`int`): Logical icon size. Defaults to `ICON_SIZE`.

<details>
<summary>Code:</summary>

```python
def themed_icon(name: str, palette: FluentPalette, color: QColor | None = None, size: int = ICON_SIZE) -> QIcon:
    token = color if color is not None else palette.text_primary
    return create_lucide_icon(name, size, color=mix(palette.window_bg, token))
```

</details>

## 🔧 Function `tooltip_qss`

```python
def tooltip_qss(palette: FluentPalette) -> str
```

Return the Fluent tooltip stylesheet.

<details>
<summary>Code:</summary>

```python
def tooltip_qss(palette: FluentPalette) -> str:
    return f"""
QToolTip {{
    background-color: {css(palette.popup_bg)};
    color: {css(palette.text_primary)};
    border: 1px solid {css(palette.popup_stroke)};
    border-radius: {RADIUS_CONTROL}px;
    padding: 4px 8px;
}}
"""
```

</details>
