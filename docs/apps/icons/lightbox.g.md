---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `lightbox.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `IconLightboxCanvas`](#%EF%B8%8F-class-iconlightboxcanvas)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `mouseDoubleClickEvent`](#%EF%B8%8F-method-mousedoubleclickevent)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `set_path`](#%EF%B8%8F-method-set_path)
  - [⚙️ Method `wheelEvent`](#%EF%B8%8F-method-wheelevent)
  - [⚙️ Method `zoom (property)`](#%EF%B8%8F-method-zoom-property)
  - [⚙️ Method `zoom_by`](#%EF%B8%8F-method-zoom_by)
- [🏛️ Class `IconLightboxDialog`](#%EF%B8%8F-class-iconlightboxdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `empty_caption`](#%EF%B8%8F-method-empty_caption)
  - [⚙️ Method `show_item`](#%EF%B8%8F-method-show_item)

</details>

## 🏛️ Class `IconLightboxCanvas`

```python
class IconLightboxCanvas(QWidget)
```

Paint, zoom, and drag one high-resolution icon preview.

<details>
<summary>Code:</summary>

```python
class IconLightboxCanvas(QWidget):

    backdrop_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize canvas state."""
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._path: Path | None = None
        self._image = None
        self._zoom = 1.0
        self._offset = QPointF()
        self._drag_start: QPointF | None = None
        self._drag_origin = QPointF()
        self._did_drag = False

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Close the lightbox on a left double-click (image or backdrop)."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = None
            self._did_drag = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.backdrop_clicked.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Pan the enlarged icon while dragging."""
        if self._drag_start is not None:
            delta = event.position() - self._drag_start
            if abs(delta.x()) + abs(delta.y()) >= _DRAG_THRESHOLD:
                self._did_drag = True
            self._offset = self._drag_origin + delta
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start panning when pressing the displayed icon."""
        if event.button() == Qt.MouseButton.LeftButton and self._image_rect().contains(event.position()):
            self._drag_start = event.position()
            self._drag_origin = QPointF(self._offset)
            self._did_drag = False
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Finish panning or close after a backdrop click."""
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            return
        was_dragging = self._drag_start is not None
        did_drag = self._did_drag
        self._drag_start = None
        self._did_drag = False
        self.setCursor(Qt.CursorShape.OpenHandCursor if self._zoom > 1.0 else Qt.CursorShape.ArrowCursor)
        if was_dragging:
            event.accept()
            return
        if not did_drag and not self._image_rect().contains(event.position()):
            self.backdrop_clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        """Draw the preview over the transparent canvas."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=True)
        if self._image is not None and not self._image.isNull():
            painter.drawImage(self._image_rect(), self._image)
        painter.end()

    def set_path(self, path: Path) -> None:
        """Load a new icon and reset its viewport."""
        self._path = path
        self._zoom = 1.0
        self._offset = QPointF()
        self._image = render_icon_to_image(path, _PREVIEW_RENDER_SIZE)
        self.update()

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        """Zoom around the mouse pointer."""
        if event.angleDelta().y() == 0:
            event.ignore()
            return
        factor = _ZOOM_STEP if event.angleDelta().y() > 0 else 1.0 / _ZOOM_STEP
        self.zoom_by(factor, anchor=event.position())
        event.accept()

    @property
    def zoom(self) -> float:
        """Current zoom factor."""
        return self._zoom

    def zoom_by(self, factor: float, *, anchor: QPointF | None = None) -> None:
        """Change zoom while keeping `anchor` fixed on the canvas."""
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

    def _base_side(self) -> float:
        return max(64.0, min(self.width(), self.height()) - _SCREEN_MARGIN * 2)

    def _image_rect(self) -> QRectF:
        side = self._base_side() * self._zoom
        center = QPointF(self.rect().center()) + self._offset
        return QRectF(center.x() - side / 2, center.y() - side / 2, side, side)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Initialize canvas state.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._path: Path | None = None
        self._image = None
        self._zoom = 1.0
        self._offset = QPointF()
        self._drag_start: QPointF | None = None
        self._drag_origin = QPointF()
        self._did_drag = False
```

</details>

### ⚙️ Method `mouseDoubleClickEvent`

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None
```

Close the lightbox on a left double-click (image or backdrop).

<details>
<summary>Code:</summary>

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = None
            self._did_drag = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.backdrop_clicked.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Pan the enlarged icon while dragging.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._drag_start is not None:
            delta = event.position() - self._drag_start
            if abs(delta.x()) + abs(delta.y()) >= _DRAG_THRESHOLD:
                self._did_drag = True
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

Start panning when pressing the displayed icon.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._image_rect().contains(event.position()):
            self._drag_start = event.position()
            self._drag_origin = QPointF(self._offset)
            self._did_drag = False
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

Finish panning or close after a backdrop click.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            return
        was_dragging = self._drag_start is not None
        did_drag = self._did_drag
        self._drag_start = None
        self._did_drag = False
        self.setCursor(Qt.CursorShape.OpenHandCursor if self._zoom > 1.0 else Qt.CursorShape.ArrowCursor)
        if was_dragging:
            event.accept()
            return
        if not did_drag and not self._image_rect().contains(event.position()):
            self.backdrop_clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Draw the preview over the transparent canvas.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=True)
        if self._image is not None and not self._image.isNull():
            painter.drawImage(self._image_rect(), self._image)
        painter.end()
```

</details>

### ⚙️ Method `set_path`

```python
def set_path(self, path: Path) -> None
```

Load a new icon and reset its viewport.

<details>
<summary>Code:</summary>

```python
def set_path(self, path: Path) -> None:
        self._path = path
        self._zoom = 1.0
        self._offset = QPointF()
        self._image = render_icon_to_image(path, _PREVIEW_RENDER_SIZE)
        self.update()
```

</details>

### ⚙️ Method `wheelEvent`

```python
def wheelEvent(self, event: QWheelEvent) -> None
```

Zoom around the mouse pointer.

<details>
<summary>Code:</summary>

```python
def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
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

Current zoom factor.

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

Change zoom while keeping `anchor` fixed on the canvas.

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

## 🏛️ Class `IconLightboxDialog`

```python
class IconLightboxDialog(AppWindowLightboxDialog)
```

Browse icon files with zoom, pan, keyboard navigation, and backdrop close.

<details>
<summary>Code:</summary>

```python
class IconLightboxDialog(AppWindowLightboxDialog):

    def __init__(
        self,
        paths: Sequence[Path],
        *,
        current_index: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        """Build a modal lightbox fitted to its application window."""
        valid_paths = [path for path in paths if path.is_file()]
        super().__init__(parent, item_count=len(valid_paths), current_index=current_index)
        self._paths = valid_paths
        self.canvas = IconLightboxCanvas(self)
        self.attach_content(self.canvas)
        self.finish_setup()

    def empty_caption(self) -> str:
        """Caption when there are no icon files."""
        return "No icon to display"

    def show_item(self, index: int) -> None:
        """Load the icon at `index`."""
        path = self._paths[index]
        self.setWindowTitle(path.name)
        self.canvas.set_path(path)
        self.set_caption(f"{path.name}  ·  {index + 1} / {len(self._paths)}")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, paths: Sequence[Path], *, current_index: int = 0, parent: QWidget | None = None) -> None
```

Build a modal lightbox fitted to its application window.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        paths: Sequence[Path],
        *,
        current_index: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        valid_paths = [path for path in paths if path.is_file()]
        super().__init__(parent, item_count=len(valid_paths), current_index=current_index)
        self._paths = valid_paths
        self.canvas = IconLightboxCanvas(self)
        self.attach_content(self.canvas)
        self.finish_setup()
```

</details>

### ⚙️ Method `empty_caption`

```python
def empty_caption(self) -> str
```

Caption when there are no icon files.

<details>
<summary>Code:</summary>

```python
def empty_caption(self) -> str:
        return "No icon to display"
```

</details>

### ⚙️ Method `show_item`

```python
def show_item(self, index: int) -> None
```

Load the icon at `index`.

<details>
<summary>Code:</summary>

```python
def show_item(self, index: int) -> None:
        path = self._paths[index]
        self.setWindowTitle(path.name)
        self.canvas.set_path(path)
        self.set_caption(f"{path.name}  ·  {index + 1} / {len(self._paths)}")
```

</details>
