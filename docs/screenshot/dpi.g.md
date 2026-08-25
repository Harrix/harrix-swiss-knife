---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `dpi.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `crop_pixmap_from_logical_rect`](#-function-crop_pixmap_from_logical_rect)
- [🔧 Function `logical_rect_to_pixel_rect`](#-function-logical_rect_to_pixel_rect)
- [🔧 Function `logical_size_to_pixel_size`](#-function-logical_size_to_pixel_size)
- [🔧 Function `pixmap_as_physical_pixels`](#-function-pixmap_as_physical_pixels)
- [🔧 Function `pixmap_device_pixel_ratio`](#-function-pixmap_device_pixel_ratio)
- [🔧 Function `screen_destination_in_physical_pixels`](#-function-screen_destination_in_physical_pixels)

</details>

## 🔧 Function `crop_pixmap_from_logical_rect`

```python
def crop_pixmap_from_logical_rect(pixmap: QPixmap, logical_rect: QRect) -> QImage | None
```

Copy `logical_rect` from `pixmap`, mapping through its device pixel ratio.

`QPixmap.copy()` uses device pixels. Mouse selection is in logical widget
coordinates, so the rectangle must be scaled by `devicePixelRatio` first.

The returned image has `devicePixelRatio` 1.0 so clipboard and preview treat
the pixels as native resolution.

<details>
<summary>Code:</summary>

```python
def crop_pixmap_from_logical_rect(pixmap: QPixmap, logical_rect: QRect) -> QImage | None:
    dpr = pixmap_device_pixel_ratio(pixmap)
    pixel_rect = logical_rect_to_pixel_rect(logical_rect, dpr)
    clipped = pixel_rect.intersected(QRect(0, 0, pixmap.width(), pixmap.height()))
    if clipped.isEmpty():
        return None
    image = pixmap.copy(clipped).toImage()
    image.setDevicePixelRatio(1.0)
    return image
```

</details>

## 🔧 Function `logical_rect_to_pixel_rect`

```python
def logical_rect_to_pixel_rect(rect: QRect, dpr: float) -> QRect
```

Scale a logical rectangle to device pixels.

<details>
<summary>Code:</summary>

```python
def logical_rect_to_pixel_rect(rect: QRect, dpr: float) -> QRect:
    scale = dpr if dpr > 0 else 1.0
    return QRect(
        round(rect.x() * scale),
        round(rect.y() * scale),
        max(0, round(rect.width() * scale)),
        max(0, round(rect.height() * scale)),
    )
```

</details>

## 🔧 Function `logical_size_to_pixel_size`

```python
def logical_size_to_pixel_size(size: QSize, dpr: float) -> QSize
```

Scale a logical size to device pixels.

<details>
<summary>Code:</summary>

```python
def logical_size_to_pixel_size(size: QSize, dpr: float) -> QSize:
    scale = dpr if dpr > 0 else 1.0
    return QSize(
        max(1, round(size.width() * scale)),
        max(1, round(size.height() * scale)),
    )
```

</details>

## 🔧 Function `pixmap_as_physical_pixels`

```python
def pixmap_as_physical_pixels(pixmap: QPixmap) -> QPixmap
```

Return a copy whose `devicePixelRatio` is 1.0 so painters use raw pixels.

<details>
<summary>Code:</summary>

```python
def pixmap_as_physical_pixels(pixmap: QPixmap) -> QPixmap:
    if pixmap_device_pixel_ratio(pixmap) == 1.0:
        return pixmap
    physical = QPixmap(pixmap)
    physical.setDevicePixelRatio(1.0)
    return physical
```

</details>

## 🔧 Function `pixmap_device_pixel_ratio`

```python
def pixmap_device_pixel_ratio(pixmap: QPixmap) -> float
```

Return a positive device pixel ratio for `pixmap`.

<details>
<summary>Code:</summary>

```python
def pixmap_device_pixel_ratio(pixmap: QPixmap) -> float:
    dpr = pixmap.devicePixelRatio()
    return dpr if dpr > 0 else 1.0
```

</details>

## 🔧 Function `screen_destination_in_physical_pixels`

```python
def screen_destination_in_physical_pixels(screen_geometry: QRect, virtual_geometry: QRect, composed_dpr: float) -> QRect
```

Map a screen's logical geometry onto the stitched physical canvas.

<details>
<summary>Code:</summary>

```python
def screen_destination_in_physical_pixels(
    screen_geometry: QRect,
    virtual_geometry: QRect,
    composed_dpr: float,
) -> QRect:
    scale = composed_dpr if composed_dpr > 0 else 1.0
    return QRect(
        round((screen_geometry.x() - virtual_geometry.x()) * scale),
        round((screen_geometry.y() - virtual_geometry.y()) * scale),
        max(1, round(screen_geometry.width() * scale)),
        max(1, round(screen_geometry.height() * scale)),
    )
```

</details>
