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
  - [⚙️ Method `cancel_crop`](#%EF%B8%8F-method-cancel_crop)
  - [⚙️ Method `clear_selection`](#%EF%B8%8F-method-clear_selection)
  - [⚙️ Method `confirm_crop`](#%EF%B8%8F-method-confirm_crop)
  - [⚙️ Method `crop_mode (property)`](#%EF%B8%8F-method-crop_mode-property)
  - [⚙️ Method `crop_pending (property)`](#%EF%B8%8F-method-crop_pending-property)
  - [⚙️ Method `delete_selected`](#%EF%B8%8F-method-delete_selected)
  - [⚙️ Method `finish_text_at`](#%EF%B8%8F-method-finish_text_at)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `keyReleaseEvent`](#%EF%B8%8F-method-keyreleaseevent)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `sample_color_at`](#%EF%B8%8F-method-sample_color_at)
  - [⚙️ Method `selected_index (property)`](#%EF%B8%8F-method-selected_index-property)
  - [⚙️ Method `set_document`](#%EF%B8%8F-method-set_document)
  - [⚙️ Method `set_style`](#%EF%B8%8F-method-set_style)
  - [⚙️ Method `set_tool`](#%EF%B8%8F-method-set_tool)
  - [⚙️ Method `tool (property)`](#%EF%B8%8F-method-tool-property)
  - [⚙️ Method `wheelEvent`](#%EF%B8%8F-method-wheelevent)
  - [⚙️ Method `zoom (property)`](#%EF%B8%8F-method-zoom-property)
  - [⚙️ Method `zoom_by`](#%EF%B8%8F-method-zoom_by)

</details>

## 🏛️ Class `ScreenshotPreviewCanvas`

```python
class ScreenshotPreviewCanvas(QWidget)
```

Show an image fitted with aspect ratio; Ctrl+wheel zooms; middle-drag pans.

Left-drag draws with the active [`AnnotationTool`](annotations.g.md#%EF%B8%8F-class-annotationtool) when a document is attached.
Crop mode uses the same dimmed blue selection frame as region capture.

<details>
<summary>Code:</summary>

```python
class ScreenshotPreviewCanvas(QWidget):

    document_changed = Signal()
    crop_mode_changed = Signal(bool)
    crop_pending_changed = Signal(bool)
    color_hovered = Signal(object)
    color_picked = Signal(QColor)
    text_requested = Signal(QPointF)

    def __init__(self, image: QImage, parent: QWidget | None = None) -> None:
        """Create a canvas for `image` at fit zoom."""
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._pixmap = QPixmap.fromImage(image)
        self._zoom = 1.0
        self._offset = QPointF()
        self._pan_start: QPointF | None = None
        self._pan_origin = QPointF()
        self._document: AnnotationDocument | None = None
        self._tool = AnnotationTool.NONE
        self._style = AnnotationStyle()
        self._draw_start: QPointF | None = None
        self._draw_current: QPointF | None = None
        self._selected_index: int | None = None
        self._edit_handle: AnnotationHandle | None = None
        self._edit_origin_points: list[QPointF] | None = None
        self._edit_press: QPointF | None = None
        self._edit_current: QPointF | None = None
        self._edit_history_saved = False
        self._crop_pending = False
        self._crop_rect: QRect | None = None
        self._crop_origin: QPoint | None = None
        self._crop_current: QPoint | None = None
        self._crop_dragging = False
        self._crop_edit_handle: HandleKind | None = None
        self._crop_press_pos: QPoint | None = None
        self._crop_press_rect: QRect | None = None
        self._snap_x_edges: list[int] = []
        self._snap_y_edges: list[int] = []
        self._snap_x_guide: float | None = None
        self._snap_y_guide: float | None = None
        self._eyedrop_hover: tuple[QPointF, QColor] | None = None

    def cancel_crop(self) -> None:
        """Discard crop selection and leave crop mode."""
        was_crop = self._tool == AnnotationTool.CROP or self._crop_pending or self._crop_rect is not None
        if self._document is not None:
            self._document.cancel_draft()
        self._clear_crop_state()
        self._clear_edit_state()
        self._selected_index = None
        self._tool = AnnotationTool.NONE
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._refresh_pixmap()
        if was_crop:
            self.crop_mode_changed.emit(False)  # noqa: FBT003
        self.crop_pending_changed.emit(False)  # noqa: FBT003

    def clear_selection(self) -> bool:
        """Deselect the current annotation. Return whether anything changed."""
        if self._selected_index is None and self._edit_handle is None:
            return False
        self._clear_edit_state()
        self._selected_index = None
        self.update()
        return True

    def confirm_crop(self) -> bool:
        """Apply the pending crop rectangle. Return whether it succeeded."""
        document = self._document
        rect = self._crop_rect
        if document is None or rect is None or rect.width() < _MIN_CROP or rect.height() < _MIN_CROP:
            self.cancel_crop()
            return False
        identity = rect == self._image_bounds()
        applied = False if identity else document.apply_crop(QRectF(rect))
        self._clear_crop_state()
        self._tool = AnnotationTool.NONE
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.crop_mode_changed.emit(False)  # noqa: FBT003
        self.crop_pending_changed.emit(False)  # noqa: FBT003
        if identity:
            self.update()
            return True
        if not applied:
            self.update()
            return False
        self._refresh_pixmap()
        self._rebuild_snap_edges()
        self.document_changed.emit()
        return True

    @property
    def crop_mode(self) -> bool:
        """Whether the canvas is in crop selection / edit mode."""
        return self._tool == AnnotationTool.CROP

    @property
    def crop_pending(self) -> bool:
        """Whether a crop rectangle is waiting for confirmation."""
        return self._crop_pending

    def delete_selected(self) -> bool:
        """Delete the selected annotation. Return whether it was removed."""
        document = self._document
        index = self._selected_index
        if document is None or index is None:
            return False
        self._clear_edit_state()
        if not document.delete_at(index):
            return False
        self._selected_index = None
        self.update()
        self.document_changed.emit()
        return True

    def finish_text_at(self, image_pos: QPointF, text: str) -> None:
        """Commit a text annotation at `image_pos` after the user entered `text`."""
        if self._document is None or not text.strip():
            return
        self._document.begin_draft(
            Annotation(
                tool=AnnotationTool.TEXT,
                points=[QPointF(image_pos)],
                text=text.strip(),
                style=AnnotationStyle(color=QColor(self._style.color), width=self._style.width),
            )
        )
        if self._document.commit_draft():
            self._selected_index = len(self._document.annotations) - 1
            self.update()
            self.document_changed.emit()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Delete or deselect a shape; re-apply Shift constraints while dragging."""
        if (
            event.key() in {Qt.Key.Key_Delete, Qt.Key.Key_Backspace}
            and self._tool != AnnotationTool.CROP
            and self.delete_selected()
        ):
            event.accept()
            return
        if event.key() == Qt.Key.Key_Escape and self._tool != AnnotationTool.CROP and self.clear_selection():
            event.accept()
            return
        if (
            event.key() == Qt.Key.Key_Shift
            and not event.isAutoRepeat()
            and (self._refresh_constrained_edit(shift=True) or self._refresh_constrained_draft(shift=True))
        ):
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Drop Shift constraints when the key is released during a drag."""
        if (
            event.key() == Qt.Key.Key_Shift
            and not event.isAutoRepeat()
            and (self._refresh_constrained_edit(shift=False) or self._refresh_constrained_draft(shift=False))
        ):
            event.accept()
            return
        super().keyReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Pan, edit a selected shape, update a draft, or refresh the hover cursor."""
        if self._pan_start is not None:
            delta = event.position() - self._pan_start
            self._offset = self._pan_origin + delta
            self.update()
            event.accept()
            return

        if self._tool == AnnotationTool.CROP:
            self._crop_mouse_move(event.position())
            event.accept()
            return

        if self._tool == AnnotationTool.EYEDROPPER:
            self._eyedrop_mouse_move(event.position())
            event.accept()
            return

        image_pos = self._widget_to_image(event.position())
        if self._edit_handle is not None and image_pos is not None:
            self._apply_annotation_drag(image_pos, shift=_shift_pressed(event.modifiers()))
            event.accept()
            return

        if self._draw_start is not None and self._document is not None:
            if image_pos is None:
                event.accept()
                return
            start = self._draw_start
            if self._document.draft is None:
                delta = image_pos - start
                if abs(delta.x()) < _DRAG_THRESHOLD and abs(delta.y()) < _DRAG_THRESHOLD:
                    event.accept()
                    return
                self._begin_shape_draft(start, image_pos)
            draft = self._document.draft
            if draft is None:
                event.accept()
                return
            if draft.tool == AnnotationTool.PEN:
                self._document.append_draft_point(image_pos)
            else:
                self._draw_current = image_pos
                end = self._constrain_and_snap_draft_end(
                    start,
                    image_pos,
                    draft.tool,
                    shift=_shift_pressed(event.modifiers()),
                )
                self._document.update_draft_points([start, end])
            self.update()
            event.accept()
            return
        self._update_hover_cursor(image_pos)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start panning, select/edit a shape, or begin a draft annotation / crop."""
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_start = event.position()
            self._pan_origin = QPointF(self._offset)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool == AnnotationTool.CROP:
            self._crop_mouse_press(event.position())
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool == AnnotationTool.EYEDROPPER:
            color = self.sample_color_at(event.position())
            if color is not None:
                self.color_picked.emit(color)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool != AnnotationTool.NONE:
            image_pos = self._widget_to_image(event.position())
            if image_pos is None or self._document is None:
                event.accept()
                return
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            if self._begin_annotation_edit(image_pos):
                event.accept()
                return
            self._selected_index = None
            snapped = self._snap_pointer(image_pos)
            if self._tool == AnnotationTool.TEXT:
                self.text_requested.emit(snapped)
                event.accept()
                return
            self._draw_start = snapped
            self._draw_current = QPointF(snapped)
            if self._tool == AnnotationTool.PEN:
                self._begin_shape_draft(snapped, snapped)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool == AnnotationTool.NONE:
            image_pos = self._widget_to_image(event.position())
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            if image_pos is not None and self._begin_annotation_edit(image_pos):
                event.accept()
                return
            self.clear_selection()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """End panning, finish a shape edit, or commit the draft annotation / crop drag."""
        if event.button() == Qt.MouseButton.MiddleButton and self._pan_start is not None:
            self._pan_start = None
            self.set_tool(self._tool)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool == AnnotationTool.CROP:
            self._crop_mouse_release(event.position())
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._edit_handle is not None:
            changed = self._edit_history_saved
            self._clear_edit_state()
            if changed:
                self.document_changed.emit()
            self.update()
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._draw_start is not None:
            self._finish_draw(event.position(), shift=_shift_pressed(event.modifiers()))
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        """Draw the fitted pixmap, live annotations, crop frame, and selection chrome."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=True)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        image_rect = self._image_rect()
        if not self._pixmap.isNull():
            painter.drawPixmap(image_rect.toRect(), self._pixmap)

        if self._tool == AnnotationTool.CROP and not image_rect.isEmpty():
            self._paint_crop_overlay(painter, image_rect)
        elif self._document is not None and not image_rect.isEmpty() and self._tool != AnnotationTool.EYEDROPPER:
            self._paint_live_annotations(painter, image_rect)
        if self._tool == AnnotationTool.EYEDROPPER:
            self._paint_eyedrop_preview(painter)
        painter.end()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Repaint when the available fit area changes."""
        super().resizeEvent(event)
        self.update()

    def sample_color_at(self, widget_pos: QPointF) -> QColor | None:
        """Return the visible pixel color under `widget_pos`, or `None` if outside the image."""
        rect = self._image_rect()
        if rect.isEmpty() or self._pixmap.isNull():
            return None
        if widget_pos.x() < rect.left() or widget_pos.x() > rect.right():
            return None
        if widget_pos.y() < rect.top() or widget_pos.y() > rect.bottom():
            return None
        width, height = self._source_size()
        if width <= 0 or height <= 0:
            return None
        x = min(max(0, int((widget_pos.x() - rect.left()) / rect.width() * width)), width - 1)
        y = min(max(0, int((widget_pos.y() - rect.top()) / rect.height() * height)), height - 1)
        image = self._pixmap.toImage()
        if x >= image.width() or y >= image.height():
            return None
        return QColor(image.pixelColor(x, y))

    @property
    def selected_index(self) -> int | None:
        """Index of the selected annotation, or `None`."""
        return self._selected_index

    def set_document(self, document: AnnotationDocument | None) -> None:
        """Attach an annotation document; canvas displays its rendered image."""
        self._clear_edit_state()
        self._selected_index = None
        self._document = document
        self._rebuild_snap_edges()
        self._refresh_pixmap()

    def set_style(self, color: QColor | None = None, width: float | None = None) -> None:
        """Update the stroke color and/or width for new annotations."""
        if color is not None:
            self._style.color = QColor(color)
        if width is not None:
            self._style.width = max(1.0, width)

    def set_tool(self, tool: AnnotationTool) -> None:
        """Select the drawing tool (`NONE` keeps view-only left-click)."""
        previous_crop = self._tool == AnnotationTool.CROP
        previous_eyedrop = self._tool == AnnotationTool.EYEDROPPER
        if previous_crop and tool != AnnotationTool.CROP:
            self._clear_crop_state()
            self.crop_pending_changed.emit(False)  # noqa: FBT003
        self._tool = tool
        self._draw_start = None
        self._draw_current = None
        self._clear_edit_state()
        if tool != AnnotationTool.EYEDROPPER:
            self._eyedrop_hover = None
        if tool == AnnotationTool.CROP:
            self._selected_index = None
        if tool == AnnotationTool.EYEDROPPER:
            self._selected_index = None
        if self._document is not None and tool != AnnotationTool.CROP:
            self._document.cancel_draft()
        if tool == AnnotationTool.CROP:
            self._rebuild_snap_edges()
            if previous_crop:
                if self._crop_pending:
                    self.setCursor(Qt.CursorShape.SizeAllCursor)
                else:
                    self.setCursor(Qt.CursorShape.CrossCursor)
            else:
                self._select_full_image_crop()
            self.crop_mode_changed.emit(True)  # noqa: FBT003
        else:
            if previous_crop:
                self.crop_mode_changed.emit(False)  # noqa: FBT003
            if tool == AnnotationTool.NONE:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            elif tool == AnnotationTool.TEXT:
                self.setCursor(Qt.CursorShape.IBeamCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)
        if tool == AnnotationTool.CROP or previous_crop or tool == AnnotationTool.EYEDROPPER or previous_eyedrop:
            self._refresh_pixmap()
        else:
            self.update()

    @property
    def tool(self) -> AnnotationTool:
        """Active annotation tool."""
        return self._tool

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

    def _active_crop_rect(self) -> QRect | None:
        if self._crop_pending and self._crop_rect is not None:
            return self._crop_rect
        if self._crop_origin is not None and self._crop_current is not None and self._crop_dragging:
            return self._crop_drag_rect()
        return self._crop_rect

    def _annotation_snap_guides(self, *, exclude_index: int | None = None) -> tuple[list[float], list[float]]:
        document = self._document
        if document is None:
            return [], []
        bounds = self._image_bounds()
        frame = None
        if bounds.isValid() and not bounds.isEmpty():
            frame = QRectF(QPointF(bounds.left(), bounds.top()), QPointF(bounds.right(), bounds.bottom()))
        return collect_annotation_guides(document.annotations, exclude_index=exclude_index, bounds=frame)

    def _apply_annotation_drag(self, image_pos: QPointF, *, shift: bool) -> None:
        document = self._document
        index = self._selected_index
        handle = self._edit_handle
        origin = self._edit_origin_points
        press = self._edit_press
        if document is None or index is None or handle is None or origin is None or press is None:
            return
        if index < 0 or index >= len(document.annotations):
            return
        annotation = document.annotations[index]
        self._edit_current = QPointF(image_pos)
        if not self._edit_history_saved:
            document.save_undo_checkpoint()
            self._edit_history_saved = True
        points = apply_annotation_edit(annotation, handle, origin, press, image_pos, shift=shift)
        xs, ys = self._annotation_snap_guides(exclude_index=index)
        snapped = snap_annotation_edit(
            annotation,
            handle,
            points,
            xs,
            ys,
            threshold=_EDGE_SNAP_THRESHOLD,
            shift=shift,
        )
        self._snap_x_guide = snapped.x_guide
        self._snap_y_guide = snapped.y_guide
        document.update_annotation_points(index, snapped.points)
        self.update()

    def _begin_annotation_edit(self, image_pos: QPointF) -> bool:
        document = self._document
        if document is None or not document.annotations:
            return False
        hit = hit_test_topmost(
            document.annotations,
            image_pos,
            handle_size=self._handle_size_image(),
            prefer_tool=self._prefer_tool(),
            selected_index=self._selected_index,
        )
        if hit is None:
            return False
        index, handle = hit
        self._selected_index = index
        self._edit_handle = handle
        self._edit_origin_points = [QPointF(p) for p in document.annotations[index].points]
        self._edit_press = QPointF(image_pos)
        self._edit_current = QPointF(image_pos)
        self._edit_history_saved = False
        self.update()
        return True

    def _begin_shape_draft(self, start: QPointF, current: QPointF) -> None:
        if self._document is None:
            return
        self._document.begin_draft(
            Annotation(
                tool=self._tool,
                points=[QPointF(start), QPointF(current)],
                style=AnnotationStyle(color=QColor(self._style.color), width=self._style.width),
            )
        )

    def _clear_crop_state(self) -> None:
        self._crop_pending = False
        self._crop_rect = None
        self._crop_origin = None
        self._crop_current = None
        self._crop_dragging = False
        self._crop_edit_handle = None
        self._crop_press_pos = None
        self._crop_press_rect = None

    def _clear_edit_state(self) -> None:
        self._edit_handle = None
        self._edit_origin_points = None
        self._edit_press = None
        self._edit_current = None
        self._edit_history_saved = False
        self._clear_snap_guides()

    def _clear_snap_guides(self) -> None:
        self._snap_x_guide = None
        self._snap_y_guide = None

    def _constrain_and_snap_draft_end(
        self,
        start: QPointF,
        image_pos: QPointF,
        tool: AnnotationTool,
        *,
        shift: bool,
    ) -> QPointF:
        end = constrain_shape_end(tool, start, image_pos, shift=shift)
        xs, ys = self._annotation_snap_guides()
        snapped, x_guide, y_guide = snap_shape_end(
            tool,
            start,
            end,
            xs,
            ys,
            threshold=_EDGE_SNAP_THRESHOLD,
            shift=shift,
        )
        self._snap_x_guide = x_guide
        self._snap_y_guide = y_guide
        return snapped

    def _crop_drag_rect(self) -> QRect | None:
        if self._crop_origin is None or self._crop_current is None:
            return None
        bounds = self._image_bounds()
        rect = QRect(self._crop_origin, self._crop_current).normalized().intersected(bounds)
        return snap_all_edges(
            rect,
            self._snap_x_edges,
            self._snap_y_edges,
            threshold=_EDGE_SNAP_THRESHOLD,
            bounds=bounds,
            min_size=_MIN_CROP,
        )

    def _crop_mouse_move(self, widget_pos: QPointF) -> None:
        image_pos = self._widget_to_image_point(widget_pos)
        if image_pos is None:
            return

        if self._crop_pending and self._crop_rect is not None:
            if (
                self._crop_edit_handle is not None
                and self._crop_press_pos is not None
                and self._crop_press_rect is not None
            ):
                bounds = self._image_bounds()
                transformed = transform_selection_rect(
                    self._crop_press_rect,
                    self._crop_edit_handle,
                    self._crop_press_pos,
                    image_pos,
                    bounds=bounds,
                    min_size=_MIN_CROP,
                )
                self._crop_rect = snap_rect_to_edges(
                    transformed,
                    self._crop_edit_handle,
                    self._snap_x_edges,
                    self._snap_y_edges,
                    threshold=_EDGE_SNAP_THRESHOLD,
                    bounds=bounds,
                    min_size=_MIN_CROP,
                )
                self.update()
                return
            handle = hit_test_selection_handle(self._crop_rect, image_pos)
            self.setCursor(getattr(Qt.CursorShape, cursor_for_handle(handle)))
            return

        if self._crop_origin is None:
            return
        self._crop_current = image_pos
        if not self._crop_dragging:
            delta = image_pos - self._crop_origin
            if abs(delta.x()) >= _DRAG_THRESHOLD or abs(delta.y()) >= _DRAG_THRESHOLD:
                self._crop_dragging = True
        self.update()

    def _crop_mouse_press(self, widget_pos: QPointF) -> None:
        image_pos = self._widget_to_image_point(widget_pos)
        if image_pos is None:
            return

        if self._crop_pending and self._crop_rect is not None:
            handle = hit_test_selection_handle(self._crop_rect, image_pos)
            if handle is None:
                # Start a new selection.
                self._crop_pending = False
                self.crop_pending_changed.emit(False)  # noqa: FBT003
                self._crop_rect = None
            else:
                self._crop_edit_handle = handle
                self._crop_press_pos = image_pos
                self._crop_press_rect = QRect(self._crop_rect)
                self.setCursor(getattr(Qt.CursorShape, cursor_for_handle(handle)))
                return

        self._crop_origin = image_pos
        self._crop_current = image_pos
        self._crop_dragging = False
        self.update()

    def _crop_mouse_release(self, widget_pos: QPointF) -> None:
        if self._crop_pending and self._crop_edit_handle is not None:
            self._crop_edit_handle = None
            self._crop_press_pos = None
            self._crop_press_rect = None
            image_pos = self._widget_to_image_point(widget_pos)
            if image_pos is not None and self._crop_rect is not None:
                handle = hit_test_selection_handle(self._crop_rect, image_pos)
                self.setCursor(getattr(Qt.CursorShape, cursor_for_handle(handle)))
            self.update()
            return

        if self._crop_origin is None:
            return
        image_pos = self._widget_to_image_point(widget_pos)
        if image_pos is not None:
            self._crop_current = image_pos
        rect = self._crop_drag_rect()
        self._crop_origin = None
        self._crop_current = None
        self._crop_dragging = False
        if rect is None or rect.width() < _MIN_CROP or rect.height() < _MIN_CROP:
            self._crop_rect = None
            self._crop_pending = False
            self.crop_pending_changed.emit(False)  # noqa: FBT003
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.update()
            return
        self._crop_rect = rect
        self._crop_pending = True
        self.crop_pending_changed.emit(True)  # noqa: FBT003
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.update()

    def _eyedrop_mouse_move(self, widget_pos: QPointF) -> None:
        color = self.sample_color_at(widget_pos)
        self._eyedrop_hover = (QPointF(widget_pos), color) if color is not None else None
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.color_hovered.emit(color)
        self.update()

    def _finish_draw(self, widget_pos: QPointF, *, shift: bool) -> None:
        document = self._document
        start = self._draw_start
        self._draw_start = None
        self._draw_current = None
        if document is None or start is None:
            self._clear_snap_guides()
            return
        image_pos = self._widget_to_image(widget_pos)
        if image_pos is not None and document.draft is not None:
            if document.draft.tool == AnnotationTool.PEN:
                document.append_draft_point(image_pos)
            else:
                end = self._constrain_and_snap_draft_end(
                    start,
                    image_pos,
                    document.draft.tool,
                    shift=shift,
                )
                document.update_draft_points([start, end])
        self._clear_snap_guides()
        if document.commit_draft():
            self._selected_index = len(document.annotations) - 1
            self.update()
            self.document_changed.emit()
        else:
            self.update()

    def _fitted_size(self) -> QSizeF:
        width, height = self._source_size()
        if width <= 0 or height <= 0 or self.width() <= 0 or self.height() <= 0:
            return QSizeF()
        fitted = QSize(width, height).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        display_w = min(fitted.width(), width)
        display_h = min(fitted.height(), height)
        return QSizeF(display_w * self._zoom, display_h * self._zoom)

    def _handle_size_image(self) -> float:
        image_rect = self._image_rect()
        width, _height = self._source_size()
        if image_rect.isEmpty() or width <= 0:
            return 8.0
        scale = image_rect.width() / width
        return max(6.0, 8.0 / max(scale, 0.01))

    def _image_bounds(self) -> QRect:
        width, height = self._source_size()
        if width <= 0 or height <= 0:
            return QRect()
        return QRect(0, 0, width, height)

    def _image_rect(self) -> QRectF:
        size = self._fitted_size()
        if size.isEmpty():
            return QRectF()
        center = QPointF(self.rect().center()) + self._offset
        return QRectF(center.x() - size.width() / 2, center.y() - size.height() / 2, size.width(), size.height())

    def _image_to_widget_rect(self, rect: QRect, image_rect: QRectF) -> QRect:
        width, height = self._source_size()
        if width <= 0 or height <= 0 or image_rect.isEmpty():
            return QRect()
        scale_x = image_rect.width() / width
        scale_y = image_rect.height() / height
        left = round(image_rect.left() + rect.left() * scale_x)
        top = round(image_rect.top() + rect.top() * scale_y)
        right = round(image_rect.left() + (rect.right() + 1) * scale_x) - 1
        bottom = round(image_rect.top() + (rect.bottom() + 1) * scale_y) - 1
        return QRect(QPoint(left, top), QPoint(right, bottom)).normalized()

    def _paint_crop_overlay(self, painter: QPainter, image_rect: QRectF) -> None:
        bounds = image_rect.toRect()
        crop = self._active_crop_rect()
        clear_widget: QRect | None = None
        source: QRect | None = None
        if crop is not None and crop.isValid() and not crop.isEmpty():
            clear_widget = self._image_to_widget_rect(crop, image_rect)
            source = crop
        paint_selection_frame(
            painter,
            bounds,
            clear_widget,
            pixmap=self._pixmap if clear_widget is not None else None,
            pixmap_source=source,
            show_handles=bool(self._crop_pending and clear_widget is not None),
            border_width=SELECTION_BORDER_WIDTH,
        )

    def _paint_eyedrop_preview(self, painter: QPainter) -> None:
        hover = self._eyedrop_hover
        if hover is None:
            return
        pos, color = hover
        size = 32
        x = int(pos.x()) + 18
        y = int(pos.y()) + 18
        if x + size > self.width() - 1:
            x = int(pos.x()) - size - 8
        if y + size > self.height() - 1:
            y = int(pos.y()) - size - 8
        box = QRect(max(0, x), max(0, y), size, size)
        painter.fillRect(box, color)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawRect(box.adjusted(1, 1, -1, -1))
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawRect(box)

    def _paint_live_annotations(self, painter: QPainter, image_rect: QRectF) -> None:
        document = self._document
        if document is None or self._pixmap.isNull():
            return
        painter.save()
        painter.translate(image_rect.topLeft())
        width, height = self._source_size()
        scale_x = image_rect.width() / max(1, width)
        scale_y = image_rect.height() / max(1, height)
        painter.scale(scale_x, scale_y)
        for item in document.annotations:
            paint_annotation(painter, item)
        if document.draft is not None:
            paint_annotation(painter, document.draft)
        index = self._selected_index
        if index is not None and 0 <= index < len(document.annotations):
            paint_annotation_selection(
                painter,
                document.annotations[index],
                handle_size=self._handle_size_image(),
            )
        self._paint_snap_guides(painter, width, height)
        painter.restore()

    def _paint_snap_guides(self, painter: QPainter, width: int, height: int) -> None:
        if self._snap_x_guide is None and self._snap_y_guide is None:
            return
        pen = QPen(_SNAP_GUIDE_COLOR, 1.0)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        painter.setPen(pen)
        if self._snap_x_guide is not None:
            painter.drawLine(QPointF(self._snap_x_guide, 0.0), QPointF(self._snap_x_guide, float(height)))
        if self._snap_y_guide is not None:
            painter.drawLine(QPointF(0.0, self._snap_y_guide), QPointF(float(width), self._snap_y_guide))

    def _prefer_tool(self) -> AnnotationTool | None:
        if self._tool in {AnnotationTool.CROP, AnnotationTool.NONE, AnnotationTool.EYEDROPPER}:
            return None
        return self._tool

    def _rebuild_snap_edges(self) -> None:
        bounds = self._image_bounds()
        self._snap_x_edges, self._snap_y_edges = collect_edge_guides((), bounds)

    def _refresh_constrained_draft(self, *, shift: bool) -> bool:
        """Recompute the live shape from the last pointer using the Shift state."""
        document = self._document
        start = self._draw_start
        current = self._draw_current
        if document is None or start is None or current is None or document.draft is None:
            return False
        if document.draft.tool == AnnotationTool.PEN:
            return False
        end = self._constrain_and_snap_draft_end(start, current, document.draft.tool, shift=shift)
        document.update_draft_points([start, end])
        self.update()
        return True

    def _refresh_constrained_edit(self, *, shift: bool) -> bool:
        """Recompute the live edit from the last pointer using the Shift state."""
        current = self._edit_current
        if self._edit_handle is None or current is None:
            return False
        self._apply_annotation_drag(current, shift=shift)
        return True

    def _refresh_pixmap(self) -> None:
        if self._document is None:
            self.update()
            return
        image = (
            self._document.render(include_draft=False)
            if self._tool in {AnnotationTool.CROP, AnnotationTool.EYEDROPPER}
            else self._document.base_image
        )
        self._pixmap = QPixmap.fromImage(image)
        self.update()

    def _select_full_image_crop(self) -> None:
        bounds = self._image_bounds()
        if not bounds.isValid() or bounds.isEmpty() or bounds.width() < _MIN_CROP or bounds.height() < _MIN_CROP:
            self.setCursor(Qt.CursorShape.CrossCursor)
            return
        self._crop_rect = QRect(bounds)
        self._crop_pending = True
        self._crop_origin = None
        self._crop_current = None
        self._crop_dragging = False
        self._crop_edit_handle = None
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.crop_pending_changed.emit(True)  # noqa: FBT003

    def _snap_pointer(self, image_pos: QPointF, *, exclude_index: int | None = None) -> QPointF:
        xs, ys = self._annotation_snap_guides(exclude_index=exclude_index)
        snapped, x_guide, y_guide = snap_point(image_pos, xs, ys, threshold=_EDGE_SNAP_THRESHOLD)
        self._snap_x_guide = x_guide
        self._snap_y_guide = y_guide
        return snapped

    def _source_size(self) -> tuple[int, int]:
        if self._document is not None and not self._document.base_image.isNull():
            image = self._document.base_image
            return image.width(), image.height()
        if self._pixmap.isNull():
            return 0, 0
        return self._pixmap.width(), self._pixmap.height()

    def _update_hover_cursor(self, image_pos: QPointF | None) -> None:
        if image_pos is None or self._document is None:
            return
        hit = hit_test_topmost(
            self._document.annotations,
            image_pos,
            handle_size=self._handle_size_image(),
            prefer_tool=self._prefer_tool(),
            selected_index=self._selected_index,
        )
        if hit is not None:
            self.setCursor(getattr(Qt.CursorShape, cursor_for_annotation_handle(hit[1])))
            return
        if self._tool == AnnotationTool.NONE:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif self._tool == AnnotationTool.TEXT:
            self.setCursor(Qt.CursorShape.IBeamCursor)
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)

    def _widget_to_image(self, pos: QPointF) -> QPointF | None:
        rect = self._image_rect()
        width, height = self._source_size()
        if rect.isEmpty() or width <= 0 or height <= 0:
            return None
        x = min(max(pos.x(), rect.left()), rect.right())
        y = min(max(pos.y(), rect.top()), rect.bottom())
        rel_x = (x - rect.left()) / rect.width()
        rel_y = (y - rect.top()) / rect.height()
        return QPointF(rel_x * width, rel_y * height)

    def _widget_to_image_point(self, pos: QPointF) -> QPoint | None:
        image_pos = self._widget_to_image(pos)
        if image_pos is None:
            return None
        width, height = self._source_size()
        return QPoint(
            min(max(0, round(image_pos.x())), max(0, width - 1)),
            min(max(0, round(image_pos.y())), max(0, height - 1)),
        )
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
        self._pan_start: QPointF | None = None
        self._pan_origin = QPointF()
        self._document: AnnotationDocument | None = None
        self._tool = AnnotationTool.NONE
        self._style = AnnotationStyle()
        self._draw_start: QPointF | None = None
        self._draw_current: QPointF | None = None
        self._selected_index: int | None = None
        self._edit_handle: AnnotationHandle | None = None
        self._edit_origin_points: list[QPointF] | None = None
        self._edit_press: QPointF | None = None
        self._edit_current: QPointF | None = None
        self._edit_history_saved = False
        self._crop_pending = False
        self._crop_rect: QRect | None = None
        self._crop_origin: QPoint | None = None
        self._crop_current: QPoint | None = None
        self._crop_dragging = False
        self._crop_edit_handle: HandleKind | None = None
        self._crop_press_pos: QPoint | None = None
        self._crop_press_rect: QRect | None = None
        self._snap_x_edges: list[int] = []
        self._snap_y_edges: list[int] = []
        self._snap_x_guide: float | None = None
        self._snap_y_guide: float | None = None
        self._eyedrop_hover: tuple[QPointF, QColor] | None = None
```

</details>

### ⚙️ Method `cancel_crop`

```python
def cancel_crop(self) -> None
```

Discard crop selection and leave crop mode.

<details>
<summary>Code:</summary>

```python
def cancel_crop(self) -> None:
        was_crop = self._tool == AnnotationTool.CROP or self._crop_pending or self._crop_rect is not None
        if self._document is not None:
            self._document.cancel_draft()
        self._clear_crop_state()
        self._clear_edit_state()
        self._selected_index = None
        self._tool = AnnotationTool.NONE
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._refresh_pixmap()
        if was_crop:
            self.crop_mode_changed.emit(False)  # noqa: FBT003
        self.crop_pending_changed.emit(False)  # noqa: FBT003
```

</details>

### ⚙️ Method `clear_selection`

```python
def clear_selection(self) -> bool
```

Deselect the current annotation. Return whether anything changed.

<details>
<summary>Code:</summary>

```python
def clear_selection(self) -> bool:
        if self._selected_index is None and self._edit_handle is None:
            return False
        self._clear_edit_state()
        self._selected_index = None
        self.update()
        return True
```

</details>

### ⚙️ Method `confirm_crop`

```python
def confirm_crop(self) -> bool
```

Apply the pending crop rectangle. Return whether it succeeded.

<details>
<summary>Code:</summary>

```python
def confirm_crop(self) -> bool:
        document = self._document
        rect = self._crop_rect
        if document is None or rect is None or rect.width() < _MIN_CROP or rect.height() < _MIN_CROP:
            self.cancel_crop()
            return False
        identity = rect == self._image_bounds()
        applied = False if identity else document.apply_crop(QRectF(rect))
        self._clear_crop_state()
        self._tool = AnnotationTool.NONE
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.crop_mode_changed.emit(False)  # noqa: FBT003
        self.crop_pending_changed.emit(False)  # noqa: FBT003
        if identity:
            self.update()
            return True
        if not applied:
            self.update()
            return False
        self._refresh_pixmap()
        self._rebuild_snap_edges()
        self.document_changed.emit()
        return True
```

</details>

### ⚙️ Method `crop_mode (property)`

```python
def crop_mode(self) -> bool
```

Whether the canvas is in crop selection / edit mode.

<details>
<summary>Code:</summary>

```python
def crop_mode(self) -> bool:
        return self._tool == AnnotationTool.CROP
```

</details>

### ⚙️ Method `crop_pending (property)`

```python
def crop_pending(self) -> bool
```

Whether a crop rectangle is waiting for confirmation.

<details>
<summary>Code:</summary>

```python
def crop_pending(self) -> bool:
        return self._crop_pending
```

</details>

### ⚙️ Method `delete_selected`

```python
def delete_selected(self) -> bool
```

Delete the selected annotation. Return whether it was removed.

<details>
<summary>Code:</summary>

```python
def delete_selected(self) -> bool:
        document = self._document
        index = self._selected_index
        if document is None or index is None:
            return False
        self._clear_edit_state()
        if not document.delete_at(index):
            return False
        self._selected_index = None
        self.update()
        self.document_changed.emit()
        return True
```

</details>

### ⚙️ Method `finish_text_at`

```python
def finish_text_at(self, image_pos: QPointF, text: str) -> None
```

Commit a text annotation at `image_pos` after the user entered `text`.

<details>
<summary>Code:</summary>

```python
def finish_text_at(self, image_pos: QPointF, text: str) -> None:
        if self._document is None or not text.strip():
            return
        self._document.begin_draft(
            Annotation(
                tool=AnnotationTool.TEXT,
                points=[QPointF(image_pos)],
                text=text.strip(),
                style=AnnotationStyle(color=QColor(self._style.color), width=self._style.width),
            )
        )
        if self._document.commit_draft():
            self._selected_index = len(self._document.annotations) - 1
            self.update()
            self.document_changed.emit()
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Delete or deselect a shape; re-apply Shift constraints while dragging.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if (
            event.key() in {Qt.Key.Key_Delete, Qt.Key.Key_Backspace}
            and self._tool != AnnotationTool.CROP
            and self.delete_selected()
        ):
            event.accept()
            return
        if event.key() == Qt.Key.Key_Escape and self._tool != AnnotationTool.CROP and self.clear_selection():
            event.accept()
            return
        if (
            event.key() == Qt.Key.Key_Shift
            and not event.isAutoRepeat()
            and (self._refresh_constrained_edit(shift=True) or self._refresh_constrained_draft(shift=True))
        ):
            event.accept()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `keyReleaseEvent`

```python
def keyReleaseEvent(self, event: QKeyEvent) -> None
```

Drop Shift constraints when the key is released during a drag.

<details>
<summary>Code:</summary>

```python
def keyReleaseEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if (
            event.key() == Qt.Key.Key_Shift
            and not event.isAutoRepeat()
            and (self._refresh_constrained_edit(shift=False) or self._refresh_constrained_draft(shift=False))
        ):
            event.accept()
            return
        super().keyReleaseEvent(event)
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Pan, edit a selected shape, update a draft, or refresh the hover cursor.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._pan_start is not None:
            delta = event.position() - self._pan_start
            self._offset = self._pan_origin + delta
            self.update()
            event.accept()
            return

        if self._tool == AnnotationTool.CROP:
            self._crop_mouse_move(event.position())
            event.accept()
            return

        if self._tool == AnnotationTool.EYEDROPPER:
            self._eyedrop_mouse_move(event.position())
            event.accept()
            return

        image_pos = self._widget_to_image(event.position())
        if self._edit_handle is not None and image_pos is not None:
            self._apply_annotation_drag(image_pos, shift=_shift_pressed(event.modifiers()))
            event.accept()
            return

        if self._draw_start is not None and self._document is not None:
            if image_pos is None:
                event.accept()
                return
            start = self._draw_start
            if self._document.draft is None:
                delta = image_pos - start
                if abs(delta.x()) < _DRAG_THRESHOLD and abs(delta.y()) < _DRAG_THRESHOLD:
                    event.accept()
                    return
                self._begin_shape_draft(start, image_pos)
            draft = self._document.draft
            if draft is None:
                event.accept()
                return
            if draft.tool == AnnotationTool.PEN:
                self._document.append_draft_point(image_pos)
            else:
                self._draw_current = image_pos
                end = self._constrain_and_snap_draft_end(
                    start,
                    image_pos,
                    draft.tool,
                    shift=_shift_pressed(event.modifiers()),
                )
                self._document.update_draft_points([start, end])
            self.update()
            event.accept()
            return
        self._update_hover_cursor(image_pos)
        super().mouseMoveEvent(event)
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Start panning, select/edit a shape, or begin a draft annotation / crop.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_start = event.position()
            self._pan_origin = QPointF(self._offset)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool == AnnotationTool.CROP:
            self._crop_mouse_press(event.position())
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool == AnnotationTool.EYEDROPPER:
            color = self.sample_color_at(event.position())
            if color is not None:
                self.color_picked.emit(color)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool != AnnotationTool.NONE:
            image_pos = self._widget_to_image(event.position())
            if image_pos is None or self._document is None:
                event.accept()
                return
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            if self._begin_annotation_edit(image_pos):
                event.accept()
                return
            self._selected_index = None
            snapped = self._snap_pointer(image_pos)
            if self._tool == AnnotationTool.TEXT:
                self.text_requested.emit(snapped)
                event.accept()
                return
            self._draw_start = snapped
            self._draw_current = QPointF(snapped)
            if self._tool == AnnotationTool.PEN:
                self._begin_shape_draft(snapped, snapped)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool == AnnotationTool.NONE:
            image_pos = self._widget_to_image(event.position())
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            if image_pos is not None and self._begin_annotation_edit(image_pos):
                event.accept()
                return
            self.clear_selection()
            event.accept()
            return
        super().mousePressEvent(event)
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

End panning, finish a shape edit, or commit the draft annotation / crop drag.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.MiddleButton and self._pan_start is not None:
            self._pan_start = None
            self.set_tool(self._tool)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._tool == AnnotationTool.CROP:
            self._crop_mouse_release(event.position())
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._edit_handle is not None:
            changed = self._edit_history_saved
            self._clear_edit_state()
            if changed:
                self.document_changed.emit()
            self.update()
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._draw_start is not None:
            self._finish_draw(event.position(), shift=_shift_pressed(event.modifiers()))
            event.accept()
            return
        super().mouseReleaseEvent(event)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Draw the fitted pixmap, live annotations, crop frame, and selection chrome.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002, N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=True)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        image_rect = self._image_rect()
        if not self._pixmap.isNull():
            painter.drawPixmap(image_rect.toRect(), self._pixmap)

        if self._tool == AnnotationTool.CROP and not image_rect.isEmpty():
            self._paint_crop_overlay(painter, image_rect)
        elif self._document is not None and not image_rect.isEmpty() and self._tool != AnnotationTool.EYEDROPPER:
            self._paint_live_annotations(painter, image_rect)
        if self._tool == AnnotationTool.EYEDROPPER:
            self._paint_eyedrop_preview(painter)
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

### ⚙️ Method `sample_color_at`

```python
def sample_color_at(self, widget_pos: QPointF) -> QColor | None
```

Return the visible pixel color under `widget_pos`, or `None` if outside the image.

<details>
<summary>Code:</summary>

```python
def sample_color_at(self, widget_pos: QPointF) -> QColor | None:
        rect = self._image_rect()
        if rect.isEmpty() or self._pixmap.isNull():
            return None
        if widget_pos.x() < rect.left() or widget_pos.x() > rect.right():
            return None
        if widget_pos.y() < rect.top() or widget_pos.y() > rect.bottom():
            return None
        width, height = self._source_size()
        if width <= 0 or height <= 0:
            return None
        x = min(max(0, int((widget_pos.x() - rect.left()) / rect.width() * width)), width - 1)
        y = min(max(0, int((widget_pos.y() - rect.top()) / rect.height() * height)), height - 1)
        image = self._pixmap.toImage()
        if x >= image.width() or y >= image.height():
            return None
        return QColor(image.pixelColor(x, y))
```

</details>

### ⚙️ Method `selected_index (property)`

```python
def selected_index(self) -> int | None
```

Index of the selected annotation, or `None`.

<details>
<summary>Code:</summary>

```python
def selected_index(self) -> int | None:
        return self._selected_index
```

</details>

### ⚙️ Method `set_document`

```python
def set_document(self, document: AnnotationDocument | None) -> None
```

Attach an annotation document; canvas displays its rendered image.

<details>
<summary>Code:</summary>

```python
def set_document(self, document: AnnotationDocument | None) -> None:
        self._clear_edit_state()
        self._selected_index = None
        self._document = document
        self._rebuild_snap_edges()
        self._refresh_pixmap()
```

</details>

### ⚙️ Method `set_style`

```python
def set_style(self, color: QColor | None = None, width: float | None = None) -> None
```

Update the stroke color and/or width for new annotations.

<details>
<summary>Code:</summary>

```python
def set_style(self, color: QColor | None = None, width: float | None = None) -> None:
        if color is not None:
            self._style.color = QColor(color)
        if width is not None:
            self._style.width = max(1.0, width)
```

</details>

### ⚙️ Method `set_tool`

```python
def set_tool(self, tool: AnnotationTool) -> None
```

Select the drawing tool (`NONE` keeps view-only left-click).

<details>
<summary>Code:</summary>

```python
def set_tool(self, tool: AnnotationTool) -> None:
        previous_crop = self._tool == AnnotationTool.CROP
        previous_eyedrop = self._tool == AnnotationTool.EYEDROPPER
        if previous_crop and tool != AnnotationTool.CROP:
            self._clear_crop_state()
            self.crop_pending_changed.emit(False)  # noqa: FBT003
        self._tool = tool
        self._draw_start = None
        self._draw_current = None
        self._clear_edit_state()
        if tool != AnnotationTool.EYEDROPPER:
            self._eyedrop_hover = None
        if tool == AnnotationTool.CROP:
            self._selected_index = None
        if tool == AnnotationTool.EYEDROPPER:
            self._selected_index = None
        if self._document is not None and tool != AnnotationTool.CROP:
            self._document.cancel_draft()
        if tool == AnnotationTool.CROP:
            self._rebuild_snap_edges()
            if previous_crop:
                if self._crop_pending:
                    self.setCursor(Qt.CursorShape.SizeAllCursor)
                else:
                    self.setCursor(Qt.CursorShape.CrossCursor)
            else:
                self._select_full_image_crop()
            self.crop_mode_changed.emit(True)  # noqa: FBT003
        else:
            if previous_crop:
                self.crop_mode_changed.emit(False)  # noqa: FBT003
            if tool == AnnotationTool.NONE:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            elif tool == AnnotationTool.TEXT:
                self.setCursor(Qt.CursorShape.IBeamCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)
        if tool == AnnotationTool.CROP or previous_crop or tool == AnnotationTool.EYEDROPPER or previous_eyedrop:
            self._refresh_pixmap()
        else:
            self.update()
```

</details>

### ⚙️ Method `tool (property)`

```python
def tool(self) -> AnnotationTool
```

Active annotation tool.

<details>
<summary>Code:</summary>

```python
def tool(self) -> AnnotationTool:
        return self._tool
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
