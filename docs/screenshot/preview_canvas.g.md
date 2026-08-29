---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `preview_canvas.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ScreenshotPreviewCanvas`](#%EF%B8%8F-class-screenshotpreviewcanvas)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `wheelEvent`](#%EF%B8%8F-method-wheelevent)
  - [⚙️ Method `zoom (property)`](#%EF%B8%8F-method-zoom-property)
  - [⚙️ Method `zoom_by`](#%EF%B8%8F-method-zoom_by)

</details>

## 🏛️ Class `ScreenshotPreviewCanvas`

```python
class ScreenshotPreviewCanvas(QWidget)
```

Show an image fitted with aspect ratio; Ctrl+wheel zooms; middle-drag pans.

<details>
<summary>Code:</summary>

```python
class ScreenshotPreviewCanvas(QWidget):

    def __init__(self, image: QImage, parent: QWidget | None = None) -> None:
        """Create a canvas for `image` at fit zoom."""
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._pixmap = QPixmap.fromImage(image)
        self._zoom = 1.0
        self._offset = QPointF()
        self._drag_start: QPointF | None = None
        self._drag_origin = QPointF()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Pan while the middle mouse button is held."""
        if self._drag_start is not None:
            delta = event.position() - self._drag_start
            self._offset = self._drag_origin + delta
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start panning on middle-button press."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._drag_start = event.position()
            self._drag_origin = QPointF(self._offset)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """End middle-button panning."""
        if event.button() == Qt.MouseButton.MiddleButton and self._drag_start is not None:
            self._drag_start = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        """Draw the fitted (and possibly zoomed/panned) pixmap."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=True)
        if not self._pixmap.isNull():
            painter.drawPixmap(self._image_rect().toRect(), self._pixmap)
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Repaint when the available fit area changes."""
        super().resizeEvent(event)
        self.update()

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        """Zoom with Ctrl+wheel around the pointer."""
        if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            event.ignore()
            return
        if event.angleDelta().y() == 0:
            event.ignore()
            return
        factor = _ZOOM_STEP if event.angleDelta().y() > 0 else 1.0 / _ZOOM_STEP
        self.zoom_by(factor, anchor=event.position())
        event.accept()

    @property
    def zoom(self) -> float:
        """Current zoom relative to the fitted size (`1.0` = fit)."""
        return self._zoom

    def zoom_by(self, factor: float, *, anchor: QPointF | None = None) -> None:
        """Multiply zoom by `factor`, keeping `anchor` fixed on the canvas."""
        old_zoom = self._zoom
        new_zoom = max(_MIN_ZOOM, min(_MAX_ZOOM, old_zoom * factor))
        if new_zoom == old_zoom:
            return
        center = QPointF(self.rect().center())
        pointer = anchor if anchor is not None else center
        relative = pointer - center - self._offset
        self._offset = pointer - center - relative * (new_zoom / old_zoom)
        self._zoom = new_zoom
        self.update()

    def _fitted_size(self) -> QSizeF:
        if self._pixmap.isNull() or self.width() <= 0 or self.height() <= 0:
            return QSizeF()
        fitted = self._pixmap.size().scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        return QSizeF(fitted.width() * self._zoom, fitted.height() * self._zoom)

    def _image_rect(self) -> QRectF:
        size = self._fitted_size()
        if size.isEmpty():
            return QRectF()
        center = QPointF(self.rect().center()) + self._offset
        return QRectF(center.x() - size.width() / 2, center.y() - size.height() / 2, size.width(), size.height())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, image: QImage, parent: QWidget | None = None) -> None
```

Create a canvas for `image` at fit zoom.

<details>
<summary>Code:</summary>

```python
def __init__(self, image: QImage, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._pixmap = QPixmap.fromImage(image)
        self._zoom = 1.0
        self._offset = QPointF()
        self._drag_start: QPointF | None = None
        self._drag_origin = QPointF()
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Pan while the middle mouse button is held.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._drag_start is not None:
            delta = event.position() - self._drag_start
            self._offset = self._drag_origin + delta
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Start panning on middle-button press.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.MiddleButton:
            self._drag_start = event.position()
            self._drag_origin = QPointF(self._offset)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

End middle-button panning.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.MiddleButton and self._drag_start is not None:
            self._drag_start = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Draw the fitted (and possibly zoomed/panned) pixmap.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=True)
        if not self._pixmap.isNull():
            painter.drawPixmap(self._image_rect().toRect(), self._pixmap)
        painter.end()
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Repaint when the available fit area changes.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.update()
```

</details>

### ⚙️ Method `wheelEvent`

```python
def wheelEvent(self, event: QWheelEvent) -> None
```

Zoom with Ctrl+wheel around the pointer.

<details>
<summary>Code:</summary>

```python
def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            event.ignore()
            return
        if event.angleDelta().y() == 0:
            event.ignore()
            return
        factor = _ZOOM_STEP if event.angleDelta().y() > 0 else 1.0 / _ZOOM_STEP
        self.zoom_by(factor, anchor=event.position())
        event.accept()
```

</details>

### ⚙️ Method `zoom (property)`

```python
def zoom(self) -> float
```

Current zoom relative to the fitted size (`1.0` = fit).

<details>
<summary>Code:</summary>

```python
def zoom(self) -> float:
        return self._zoom
```

</details>

### ⚙️ Method `zoom_by`

```python
def zoom_by(self, factor: float, *, anchor: QPointF | None = None) -> None
```

Multiply zoom by `factor`, keeping `anchor` fixed on the canvas.

<details>
<summary>Code:</summary>

```python
def zoom_by(self, factor: float, *, anchor: QPointF | None = None) -> None:
        old_zoom = self._zoom
        new_zoom = max(_MIN_ZOOM, min(_MAX_ZOOM, old_zoom * factor))
        if new_zoom == old_zoom:
            return
        center = QPointF(self.rect().center())
        pointer = anchor if anchor is not None else center
        relative = pointer - center - self._offset
        self._offset = pointer - center - relative * (new_zoom / old_zoom)
        self._zoom = new_zoom
        self.update()
```

</details>
