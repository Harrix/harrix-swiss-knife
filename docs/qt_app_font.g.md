---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_app_font.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_mono_font`](#-function-apply_mono_font)
- [🔧 Function `apply_ui_font_scale`](#-function-apply_ui_font_scale)
- [🔧 Function `bundled_font_paths`](#-function-bundled_font_paths)
- [🔧 Function `bundled_font_resource_paths`](#-function-bundled_font_resource_paths)
- [🔧 Function `current_ui_font_scale`](#-function-current_ui_font_scale)
- [🔧 Function `install_app_fonts`](#-function-install_app_fonts)
- [🔧 Function `load_fira_sans_fonts`](#-function-load_fira_sans_fonts)
- [🔧 Function `load_jetbrains_mono_fonts`](#-function-load_jetbrains_mono_fonts)
- [🔧 Function `mono_qfont`](#-function-mono_qfont)
- [🔧 Function `scale_explicit_widget_font`](#-function-scale_explicit_widget_font)

</details>

## 🔧 Function `apply_mono_font`

```python
def apply_mono_font(widget: QWidget) -> None
```

Set JetBrains Mono on `widget` after the bundled mono fonts are loaded.

<details>
<summary>Code:</summary>

```python
def apply_mono_font(widget: QWidget) -> None:
    load_jetbrains_mono_fonts()
    widget.setFont(mono_qfont(widget.font()))
```

</details>

## 🔧 Function `apply_ui_font_scale`

```python
def apply_ui_font_scale(root: QWidget) -> None
```

Scale explicit fonts on [`root`](apps/habits/habit_comments.g.md#%EF%B8%8F-method-root) and its children.

<details>
<summary>Code:</summary>

```python
def apply_ui_font_scale(root: QWidget) -> None:
    scale_explicit_widget_font(root)
    for widget in root.findChildren(QWidget):
        scale_explicit_widget_font(widget)
```

</details>

## 🔧 Function `bundled_font_paths`

```python
def bundled_font_paths() -> list[Path]
```

Return existing bundled TTF files shipped next to the package.

<details>
<summary>Code:</summary>

```python
def bundled_font_paths() -> list[Path]:
    return [path for name in (*_UI_FONT_FILES, *_MONO_FONT_FILES) if (path := _FONT_DIR / name).is_file()]
```

</details>

## 🔧 Function `bundled_font_resource_paths`

```python
def bundled_font_resource_paths() -> list[str]
```

Return Qt resource paths for bundled fonts that exist in `resources_rc`.

<details>
<summary>Code:</summary>

```python
def bundled_font_resource_paths() -> list[str]:
    return [path for name in (*_UI_FONT_FILES, *_MONO_FONT_FILES) if QFile.exists(path := f"{_QRC_FONT_PREFIX}/{name}")]
```

</details>

## 🔧 Function `current_ui_font_scale`

```python
def current_ui_font_scale() -> float
```

Return the UI font scale stored on the current `QApplication`.

<details>
<summary>Code:</summary>

```python
def current_ui_font_scale() -> float:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        return 1.0
    raw = app.property(_SCALE_PROP)
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 1.0
```

</details>

## 🔧 Function `install_app_fonts`

```python
def install_app_fonts(app: QApplication, scale: float | None = None) -> None
```

Register bundled fonts and apply Fira Sans as the default UI font.

`scale` multiplies the application font and any widget that set its own point
size in Designer. When omitted, the value comes from `config.json`
`ui_font_scale` (default `1.0`).

<details>
<summary>Code:</summary>

```python
def install_app_fonts(app: QApplication, scale: float | None = None) -> None:
    if not isinstance(app, QApplication) or app.property(_PROP) == "1":
        return
    load_jetbrains_mono_fonts()
    if not load_fira_sans_fonts():
        return
    resolved = _resolve_ui_font_scale(scale)
    app.setProperty(_SCALE_PROP, resolved)
    font = _font_with_family(app.font(), APP_FONT_FAMILY)
    point = font.pointSizeF()
    if resolved != 1.0 and point > 0:
        font.setPointSizeF(max(_MIN_POINT_SIZE, point * resolved))
    app.setFont(font)
    _install_ui_font_scale_filter(app)
    app.setProperty(_PROP, "1")
```

</details>

## 🔧 Function `load_fira_sans_fonts`

```python
def load_fira_sans_fonts() -> bool
```

Load bundled Fira Sans files. Return whether Regular loaded.

<details>
<summary>Code:</summary>

```python
def load_fira_sans_fonts() -> bool:
    return _load_font_files(_UI_FONT_FILES, APP_FONT_FAMILY)
```

</details>

## 🔧 Function `load_jetbrains_mono_fonts`

```python
def load_jetbrains_mono_fonts() -> bool
```

Load bundled JetBrains Mono files. Return whether Regular loaded.

<details>
<summary>Code:</summary>

```python
def load_jetbrains_mono_fonts() -> bool:
    return _load_font_files(_MONO_FONT_FILES, MONO_FONT_FAMILY)
```

</details>

## 🔧 Function `mono_qfont`

```python
def mono_qfont(source: QFont | None = None) -> QFont
```

Return a copy of `source` using JetBrains Mono.

<details>
<summary>Code:</summary>

```python
def mono_qfont(source: QFont | None = None) -> QFont:
    font = QFont(source) if source is not None else QFont()
    return _font_with_family(font, MONO_FONT_FAMILY)
```

</details>

## 🔧 Function `scale_explicit_widget_font`

```python
def scale_explicit_widget_font(widget: QWidget) -> None
```

Multiply a widget's own point size by the current UI font scale once.

<details>
<summary>Code:</summary>

```python
def scale_explicit_widget_font(widget: QWidget) -> None:
    scale = current_ui_font_scale()
    if abs(scale - 1.0) < _SCALE_EPSILON or widget.property(_SCALED_PROP) == "1":
        return
    if not widget.testAttribute(Qt.WidgetAttribute.WA_SetFont):
        return
    font = widget.font()
    point = font.pointSizeF()
    if point > 0:
        font.setPointSizeF(max(_MIN_POINT_SIZE, point * scale))
        widget.setFont(font)
    widget.setProperty(_SCALED_PROP, "1")
```

</details>
