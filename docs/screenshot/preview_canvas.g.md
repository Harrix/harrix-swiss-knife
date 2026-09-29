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
  - [⚙️ Method `annotation_style (property)`](#%EF%B8%8F-method-annotation_style-property)
  - [⚙️ Method `begin_text_at`](#%EF%B8%8F-method-begin_text_at)
  - [⚙️ Method `begin_text_edit`](#%EF%B8%8F-method-begin_text_edit)
  - [⚙️ Method `bring_forward`](#%EF%B8%8F-method-bring_forward)
  - [⚙️ Method `bring_to_front`](#%EF%B8%8F-method-bring_to_front)
  - [⚙️ Method `cancel_crop`](#%EF%B8%8F-method-cancel_crop)
  - [⚙️ Method `cancel_text_edit`](#%EF%B8%8F-method-cancel_text_edit)
  - [⚙️ Method `clear_selection`](#%EF%B8%8F-method-clear_selection)
  - [⚙️ Method `commit_text_edit`](#%EF%B8%8F-method-commit_text_edit)
  - [⚙️ Method `confirm_crop`](#%EF%B8%8F-method-confirm_crop)
  - [⚙️ Method `contextMenuEvent`](#%EF%B8%8F-method-contextmenuevent)
  - [⚙️ Method `copy_selected`](#%EF%B8%8F-method-copy_selected)
  - [⚙️ Method `crop_mode (property)`](#%EF%B8%8F-method-crop_mode-property)
  - [⚙️ Method `crop_pending (property)`](#%EF%B8%8F-method-crop_pending-property)
  - [⚙️ Method `cut_selected`](#%EF%B8%8F-method-cut_selected)
  - [⚙️ Method `delete_all`](#%EF%B8%8F-method-delete_all)
  - [⚙️ Method `delete_selected`](#%EF%B8%8F-method-delete_selected)
  - [⚙️ Method `duplicate_selected`](#%EF%B8%8F-method-duplicate_selected)
  - [⚙️ Method `finish_text_at`](#%EF%B8%8F-method-finish_text_at)
  - [⚙️ Method `fit_to_view`](#%EF%B8%8F-method-fit_to_view)
  - [⚙️ Method `flatten_annotations`](#%EF%B8%8F-method-flatten_annotations)
  - [⚙️ Method `is_text_editing (property)`](#%EF%B8%8F-method-is_text_editing-property)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `keyReleaseEvent`](#%EF%B8%8F-method-keyreleaseevent)
  - [⚙️ Method `mouseDoubleClickEvent`](#%EF%B8%8F-method-mousedoubleclickevent)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `paste_clipboard`](#%EF%B8%8F-method-paste_clipboard)
  - [⚙️ Method `redo`](#%EF%B8%8F-method-redo)
  - [⚙️ Method `reset_to_original_size`](#%EF%B8%8F-method-reset_to_original_size)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `sample_color_at`](#%EF%B8%8F-method-sample_color_at)
  - [⚙️ Method `selected_index (property)`](#%EF%B8%8F-method-selected_index-property)
  - [⚙️ Method `selected_indices (property)`](#%EF%B8%8F-method-selected_indices-property)
  - [⚙️ Method `send_backward`](#%EF%B8%8F-method-send_backward)
  - [⚙️ Method `send_to_back`](#%EF%B8%8F-method-send_to_back)
  - [⚙️ Method `set_document`](#%EF%B8%8F-method-set_document)
  - [⚙️ Method `set_style`](#%EF%B8%8F-method-set_style)
  - [⚙️ Method `set_tool`](#%EF%B8%8F-method-set_tool)
  - [⚙️ Method `tool (property)`](#%EF%B8%8F-method-tool-property)
  - [⚙️ Method `undo`](#%EF%B8%8F-method-undo)
  - [⚙️ Method `wheelEvent`](#%EF%B8%8F-method-wheelevent)
  - [⚙️ Method `zoom (property)`](#%EF%B8%8F-method-zoom-property)
  - [⚙️ Method `zoom_by`](#%EF%B8%8F-method-zoom_by)
  - [⚙️ Method `zoom_in`](#%EF%B8%8F-method-zoom_in)
  - [⚙️ Method `zoom_out`](#%EF%B8%8F-method-zoom_out)

</details>

## 🏛️ Class `ScreenshotPreviewCanvas`

```python
class ScreenshotPreviewCanvas(QWidget)
```

Show an image fitted with aspect ratio; Ctrl+wheel and Ctrl++ / Ctrl+- zoom; middle-drag pans.

Left-drag draws with the active [`AnnotationTool`](annotations.g.md#%EF%B8%8F-class-annotationtool) when a document is attached.
Crop mode uses the same dimmed blue selection frame as region capture.
Right-click opens annotation edit commands (undo, cut/copy/paste, layer order).
Double-click in the view tool returns a zoomed image to that opening size.
At the opening size, a small image is fitted into the view.

<details>
<summary>Code:</summary>

```python
class ScreenshotPreviewCanvas(QWidget):

    document_changed = Signal()
    crop_mode_changed = Signal(bool)
    crop_pending_changed = Signal(bool)
    color_hovered = Signal(object)
    color_picked = Signal(QColor)
    text_editing_changed = Signal(bool)

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
        self._smart_eraser_color: QColor | None = None
        self._selected_index: int | None = None
        self._selected_others: set[int] = set()
        self._edit_handle: AnnotationHandle | None = None
        self._edit_origin_points: list[QPointF] | None = None
        self._edit_group_origins: dict[int, list[QPointF]] | None = None
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
        self._text_editor: QPlainTextEdit | None = None
        self._text_edit_index: int | None = None
        self._text_edit_active = False

    @property
    def annotation_style(self) -> AnnotationStyle:
        """Style used for new shapes / the active text editor."""
        return copy_annotation_style(self._style)

    def begin_text_at(self, image_pos: QPointF) -> None:
        """Start an on-canvas multiline text editor at `image_pos`."""
        if self._document is None:
            return
        self.commit_text_edit()
        style = copy_annotation_style(self._style)
        points = default_text_box_points(image_pos, style)
        self._document.begin_draft(Annotation(tool=AnnotationTool.TEXT, points=points, text="", style=style))
        self._text_edit_index = None
        self._open_text_editor(text="", style=style, image_rect=QRectF(points[0], points[1]).normalized())

    def begin_text_edit(self, index: int) -> None:
        """Open the on-canvas editor for a committed text annotation."""
        document = self._document
        if document is None or index < 0 or index >= len(document.annotations):
            return
        annotation = document.annotations[index]
        if annotation.tool != AnnotationTool.TEXT:
            return
        self.commit_text_edit()
        self._set_only_selection(index)
        self._text_edit_index = index
        self._style = copy_annotation_style(annotation.style)
        self._open_text_editor(
            text=annotation.text,
            style=annotation.style,
            image_rect=text_annotation_rect(annotation),
        )

    def bring_forward(self) -> bool:
        """Move the selection one step toward the front."""
        return self._apply_z_order(lambda doc, indices: doc.bring_forward(indices))

    def bring_to_front(self) -> bool:
        """Move the selection to the front."""
        return self._apply_z_order(lambda doc, indices: doc.bring_to_front(indices))

    def cancel_crop(self) -> None:
        """Discard crop selection and leave crop mode."""
        was_crop = self._tool == AnnotationTool.CROP or self._crop_pending or self._crop_rect is not None
        if self._document is not None:
            self._document.cancel_draft()
        self._clear_crop_state()
        self._clear_edit_state()
        self._set_only_selection(None)
        self._tool = AnnotationTool.NONE
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._refresh_pixmap()
        if was_crop:
            self.crop_mode_changed.emit(False)  # noqa: FBT003
        self.crop_pending_changed.emit(False)  # noqa: FBT003

    def cancel_text_edit(self) -> None:
        """Discard an in-progress text edit without committing."""
        if not self._text_edit_active:
            return
        document = self._document
        if document is not None and self._text_edit_index is None:
            document.cancel_draft()
        self._close_text_editor()
        self.update()

    def clear_selection(self) -> bool:
        """Deselect every annotation. Return whether anything changed."""
        if not self._selection() and self._edit_handle is None:
            return False
        self._clear_edit_state()
        self._set_only_selection(None)
        self.update()
        return True

    def commit_text_edit(self) -> bool:
        """Commit the on-canvas text editor. Return whether text was saved."""
        if not self._text_edit_active or self._text_editor is None or self._document is None:
            return False
        text = self._text_editor.toPlainText()
        index = self._text_edit_index
        if index is not None and 0 <= index < len(self._document.annotations):
            annotation = self._document.annotations[index]
            if not text.strip():
                self._close_text_editor()
                if self._document.delete_at(index):
                    self._drop_deleted_indices({index})
                    self.update()
                    self.document_changed.emit()
                return False
            self._document.save_undo_checkpoint()
            annotation.text = text
            annotation.style = copy_annotation_style(self._style)
            self._set_only_selection(index)
            self._close_text_editor()
            self.update()
            self.document_changed.emit()
            return True
        draft = self._document.draft
        if draft is None or draft.tool != AnnotationTool.TEXT:
            self._close_text_editor()
            return False
        draft.text = text
        draft.style = copy_annotation_style(self._style)
        self._close_text_editor()
        if self._document.commit_draft():
            self._set_only_selection(len(self._document.annotations) - 1)
            self.update()
            self.document_changed.emit()
            return True
        self.update()
        return False

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

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # noqa: N802
        """Show annotation edit commands; select the shape under the pointer when needed."""
        if self._tool == AnnotationTool.CROP:
            event.ignore()
            return
        image_pos = self._widget_to_image(QPointF(event.pos()))
        if image_pos is not None:
            self._select_for_context_menu(image_pos)
        self._annotation_menu().exec(event.globalPos())
        event.accept()

    def copy_selected(self) -> bool:
        """Copy selected annotations to the internal clipboard."""
        document = self._document
        indices = sorted(self._selection())
        if document is None or not indices:
            return False
        _annotation_clipboard.clear()
        _annotation_clipboard.extend(clone_annotation(document.annotations[index]) for index in indices)
        return True

    @property
    def crop_mode(self) -> bool:
        """Whether the canvas is in crop selection / edit mode."""
        return self._tool == AnnotationTool.CROP

    @property
    def crop_pending(self) -> bool:
        """Whether a crop rectangle is waiting for confirmation."""
        return self._crop_pending

    def cut_selected(self) -> bool:
        """Copy selected annotations then delete them."""
        if not self.copy_selected():
            return False
        return self.delete_selected()

    def delete_all(self) -> bool:
        """Remove every annotation. Return whether any were removed."""
        document = self._document
        if document is None or not document.annotations:
            return False
        self._clear_edit_state()
        if not document.delete_all():
            return False
        self._set_only_selection(None)
        self.update()
        self.document_changed.emit()
        return True

    def delete_selected(self) -> bool:
        """Delete every selected annotation. Return whether any were removed."""
        document = self._document
        indices = self._selection()
        if document is None or not indices:
            return False
        self._clear_edit_state()
        if not document.delete_indices(sorted(indices)):
            return False
        self._set_only_selection(None)
        self.update()
        self.document_changed.emit()
        return True

    def duplicate_selected(self) -> bool:
        """Paste clones of the selection offset from the originals."""
        document = self._document
        indices = sorted(self._selection())
        if document is None or not indices:
            return False
        clones = [
            _offset_annotation(clone_annotation(document.annotations[index]), _PASTE_OFFSET, _PASTE_OFFSET)
            for index in indices
        ]
        new_indices = document.insert_annotations(clones)
        if not new_indices:
            return False
        self._apply_selection_indices(new_indices)
        self.update()
        self.document_changed.emit()
        return True

    def finish_text_at(self, image_pos: QPointF, text: str) -> None:
        """Commit a text annotation at `image_pos` (compat helper for tests)."""
        if self._document is None or not text.strip():
            return
        style = copy_annotation_style(self._style)
        self._document.begin_draft(
            Annotation(
                tool=AnnotationTool.TEXT,
                points=default_text_box_points(image_pos, style),
                text=text.strip(),
                style=style,
            )
        )
        if self._document.commit_draft():
            self._set_only_selection(len(self._document.annotations) - 1)
            self.update()
            self.document_changed.emit()

    def fit_to_view(self) -> None:
        """Scale the image so it fills the visible area, including a small image."""
        self._zoom = self._fit_zoom()
        self._offset = QPointF()
        self._sync_text_editor_geometry()
        self.update()

    def flatten_annotations(self) -> bool:
        """Bake annotations into the base image."""
        document = self._document
        if document is None or not document.flatten():
            return False
        self._clear_edit_state()
        self._set_only_selection(None)
        self._refresh_pixmap()
        self.document_changed.emit()
        return True

    @property
    def is_text_editing(self) -> bool:
        """Whether the inline text editor is open."""
        return self._text_edit_active

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Delete or deselect a shape; re-apply Shift constraints while dragging."""
        if self._text_edit_active:
            if event.key() == Qt.Key.Key_Escape:
                self.cancel_text_edit()
                event.accept()
                return
            if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter} and (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                self.commit_text_edit()
                event.accept()
                return
            # Let the editor receive typing; do not steal other keys.
            super().keyPressEvent(event)
            return
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

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Edit text, or toggle the opening size and fit-to-view."""
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseDoubleClickEvent(event)
            return
        image_pos = self._widget_to_image(event.position())
        document = self._document
        if image_pos is not None and document is not None:
            hit = hit_test_topmost(
                document.annotations,
                image_pos,
                handle_size=self._handle_size_image(),
                prefer_tool=AnnotationTool.TEXT,
                selected_index=self._selected_index,
            )
            if hit is not None and document.annotations[hit[0]].tool == AnnotationTool.TEXT:
                self.begin_text_edit(hit[0])
                event.accept()
                return
        if self._tool == AnnotationTool.NONE and not self._text_edit_active:
            self._toggle_opening_view()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

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
            elif draft.tool == AnnotationTool.STEP:
                self._document.update_draft_points(step_circle_points(start, image_pos))
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
            if self._text_edit_active:
                editor = self._text_editor
                if editor is not None and editor.geometry().contains(event.position().toPoint()):
                    event.ignore()
                    return
                self.commit_text_edit()
            if self._begin_annotation_edit(image_pos, shift=_shift_pressed(event.modifiers())):
                event.accept()
                return
            self._set_only_selection(None)
            snapped = self._snap_pointer(image_pos)
            if self._tool == AnnotationTool.SMART_ERASER and self._document is not None:
                self._smart_eraser_color = sample_composited_color(
                    self._document.base_image,
                    self._document.annotations,
                    image_pos,
                )
            if self._tool == AnnotationTool.TEXT:
                self.begin_text_at(snapped)
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
            if self._text_edit_active:
                self.commit_text_edit()
            if image_pos is not None and self._begin_annotation_edit(
                image_pos, shift=_shift_pressed(event.modifiers())
            ):
                event.accept()
                return
            if not _shift_pressed(event.modifiers()):
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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        image_rect = self._image_rect()
        if not self._pixmap.isNull():
            painter.setRenderHint(
                QPainter.RenderHint.SmoothPixmapTransform,
                on=not self._crisp_source_pixels(),
            )
            painter.drawPixmap(image_rect.toRect(), self._pixmap)

        if self._tool == AnnotationTool.CROP and not image_rect.isEmpty():
            self._paint_crop_overlay(painter, image_rect)
        elif self._document is not None and not image_rect.isEmpty() and self._tool != AnnotationTool.EYEDROPPER:
            self._paint_live_annotations(painter, image_rect)
        if self._tool == AnnotationTool.EYEDROPPER:
            self._paint_eyedrop_preview(painter)
        painter.end()

    def paste_clipboard(self) -> bool:
        """Paste annotations from the internal clipboard with a small offset."""
        document = self._document
        if document is None or not _annotation_clipboard:
            return False
        clones = [
            _offset_annotation(clone_annotation(item), _PASTE_OFFSET, _PASTE_OFFSET) for item in _annotation_clipboard
        ]
        new_indices = document.insert_annotations(clones)
        if not new_indices:
            return False
        self._apply_selection_indices(new_indices)
        self.update()
        self.document_changed.emit()
        return True

    def redo(self) -> bool:
        """Redo the last undone change."""
        document = self._document
        if document is None or not document.redo():
            return False
        self._clear_edit_state()
        self._set_only_selection(None)
        self._refresh_pixmap()
        self.document_changed.emit()
        return True

    def reset_to_original_size(self) -> None:
        """Restore the opening view: native pixels when small, fitted down when large."""
        self._zoom = 1.0
        self._offset = QPointF()
        self._sync_text_editor_geometry()
        self.update()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Repaint when the available fit area changes."""
        super().resizeEvent(event)
        self._sync_text_editor_geometry()
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
        """Index of the primary selected annotation, or `None`."""
        return self._selected_index

    @property
    def selected_indices(self) -> set[int]:
        """Indices of every selected annotation."""
        return self._selection()

    def send_backward(self) -> bool:
        """Move the selection one step toward the back."""
        return self._apply_z_order(lambda doc, indices: doc.send_backward(indices))

    def send_to_back(self) -> bool:
        """Move the selection to the back."""
        return self._apply_z_order(lambda doc, indices: doc.send_to_back(indices))

    def set_document(self, document: AnnotationDocument | None) -> None:
        """Attach an annotation document; canvas displays its rendered image."""
        self.commit_text_edit()
        self._clear_edit_state()
        self._set_only_selection(None)
        self._document = document
        self._rebuild_snap_edges()
        self._refresh_pixmap()

    def set_style(
        self,
        style: AnnotationStyle | None = None,
        *,
        color: QColor | None = None,
        width: float | None = None,
    ) -> None:
        """Update style for new annotations and the active text editor."""
        if style is not None:
            self._style = copy_annotation_style(style)
        if color is not None:
            self._style.color = QColor(color)
        if width is not None:
            self._style.width = max(1.0, width)
        self._sync_text_editor_style()

    def set_tool(self, tool: AnnotationTool) -> None:
        """Select the drawing tool (`NONE` keeps view-only left-click)."""
        if tool != AnnotationTool.TEXT and self._text_edit_active:
            self.commit_text_edit()
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
            self._set_only_selection(None)
        if tool == AnnotationTool.EYEDROPPER:
            self._set_only_selection(None)
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

    def undo(self) -> bool:
        """Undo the last change on this canvas's document."""
        document = self._document
        if document is None or not document.undo():
            return False
        self._clear_edit_state()
        self._set_only_selection(None)
        self._refresh_pixmap()
        self.document_changed.emit()
        return True

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
        self._sync_text_editor_geometry()
        self.update()

    def zoom_in(self) -> None:
        """Zoom in one step around the center, matching one Ctrl+wheel notch."""
        self.zoom_by(_ZOOM_STEP)

    def zoom_out(self) -> None:
        """Zoom out one step around the center, matching one Ctrl+wheel notch."""
        self.zoom_by(1.0 / _ZOOM_STEP)

    def _active_crop_rect(self) -> QRect | None:
        if self._crop_pending and self._crop_rect is not None:
            return self._crop_rect
        if self._crop_origin is not None and self._crop_current is not None and self._crop_dragging:
            return self._crop_drag_rect()
        return self._crop_rect

    def _annotation_menu(self) -> QMenu:
        """Build the ShareX-style right-click menu for annotations."""
        document = self._document
        has_selection = bool(self._selection())
        has_annotations = bool(document is not None and document.annotations)
        can_undo = bool(document is not None and document.can_undo)
        can_redo = bool(document is not None and document.can_redo)
        can_paste = bool(_annotation_clipboard)
        selected = sorted(self._selection()) if document is not None else []
        at_front = bool(
            selected
            and document is not None
            and selected == list(range(len(document.annotations) - len(selected), len(document.annotations)))
        )
        at_back = bool(selected and selected == list(range(len(selected))))

        menu = QMenu(self)
        undo = add_lucide_action(menu, "Undo", "undo-2")
        undo.setShortcut(QKeySequence.StandardKey.Undo)
        undo.setEnabled(can_undo)
        undo.triggered.connect(lambda _checked=False: self.undo())
        redo = add_lucide_action(menu, "Redo", "redo-2")
        redo.setShortcut(QKeySequence.StandardKey.Redo)
        redo.setEnabled(can_redo)
        redo.triggered.connect(lambda _checked=False: self.redo())
        menu.addSeparator()
        delete = add_lucide_action(menu, "Delete", "trash-2")
        delete.setShortcut(QKeySequence.StandardKey.Delete)
        delete.setEnabled(has_selection)
        delete.triggered.connect(lambda _checked=False: self.delete_selected())
        delete_all = add_lucide_action(menu, "Delete all", "broom")
        delete_all.setShortcut(QKeySequence("Shift+Delete"))
        delete_all.setEnabled(has_annotations)
        delete_all.triggered.connect(lambda _checked=False: self.delete_all())
        flatten = add_lucide_action(menu, "Flatten", "layers")
        flatten.setShortcut(QKeySequence("Ctrl+Shift+F"))
        flatten.setEnabled(has_annotations)
        flatten.triggered.connect(lambda _checked=False: self.flatten_annotations())
        menu.addSeparator()
        cut = add_lucide_action(menu, "Cut", "scissors")
        cut.setShortcut(QKeySequence.StandardKey.Cut)
        cut.setEnabled(has_selection)
        cut.triggered.connect(lambda _checked=False: self.cut_selected())
        copy = add_lucide_action(menu, "Copy", "clipboard-copy")
        copy.setShortcut(QKeySequence.StandardKey.Copy)
        copy.setEnabled(has_selection)
        copy.triggered.connect(lambda _checked=False: self.copy_selected())
        paste = add_lucide_action(menu, "Paste", "clipboard-paste")
        paste.setShortcut(QKeySequence.StandardKey.Paste)
        paste.setEnabled(can_paste)
        paste.triggered.connect(lambda _checked=False: self.paste_clipboard())
        duplicate = add_lucide_action(menu, "Duplicate", "copy-plus")
        duplicate.setShortcut(QKeySequence("Ctrl+D"))
        duplicate.setEnabled(has_selection)
        duplicate.triggered.connect(lambda _checked=False: self.duplicate_selected())
        menu.addSeparator()
        to_front = add_lucide_action(menu, "Bring to front", "bring-to-front")
        to_front.setShortcut(QKeySequence(Qt.Key.Key_Home))
        to_front.setEnabled(has_selection and not at_front)
        to_front.triggered.connect(lambda _checked=False: self.bring_to_front())
        forward = add_lucide_action(menu, "Bring forward", "arrow-up")
        forward.setShortcut(QKeySequence(Qt.Key.Key_PageUp))
        forward.setEnabled(has_selection and not at_front)
        forward.triggered.connect(lambda _checked=False: self.bring_forward())
        backward = add_lucide_action(menu, "Send backward", "arrow-down")
        backward.setShortcut(QKeySequence(Qt.Key.Key_PageDown))
        backward.setEnabled(has_selection and not at_back)
        backward.triggered.connect(lambda _checked=False: self.send_backward())
        to_back = add_lucide_action(menu, "Send to back", "send-to-back")
        to_back.setShortcut(QKeySequence(Qt.Key.Key_End))
        to_back.setEnabled(has_selection and not at_back)
        to_back.triggered.connect(lambda _checked=False: self.send_to_back())
        menu.addSeparator()
        if self._size_changed():
            original = add_lucide_action(menu, "Original size", "undo-2")
            original.triggered.connect(lambda _checked=False: self.reset_to_original_size())
        fit = add_lucide_action(menu, "Fit to view", "expand")
        fit.triggered.connect(lambda _checked=False: self.fit_to_view())
        return menu

    def _annotation_snap_guides(self, *, exclude_indices: set[int] | None = None) -> tuple[list[float], list[float]]:
        document = self._document
        if document is None:
            return [], []
        bounds = self._image_bounds()
        frame = None
        if bounds.isValid() and not bounds.isEmpty():
            frame = QRectF(QPointF(bounds.left(), bounds.top()), QPointF(bounds.right(), bounds.bottom()))
        skip = exclude_indices or set()
        annotations = [item for index, item in enumerate(document.annotations) if index not in skip]
        return collect_annotation_guides(annotations, bounds=frame)

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
        exclude = self._selection() if handle == "move" else {index}
        xs, ys = self._annotation_snap_guides(exclude_indices=exclude)
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
        origins = self._edit_group_origins
        if handle == "move" and origins and origin:
            dx = snapped.points[0].x() - origin[0].x()
            dy = snapped.points[0].y() - origin[0].y()
            for other, other_points in origins.items():
                document.update_annotation_points(
                    other,
                    [QPointF(point.x() + dx, point.y() + dy) for point in other_points],
                )
        elif annotation.tool == AnnotationTool.STEP and handle != "move":
            radius = step_circle_radius(snapped.points)
            for other_index, points in step_points_for_shared_radius(
                document.annotations,
                radius,
                exclude_index=index,
            ).items():
                document.update_annotation_points(other_index, points)
        self.update()

    def _apply_selection_indices(self, indices: Sequence[int]) -> None:
        if not indices:
            self._set_only_selection(None)
            return
        ordered = sorted(indices)
        self._selected_index = ordered[-1]
        self._selected_others = set(ordered[:-1])

    def _apply_z_order(
        self,
        action: Callable[[AnnotationDocument, Sequence[int]], Sequence[int] | None],
    ) -> bool:
        document = self._document
        indices = sorted(self._selection())
        if document is None or not indices:
            return False
        new_indices = action(document, indices)
        if new_indices is None:
            return False
        self._clear_edit_state()
        self._apply_selection_indices(list(new_indices))
        self.update()
        self.document_changed.emit()
        return True

    def _begin_annotation_edit(self, image_pos: QPointF, *, shift: bool = False) -> bool:
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
        if shift:
            self._toggle_selection(index)
            self._clear_edit_state()
            self.update()
            return True
        keep_group = handle == "move" and index in self._selection()
        if keep_group:
            self._selected_others = self._selection() - {index}
            self._selected_index = index
        else:
            self._set_only_selection(index)
        self._edit_handle = handle
        self._edit_origin_points = [QPointF(point) for point in document.annotations[index].points]
        self._edit_press = QPointF(image_pos)
        self._edit_current = QPointF(image_pos)
        self._edit_history_saved = False
        self._edit_group_origins = None
        if keep_group:
            self._edit_group_origins = {
                other: [QPointF(point) for point in document.annotations[other].points]
                for other in self._selected_others
                if 0 <= other < len(document.annotations)
            }
        self.update()
        return True

    def _begin_shape_draft(self, start: QPointF, current: QPointF, *, clicked: bool = False) -> None:
        if self._document is None:
            return
        style = copy_annotation_style(self._style)
        if self._tool == AnnotationTool.SMART_ERASER and self._smart_eraser_color is not None:
            style.color = QColor(self._smart_eraser_color)
        points = [QPointF(start), QPointF(current)]
        text = ""
        if self._tool == AnnotationTool.STEP:
            points = step_circle_points(start, current, clicked=clicked)
            text = str(next_step_number(self._document.annotations))
        self._document.begin_draft(
            Annotation(
                tool=self._tool,
                points=points,
                style=style,
                text=text,
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
        self._edit_group_origins = None
        self._clear_snap_guides()

    def _clear_snap_guides(self) -> None:
        self._snap_x_guide = None
        self._snap_y_guide = None

    def _close_text_editor(self) -> None:
        was_active = self._text_edit_active
        editor = self._text_editor
        self._text_editor = None
        self._text_edit_index = None
        self._text_edit_active = False
        if editor is not None:
            editor.hide()
            editor.deleteLater()
        if was_active:
            self.text_editing_changed.emit(False)  # noqa: FBT003

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

    def _crisp_source_pixels(self) -> bool:
        """Draw enlarged eyedropper pixels as solid source colors, without smoothing."""
        if self._tool != AnnotationTool.EYEDROPPER:
            return False
        rect = self._image_rect()
        width, height = self._source_size()
        if width <= 0 or height <= 0 or rect.isEmpty():
            return False
        return rect.width() > width or rect.height() > height

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

    def _drop_deleted_indices(self, deleted: set[int]) -> None:
        """Keep the selection after removing `deleted` indices, shifting the rest down."""
        remaining: list[int] = []
        for index in self._selection():
            if index in deleted:
                continue
            shift = sum(1 for removed in deleted if removed < index)
            remaining.append(index - shift)
        if not remaining:
            self._set_only_selection(None)
            return
        self._selected_index = remaining[-1]
        self._selected_others = set(remaining[:-1])

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
            elif document.draft.tool == AnnotationTool.STEP:
                document.update_draft_points(step_circle_points(start, image_pos))
            else:
                end = self._constrain_and_snap_draft_end(
                    start,
                    image_pos,
                    document.draft.tool,
                    shift=shift,
                )
                document.update_draft_points([start, end])
        elif self._tool == AnnotationTool.STEP:
            self._begin_shape_draft(start, start, clicked=True)
        self._clear_snap_guides()
        if document.commit_draft():
            self._set_only_selection(len(document.annotations) - 1)
            self.update()
            self.document_changed.emit()
        else:
            self.update()

    def _fit_zoom(self) -> float:
        """Zoom that fills the widget, scaling a small image up past its native size."""
        width, height = self._source_size()
        if width <= 0 or height <= 0 or self.width() <= 0 or self.height() <= 0:
            return 1.0
        fitted = QSize(width, height).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        base_width = min(fitted.width(), width)
        if base_width <= 0:
            return 1.0
        return max(_MIN_ZOOM, min(_MAX_ZOOM, fitted.width() / base_width))

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

    def _image_rectf_to_widget(self, rect: QRectF) -> QRect:
        image_rect = self._image_rect()
        width, height = self._source_size()
        if width <= 0 or height <= 0 or image_rect.isEmpty() or rect.isNull():
            return QRect()
        scale_x = image_rect.width() / width
        scale_y = image_rect.height() / height
        left = round(image_rect.left() + rect.left() * scale_x)
        top = round(image_rect.top() + rect.top() * scale_y)
        right = round(image_rect.left() + rect.right() * scale_x)
        bottom = round(image_rect.top() + rect.bottom() * scale_y)
        return QRect(QPoint(left, top), QPoint(max(left + 8, right), max(top + 8, bottom)))

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

    def _open_text_editor(self, *, text: str, style: AnnotationStyle, image_rect: QRectF) -> None:
        self._style = copy_annotation_style(style)
        editor = QPlainTextEdit(self)
        editor.setPlainText(text)
        editor.setFrameShape(QPlainTextEdit.Shape.NoFrame)
        editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        editor.setTabChangesFocus(False)
        editor.setStyleSheet(
            "QPlainTextEdit {  background: rgba(255, 255, 255, 210);  border: 1px dashed #2e86b7;  padding: 2px;}"
        )
        self._text_editor = editor
        self._text_edit_active = True
        self._sync_text_editor_style()
        editor.setGeometry(self._image_rectf_to_widget(image_rect))
        editor.show()
        editor.setFocus(Qt.FocusReason.MouseFocusReason)
        self.text_editing_changed.emit(True)  # noqa: FBT003
        self.update()

    def _paint_blur_draft_outline(self, painter: QPainter) -> None:
        """Draw a dashed edge while a blur or pixelate rectangle is still being dragged."""
        document = self._document
        if document is None or document.draft is None or document.draft.tool not in RASTER_EFFECT_TOOLS:
            return
        points = document.draft.points
        if len(points) <= 1:
            return
        pen = QPen(QColor(0, 0, 0), 1.0)
        pen.setCosmetic(True)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(QRectF(points[0], points[-1]).normalized())

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
        items = self._visible_annotations()
        if any(item.tool in RASTER_EFFECT_TOOLS for item in items):
            image = composite_annotations(document.base_image, items)
            painter.drawImage(QPointF(0, 0), image)
            self._paint_blur_draft_outline(painter)
        else:
            for item in items:
                paint_annotation(painter, item)
        index = self._selected_index
        handle_size = self._handle_size_image()
        for selected in sorted(self._selection()):
            if self._text_edit_active or not 0 <= selected < len(document.annotations):
                continue
            paint_annotation_selection(
                painter,
                document.annotations[selected],
                handle_size=handle_size,
                handles=selected == index,
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

    def _select_for_context_menu(self, image_pos: QPointF) -> None:
        document = self._document
        if document is None or not document.annotations:
            return
        hit = hit_test_topmost(
            document.annotations,
            image_pos,
            handle_size=self._handle_size_image(),
            prefer_tool=self._prefer_tool(),
            selected_index=self._selected_index,
        )
        if hit is None:
            return
        index, _handle = hit
        if index not in self._selection():
            self._set_only_selection(index)
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

    def _selection(self) -> set[int]:
        if self._selected_index is None:
            return set(self._selected_others)
        return {self._selected_index, *self._selected_others}

    def _set_only_selection(self, index: int | None) -> None:
        self._selected_index = index
        self._selected_others.clear()

    def _size_changed(self) -> bool:
        """Whether zoom left the opening size."""
        return abs(self._zoom - 1.0) > _ZOOM_UNCHANGED

    def _snap_pointer(self, image_pos: QPointF, *, exclude_index: int | None = None) -> QPointF:
        xs, ys = self._annotation_snap_guides(
            exclude_indices={exclude_index} if exclude_index is not None else None,
        )
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

    def _sync_text_editor_geometry(self) -> None:
        if not self._text_edit_active or self._text_editor is None or self._document is None:
            return
        if self._text_edit_index is not None and 0 <= self._text_edit_index < len(self._document.annotations):
            rect = text_annotation_rect(self._document.annotations[self._text_edit_index])
        elif self._document.draft is not None and self._document.draft.tool == AnnotationTool.TEXT:
            rect = text_annotation_rect(self._document.draft)
        else:
            return
        self._text_editor.setGeometry(self._image_rectf_to_widget(rect))

    def _sync_text_editor_style(self) -> None:
        editor = self._text_editor
        if editor is None or not self._text_edit_active:
            return
        style = self._style
        editor.setFont(annotation_qfont(style))
        color = style.color.name() if style.color.isValid() else "#de2b26"
        bg = "rgba(255, 255, 255, 230)" if style.background_fill else "rgba(255, 255, 255, 120)"
        align = style.align
        qt_align = Qt.AlignmentFlag.AlignLeft
        if align == "center":
            qt_align = Qt.AlignmentFlag.AlignHCenter
        elif align == "right":
            qt_align = Qt.AlignmentFlag.AlignRight
        option = editor.document().defaultTextOption()
        option.setAlignment(qt_align)
        editor.document().setDefaultTextOption(option)
        cursor = editor.textCursor()
        cursor.beginEditBlock()
        cursor.select(QTextCursor.SelectionType.Document)
        block_format = QTextBlockFormat()
        block_format.setAlignment(qt_align)
        cursor.mergeBlockFormat(block_format)
        cursor.clearSelection()
        cursor.endEditBlock()
        editor.setTextCursor(cursor)
        editor.setStyleSheet(
            f"QPlainTextEdit {{  color: {color};  background: {bg};  border: 1px dashed #2e86b7;  padding: 2px;}}"
        )
        document = self._document
        if document is None:
            return
        if self._text_edit_index is not None and 0 <= self._text_edit_index < len(document.annotations):
            document.annotations[self._text_edit_index].style = copy_annotation_style(style)
        elif document.draft is not None and document.draft.tool == AnnotationTool.TEXT:
            document.draft.style = copy_annotation_style(style)

    def _toggle_opening_view(self) -> None:
        """Return a zoomed image to the opening size, or fit a small image into the view."""
        if self._size_changed():
            self.reset_to_original_size()
            return
        if self._fit_zoom() > 1.0 + _ZOOM_UNCHANGED:
            self.fit_to_view()

    def _toggle_selection(self, index: int) -> None:
        selected = self._selection()
        if index in selected:
            selected.remove(index)
        else:
            selected.add(index)
        if not selected:
            self._set_only_selection(None)
            return
        primary = index if index in selected else max(selected)
        self._selected_index = primary
        self._selected_others = selected - {primary}

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

    def _view_menu(self) -> QMenu:
        """Zoom helpers kept for tests and as the trailing context-menu section."""
        menu = QMenu(self)
        if self._size_changed():
            original = add_lucide_action(menu, "Original size", "undo-2")
            original.triggered.connect(lambda _checked=False: self.reset_to_original_size())
        fit = add_lucide_action(menu, "Fit to view", "expand")
        fit.triggered.connect(lambda _checked=False: self.fit_to_view())
        return menu

    def _visible_annotations(self) -> list[Annotation]:
        """Return committed annotations plus the draft, omitting text open in the editor."""
        document = self._document
        if document is None:
            return []
        items: list[Annotation] = []
        for index, item in enumerate(document.annotations):
            if self._text_edit_active and self._text_edit_index is not None and index == self._text_edit_index:
                continue
            items.append(item)
        draft = document.draft
        if draft is not None and not (
            self._text_edit_active and self._text_edit_index is None and draft.tool == AnnotationTool.TEXT
        ):
            items.append(draft)
        return items

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
        self._smart_eraser_color: QColor | None = None
        self._selected_index: int | None = None
        self._selected_others: set[int] = set()
        self._edit_handle: AnnotationHandle | None = None
        self._edit_origin_points: list[QPointF] | None = None
        self._edit_group_origins: dict[int, list[QPointF]] | None = None
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
        self._text_editor: QPlainTextEdit | None = None
        self._text_edit_index: int | None = None
        self._text_edit_active = False
```

</details>

### ⚙️ Method `annotation_style (property)`

```python
def annotation_style(self) -> AnnotationStyle
```

Style used for new shapes / the active text editor.

<details>
<summary>Code:</summary>

```python
def annotation_style(self) -> AnnotationStyle:
        return copy_annotation_style(self._style)
```

</details>

### ⚙️ Method `begin_text_at`

```python
def begin_text_at(self, image_pos: QPointF) -> None
```

Start an on-canvas multiline text editor at `image_pos`.

<details>
<summary>Code:</summary>

```python
def begin_text_at(self, image_pos: QPointF) -> None:
        if self._document is None:
            return
        self.commit_text_edit()
        style = copy_annotation_style(self._style)
        points = default_text_box_points(image_pos, style)
        self._document.begin_draft(Annotation(tool=AnnotationTool.TEXT, points=points, text="", style=style))
        self._text_edit_index = None
        self._open_text_editor(text="", style=style, image_rect=QRectF(points[0], points[1]).normalized())
```

</details>

### ⚙️ Method `begin_text_edit`

```python
def begin_text_edit(self, index: int) -> None
```

Open the on-canvas editor for a committed text annotation.

<details>
<summary>Code:</summary>

```python
def begin_text_edit(self, index: int) -> None:
        document = self._document
        if document is None or index < 0 or index >= len(document.annotations):
            return
        annotation = document.annotations[index]
        if annotation.tool != AnnotationTool.TEXT:
            return
        self.commit_text_edit()
        self._set_only_selection(index)
        self._text_edit_index = index
        self._style = copy_annotation_style(annotation.style)
        self._open_text_editor(
            text=annotation.text,
            style=annotation.style,
            image_rect=text_annotation_rect(annotation),
        )
```

</details>

### ⚙️ Method `bring_forward`

```python
def bring_forward(self) -> bool
```

Move the selection one step toward the front.

<details>
<summary>Code:</summary>

```python
def bring_forward(self) -> bool:
        return self._apply_z_order(lambda doc, indices: doc.bring_forward(indices))
```

</details>

### ⚙️ Method `bring_to_front`

```python
def bring_to_front(self) -> bool
```

Move the selection to the front.

<details>
<summary>Code:</summary>

```python
def bring_to_front(self) -> bool:
        return self._apply_z_order(lambda doc, indices: doc.bring_to_front(indices))
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
        self._set_only_selection(None)
        self._tool = AnnotationTool.NONE
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._refresh_pixmap()
        if was_crop:
            self.crop_mode_changed.emit(False)  # noqa: FBT003
        self.crop_pending_changed.emit(False)  # noqa: FBT003
```

</details>

### ⚙️ Method `cancel_text_edit`

```python
def cancel_text_edit(self) -> None
```

Discard an in-progress text edit without committing.

<details>
<summary>Code:</summary>

```python
def cancel_text_edit(self) -> None:
        if not self._text_edit_active:
            return
        document = self._document
        if document is not None and self._text_edit_index is None:
            document.cancel_draft()
        self._close_text_editor()
        self.update()
```

</details>

### ⚙️ Method `clear_selection`

```python
def clear_selection(self) -> bool
```

Deselect every annotation. Return whether anything changed.

<details>
<summary>Code:</summary>

```python
def clear_selection(self) -> bool:
        if not self._selection() and self._edit_handle is None:
            return False
        self._clear_edit_state()
        self._set_only_selection(None)
        self.update()
        return True
```

</details>

### ⚙️ Method `commit_text_edit`

```python
def commit_text_edit(self) -> bool
```

Commit the on-canvas text editor. Return whether text was saved.

<details>
<summary>Code:</summary>

```python
def commit_text_edit(self) -> bool:
        if not self._text_edit_active or self._text_editor is None or self._document is None:
            return False
        text = self._text_editor.toPlainText()
        index = self._text_edit_index
        if index is not None and 0 <= index < len(self._document.annotations):
            annotation = self._document.annotations[index]
            if not text.strip():
                self._close_text_editor()
                if self._document.delete_at(index):
                    self._drop_deleted_indices({index})
                    self.update()
                    self.document_changed.emit()
                return False
            self._document.save_undo_checkpoint()
            annotation.text = text
            annotation.style = copy_annotation_style(self._style)
            self._set_only_selection(index)
            self._close_text_editor()
            self.update()
            self.document_changed.emit()
            return True
        draft = self._document.draft
        if draft is None or draft.tool != AnnotationTool.TEXT:
            self._close_text_editor()
            return False
        draft.text = text
        draft.style = copy_annotation_style(self._style)
        self._close_text_editor()
        if self._document.commit_draft():
            self._set_only_selection(len(self._document.annotations) - 1)
            self.update()
            self.document_changed.emit()
            return True
        self.update()
        return False
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

### ⚙️ Method `contextMenuEvent`

```python
def contextMenuEvent(self, event: QContextMenuEvent) -> None
```

Show annotation edit commands; select the shape under the pointer when needed.

<details>
<summary>Code:</summary>

```python
def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # noqa: N802
        if self._tool == AnnotationTool.CROP:
            event.ignore()
            return
        image_pos = self._widget_to_image(QPointF(event.pos()))
        if image_pos is not None:
            self._select_for_context_menu(image_pos)
        self._annotation_menu().exec(event.globalPos())
        event.accept()
```

</details>

### ⚙️ Method `copy_selected`

```python
def copy_selected(self) -> bool
```

Copy selected annotations to the internal clipboard.

<details>
<summary>Code:</summary>

```python
def copy_selected(self) -> bool:
        document = self._document
        indices = sorted(self._selection())
        if document is None or not indices:
            return False
        _annotation_clipboard.clear()
        _annotation_clipboard.extend(clone_annotation(document.annotations[index]) for index in indices)
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

### ⚙️ Method `cut_selected`

```python
def cut_selected(self) -> bool
```

Copy selected annotations then delete them.

<details>
<summary>Code:</summary>

```python
def cut_selected(self) -> bool:
        if not self.copy_selected():
            return False
        return self.delete_selected()
```

</details>

### ⚙️ Method `delete_all`

```python
def delete_all(self) -> bool
```

Remove every annotation. Return whether any were removed.

<details>
<summary>Code:</summary>

```python
def delete_all(self) -> bool:
        document = self._document
        if document is None or not document.annotations:
            return False
        self._clear_edit_state()
        if not document.delete_all():
            return False
        self._set_only_selection(None)
        self.update()
        self.document_changed.emit()
        return True
```

</details>

### ⚙️ Method `delete_selected`

```python
def delete_selected(self) -> bool
```

Delete every selected annotation. Return whether any were removed.

<details>
<summary>Code:</summary>

```python
def delete_selected(self) -> bool:
        document = self._document
        indices = self._selection()
        if document is None or not indices:
            return False
        self._clear_edit_state()
        if not document.delete_indices(sorted(indices)):
            return False
        self._set_only_selection(None)
        self.update()
        self.document_changed.emit()
        return True
```

</details>

### ⚙️ Method `duplicate_selected`

```python
def duplicate_selected(self) -> bool
```

Paste clones of the selection offset from the originals.

<details>
<summary>Code:</summary>

```python
def duplicate_selected(self) -> bool:
        document = self._document
        indices = sorted(self._selection())
        if document is None or not indices:
            return False
        clones = [
            _offset_annotation(clone_annotation(document.annotations[index]), _PASTE_OFFSET, _PASTE_OFFSET)
            for index in indices
        ]
        new_indices = document.insert_annotations(clones)
        if not new_indices:
            return False
        self._apply_selection_indices(new_indices)
        self.update()
        self.document_changed.emit()
        return True
```

</details>

### ⚙️ Method `finish_text_at`

```python
def finish_text_at(self, image_pos: QPointF, text: str) -> None
```

Commit a text annotation at `image_pos` (compat helper for tests).

<details>
<summary>Code:</summary>

```python
def finish_text_at(self, image_pos: QPointF, text: str) -> None:
        if self._document is None or not text.strip():
            return
        style = copy_annotation_style(self._style)
        self._document.begin_draft(
            Annotation(
                tool=AnnotationTool.TEXT,
                points=default_text_box_points(image_pos, style),
                text=text.strip(),
                style=style,
            )
        )
        if self._document.commit_draft():
            self._set_only_selection(len(self._document.annotations) - 1)
            self.update()
            self.document_changed.emit()
```

</details>

### ⚙️ Method `fit_to_view`

```python
def fit_to_view(self) -> None
```

Scale the image so it fills the visible area, including a small image.

<details>
<summary>Code:</summary>

```python
def fit_to_view(self) -> None:
        self._zoom = self._fit_zoom()
        self._offset = QPointF()
        self._sync_text_editor_geometry()
        self.update()
```

</details>

### ⚙️ Method `flatten_annotations`

```python
def flatten_annotations(self) -> bool
```

Bake annotations into the base image.

<details>
<summary>Code:</summary>

```python
def flatten_annotations(self) -> bool:
        document = self._document
        if document is None or not document.flatten():
            return False
        self._clear_edit_state()
        self._set_only_selection(None)
        self._refresh_pixmap()
        self.document_changed.emit()
        return True
```

</details>

### ⚙️ Method `is_text_editing (property)`

```python
def is_text_editing(self) -> bool
```

Whether the inline text editor is open.

<details>
<summary>Code:</summary>

```python
def is_text_editing(self) -> bool:
        return self._text_edit_active
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
        if self._text_edit_active:
            if event.key() == Qt.Key.Key_Escape:
                self.cancel_text_edit()
                event.accept()
                return
            if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter} and (
                event.modifiers() & Qt.KeyboardModifier.ControlModifier
            ):
                self.commit_text_edit()
                event.accept()
                return
            # Let the editor receive typing; do not steal other keys.
            super().keyPressEvent(event)
            return
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

### ⚙️ Method `mouseDoubleClickEvent`

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None
```

Edit text, or toggle the opening size and fit-to-view.

<details>
<summary>Code:</summary>

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseDoubleClickEvent(event)
            return
        image_pos = self._widget_to_image(event.position())
        document = self._document
        if image_pos is not None and document is not None:
            hit = hit_test_topmost(
                document.annotations,
                image_pos,
                handle_size=self._handle_size_image(),
                prefer_tool=AnnotationTool.TEXT,
                selected_index=self._selected_index,
            )
            if hit is not None and document.annotations[hit[0]].tool == AnnotationTool.TEXT:
                self.begin_text_edit(hit[0])
                event.accept()
                return
        if self._tool == AnnotationTool.NONE and not self._text_edit_active:
            self._toggle_opening_view()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
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
            elif draft.tool == AnnotationTool.STEP:
                self._document.update_draft_points(step_circle_points(start, image_pos))
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
            if self._text_edit_active:
                editor = self._text_editor
                if editor is not None and editor.geometry().contains(event.position().toPoint()):
                    event.ignore()
                    return
                self.commit_text_edit()
            if self._begin_annotation_edit(image_pos, shift=_shift_pressed(event.modifiers())):
                event.accept()
                return
            self._set_only_selection(None)
            snapped = self._snap_pointer(image_pos)
            if self._tool == AnnotationTool.SMART_ERASER and self._document is not None:
                self._smart_eraser_color = sample_composited_color(
                    self._document.base_image,
                    self._document.annotations,
                    image_pos,
                )
            if self._tool == AnnotationTool.TEXT:
                self.begin_text_at(snapped)
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
            if self._text_edit_active:
                self.commit_text_edit()
            if image_pos is not None and self._begin_annotation_edit(
                image_pos, shift=_shift_pressed(event.modifiers())
            ):
                event.accept()
                return
            if not _shift_pressed(event.modifiers()):
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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        image_rect = self._image_rect()
        if not self._pixmap.isNull():
            painter.setRenderHint(
                QPainter.RenderHint.SmoothPixmapTransform,
                on=not self._crisp_source_pixels(),
            )
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

### ⚙️ Method `paste_clipboard`

```python
def paste_clipboard(self) -> bool
```

Paste annotations from the internal clipboard with a small offset.

<details>
<summary>Code:</summary>

```python
def paste_clipboard(self) -> bool:
        document = self._document
        if document is None or not _annotation_clipboard:
            return False
        clones = [
            _offset_annotation(clone_annotation(item), _PASTE_OFFSET, _PASTE_OFFSET) for item in _annotation_clipboard
        ]
        new_indices = document.insert_annotations(clones)
        if not new_indices:
            return False
        self._apply_selection_indices(new_indices)
        self.update()
        self.document_changed.emit()
        return True
```

</details>

### ⚙️ Method `redo`

```python
def redo(self) -> bool
```

Redo the last undone change.

<details>
<summary>Code:</summary>

```python
def redo(self) -> bool:
        document = self._document
        if document is None or not document.redo():
            return False
        self._clear_edit_state()
        self._set_only_selection(None)
        self._refresh_pixmap()
        self.document_changed.emit()
        return True
```

</details>

### ⚙️ Method `reset_to_original_size`

```python
def reset_to_original_size(self) -> None
```

Restore the opening view: native pixels when small, fitted down when large.

<details>
<summary>Code:</summary>

```python
def reset_to_original_size(self) -> None:
        self._zoom = 1.0
        self._offset = QPointF()
        self._sync_text_editor_geometry()
        self.update()
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
        self._sync_text_editor_geometry()
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

Index of the primary selected annotation, or `None`.

<details>
<summary>Code:</summary>

```python
def selected_index(self) -> int | None:
        return self._selected_index
```

</details>

### ⚙️ Method `selected_indices (property)`

```python
def selected_indices(self) -> set[int]
```

Indices of every selected annotation.

<details>
<summary>Code:</summary>

```python
def selected_indices(self) -> set[int]:
        return self._selection()
```

</details>

### ⚙️ Method `send_backward`

```python
def send_backward(self) -> bool
```

Move the selection one step toward the back.

<details>
<summary>Code:</summary>

```python
def send_backward(self) -> bool:
        return self._apply_z_order(lambda doc, indices: doc.send_backward(indices))
```

</details>

### ⚙️ Method `send_to_back`

```python
def send_to_back(self) -> bool
```

Move the selection to the back.

<details>
<summary>Code:</summary>

```python
def send_to_back(self) -> bool:
        return self._apply_z_order(lambda doc, indices: doc.send_to_back(indices))
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
        self.commit_text_edit()
        self._clear_edit_state()
        self._set_only_selection(None)
        self._document = document
        self._rebuild_snap_edges()
        self._refresh_pixmap()
```

</details>

### ⚙️ Method `set_style`

```python
def set_style(self, style: AnnotationStyle | None = None, *, color: QColor | None = None, width: float | None = None) -> None
```

Update style for new annotations and the active text editor.

<details>
<summary>Code:</summary>

```python
def set_style(
        self,
        style: AnnotationStyle | None = None,
        *,
        color: QColor | None = None,
        width: float | None = None,
    ) -> None:
        if style is not None:
            self._style = copy_annotation_style(style)
        if color is not None:
            self._style.color = QColor(color)
        if width is not None:
            self._style.width = max(1.0, width)
        self._sync_text_editor_style()
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
        if tool != AnnotationTool.TEXT and self._text_edit_active:
            self.commit_text_edit()
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
            self._set_only_selection(None)
        if tool == AnnotationTool.EYEDROPPER:
            self._set_only_selection(None)
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

### ⚙️ Method `undo`

```python
def undo(self) -> bool
```

Undo the last change on this canvas's document.

<details>
<summary>Code:</summary>

```python
def undo(self) -> bool:
        document = self._document
        if document is None or not document.undo():
            return False
        self._clear_edit_state()
        self._set_only_selection(None)
        self._refresh_pixmap()
        self.document_changed.emit()
        return True
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
        self._sync_text_editor_geometry()
        self.update()
```

</details>

### ⚙️ Method `zoom_in`

```python
def zoom_in(self) -> None
```

Zoom in one step around the center, matching one Ctrl+wheel notch.

<details>
<summary>Code:</summary>

```python
def zoom_in(self) -> None:
        self.zoom_by(_ZOOM_STEP)
```

</details>

### ⚙️ Method `zoom_out`

```python
def zoom_out(self) -> None
```

Zoom out one step around the center, matching one Ctrl+wheel notch.

<details>
<summary>Code:</summary>

```python
def zoom_out(self) -> None:
        self.zoom_by(1.0 / _ZOOM_STEP)
```

</details>
