---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `system.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ScreenCaptureManager`](#%EF%B8%8F-class-screencapturemanager)
  - [⚙️ Method `capture_region`](#%EF%B8%8F-method-capture_region)
  - [⚙️ Method `capture_screen`](#%EF%B8%8F-method-capture_screen)
  - [⚙️ Method `screens`](#%EF%B8%8F-method-screens)
- [🏛️ Class `ScreenInfo`](#%EF%B8%8F-class-screeninfo)
- [🔧 Function `exponential_blur`](#-function-exponential_blur)

</details>

## 🏛️ Class `ScreenCaptureManager`

```python
class ScreenCaptureManager
```

List monitors and grab a monitor or a desktop region as a `QPixmap`.

<details>
<summary>Code:</summary>

```python
class ScreenCaptureManager:

    def capture_region(self, region: QRect) -> QPixmap:
        """Grab a rectangle in virtual-desktop coordinates (from the screen that holds its center)."""
        screen = QGuiApplication.screenAt(region.center()) or QGuiApplication.primaryScreen()
        if screen is None:
            return QPixmap()
        local = region.translated(-screen.geometry().topLeft())
        return screen.grabWindow(0, local.x(), local.y(), local.width(), local.height())

    def capture_screen(self, index: int = 0) -> QPixmap:
        """Grab the whole monitor at `index`."""
        screens = QGuiApplication.screens()
        if not 0 <= index < len(screens):
            return QPixmap()
        return screens[index].grabWindow(0)

    def screens(self) -> list[ScreenInfo]:
        """Return the connected monitors."""
        return [
            ScreenInfo(index, screen.name(), screen.geometry(), screen.devicePixelRatio())
            for index, screen in enumerate(QGuiApplication.screens())
        ]
```

</details>

### ⚙️ Method `capture_region`

```python
def capture_region(self, region: QRect) -> QPixmap
```

Grab a rectangle in virtual-desktop coordinates (from the screen that holds its center).

<details>
<summary>Code:</summary>

```python
def capture_region(self, region: QRect) -> QPixmap:
        screen = QGuiApplication.screenAt(region.center()) or QGuiApplication.primaryScreen()
        if screen is None:
            return QPixmap()
        local = region.translated(-screen.geometry().topLeft())
        return screen.grabWindow(0, local.x(), local.y(), local.width(), local.height())
```

</details>

### ⚙️ Method `capture_screen`

```python
def capture_screen(self, index: int = 0) -> QPixmap
```

Grab the whole monitor at `index`.

<details>
<summary>Code:</summary>

```python
def capture_screen(self, index: int = 0) -> QPixmap:
        screens = QGuiApplication.screens()
        if not 0 <= index < len(screens):
            return QPixmap()
        return screens[index].grabWindow(0)
```

</details>

### ⚙️ Method `screens`

```python
def screens(self) -> list[ScreenInfo]
```

Return the connected monitors.

<details>
<summary>Code:</summary>

```python
def screens(self) -> list[ScreenInfo]:
        return [
            ScreenInfo(index, screen.name(), screen.geometry(), screen.devicePixelRatio())
            for index, screen in enumerate(QGuiApplication.screens())
        ]
```

</details>

## 🏛️ Class `ScreenInfo`

```python
class ScreenInfo
```

One monitor known to [`ScreenCaptureManager`](#%EF%B8%8F-class-screencapturemanager).

<details>
<summary>Code:</summary>

```python
class ScreenInfo:

    index: int
    name: str
    geometry: QRect
    device_pixel_ratio: float
```

</details>

## 🔧 Function `exponential_blur`

```python
def exponential_blur(image: QImage, radius: int) -> QImage
```

Return a blurred copy of `image` using a two-pass exponential (IIR) filter.

Args:

- `image` (`QImage`): Source image (any format; converted to ARGB32).
- `radius` (`int`): Blur radius in pixels (`<= 0` returns a copy).

<details>
<summary>Code:</summary>

```python
def exponential_blur(image: QImage, radius: int) -> QImage:
    source = image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
    if radius <= 0 or source.isNull():
        return source.copy()
    width, height = source.width(), source.height()
    pointer = source.constBits()
    data = np.frombuffer(pointer, dtype=np.uint8, count=source.sizeInBytes()).reshape(height, source.bytesPerLine())
    pixels = data[:, : width * 4].reshape(height, width, 4).astype(np.int64) << _PARAM_PRECISION
    alpha = int((1 << _ALPHA_PRECISION) * (1.0 - np.exp(-2.3 / (radius + 1.0))))
    for _ in range(2):
        for axis in (1, 0):
            pixels = _blur_axis(pixels, alpha, axis)
    result = np.clip(pixels >> _PARAM_PRECISION, 0, 255).astype(np.uint8)
    output = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    buffer = np.frombuffer(output.bits(), dtype=np.uint8, count=output.sizeInBytes()).reshape(
        height, output.bytesPerLine()
    )
    buffer[:, : width * 4] = result.reshape(height, width * 4)
    return output
```

</details>
