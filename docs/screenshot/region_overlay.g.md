---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `region_overlay.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RegionOverlay`](#️-class-regionoverlay)
  - [⚙️ Method `__init__`](#️-method-__init__)
  - [⚙️ Method `cropped_image`](#️-method-cropped_image)
  - [⚙️ Method `keyPressEvent`](#️-method-keypressevent)
  - [⚙️ Method `mouseMoveEvent`](#️-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#️-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#️-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#️-method-paintevent)

</details>

## 🏛️ Class `RegionOverlay`

```python
class RegionOverlay(QDialog)
```

Overlay that shows a frozen desktop grab and lets the user select a region.

<details>
<summary>Code:</summary>

```python
class RegionOverlay(QDialog):

    def __init__(self, frozen: QPixmap, geometry: QRect) -> None:
        """Create the overlay covering `geometry` with the frozen desktop image.

        Args:
        frozen: Stitched screenshot of the virtual desktop.
        geometry: Virtual-desktop geometry in global coordinates.

        """
        super().__init__(None)
        mark_screenshot_ui(self)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.Window
        )
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMouseTracking(True)
        self.setGeometry(geometry)

        self._frozen = frozen
        self._origin: QPoint | None = None
        self._current: QPoint | None = None
        self._crop: QImage | None = None

    @property
    def cropped_image(self) -> QImage | None:
        """Return the selected crop, or `None` if cancelled / empty."""
        return self._crop

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Cancel selection on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self._crop = None
            self.reject()
            return
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Update the selection rectangle while dragging."""
        if self._origin is None:
            return
        self._current = event.position().toPoint()
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start a new selection rectangle."""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._origin = event.position().toPoint()
        self._current = self._origin
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Finish selection and crop the frozen pixmap."""
        if event.button() != Qt.MouseButton.LeftButton or self._origin is None:
            return
        self._current = event.position().toPoint()
        rect = self._selection_rect()
        self._origin = None
        self._current = None

        if rect is None or rect.width() < _MIN_SELECTION or rect.height() < _MIN_SELECTION:
            self._crop = None
            self.reject()
            return

        clipped = rect.intersected(self._frozen.rect())
        if clipped.isEmpty():
            self._crop = None
            self.reject()
            return

        self._crop = self._frozen.copy(clipped).toImage()
        self.accept()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Draw frozen desktop, dim overlay, and clear selection region."""
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._frozen)
        painter.fillRect(self.rect(), _DIM_COLOR)

        rect = self._selection_rect()
        if rect is not None and rect.isValid():
            painter.drawPixmap(rect, self._frozen, rect)
            pen = QPen(_BORDER_COLOR, _BORDER_WIDTH)
            painter.setPen(pen)
            painter.drawRect(rect.adjusted(0, 0, -1, -1))

    def _selection_rect(self) -> QRect | None:
        if self._origin is None or self._current is None:
            return None
        return QRect(self._origin, self._current).normalized()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, frozen: QPixmap, geometry: QRect) -> None
```

Create the overlay covering `geometry` with the frozen desktop image.

Args:
frozen: Stitched screenshot of the virtual desktop.
geometry: Virtual-desktop geometry in global coordinates.

<details>
<summary>Code:</summary>

```python
def __init__(self, frozen: QPixmap, geometry: QRect) -> None:
        super().__init__(None)
        mark_screenshot_ui(self)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.Window
        )
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMouseTracking(True)
        self.setGeometry(geometry)

        self._frozen = frozen
        self._origin: QPoint | None = None
        self._current: QPoint | None = None
        self._crop: QImage | None = None
```

</details>

### ⚙️ Method `cropped_image`

```python
def cropped_image(self) -> QImage | None
```

Return the selected crop, or `None` if cancelled / empty.

<details>
<summary>Code:</summary>

```python
def cropped_image(self) -> QImage | None:
        return self._crop
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Cancel selection on Escape.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self._crop = None
            self.reject()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Update the selection rectangle while dragging.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._origin is None:
            return
        self._current = event.position().toPoint()
        self.update()
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Start a new selection rectangle.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self._origin = event.position().toPoint()
        self._current = self._origin
        self.update()
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Finish selection and crop the frozen pixmap.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton or self._origin is None:
            return
        self._current = event.position().toPoint()
        rect = self._selection_rect()
        self._origin = None
        self._current = None

        if rect is None or rect.width() < _MIN_SELECTION or rect.height() < _MIN_SELECTION:
            self._crop = None
            self.reject()
            return

        clipped = rect.intersected(self._frozen.rect())
        if clipped.isEmpty():
            self._crop = None
            self.reject()
            return

        self._crop = self._frozen.copy(clipped).toImage()
        self.accept()
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Draw frozen desktop, dim overlay, and clear selection region.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._frozen)
        painter.fillRect(self.rect(), _DIM_COLOR)

        rect = self._selection_rect()
        if rect is not None and rect.isValid():
            painter.drawPixmap(rect, self._frozen, rect)
            pen = QPen(_BORDER_COLOR, _BORDER_WIDTH)
            painter.setPen(pen)
            painter.drawRect(rect.adjusted(0, 0, -1, -1))
```

</details>
