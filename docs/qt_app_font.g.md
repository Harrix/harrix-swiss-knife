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
- [🔧 Function `bundled_font_paths`](#-function-bundled_font_paths)
- [🔧 Function `bundled_font_resource_paths`](#-function-bundled_font_resource_paths)
- [🔧 Function `install_app_fonts`](#-function-install_app_fonts)
- [🔧 Function `load_fira_sans_fonts`](#-function-load_fira_sans_fonts)
- [🔧 Function `load_jetbrains_mono_fonts`](#-function-load_jetbrains_mono_fonts)
- [🔧 Function `mono_qfont`](#-function-mono_qfont)

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

## 🔧 Function `install_app_fonts`

```python
def install_app_fonts(app: QApplication) -> None
```

Register bundled fonts and apply Fira Sans as the default UI font.

<details>
<summary>Code:</summary>

```python
def install_app_fonts(app: QApplication) -> None:
    if not isinstance(app, QApplication) or app.property(_PROP) == "1":
        return
    load_jetbrains_mono_fonts()
    if not load_fira_sans_fonts():
        return
    app.setFont(_font_with_family(app.font(), APP_FONT_FAMILY))
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
