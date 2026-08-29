---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `region_overlay.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RegionOverlay`](#%EF%B8%8F-class-regionoverlay)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `cropped_image (property)`](#%EF%B8%8F-method-cropped_image-property)
  - [⚙️ Method `event`](#%EF%B8%8F-method-event)
  - [⚙️ Method `hideEvent`](#%EF%B8%8F-method-hideevent)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `mouseDoubleClickEvent`](#%EF%B8%8F-method-mousedoubleclickevent)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)

</details>

## 🏛️ Class `RegionOverlay`

```python
class RegionOverlay(QDialog)
```

Overlay that shows a frozen desktop grab and lets the user select a region.

With `with_shutter_controls=True`, arrange/adjust/close buttons are embedded as
child widgets. Arrange finishes with `RESULT_TOGGLE_ARRANGE`. Adjust (checkable)
keeps the next selection editable: move/resize with handles, Enter or double-click
to capture.

When `window_rects` is provided, hovering highlights the most specific region under
the pointer; a click without a drag captures (or edits) that region.

<details>
<summary>Code:</summary>

```python
class RegionOverlay(QDialog):

    def __init__(
        self,
        frozen: QPixmap,
        geometry: QRect,
        *,
        with_shutter_controls: bool = False,
        window_rects: Sequence[QRect] | None = None,
    ) -> None:
        """Create a fullscreen overlay for region selection, displaying the frozen desktop.

        Args:

        - `frozen` (`QPixmap`): Stitched screenshot of the virtual desktop to display as background.
        - `geometry` (`QRect`): The target geometry in global (screen) coordinates for overlay placement.
        - `with_shutter_controls` (`bool`): If `True`, embed shutter controls on the left edge.
        - `window_rects` (`Sequence[QRect] | None`): Snappable window bounds in global logical pixels.

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
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setGeometry(geometry)

        self._frozen = frozen
        self._origin: QPoint | None = None
        self._current: QPoint | None = None
        self._crop: QImage | None = None
        self._dragging = False
        self._snap_rect: QRect | None = None
        self._panel: ShutterPanel | None = None
        self._edit_rect: QRect | None = None
        self._edit_handle: HandleKind | None = None
        self._edit_press_pos: QPoint | None = None
        self._edit_press_rect: QRect | None = None
        origin = geometry.topLeft()
        self._window_rects_local = [
            rect.translated(-origin.x(), -origin.y()).intersected(QRect(0, 0, geometry.width(), geometry.height()))
            for rect in (window_rects or ())
        ]
        self._window_rects_local = [rect for rect in self._window_rects_local if rect.isValid() and not rect.isEmpty()]

        if with_shutter_controls:
            panel = ShutterPanel(self)
            panel.set_mode("selection")
            panel.triggered.connect(lambda: self.done(RESULT_TOGGLE_ARRANGE))
            panel.cancelled.connect(self.reject)
            panel.geometry_changed.connect(lambda: position_panel_on_left_edge(panel, geometry))
            position_panel_on_left_edge(panel, geometry)
            panel.show()
            self._panel = panel

    @property
    def cropped_image(self) -> QImage | None:
        """Return the selected crop, or `None` if cancelled / empty."""
        return self._crop

    def event(self, event: QEvent) -> bool:
        """Accept Escape as a shortcut override so it is not stolen by other Windows.

        Args:

        - `event` (`QEvent`): The event being delivered to the overlay.

        """
        if event.type() == QEvent.Type.ShortcutOverride and _is_escape_key(event):
            event.accept()
            return True
        return super().event(event)

    def hideEvent(self, event: QHideEvent) -> None:  # noqa: N802
        """Release the keyboard grab when the overlay is hidden."""
        release_screenshot_keyboard(self)
        super().hideEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Enter confirms an editable frame; Escape clears it or cancels capture."""
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter} and self._edit_rect is not None:
            self._finish_with_rect(self._edit_rect)
            event.accept()
            return
        if event.key() == Qt.Key.Key_Escape:
            if self._edit_rect is not None:
                self._clear_edit_rect()
                event.accept()
                return
            self._crop = None
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Double-click confirms the editable selection frame."""
        if event.button() != Qt.MouseButton.LeftButton or self._edit_rect is None:
            return
        if self._edit_rect.contains(event.position().toPoint()):
            self._finish_with_rect(self._edit_rect)
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Update snap, free-drag selection, or editable frame move/resize."""
        pos = event.position().toPoint()

        if self._edit_rect is not None:
            if self._edit_handle is not None and self._edit_press_pos is not None and self._edit_press_rect is not None:
                self._edit_rect = transform_selection_rect(
                    self._edit_press_rect,
                    self._edit_handle,
                    self._edit_press_pos,
                    pos,
                    bounds=self.rect(),
                    min_size=_MIN_SELECTION,
                )
                self.update()
                return
            self._apply_edit_cursor(hit_test_selection_handle(self._edit_rect, pos))
            return

        if self._origin is None:
            self._update_snap_at(pos)
            return

        self._current = pos
        if not self._dragging:
            delta = pos - self._origin
            if abs(delta.x()) >= _DRAG_THRESHOLD or abs(delta.y()) >= _DRAG_THRESHOLD:
                self._dragging = True
                self._snap_rect = None
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start free selection, snap capture, or begin editing an adjustable frame."""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.position().toPoint()

        if self._edit_rect is not None:
            handle = hit_test_selection_handle(self._edit_rect, pos)
            if handle is None:
                return
            self._edit_handle = handle
            self._edit_press_pos = pos
            self._edit_press_rect = QRect(self._edit_rect)
            self._apply_edit_cursor(handle)
            return

        self._origin = pos
        self._current = pos
        self._dragging = False
        self._update_snap_at(pos)
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Finish free selection, enter edit mode, or end a frame edit drag."""
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if self._edit_rect is not None:
            self._edit_handle = None
            self._edit_press_pos = None
            self._edit_press_rect = None
            self._apply_edit_cursor(hit_test_selection_handle(self._edit_rect, event.position().toPoint()))
            self.update()
            return

        if self._origin is None:
            return

        pos = event.position().toPoint()
        self._current = pos

        capture_rect: QRect | None
        if self._dragging:
            capture_rect = self._selection_rect()
        elif self._snap_rect is not None:
            capture_rect = QRect(self._snap_rect)
        else:
            capture_rect = None

        was_dragging = self._dragging
        self._origin = None
        self._current = None
        self._dragging = False

        if capture_rect is None:
            self._update_snap_at(pos)
            self.update()
            return

        if capture_rect.width() < _MIN_SELECTION or capture_rect.height() < _MIN_SELECTION:
            self._crop = None
            if was_dragging:
                self.reject()
            else:
                self._update_snap_at(pos)
                self.update()
            return

        if self._adjust_mode_enabled():
            self._enter_edit_rect(capture_rect)
            return

        self._finish_with_rect(capture_rect)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Draw frozen desktop, dim overlay, selection/snap, and edit handles."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=False)
        painter.drawPixmap(self.rect(), self._frozen)
        painter.fillRect(self.rect(), _DIM_COLOR)

        rect = self._active_highlight_rect()
        if rect is not None and rect.isValid():
            source = logical_rect_to_pixel_rect(rect, pixmap_device_pixel_ratio(self._frozen))
            painter.drawPixmap(rect, self._frozen, source)
            pen = QPen(_BORDER_COLOR, _BORDER_WIDTH)
            painter.setPen(pen)
            painter.drawRect(rect.adjusted(0, 0, -1, -1))
            if self._edit_rect is not None:
                self._paint_edit_handles(painter, rect)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Take keyboard focus so Escape cancels capture on Tool overlays."""
        super().showEvent(event)
        claim_screenshot_keyboard(self)
        self._update_snap_at(self.mapFromGlobal(QCursor.pos()))

    def _active_highlight_rect(self) -> QRect | None:
        """Return the rectangle currently shown as the clear selection / snap region."""
        if self._edit_rect is not None:
            return self._edit_rect
        if self._dragging:
            return self._selection_rect()
        if self._snap_rect is not None:
            return self._snap_rect
        return self._selection_rect()

    def _adjust_mode_enabled(self) -> bool:
        return self._panel is not None and self._panel.adjust_mode

    def _apply_edit_cursor(self, handle: HandleKind | None) -> None:
        shape_name = cursor_for_handle(handle)
        self.setCursor(getattr(Qt.CursorShape, shape_name))

    def _clear_edit_rect(self) -> None:
        self._edit_rect = None
        self._edit_handle = None
        self._edit_press_pos = None
        self._edit_press_rect = None
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._update_snap_at(self.mapFromGlobal(QCursor.pos()))
        self.update()

    def _enter_edit_rect(self, rect: QRect) -> None:
        self._edit_rect = QRect(rect)
        self._snap_rect = None
        self._origin = None
        self._current = None
        self._dragging = False
        self._apply_edit_cursor(hit_test_selection_handle(self._edit_rect, self.mapFromGlobal(QCursor.pos())))
        self.update()

    def _finish_with_rect(self, rect: QRect) -> None:
        """Crop `rect` from the frozen desktop and accept the dialog."""
        self._crop = crop_pixmap_from_logical_rect(self._frozen, rect)
        if self._crop is None or self._crop.isNull():
            self._crop = None
            self.reject()
            return
        self.accept()

    def _paint_edit_handles(self, painter: QPainter, rect: QRect) -> None:
        half = _HANDLE_DRAW // 2
        points = [
            rect.topLeft(),
            QPoint(rect.center().x(), rect.top()),
            rect.topRight(),
            QPoint(rect.left(), rect.center().y()),
            QPoint(rect.right(), rect.center().y()),
            rect.bottomLeft(),
            QPoint(rect.center().x(), rect.bottom()),
            rect.bottomRight(),
        ]
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_HANDLE_FILL)
        for point in points:
            painter.drawRect(point.x() - half, point.y() - half, _HANDLE_DRAW, _HANDLE_DRAW)

    def _selection_rect(self) -> QRect | None:
        if self._origin is None or self._current is None:
            return None
        return QRect(self._origin, self._current).normalized()

    def _update_snap_at(self, pos: QPoint) -> None:
        """Refresh the hover snap rectangle for `pos` and repaint when it changes."""
        if self._edit_rect is not None:
            return
        new_snap = snap_rect_at_point(pos, self._window_rects_local)
        if new_snap == self._snap_rect:
            return
        self._snap_rect = new_snap
        self.update()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, frozen: QPixmap, geometry: QRect, *, with_shutter_controls: bool = False, window_rects: Sequence[QRect] | None = None) -> None
```

Create a fullscreen overlay for region selection, displaying the frozen desktop.

Args:

- `frozen` (`QPixmap`): Stitched screenshot of the virtual desktop to display as background.
- `geometry` (`QRect`): The target geometry in global (screen) coordinates for overlay placement.
- `with_shutter_controls` (`bool`): If `True`, embed shutter controls on the left edge.
- `window_rects` (`Sequence[QRect] | None`): Snappable window bounds in global logical pixels.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        frozen: QPixmap,
        geometry: QRect,
        *,
        with_shutter_controls: bool = False,
        window_rects: Sequence[QRect] | None = None,
    ) -> None:
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
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setGeometry(geometry)

        self._frozen = frozen
        self._origin: QPoint | None = None
        self._current: QPoint | None = None
        self._crop: QImage | None = None
        self._dragging = False
        self._snap_rect: QRect | None = None
        self._panel: ShutterPanel | None = None
        self._edit_rect: QRect | None = None
        self._edit_handle: HandleKind | None = None
        self._edit_press_pos: QPoint | None = None
        self._edit_press_rect: QRect | None = None
        origin = geometry.topLeft()
        self._window_rects_local = [
            rect.translated(-origin.x(), -origin.y()).intersected(QRect(0, 0, geometry.width(), geometry.height()))
            for rect in (window_rects or ())
        ]
        self._window_rects_local = [rect for rect in self._window_rects_local if rect.isValid() and not rect.isEmpty()]

        if with_shutter_controls:
            panel = ShutterPanel(self)
            panel.set_mode("selection")
            panel.triggered.connect(lambda: self.done(RESULT_TOGGLE_ARRANGE))
            panel.cancelled.connect(self.reject)
            panel.geometry_changed.connect(lambda: position_panel_on_left_edge(panel, geometry))
            position_panel_on_left_edge(panel, geometry)
            panel.show()
            self._panel = panel
```

</details>

### ⚙️ Method `cropped_image (property)`

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

### ⚙️ Method `event`

```python
def event(self, event: QEvent) -> bool
```

Accept Escape as a shortcut override so it is not stolen by other Windows.

Args:

- `event` (`QEvent`): The event being delivered to the overlay.

<details>
<summary>Code:</summary>

```python
def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.ShortcutOverride and _is_escape_key(event):
            event.accept()
            return True
        return super().event(event)
```

</details>

### ⚙️ Method `hideEvent`

```python
def hideEvent(self, event: QHideEvent) -> None
```

Release the keyboard grab when the overlay is hidden.

<details>
<summary>Code:</summary>

```python
def hideEvent(self, event: QHideEvent) -> None:  # noqa: N802
        release_screenshot_keyboard(self)
        super().hideEvent(event)
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Enter confirms an editable frame; Escape clears it or cancels capture.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter} and self._edit_rect is not None:
            self._finish_with_rect(self._edit_rect)
            event.accept()
            return
        if event.key() == Qt.Key.Key_Escape:
            if self._edit_rect is not None:
                self._clear_edit_rect()
                event.accept()
                return
            self._crop = None
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `mouseDoubleClickEvent`

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None
```

Double-click confirms the editable selection frame.

<details>
<summary>Code:</summary>

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton or self._edit_rect is None:
            return
        if self._edit_rect.contains(event.position().toPoint()):
            self._finish_with_rect(self._edit_rect)
            event.accept()
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Update snap, free-drag selection, or editable frame move/resize.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        pos = event.position().toPoint()

        if self._edit_rect is not None:
            if self._edit_handle is not None and self._edit_press_pos is not None and self._edit_press_rect is not None:
                self._edit_rect = transform_selection_rect(
                    self._edit_press_rect,
                    self._edit_handle,
                    self._edit_press_pos,
                    pos,
                    bounds=self.rect(),
                    min_size=_MIN_SELECTION,
                )
                self.update()
                return
            self._apply_edit_cursor(hit_test_selection_handle(self._edit_rect, pos))
            return

        if self._origin is None:
            self._update_snap_at(pos)
            return

        self._current = pos
        if not self._dragging:
            delta = pos - self._origin
            if abs(delta.x()) >= _DRAG_THRESHOLD or abs(delta.y()) >= _DRAG_THRESHOLD:
                self._dragging = True
                self._snap_rect = None
        self.update()
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Start free selection, snap capture, or begin editing an adjustable frame.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.position().toPoint()

        if self._edit_rect is not None:
            handle = hit_test_selection_handle(self._edit_rect, pos)
            if handle is None:
                return
            self._edit_handle = handle
            self._edit_press_pos = pos
            self._edit_press_rect = QRect(self._edit_rect)
            self._apply_edit_cursor(handle)
            return

        self._origin = pos
        self._current = pos
        self._dragging = False
        self._update_snap_at(pos)
        self.update()
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Finish free selection, enter edit mode, or end a frame edit drag.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if self._edit_rect is not None:
            self._edit_handle = None
            self._edit_press_pos = None
            self._edit_press_rect = None
            self._apply_edit_cursor(hit_test_selection_handle(self._edit_rect, event.position().toPoint()))
            self.update()
            return

        if self._origin is None:
            return

        pos = event.position().toPoint()
        self._current = pos

        capture_rect: QRect | None
        if self._dragging:
            capture_rect = self._selection_rect()
        elif self._snap_rect is not None:
            capture_rect = QRect(self._snap_rect)
        else:
            capture_rect = None

        was_dragging = self._dragging
        self._origin = None
        self._current = None
        self._dragging = False

        if capture_rect is None:
            self._update_snap_at(pos)
            self.update()
            return

        if capture_rect.width() < _MIN_SELECTION or capture_rect.height() < _MIN_SELECTION:
            self._crop = None
            if was_dragging:
                self.reject()
            else:
                self._update_snap_at(pos)
                self.update()
            return

        if self._adjust_mode_enabled():
            self._enter_edit_rect(capture_rect)
            return

        self._finish_with_rect(capture_rect)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Draw frozen desktop, dim overlay, selection/snap, and edit handles.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=False)
        painter.drawPixmap(self.rect(), self._frozen)
        painter.fillRect(self.rect(), _DIM_COLOR)

        rect = self._active_highlight_rect()
        if rect is not None and rect.isValid():
            source = logical_rect_to_pixel_rect(rect, pixmap_device_pixel_ratio(self._frozen))
            painter.drawPixmap(rect, self._frozen, source)
            pen = QPen(_BORDER_COLOR, _BORDER_WIDTH)
            painter.setPen(pen)
            painter.drawRect(rect.adjusted(0, 0, -1, -1))
            if self._edit_rect is not None:
                self._paint_edit_handles(painter, rect)
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

Take keyboard focus so Escape cancels capture on Tool overlays.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        claim_screenshot_keyboard(self)
        self._update_snap_at(self.mapFromGlobal(QCursor.pos()))
```

</details>
