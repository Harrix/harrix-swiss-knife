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
  - [⚙️ Method `adjust_mode (property)`](#%EF%B8%8F-method-adjust_mode-property)
  - [⚙️ Method `clipboard_only (property)`](#%EF%B8%8F-method-clipboard_only-property)
  - [⚙️ Method `cropped_image (property)`](#%EF%B8%8F-method-cropped_image-property)
  - [⚙️ Method `event`](#%EF%B8%8F-method-event)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `guides_mode (property)`](#%EF%B8%8F-method-guides_mode-property)
  - [⚙️ Method `hideEvent`](#%EF%B8%8F-method-hideevent)
  - [⚙️ Method `keep_windows (property)`](#%EF%B8%8F-method-keep_windows-property)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `mouseDoubleClickEvent`](#%EF%B8%8F-method-mousedoubleclickevent)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `paint_screen_pane`](#%EF%B8%8F-method-paint_screen_pane)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)

</details>

## 🏛️ Class `RegionOverlay`

```python
class RegionOverlay(QDialog)
```

Overlay that shows a frozen desktop grab and lets the user select a region.

With `with_shutter_controls=True`, arrange/adjust/guides/keep-Windows/
clipboard/close buttons are embedded as child widgets. Arrange finishes
with `RESULT_TOGGLE_ARRANGE`. Keep Windows finishes with
`RESULT_TOGGLE_KEEP_WINDOWS` so the capture loop can hide or restore app
Windows and grab again. Clipboard-only skips the preview after capture.
Adjust (checkable) keeps the next selection editable: move/resize with
handles, Enter or double-click to capture. Double-click the width or height
numbers (when guides are on) to type a size; Enter or a click elsewhere
applies it. Guides (checkable) draw a thinner frame with thirds, halves,
diagonal, size, and angle.

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
        screen_grabs: Sequence[ScreenGrab] | None = None,
        with_shutter_controls: bool = False,
        window_rects: Sequence[QRect] | None = None,
        keep_windows: bool = False,
        clipboard_only: bool = False,
        adjust_mode: bool = False,
        guides_mode: bool = False,
    ) -> None:
        """Create a fullscreen overlay for region selection, displaying the frozen desktop.

        Args:

        - `frozen` (`QPixmap`): Stitched screenshot of the virtual desktop to display as background.
        - `geometry` (`QRect`): The target geometry in global (screen) coordinates for overlay placement.
        - `screen_grabs` (`Sequence[ScreenGrab] | None`): Native per-monitor grabs. When set,
          each screen gets its own fullscreen pane so mixed DPI layouts cover every pixel.
        - `with_shutter_controls` (`bool`): If `True`, embed shutter controls on the left edge.
        - `window_rects` (`Sequence[QRect] | None`): Snappable window bounds in global logical pixels.
        - `keep_windows` (`bool`): If `True`, start with the keep-Windows shutter button on.
        - `clipboard_only` (`bool`): If `True`, start with the clipboard-only shutter button on.
        - `adjust_mode` (`bool`): If `True`, start with adjust-region enabled.
        - `guides_mode` (`bool`): If `True`, start with composition guides enabled.

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
        self._virtual_origin = geometry.topLeft()
        self._desktop_rect = QRect(0, 0, geometry.width(), geometry.height())
        self._screen_grabs: tuple[ScreenGrab, ...] = tuple(screen_grabs or ())
        self._panes: list[_ScreenPane] = []
        if self._screen_grabs:
            self.setGeometry(QRect(-16, -16, 1, 1))
        else:
            self.setGeometry(geometry)

        self._frozen = frozen
        self._origin: QPoint | None = None
        self._current: QPoint | None = None
        self._crop: QImage | None = None
        self._dragging = False
        self._snap_rect: QRect | None = None
        self._panel: ShutterPanel | None = None
        self._keep_windows = keep_windows
        self._clipboard_only = clipboard_only
        self._guides_enabled = False
        self._edit_rect: QRect | None = None
        self._edit_handle: HandleKind | None = None
        self._edit_press_pos: QPoint | None = None
        self._edit_press_rect: QRect | None = None
        self._size_edit_kind: SizeLabelKind | None = None
        self._size_edit_closing = False
        self._suppress_confirm_once = False
        self._size_editor = self._make_size_editor()
        origin = geometry.topLeft()
        self._window_rects_local = [
            rect.translated(-origin.x(), -origin.y()).intersected(self._desktop_rect) for rect in (window_rects or ())
        ]
        self._window_rects_local = [rect for rect in self._window_rects_local if rect.isValid() and not rect.isEmpty()]
        self._snap_x_edges, self._snap_y_edges = collect_edge_guides(self._window_rects_local, self._desktop_rect)

        if self._screen_grabs:
            self._panes = [_ScreenPane(self, grab) for grab in self._screen_grabs]

        if with_shutter_controls:
            panel_parent: QWidget = self._primary_pane() or self
            panel = ShutterPanel(panel_parent)
            panel.set_mode("selection")
            panel.set_keep_windows(enabled=keep_windows)
            panel.set_clipboard_only(enabled=clipboard_only)
            panel.triggered.connect(lambda: self.done(RESULT_TOGGLE_ARRANGE))
            panel.cancelled.connect(self.reject)
            panel.keep_windows_toggled.connect(lambda _enabled: self.done(RESULT_TOGGLE_KEEP_WINDOWS))
            panel.guides_toggled.connect(lambda enabled: self._set_guides_enabled(enabled=enabled))
            panel.geometry_changed.connect(lambda: position_panel_on_left_edge(panel, geometry))
            if adjust_mode:
                panel.set_adjust_mode(enabled=True)
            if guides_mode:
                panel.set_guides_mode(enabled=True)
            position_panel_on_left_edge(panel, geometry)
            panel.show()
            self._panel = panel

    @property
    def adjust_mode(self) -> bool:
        """Whether the next selection should stay editable until confirmed."""
        return self._panel is not None and self._panel.adjust_mode

    @property
    def clipboard_only(self) -> bool:
        """Whether capture should skip the preview and only copy to the clipboard."""
        if self._panel is not None:
            return self._panel.clipboard_only
        return self._clipboard_only

    @property
    def cropped_image(self) -> QImage | None:
        """Return the selected crop, or `None` if cancelled / empty."""
        return self._crop

    def event(self, event: QEvent) -> bool:
        """Accept Escape as a shortcut override so it is not stolen by other Windows.

        Args:

        - `event` (`QEvent`): The event being delivered to the overlay.

        """
        editor = getattr(self, "_size_editor", None)
        if editor is not None and editor.isVisible() and event.type() == QEvent.Type.ShortcutOverride:
            return super().event(event)
        if event.type() == QEvent.Type.ShortcutOverride and (
            _is_escape_key(event) or _is_arrow_key(event) or _is_enter_key(event)
        ):
            event.accept()
            return True
        return super().event(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Escape cancels the typed size; Enter applies it without capturing."""
        if watched is self._size_editor and event.type() == QEvent.Type.KeyPress:
            if _is_escape_key(event):
                self._cancel_size_edit()
                return True
            if _is_enter_key(event):
                self._commit_size_edit(from_enter=True)
                return True
        return super().eventFilter(watched, event)

    @property
    def guides_mode(self) -> bool:
        """Whether composition guides are drawn on the selection frame."""
        return self._guides_enabled

    def hideEvent(self, event: QHideEvent) -> None:  # noqa: N802
        """Release the keyboard grab when the overlay is hidden."""
        self._close_size_editor()
        release_screenshot_keyboard(self)
        for pane in self._panes:
            pane.hide()
        super().hideEvent(event)

    @property
    def keep_windows(self) -> bool:
        """Whether application Windows should stay visible in the next grab."""
        if self._panel is not None:
            return self._panel.keep_windows
        return self._keep_windows

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Enter confirms; arrows nudge/resize; Escape clears the frame or cancels."""
        if self._size_editor.isVisible():
            if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
                self._commit_size_edit(from_enter=True)
                event.accept()
                return
            if event.key() == Qt.Key.Key_Escape:
                self._cancel_size_edit()
                event.accept()
                return
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter} and self._edit_rect is not None:
            if self._suppress_confirm_once:
                self._suppress_confirm_once = False
                event.accept()
                return
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
        direction = _ARROW_KEYS.get(event.key())
        if direction is not None and self._edit_rect is not None:
            self._nudge_edit_rect(direction, event.modifiers())
            event.accept()
            return
        super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Double-click a size number to type it, or the frame to capture."""
        if event.button() != Qt.MouseButton.LeftButton or self._edit_rect is None:
            return
        pos = self._event_virtual_pos(event)
        kind = self._hit_size_label(pos)
        if kind is not None:
            self._start_size_edit(kind)
            event.accept()
            return
        if self._edit_rect.contains(pos):
            self._finish_with_rect(self._edit_rect)
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Update snap, free-drag selection, or editable frame move/resize."""
        pos = self._event_virtual_pos(event)

        if self._edit_rect is not None:
            if self._edit_handle is not None and self._edit_press_pos is not None and self._edit_press_rect is not None:
                transformed = transform_selection_rect(
                    self._edit_press_rect,
                    self._edit_handle,
                    self._edit_press_pos,
                    pos,
                    bounds=self._desktop_rect,
                    min_size=_MIN_SELECTION,
                )
                self._edit_rect = snap_rect_to_edges(
                    transformed,
                    self._edit_handle,
                    self._snap_x_edges,
                    self._snap_y_edges,
                    threshold=_EDGE_SNAP_THRESHOLD,
                    bounds=self._desktop_rect,
                    min_size=_MIN_SELECTION,
                )
                self._repaint_surfaces()
                return
            if self._hit_size_label(pos) is not None:
                self._set_overlay_cursor(Qt.CursorShape.IBeamCursor)
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
        self._repaint_surfaces()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start free selection, snap capture, or begin editing an adjustable frame."""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = self._event_virtual_pos(event)

        if self._size_editor.isVisible():
            self._commit_size_edit()
        if self._edit_rect is not None:
            if self._hit_size_label(pos) is not None:
                return
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
        self._repaint_surfaces()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Finish free selection, enter edit mode, or end a frame edit drag."""
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if self._edit_rect is not None:
            self._edit_handle = None
            self._edit_press_pos = None
            self._edit_press_rect = None
            self._apply_edit_cursor(hit_test_selection_handle(self._edit_rect, self._event_virtual_pos(event)))
            self._repaint_surfaces()
            return

        if self._origin is None:
            return

        pos = self._event_virtual_pos(event)
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
            self._repaint_surfaces()
            return

        if capture_rect.width() < _MIN_SELECTION or capture_rect.height() < _MIN_SELECTION:
            self._crop = None
            if was_dragging:
                self.reject()
            else:
                self._update_snap_at(pos)
                self._repaint_surfaces()
            return

        if self._adjust_mode_enabled():
            self._enter_edit_rect(capture_rect)
            return

        self._finish_with_rect(capture_rect)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Draw frozen desktop, dim overlay, selection/snap, and edit handles."""
        if self._panes:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=False)
        self._paint_surface(
            painter,
            self.rect(),
            self._frozen,
            pixmap_device_pixel_ratio(self._frozen),
            QPoint(0, 0),
        )

    def paint_screen_pane(self, pane: _ScreenPane) -> None:
        """Paint one monitor pane with that screen's grab and the shared selection."""
        grab = pane.grab
        painter = QPainter(pane)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=False)
        offset = grab.geometry.topLeft() - self._virtual_origin
        self._paint_surface(painter, pane.rect(), grab.pixmap, grab.dpr, offset)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Take keyboard focus so Escape cancels capture on Tool overlays."""
        super().showEvent(event)
        for pane in self._panes:
            pane.show()
            pane.raise_()
        claim_screenshot_keyboard(self)
        self._update_snap_at(self._global_to_virtual(QCursor.pos()))

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
        self._set_overlay_cursor(getattr(Qt.CursorShape, cursor_for_handle(handle)))

    def _cancel_size_edit(self) -> None:
        self._close_size_editor()

    def _clear_edit_rect(self) -> None:
        self._close_size_editor()
        self._edit_rect = None
        self._edit_handle = None
        self._edit_press_pos = None
        self._edit_press_rect = None
        self._set_overlay_cursor(Qt.CursorShape.CrossCursor)
        if self._panel is not None:
            self._panel.set_edit_keys_visible(visible=False)
        self._update_snap_at(self._global_to_virtual(QCursor.pos()))
        self._repaint_surfaces()

    def _clear_suppress_confirm(self) -> None:
        self._suppress_confirm_once = False

    def _close_size_editor(self) -> None:
        if self._size_edit_closing:
            return
        self._size_edit_closing = True
        try:
            self._size_edit_kind = None
            if self._size_editor.isVisible():
                self._size_editor.hide()
            if QWidget.keyboardGrabber() is self._size_editor:
                self._size_editor.releaseKeyboard()
            if self.isVisible() and QWidget.keyboardGrabber() is None:
                QTimer.singleShot(0, self._restore_overlay_keyboard)
            self._repaint_surfaces()
        finally:
            self._size_edit_closing = False

    def _commit_size_edit(self, *, from_enter: bool = False) -> None:
        if self._size_edit_closing:
            return
        kind = self._size_edit_kind
        rect = self._edit_rect
        text = self._size_editor.text()
        if from_enter:
            self._suppress_confirm_once = True
            QTimer.singleShot(0, self._clear_suppress_confirm)
        self._close_size_editor()
        if kind is None or rect is None:
            return
        parsed = parse_size_label(text)
        if parsed is None:
            return
        self._edit_rect = resize_selection_to_size(
            rect,
            width=parsed if kind == "width" else None,
            height=parsed if kind == "height" else None,
            bounds=self._desktop_rect,
            min_size=_MIN_SELECTION,
        )
        self._repaint_surfaces()

    def _enter_edit_rect(self, rect: QRect) -> None:
        self._close_size_editor()
        self._edit_rect = QRect(rect)
        self._snap_rect = None
        self._origin = None
        self._current = None
        self._dragging = False
        self._snap_x_edges, self._snap_y_edges = collect_edge_guides(self._window_rects_local, self._desktop_rect)
        if self._panel is not None:
            self._panel.set_edit_keys_visible(visible=True)
        self._apply_edit_cursor(hit_test_selection_handle(self._edit_rect, self._global_to_virtual(QCursor.pos())))
        self._repaint_surfaces()

    def _event_virtual_pos(self, event: QMouseEvent) -> QPoint:
        if self._panes:
            return self._global_to_virtual(event.globalPosition().toPoint())
        return event.position().toPoint()

    def _finish_with_rect(self, rect: QRect) -> None:
        """Crop `rect` from the frozen desktop and accept the dialog."""
        if self._screen_grabs:
            self._crop = crop_from_mixed_dpi_grabs(rect.translated(self._virtual_origin), self._screen_grabs)
        else:
            self._crop = crop_pixmap_from_logical_rect(self._frozen, rect)
        if self._crop is None or self._crop.isNull():
            self._crop = None
            self.reject()
            return
        self.accept()

    def _global_to_virtual(self, global_pos: QPoint) -> QPoint:
        return QPoint(global_pos.x() - self._virtual_origin.x(), global_pos.y() - self._virtual_origin.y())

    def _guide_metrics(self) -> QFontMetrics:
        return QFontMetrics(guide_label_font(self.font()))

    def _hit_size_label(self, pos: QPoint) -> SizeLabelKind | None:
        if self._edit_rect is None or not self._guides_enabled:
            return None
        return hit_test_size_label(self._edit_rect, self._desktop_rect, pos, self._guide_metrics())

    def _make_size_editor(self) -> QLineEdit:
        editor = QLineEdit(self)
        editor.hide()
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        editor.setMaxLength(5)
        editor.setStyleSheet(_SIZE_EDITOR_STYLE)
        editor.setFont(guide_label_font(self.font()))
        editor.editingFinished.connect(self._commit_size_edit)
        editor.installEventFilter(self)
        return editor

    def _nudge_edit_rect(self, direction: ArrowDir, modifiers: Qt.KeyboardModifier) -> None:
        if self._edit_rect is None:
            return
        step = _ARROW_STEP_SHIFT if modifiers & Qt.KeyboardModifier.ShiftModifier else _ARROW_STEP
        resize = bool(modifiers & Qt.KeyboardModifier.ControlModifier)
        self._edit_rect = nudge_selection_rect(
            self._edit_rect,
            direction,
            step=step,
            resize=resize,
            bounds=self._desktop_rect,
            min_size=_MIN_SELECTION,
        )
        self._repaint_surfaces()

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

    def _paint_surface(
        self,
        painter: QPainter,
        widget_rect: QRect,
        pixmap: QPixmap,
        dpr: float,
        pane_offset: QPoint,
    ) -> None:
        painter.drawPixmap(widget_rect, pixmap)
        painter.fillRect(widget_rect, _DIM_COLOR)
        rect = self._active_highlight_rect()
        if rect is None or not rect.isValid():
            return
        local = rect.translated(-pane_offset)
        source = logical_rect_to_pixel_rect(local, dpr)
        painter.drawPixmap(local, pixmap, source)
        guides_on = self._guides_enabled
        pen = QPen(_BORDER_COLOR, _GUIDE_BORDER_WIDTH if guides_on else _BORDER_WIDTH)
        painter.setPen(pen)
        painter.drawRect(local.adjusted(0, 0, -1, -1))
        if guides_on:
            skip = self._size_edit_kind if self._size_editor.isVisible() else None
            paint_selection_guides(painter, local, widget_rect, skip_size=skip)
        if self._edit_rect is not None:
            self._paint_edit_handles(painter, local)

    def _pane_at_virtual(self, pos: QPoint) -> _ScreenPane | None:
        global_pos = QPoint(pos.x() + self._virtual_origin.x(), pos.y() + self._virtual_origin.y())
        for pane in self._panes:
            if pane.grab.geometry.contains(global_pos):
                return pane
        return None

    def _primary_pane(self) -> _ScreenPane | None:
        if not self._panes:
            return None
        primary = QApplication.primaryScreen()
        if primary is not None:
            primary_geo = primary.geometry()
            for pane, grab in zip(self._panes, self._screen_grabs, strict=True):
                if grab.geometry == primary_geo:
                    return pane
        return self._panes[0]

    def _repaint_surfaces(self) -> None:
        """Repaint the dialog and every per-monitor pane."""
        super().update()
        for pane in self._panes:
            pane.update()

    def _restore_overlay_keyboard(self) -> None:
        if not self.isVisible() or self._size_editor.isVisible():
            return
        if QWidget.keyboardGrabber() is None:
            self.grabKeyboard()
            self.setFocus(Qt.FocusReason.OtherFocusReason)

    def _selection_rect(self) -> QRect | None:
        if self._origin is None or self._current is None:
            return None
        return QRect(self._origin, self._current).normalized()

    def _set_guides_enabled(self, *, enabled: bool) -> None:
        self._guides_enabled = enabled
        if not enabled:
            self._close_size_editor()
        self._repaint_surfaces()

    def _set_overlay_cursor(self, shape: Qt.CursorShape) -> None:
        self.setCursor(shape)
        for pane in self._panes:
            pane.setCursor(shape)

    def _size_editor_geometry(self, box: QRect, bounds: QRect | None = None) -> QRect:
        metrics = self._guide_metrics()
        min_width = metrics.horizontalAdvance(_SIZE_EDITOR_MIN_DIGITS) + _SIZE_EDITOR_PAD_X
        width = max(box.width() + _SIZE_EDITOR_PAD_X, min_width)
        height = max(box.height() + _SIZE_EDITOR_PAD_Y, metrics.height() + _SIZE_EDITOR_PAD_Y)
        geo = QRect(box.center().x() - width // 2, box.center().y() - height // 2, width, height)
        area = bounds if bounds is not None else self._desktop_rect
        if geo.left() < area.left():
            geo.moveLeft(area.left())
        if geo.top() < area.top():
            geo.moveTop(area.top())
        if geo.right() > area.right():
            geo.moveRight(area.right())
        if geo.bottom() > area.bottom():
            geo.moveBottom(area.bottom())
        return geo

    def _size_label_box(self, kind: SizeLabelKind) -> QRect:
        if self._edit_rect is None:
            return QRect()
        width_label, height_label, _, _ = selection_guide_labels(
            self._edit_rect,
            self._desktop_rect,
            self._guide_metrics(),
        )
        return width_label.box if kind == "width" else height_label.box

    def _start_size_edit(self, kind: SizeLabelKind) -> None:
        if self._edit_rect is None:
            return
        if self._size_editor.isVisible():
            self._commit_size_edit()
        self._size_edit_kind = kind
        value = self._edit_rect.width() if kind == "width" else self._edit_rect.height()
        max_value = self._desktop_rect.width() if kind == "width" else self._desktop_rect.height()
        self._size_editor.setValidator(QIntValidator(_MIN_SELECTION, max_value, self._size_editor))
        self._size_editor.setFont(guide_label_font(self.font()))
        box = self._size_label_box(kind)
        pane = self._pane_at_virtual(box.center())
        if pane is not None:
            self._size_editor.setParent(pane)
            offset = pane.grab.geometry.topLeft() - self._virtual_origin
            local_box = box.translated(-offset.x(), -offset.y())
            self._size_editor.setGeometry(self._size_editor_geometry(local_box, pane.rect()))
        else:
            self._size_editor.setParent(self)
            self._size_editor.setGeometry(self._size_editor_geometry(box))
        self._size_editor.setText(str(value))
        self._size_editor.show()
        self._size_editor.raise_()
        if QWidget.keyboardGrabber() is self:
            self.releaseKeyboard()
        self._size_editor.setFocus(Qt.FocusReason.MouseFocusReason)
        self._size_editor.selectAll()
        self._size_editor.grabKeyboard()
        self._repaint_surfaces()

    def _update_snap_at(self, pos: QPoint) -> None:
        """Refresh the hover snap rectangle for `pos` and repaint when it changes."""
        if self._edit_rect is not None:
            return
        new_snap = snap_rect_at_point(pos, self._window_rects_local)
        if new_snap == self._snap_rect:
            return
        self._snap_rect = new_snap
        self._repaint_surfaces()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, frozen: QPixmap, geometry: QRect, *, screen_grabs: Sequence[ScreenGrab] | None = None, with_shutter_controls: bool = False, window_rects: Sequence[QRect] | None = None, keep_windows: bool = False, clipboard_only: bool = False, adjust_mode: bool = False, guides_mode: bool = False) -> None
```

Create a fullscreen overlay for region selection, displaying the frozen desktop.

Args:

- `frozen` (`QPixmap`): Stitched screenshot of the virtual desktop to display as background.
- `geometry` (`QRect`): The target geometry in global (screen) coordinates for overlay placement.
- `screen_grabs` (`Sequence[ScreenGrab] | None`): Native per-monitor grabs. When set,
  each screen gets its own fullscreen pane so mixed DPI layouts cover every pixel.
- `with_shutter_controls` (`bool`): If `True`, embed shutter controls on the left edge.
- `window_rects` (`Sequence[QRect] | None`): Snappable window bounds in global logical pixels.
- `keep_windows` (`bool`): If `True`, start with the keep-Windows shutter button on.
- `clipboard_only` (`bool`): If `True`, start with the clipboard-only shutter button on.
- `adjust_mode` (`bool`): If `True`, start with adjust-region enabled.
- `guides_mode` (`bool`): If `True`, start with composition guides enabled.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        frozen: QPixmap,
        geometry: QRect,
        *,
        screen_grabs: Sequence[ScreenGrab] | None = None,
        with_shutter_controls: bool = False,
        window_rects: Sequence[QRect] | None = None,
        keep_windows: bool = False,
        clipboard_only: bool = False,
        adjust_mode: bool = False,
        guides_mode: bool = False,
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
        self._virtual_origin = geometry.topLeft()
        self._desktop_rect = QRect(0, 0, geometry.width(), geometry.height())
        self._screen_grabs: tuple[ScreenGrab, ...] = tuple(screen_grabs or ())
        self._panes: list[_ScreenPane] = []
        if self._screen_grabs:
            self.setGeometry(QRect(-16, -16, 1, 1))
        else:
            self.setGeometry(geometry)

        self._frozen = frozen
        self._origin: QPoint | None = None
        self._current: QPoint | None = None
        self._crop: QImage | None = None
        self._dragging = False
        self._snap_rect: QRect | None = None
        self._panel: ShutterPanel | None = None
        self._keep_windows = keep_windows
        self._clipboard_only = clipboard_only
        self._guides_enabled = False
        self._edit_rect: QRect | None = None
        self._edit_handle: HandleKind | None = None
        self._edit_press_pos: QPoint | None = None
        self._edit_press_rect: QRect | None = None
        self._size_edit_kind: SizeLabelKind | None = None
        self._size_edit_closing = False
        self._suppress_confirm_once = False
        self._size_editor = self._make_size_editor()
        origin = geometry.topLeft()
        self._window_rects_local = [
            rect.translated(-origin.x(), -origin.y()).intersected(self._desktop_rect) for rect in (window_rects or ())
        ]
        self._window_rects_local = [rect for rect in self._window_rects_local if rect.isValid() and not rect.isEmpty()]
        self._snap_x_edges, self._snap_y_edges = collect_edge_guides(self._window_rects_local, self._desktop_rect)

        if self._screen_grabs:
            self._panes = [_ScreenPane(self, grab) for grab in self._screen_grabs]

        if with_shutter_controls:
            panel_parent: QWidget = self._primary_pane() or self
            panel = ShutterPanel(panel_parent)
            panel.set_mode("selection")
            panel.set_keep_windows(enabled=keep_windows)
            panel.set_clipboard_only(enabled=clipboard_only)
            panel.triggered.connect(lambda: self.done(RESULT_TOGGLE_ARRANGE))
            panel.cancelled.connect(self.reject)
            panel.keep_windows_toggled.connect(lambda _enabled: self.done(RESULT_TOGGLE_KEEP_WINDOWS))
            panel.guides_toggled.connect(lambda enabled: self._set_guides_enabled(enabled=enabled))
            panel.geometry_changed.connect(lambda: position_panel_on_left_edge(panel, geometry))
            if adjust_mode:
                panel.set_adjust_mode(enabled=True)
            if guides_mode:
                panel.set_guides_mode(enabled=True)
            position_panel_on_left_edge(panel, geometry)
            panel.show()
            self._panel = panel
```

</details>

### ⚙️ Method `adjust_mode (property)`

```python
def adjust_mode(self) -> bool
```

Whether the next selection should stay editable until confirmed.

<details>
<summary>Code:</summary>

```python
def adjust_mode(self) -> bool:
        return self._panel is not None and self._panel.adjust_mode
```

</details>

### ⚙️ Method `clipboard_only (property)`

```python
def clipboard_only(self) -> bool
```

Whether capture should skip the preview and only copy to the clipboard.

<details>
<summary>Code:</summary>

```python
def clipboard_only(self) -> bool:
        if self._panel is not None:
            return self._panel.clipboard_only
        return self._clipboard_only
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
        editor = getattr(self, "_size_editor", None)
        if editor is not None and editor.isVisible() and event.type() == QEvent.Type.ShortcutOverride:
            return super().event(event)
        if event.type() == QEvent.Type.ShortcutOverride and (
            _is_escape_key(event) or _is_arrow_key(event) or _is_enter_key(event)
        ):
            event.accept()
            return True
        return super().event(event)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Escape cancels the typed size; Enter applies it without capturing.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._size_editor and event.type() == QEvent.Type.KeyPress:
            if _is_escape_key(event):
                self._cancel_size_edit()
                return True
            if _is_enter_key(event):
                self._commit_size_edit(from_enter=True)
                return True
        return super().eventFilter(watched, event)
```

</details>

### ⚙️ Method `guides_mode (property)`

```python
def guides_mode(self) -> bool
```

Whether composition guides are drawn on the selection frame.

<details>
<summary>Code:</summary>

```python
def guides_mode(self) -> bool:
        return self._guides_enabled
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
        self._close_size_editor()
        release_screenshot_keyboard(self)
        for pane in self._panes:
            pane.hide()
        super().hideEvent(event)
```

</details>

### ⚙️ Method `keep_windows (property)`

```python
def keep_windows(self) -> bool
```

Whether application Windows should stay visible in the next grab.

<details>
<summary>Code:</summary>

```python
def keep_windows(self) -> bool:
        if self._panel is not None:
            return self._panel.keep_windows
        return self._keep_windows
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Enter confirms; arrows nudge/resize; Escape clears the frame or cancels.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if self._size_editor.isVisible():
            if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}:
                self._commit_size_edit(from_enter=True)
                event.accept()
                return
            if event.key() == Qt.Key.Key_Escape:
                self._cancel_size_edit()
                event.accept()
                return
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter} and self._edit_rect is not None:
            if self._suppress_confirm_once:
                self._suppress_confirm_once = False
                event.accept()
                return
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
        direction = _ARROW_KEYS.get(event.key())
        if direction is not None and self._edit_rect is not None:
            self._nudge_edit_rect(direction, event.modifiers())
            event.accept()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `mouseDoubleClickEvent`

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None
```

Double-click a size number to type it, or the frame to capture.

<details>
<summary>Code:</summary>

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton or self._edit_rect is None:
            return
        pos = self._event_virtual_pos(event)
        kind = self._hit_size_label(pos)
        if kind is not None:
            self._start_size_edit(kind)
            event.accept()
            return
        if self._edit_rect.contains(pos):
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
        pos = self._event_virtual_pos(event)

        if self._edit_rect is not None:
            if self._edit_handle is not None and self._edit_press_pos is not None and self._edit_press_rect is not None:
                transformed = transform_selection_rect(
                    self._edit_press_rect,
                    self._edit_handle,
                    self._edit_press_pos,
                    pos,
                    bounds=self._desktop_rect,
                    min_size=_MIN_SELECTION,
                )
                self._edit_rect = snap_rect_to_edges(
                    transformed,
                    self._edit_handle,
                    self._snap_x_edges,
                    self._snap_y_edges,
                    threshold=_EDGE_SNAP_THRESHOLD,
                    bounds=self._desktop_rect,
                    min_size=_MIN_SELECTION,
                )
                self._repaint_surfaces()
                return
            if self._hit_size_label(pos) is not None:
                self._set_overlay_cursor(Qt.CursorShape.IBeamCursor)
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
        self._repaint_surfaces()
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
        pos = self._event_virtual_pos(event)

        if self._size_editor.isVisible():
            self._commit_size_edit()
        if self._edit_rect is not None:
            if self._hit_size_label(pos) is not None:
                return
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
        self._repaint_surfaces()
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
            self._apply_edit_cursor(hit_test_selection_handle(self._edit_rect, self._event_virtual_pos(event)))
            self._repaint_surfaces()
            return

        if self._origin is None:
            return

        pos = self._event_virtual_pos(event)
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
            self._repaint_surfaces()
            return

        if capture_rect.width() < _MIN_SELECTION or capture_rect.height() < _MIN_SELECTION:
            self._crop = None
            if was_dragging:
                self.reject()
            else:
                self._update_snap_at(pos)
                self._repaint_surfaces()
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
        if self._panes:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=False)
        self._paint_surface(
            painter,
            self.rect(),
            self._frozen,
            pixmap_device_pixel_ratio(self._frozen),
            QPoint(0, 0),
        )
```

</details>

### ⚙️ Method `paint_screen_pane`

```python
def paint_screen_pane(self, pane: _ScreenPane) -> None
```

Paint one monitor pane with that screen's grab and the shared selection.

<details>
<summary>Code:</summary>

```python
def paint_screen_pane(self, pane: _ScreenPane) -> None:
        grab = pane.grab
        painter = QPainter(pane)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, on=False)
        offset = grab.geometry.topLeft() - self._virtual_origin
        self._paint_surface(painter, pane.rect(), grab.pixmap, grab.dpr, offset)
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
        for pane in self._panes:
            pane.show()
            pane.raise_()
        claim_screenshot_keyboard(self)
        self._update_snap_at(self._global_to_virtual(QCursor.pos()))
```

</details>
