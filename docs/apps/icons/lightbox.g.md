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
  - [⚙️ Method `current_index (property)`](#%EF%B8%8F-method-current_index-property)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `show_next`](#%EF%B8%8F-method-show_next)
  - [⚙️ Method `show_previous`](#%EF%B8%8F-method-show_previous)

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
class IconLightboxDialog(QDialog)
```

Browse icon files with zoom, pan, keyboard navigation, and backdrop close.

<details>
<summary>Code:</summary>

```python
class IconLightboxDialog(QDialog):

    def __init__(
        self,
        paths: Sequence[Path],
        *,
        current_index: int = 0,
        parent: QWidget | None = None,
    ) -> None:
        """Build a modal lightbox fitted to its application window."""
        owner = parent.window() if parent is not None else None
        super().__init__(owner)
        self._paths = [path for path in paths if path.is_file()]
        self._index = max(0, min(current_index, len(self._paths) - 1))
        qt_modality.set_owner_window_modal(self)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        if owner is not None:
            owner.installEventFilter(self)
            self._fit_to_owner()
        else:
            screen = QGuiApplication.primaryScreen()
            if screen is not None:
                self.setGeometry(screen.availableGeometry())
            else:
                self.resize(1280, 720)
        self.setStyleSheet("IconLightboxDialog { background-color: white; }")

        self.canvas = IconLightboxCanvas(self)
        self.canvas.backdrop_clicked.connect(self.accept)

        self._close_button = self._make_button("", "Close")
        self._close_button.setIcon(create_emoji_icon(CLOSE_BUTTON_EMOJI, 22))
        self._close_button.clicked.connect(self.accept)
        self._previous_button = self._make_button("←", "Previous (Left arrow)")
        self._previous_button.clicked.connect(self.show_previous)
        self._next_button = self._make_button("→", "Next (Right arrow)")
        self._next_button.clicked.connect(self.show_next)

        self._black_backdrop_button = self._make_backdrop_button(color="black")
        self._black_backdrop_button.clicked.connect(lambda: self._set_backdrop_color("black"))
        self._white_backdrop_button = self._make_backdrop_button(color="white")
        self._white_backdrop_button.clicked.connect(lambda: self._set_backdrop_color("white"))
        self._set_backdrop_color("white")

        self._previous_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        self._previous_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self._previous_shortcut.activated.connect(self.show_previous)
        self._next_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        self._next_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self._next_shortcut.activated.connect(self.show_next)

        self._caption = QLabel(self)
        self._caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._caption.setStyleSheet(
            "color: white; background: rgba(20, 20, 20, 180);border-radius: 7px; padding: 6px 12px;"
        )
        self._show_current()
        self._position_controls()

    @property
    def current_index(self) -> int:
        """Current path index."""
        return self._index

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Keep the overlay aligned with the owner window."""
        owner = self.parentWidget()
        if watched is owner and event.type() in {QEvent.Type.Resize, QEvent.Type.Move}:
            self._fit_to_owner()
        return super().eventFilter(watched, event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Handle Escape and left/right navigation."""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        if event.key() == Qt.Key.Key_Left:
            self.show_previous()
            return
        if event.key() == Qt.Key.Key_Right:
            self.show_next()
            return
        super().keyPressEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Keep canvas and overlay controls aligned."""
        super().resizeEvent(event)
        self._position_controls()

    def show_next(self) -> None:
        """Show the next icon, wrapping at the end."""
        if len(self._paths) > 1:
            self._index = (self._index + 1) % len(self._paths)
            self._show_current()

    def show_previous(self) -> None:
        """Show the previous icon, wrapping at the beginning."""
        if len(self._paths) > 1:
            self._index = (self._index - 1) % len(self._paths)
            self._show_current()

    def _fit_to_owner(self) -> None:
        owner = self.parentWidget()
        if owner is None:
            return
        if self.isWindow():
            top_left = owner.mapToGlobal(QPoint(0, 0))
            self.setGeometry(top_left.x(), top_left.y(), owner.width(), owner.height())
            return
        self.setGeometry(owner.rect())

    def _make_backdrop_button(self, *, color: str) -> QPushButton:
        button = QPushButton(self)
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.setFixedSize(_SWATCH_SIZE, _SWATCH_SIZE)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip("Black backdrop" if color == "black" else "White backdrop")
        border = "#888" if color == "white" else "#ccc"
        radius = _SWATCH_SIZE // 2
        button.setStyleSheet(
            f"QPushButton {{ background: {color}; border: 1px solid {border};"
            f"border-radius: {radius}px; padding: 0; }}"
            "QPushButton:checked { border: 3px solid #2f80ed; }"
        )
        return button

    def _make_button(self, text: str, tooltip: str) -> QPushButton:
        button = QPushButton(text, self)
        button.setFixedSize(QSize(_BUTTON_SIZE, _BUTTON_SIZE))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip(tooltip)
        button.setStyleSheet(
            "QPushButton { color: white; font-size: 24px; font-weight: bold;"
            "background: rgba(40, 40, 40, 125); border: 1px solid rgba(255, 255, 255, 90);"
            "border-radius: 9px; }"
            "QPushButton:hover { background: rgba(40, 40, 40, 190); }"
        )
        button.raise_()
        return button

    def _position_controls(self) -> None:
        self.canvas.setGeometry(self.rect())
        self._black_backdrop_button.move(_SIDE_MARGIN, _SIDE_MARGIN)
        self._white_backdrop_button.move(_SIDE_MARGIN + self._black_backdrop_button.width() + 8, _SIDE_MARGIN)
        self._close_button.move(self.width() - _BUTTON_SIZE - _SIDE_MARGIN, _SIDE_MARGIN)
        center_y = (self.height() - _BUTTON_SIZE) // 2
        self._previous_button.move(_SIDE_MARGIN, center_y)
        self._next_button.move(self.width() - _BUTTON_SIZE - _SIDE_MARGIN, center_y)
        caption_width = min(640, max(240, self.width() - 240))
        self._caption.setFixedWidth(caption_width)
        self._caption.adjustSize()
        self._caption.move((self.width() - caption_width) // 2, self.height() - self._caption.height() - _SIDE_MARGIN)
        for widget in (
            self._black_backdrop_button,
            self._white_backdrop_button,
            self._close_button,
            self._previous_button,
            self._next_button,
            self._caption,
        ):
            widget.raise_()

    def _set_backdrop_color(self, color: str) -> None:
        is_black = color == "black"
        self.setStyleSheet(f"IconLightboxDialog {{ background-color: {'black' if is_black else 'white'}; }}")
        self._black_backdrop_button.setChecked(is_black)
        self._white_backdrop_button.setChecked(not is_black)

    def _show_current(self) -> None:
        if not self._paths:
            self._caption.setText("No icon to display")
            self._previous_button.hide()
            self._next_button.hide()
            return
        path = self._paths[self._index]
        self.setWindowTitle(path.name)
        self.canvas.set_path(path)
        self._caption.setText(f"{path.name}  ·  {self._index + 1} / {len(self._paths)}")
        show_navigation = len(self._paths) > 1
        self._previous_button.setVisible(show_navigation)
        self._next_button.setVisible(show_navigation)
        self._position_controls()
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
        owner = parent.window() if parent is not None else None
        super().__init__(owner)
        self._paths = [path for path in paths if path.is_file()]
        self._index = max(0, min(current_index, len(self._paths) - 1))
        qt_modality.set_owner_window_modal(self)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        if owner is not None:
            owner.installEventFilter(self)
            self._fit_to_owner()
        else:
            screen = QGuiApplication.primaryScreen()
            if screen is not None:
                self.setGeometry(screen.availableGeometry())
            else:
                self.resize(1280, 720)
        self.setStyleSheet("IconLightboxDialog { background-color: white; }")

        self.canvas = IconLightboxCanvas(self)
        self.canvas.backdrop_clicked.connect(self.accept)

        self._close_button = self._make_button("", "Close")
        self._close_button.setIcon(create_emoji_icon(CLOSE_BUTTON_EMOJI, 22))
        self._close_button.clicked.connect(self.accept)
        self._previous_button = self._make_button("←", "Previous (Left arrow)")
        self._previous_button.clicked.connect(self.show_previous)
        self._next_button = self._make_button("→", "Next (Right arrow)")
        self._next_button.clicked.connect(self.show_next)

        self._black_backdrop_button = self._make_backdrop_button(color="black")
        self._black_backdrop_button.clicked.connect(lambda: self._set_backdrop_color("black"))
        self._white_backdrop_button = self._make_backdrop_button(color="white")
        self._white_backdrop_button.clicked.connect(lambda: self._set_backdrop_color("white"))
        self._set_backdrop_color("white")

        self._previous_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        self._previous_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self._previous_shortcut.activated.connect(self.show_previous)
        self._next_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        self._next_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self._next_shortcut.activated.connect(self.show_next)

        self._caption = QLabel(self)
        self._caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._caption.setStyleSheet(
            "color: white; background: rgba(20, 20, 20, 180);border-radius: 7px; padding: 6px 12px;"
        )
        self._show_current()
        self._position_controls()
```

</details>

### ⚙️ Method `current_index (property)`

```python
def current_index(self) -> int
```

Current path index.

<details>
<summary>Code:</summary>

```python
def current_index(self) -> int:
        return self._index
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Keep the overlay aligned with the owner window.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        owner = self.parentWidget()
        if watched is owner and event.type() in {QEvent.Type.Resize, QEvent.Type.Move}:
            self._fit_to_owner()
        return super().eventFilter(watched, event)
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Handle Escape and left/right navigation.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        if event.key() == Qt.Key.Key_Left:
            self.show_previous()
            return
        if event.key() == Qt.Key.Key_Right:
            self.show_next()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Keep canvas and overlay controls aligned.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._position_controls()
```

</details>

### ⚙️ Method `show_next`

```python
def show_next(self) -> None
```

Show the next icon, wrapping at the end.

<details>
<summary>Code:</summary>

```python
def show_next(self) -> None:
        if len(self._paths) > 1:
            self._index = (self._index + 1) % len(self._paths)
            self._show_current()
```

</details>

### ⚙️ Method `show_previous`

```python
def show_previous(self) -> None
```

Show the previous icon, wrapping at the beginning.

<details>
<summary>Code:</summary>

```python
def show_previous(self) -> None:
        if len(self._paths) > 1:
            self._index = (self._index - 1) % len(self._paths)
            self._show_current()
```

</details>
