---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `geometry.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `GdigrabRegion`](#%EF%B8%8F-class-gdigrabregion)
- [🔧 Function `even_size`](#-function-even_size)
- [🔧 Function `logical_rect_to_gdigrab`](#-function-logical_rect_to_gdigrab)

</details>

## 🏛️ Class `GdigrabRegion`

```python
class GdigrabRegion
```

Physical desktop crop for `-f gdigrab`.

<details>
<summary>Code:</summary>

```python
class GdigrabRegion:

    offset_x: int
    offset_y: int
    width: int
    height: int
```

</details>

## 🔧 Function `even_size`

```python
def even_size(width: int, height: int) -> tuple[int, int]
```

Return even width/height (required by many video codecs).

<details>
<summary>Code:</summary>

```python
def even_size(width: int, height: int) -> tuple[int, int]:
    return max(_MIN_EVEN_SIZE, width - (width % 2)), max(_MIN_EVEN_SIZE, height - (height % 2))
```

</details>

## 🔧 Function `logical_rect_to_gdigrab`

```python
def logical_rect_to_gdigrab(region: QRect) -> GdigrabRegion | None
```

Convert a global logical Qt rectangle to gdigrab offsets and size.

Prefers a single monitor that contains the selection center. Mixed-DPI
selections that span monitors are clamped to the primary intersecting screen.

<details>
<summary>Code:</summary>

```python
def logical_rect_to_gdigrab(region: QRect) -> GdigrabRegion | None:
    if region.isEmpty() or region.width() < _MIN_EVEN_SIZE or region.height() < _MIN_EVEN_SIZE:
        return None
    app = QApplication.instance()
    if app is None:
        return None
    screen = app.screenAt(region.center()) or app.primaryScreen()
    if screen is None:
        return None
    geo = screen.geometry()
    clipped = region.intersected(geo)
    if clipped.isEmpty():
        return None
    dpr = screen.devicePixelRatio()
    local = clipped.translated(-geo.x(), -geo.y())
    physical_local = logical_rect_to_pixel_rect(local, dpr)
    monitor_origin = _physical_monitor_origin(geo.topLeft())
    width, height = even_size(physical_local.width(), physical_local.height())
    if width < _MIN_EVEN_SIZE or height < _MIN_EVEN_SIZE:
        return None
    return GdigrabRegion(
        offset_x=monitor_origin.x() + physical_local.x(),
        offset_y=monitor_origin.y() + physical_local.y(),
        width=width,
        height=height,
    )
```

</details>
