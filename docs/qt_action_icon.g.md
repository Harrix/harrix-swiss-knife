---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_action_icon.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `action_svg_path`](#-function-action_svg_path)
- [🔧 Function `create_action_icon`](#-function-create_action_icon)
- [🔧 Function `create_menu_icon`](#-function-create_menu_icon)
- [🔧 Function `create_svg_file_icon`](#-function-create_svg_file_icon)
- [🔧 Function `resolve_ui_icon_spec`](#-function-resolve_ui_icon_spec)

</details>

## 🔧 Function `action_svg_path`

```python
def action_svg_path(name: str) -> Path | None
```

Return `assets/actions/<name>.svg` when `name` is a safe existing file.

<details>
<summary>Code:</summary>

```python
def action_svg_path(name: str) -> Path | None:
    raw = name.strip()
    if not raw or ".." in raw or "/" in raw or "\\" in raw:
        return None
    filename = raw if raw.casefold().endswith(".svg") else f"{raw}.svg"
    if Path(filename).name != filename:
        return None
    path = _actions_dir() / filename
    if path.is_file():
        return path
    return None
```

</details>

## 🔧 Function `create_action_icon`

```python
def create_action_icon(action_cls: type, size: int = 32) -> QIcon
```

Build the GUI `QIcon` for an action class (`icon_svg`, else `icon`).

<details>
<summary>Code:</summary>

```python
def create_action_icon(action_cls: type, size: int = 32) -> QIcon:
    return create_menu_icon(resolve_ui_icon_spec(action_cls), size)
```

</details>

## 🔧 Function `create_menu_icon`

```python
def create_menu_icon(spec: str, size: int = 32, *, device_pixel_ratio: float | None = None) -> QIcon
```

Load a GUI icon from an action SVG, a Qt resource SVG, or an emoji.

<details>
<summary>Code:</summary>

```python
def create_menu_icon(spec: str, size: int = 32, *, device_pixel_ratio: float | None = None) -> QIcon:
    if not spec:
        return QIcon()
    svg_path = action_svg_path(spec)
    if svg_path is not None:
        return create_svg_file_icon(svg_path, size, device_pixel_ratio=device_pixel_ratio)
    if ".svg" in spec:
        return QIcon(f":/assets/{spec}")
    return create_emoji_icon(spec, size, device_pixel_ratio=device_pixel_ratio)
```

</details>

## 🔧 Function `create_svg_file_icon`

```python
def create_svg_file_icon(path: Path, size: int = 32, *, device_pixel_ratio: float | None = None) -> QIcon
```

Rasterize a colored SVG file into a square `QIcon`.

<details>
<summary>Code:</summary>

```python
def create_svg_file_icon(
    path: Path,
    size: int = 32,
    *,
    device_pixel_ratio: float | None = None,
) -> QIcon:
    ratio = device_pixel_ratio if device_pixel_ratio is not None else _icon_device_pixel_ratio()
    if ratio <= 0:
        ratio = 1.0
    cache_key = (str(path.resolve()), size, ratio)
    cached = _CACHE.get(cache_key)
    if cached is not None:
        return cached

    renderer = QSvgRenderer(str(path))
    if not renderer.isValid():
        logger.warning("Action SVG `%s` is invalid", path)
        return QIcon()

    physical = max(1, round(size * ratio))
    pixmap = QPixmap(physical, physical)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
    renderer.render(painter, QRectF(0.0, 0.0, float(physical), float(physical)))
    painter.end()
    pixmap.setDevicePixelRatio(ratio)

    icon = QIcon()
    icon.addPixmap(pixmap)
    _CACHE[cache_key] = icon
    return icon
```

</details>

## 🔧 Function `resolve_ui_icon_spec`

```python
def resolve_ui_icon_spec(action_cls: type) -> str
```

Return the GUI icon spec: existing `icon_svg` file, else emoji `icon`.

<details>
<summary>Code:</summary>

```python
def resolve_ui_icon_spec(action_cls: type) -> str:
    svg = str(getattr(action_cls, "icon_svg", "") or "").strip()
    emoji = str(getattr(action_cls, "icon", "") or "").strip()
    if svg and action_svg_path(svg) is not None:
        return svg if svg.casefold().endswith(".svg") else f"{svg}.svg"
    return emoji
```

</details>
