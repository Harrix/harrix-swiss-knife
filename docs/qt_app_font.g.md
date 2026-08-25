---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_app_font.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `bundled_font_paths`](#-function-bundled_font_paths)
- [🔧 Function `bundled_font_resource_paths`](#-function-bundled_font_resource_paths)
- [🔧 Function `install_app_fonts`](#-function-install_app_fonts)
- [🔧 Function `load_jetbrains_mono_fonts`](#-function-load_jetbrains_mono_fonts)

</details>

## 🔧 Function `bundled_font_paths`

```python
def bundled_font_paths() -> list[Path]
```

Return existing JetBrains Mono files shipped next to the package.

<details>
<summary>Code:</summary>

```python
def bundled_font_paths() -> list[Path]:
    return [path for name in _FONT_FILES if (path := _FONT_DIR / name).is_file()]
```

</details>

## 🔧 Function `bundled_font_resource_paths`

```python
def bundled_font_resource_paths() -> list[str]
```

Return Qt resource paths for JetBrains Mono that exist in `resources_rc`.

<details>
<summary>Code:</summary>

```python
def bundled_font_resource_paths() -> list[str]:
    return [path for name in _FONT_FILES if QFile.exists(path := f"{_QRC_FONT_PREFIX}/{name}")]
```

</details>

## 🔧 Function `install_app_fonts`

```python
def install_app_fonts(app: QApplication) -> None
```

Register bundled JetBrains Mono and apply it as the default UI font.

<details>
<summary>Code:</summary>

```python
def install_app_fonts(app: QApplication) -> None:
    if not isinstance(app, QApplication) or app.property(_PROP) == "1":
        return
    if not load_jetbrains_mono_fonts():
        return
    app.setFont(_font_with_app_family(app.font()))
    app.setProperty(_PROP, "1")
```

</details>

## 🔧 Function `load_jetbrains_mono_fonts`

```python
def load_jetbrains_mono_fonts() -> bool
```

Load bundled TTF files into `QFontDatabase`. Return whether Regular loaded.

<details>
<summary>Code:</summary>

```python
def load_jetbrains_mono_fonts() -> bool:
    already = APP_FONT_FAMILY in QFontDatabase.families()
    loaded_regular = already
    for name in _FONT_FILES:
        qrc_path = f"{_QRC_FONT_PREFIX}/{name}"
        disk_path = _FONT_DIR / name
        loaded = _add_font(qrc_path) or _add_font(str(disk_path))
        if name == _FONT_FILES[0] and loaded:
            loaded_regular = True
    return loaded_regular
```

</details>
