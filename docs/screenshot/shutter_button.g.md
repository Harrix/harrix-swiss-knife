---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `shutter_button.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ArrangeModeDialog`](#%EF%B8%8F-class-arrangemodedialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `event`](#%EF%B8%8F-method-event)
  - [⚙️ Method `hideEvent`](#%EF%B8%8F-method-hideevent)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)
- [🏛️ Class `ShutterPanel`](#%EF%B8%8F-class-shutterpanel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `adjust_mode (property)`](#%EF%B8%8F-method-adjust_mode-property)
  - [⚙️ Method `apply_available_height`](#%EF%B8%8F-method-apply_available_height)
  - [⚙️ Method `clipboard_only (property)`](#%EF%B8%8F-method-clipboard_only-property)
  - [⚙️ Method `collapsed (property)`](#%EF%B8%8F-method-collapsed-property)
  - [⚙️ Method `guides_mode (property)`](#%EF%B8%8F-method-guides_mode-property)
  - [⚙️ Method `keep_windows (property)`](#%EF%B8%8F-method-keep_windows-property)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `ocr_translate (property)`](#%EF%B8%8F-method-ocr_translate-property)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `set_adjust_mode`](#%EF%B8%8F-method-set_adjust_mode)
  - [⚙️ Method `set_clipboard_only`](#%EF%B8%8F-method-set_clipboard_only)
  - [⚙️ Method `set_collapsed`](#%EF%B8%8F-method-set_collapsed)
  - [⚙️ Method `set_edit_keys_visible`](#%EF%B8%8F-method-set_edit_keys_visible)
  - [⚙️ Method `set_guides_mode`](#%EF%B8%8F-method-set_guides_mode)
  - [⚙️ Method `set_keep_windows`](#%EF%B8%8F-method-set_keep_windows)
  - [⚙️ Method `set_mode`](#%EF%B8%8F-method-set_mode)
  - [⚙️ Method `set_ocr_translate`](#%EF%B8%8F-method-set_ocr_translate)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent-1)
  - [⚙️ Method `user_moved (property)`](#%EF%B8%8F-method-user_moved-property)
- [🏛️ Class `ShutterSwitch`](#%EF%B8%8F-class-shutterswitch)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-1)
- [🏛️ Class `ShutterToggleControl`](#%EF%B8%8F-class-shuttertogglecontrol)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `isChecked`](#%EF%B8%8F-method-ischecked)
  - [⚙️ Method `setChecked`](#%EF%B8%8F-method-setchecked)
  - [⚙️ Method `toolTip`](#%EF%B8%8F-method-tooltip)
- [🔧 Function `position_panel_at_left_center`](#-function-position_panel_at_left_center)

</details>

## 🏛️ Class `ArrangeModeDialog`

```python
class ArrangeModeDialog(QDialog)
```

Small frameless stay-on-top dialog shown while the user arranges the desktop.

Runs via `exec()` so it becomes the newest application-modal window and
receives input above any concealed dialogs. Camera click accepts (back to
region selection), close or Escape rejects (cancel capture).

<details>
<summary>Code:</summary>

```python
class ArrangeModeDialog(QDialog):

    def __init__(self) -> None:
        """Create the arrange-mode controls dialog."""
        super().__init__(None)
        mark_screenshot_ui(self)
        self.setWindowFlags(frameless_stay_on_top_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        panel = ShutterPanel(self)
        panel.set_mode("arrange")
        panel.triggered.connect(self.accept)
        panel.cancelled.connect(self.reject)
        panel.geometry_changed.connect(self._fit_panel)
        self._panel = panel
        self._fit_panel()

    def event(self, event: QEvent) -> bool:
        """Accept Escape as a shortcut override so it is not stolen by other Windows.

        Args:

        - `event` (`QEvent`): The event being delivered to the dialog.

        """
        key = getattr(event, "key", None)
        if event.type() == QEvent.Type.ShortcutOverride and callable(key) and key() == Qt.Key.Key_Escape:
            event.accept()
            return True
        return super().event(event)

    def hideEvent(self, event: QHideEvent) -> None:  # noqa: N802
        """Release the keyboard grab when arrange mode is closed."""
        release_screenshot_keyboard(self)
        super().hideEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Escape cancels the screenshot capture."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Take keyboard focus so Escape cancels capture in arrange mode."""
        super().showEvent(event)
        claim_screenshot_keyboard(self)

    def _fit_panel(self) -> None:
        """Keep the dialog size matched to the panel (grows when a hint is shown)."""
        self._panel.apply_available_height(_primary_available_height())
        self.setMinimumSize(0, 0)
        self.setMaximumSize(_QWIDGETSIZE_MAX, _QWIDGETSIZE_MAX)
        hint = self._panel.sizeHint()
        self.setFixedSize(hint)
        self._position_on_primary_screen()

    def _position_on_primary_screen(self) -> None:
        """Place the controls at the left center unless the user dragged them."""
        if self._panel.user_moved:
            return
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.x() + TOOLBAR_EDGE_MARGIN
        y = geo.y() + (geo.height() - self.height()) // 2
        self.move(x, y)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Create the arrange-mode controls dialog.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        super().__init__(None)
        mark_screenshot_ui(self)
        self.setWindowFlags(frameless_stay_on_top_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        panel = ShutterPanel(self)
        panel.set_mode("arrange")
        panel.triggered.connect(self.accept)
        panel.cancelled.connect(self.reject)
        panel.geometry_changed.connect(self._fit_panel)
        self._panel = panel
        self._fit_panel()
```

</details>

### ⚙️ Method `event`

```python
def event(self, event: QEvent) -> bool
```

Accept Escape as a shortcut override so it is not stolen by other Windows.

Args:

- `event` (`QEvent`): The event being delivered to the dialog.

<details>
<summary>Code:</summary>

```python
def event(self, event: QEvent) -> bool:
        key = getattr(event, "key", None)
        if event.type() == QEvent.Type.ShortcutOverride and callable(key) and key() == Qt.Key.Key_Escape:
            event.accept()
            return True
        return super().event(event)
```

</details>

### ⚙️ Method `hideEvent`

```python
def hideEvent(self, event: QHideEvent) -> None
```

Release the keyboard grab when arrange mode is closed.

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

Escape cancels the screenshot capture.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

Take keyboard focus so Escape cancels capture in arrange mode.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        claim_screenshot_keyboard(self)
```

</details>

## 🏛️ Class `ShutterPanel`

```python
class ShutterPanel(QWidget)
```

Left-centered translucent tool panel, embeddable as a child.

Being a regular child widget (not a separate native window) guarantees that
clicks reach the buttons even when the application has modal dialogs in
`exec()` — the parent (overlay or arrange dialog) owns the modal input.

Tools sit in one rounded dark plate (same family as toasts). Action cells
show a left-aligned icon with the caption underneath. Toggle cells show a
left-aligned icon plus a large switch, with the caption under both.
Clipboard-only and OCR + translate are mutually exclusive. A collapse
control hides the tool list to a single expand cell. The plate can be
dragged so it does not cover the region being captured.

<details>
<summary>Code:</summary>

```python
class ShutterPanel(QWidget):

    adjust_toggled = Signal(bool)
    cancelled = Signal()
    geometry_changed = Signal()
    guides_toggled = Signal(bool)
    clipboard_toggled = Signal(bool)
    ocr_translate_toggled = Signal(bool)
    keep_windows_toggled = Signal(bool)
    triggered = Signal()

    def __init__(self, parent: QWidget | None = None, *, capture_options: bool = True) -> None:
        """Create the shutter panel with desktop/adjust/close controls.

        Args:

        - `parent` (`QWidget | None`): Parent widget.
        - `capture_options` (`bool`): When `False` (screen recording), hide Adjust /
          Show Harrix app / Clipboard / OCR — only Desktop, Guides, and Cancel remain.

        """
        super().__init__(parent)
        self.setObjectName("ShutterPanelRoot")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._capture_options = capture_options
        self._available_height = _primary_available_height()
        self._collapsed = False
        self._mode: ShutterMode = "selection"
        self._user_moved = False
        self._dragging = False
        self._drag_offset = QPoint()

        root = QVBoxLayout(self)
        root.setContentsMargins(_PANEL_PAD, _PANEL_PAD, _PANEL_PAD, _PANEL_PAD)
        root.setSpacing(_ROW_GAP)

        self._collapse_row, self._collapse_button, self._collapse_label = self._make_action_cell(
            _COLLAPSE_ICON,
            "Collapse",
            "Collapse tools panel",
        )
        self._collapse_button.clicked.connect(self._toggle_collapsed)
        root.addWidget(self._collapse_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._tools_host = QWidget(self)
        self._tools_host.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._tools_host.setAutoFillBackground(False)
        self._tools_host.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self._tools_layout = QVBoxLayout(self._tools_host)
        self._tools_layout.setContentsMargins(0, 0, 0, 0)
        self._tools_layout.setSpacing(_ROW_GAP)

        self._mode_row, self._mode_button, self._mode_label = self._make_action_cell(
            _ARRANGE_ICON,
            "Desktop",
            "Desktop — interact with other windows (OpenBoard-style)",
        )
        self._mode_button.clicked.connect(self.triggered.emit)
        self._tools_layout.addWidget(self._mode_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._adjust_row, self._adjust_button, self._adjust_label = self._make_toggle_cell(
            _ADJUST_ICON,
            "Adjust",
            "Adjust region after select (Enter confirms)",
        )
        self._adjust_button.toggled.connect(self.adjust_toggled.emit)
        self._tools_layout.addWidget(self._adjust_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._guides_row, self._guides_button, self._guides_label = self._make_toggle_cell(
            _GUIDES_ICON,
            "Guides",
            "Composition guides: thirds, diagonal, size, and angle",
        )
        self._guides_button.toggled.connect(self.guides_toggled.emit)
        self._tools_layout.addWidget(self._guides_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._keep_windows_row, self._keep_windows_button, self._keep_windows_label = self._make_toggle_cell(
            _KEEP_WINDOWS_ICON,
            "Show Harrix app",
            "Keep Harrix Swiss Knife windows visible in the screenshot",
        )
        self._keep_windows_button.toggled.connect(self.keep_windows_toggled.emit)
        self._tools_layout.addWidget(self._keep_windows_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._clipboard_row, self._clipboard_button, self._clipboard_label = self._make_toggle_cell(
            _CLIPBOARD_ICON,
            "Clipboard only",
            "Clipboard only (skip preview)",
        )
        self._clipboard_button.toggled.connect(lambda checked: self._on_clipboard_toggled(checked=checked))
        self._tools_layout.addWidget(self._clipboard_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._ocr_row, self._ocr_translate_button, self._ocr_label = self._make_toggle_cell(
            _OCR_TRANSLATE_ICON,
            "OCR + translate",
            "OCR + translate (skip preview)",
        )
        self._ocr_translate_button.toggled.connect(lambda checked: self._on_ocr_translate_toggled(checked=checked))
        self._tools_layout.addWidget(self._ocr_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._close_row, self._close_button, self._close_label = self._make_action_cell(
            _CLOSE_ICON,
            "Cancel",
            "Cancel" if not capture_options else "Cancel screenshot",
        )
        self._close_button.clicked.connect(self.cancelled.emit)
        self._tools_layout.addWidget(self._close_row, 0, Qt.AlignmentFlag.AlignLeft)

        root.addWidget(self._tools_host)

        self._edit_keys_label = QLabel(self)
        self._edit_keys_label.setStyleSheet(_HINT_STYLE)
        self._edit_keys_label.setWordWrap(True)
        self._edit_keys_label.setText(_EDIT_KEYS_TEXT)
        self._edit_keys_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._edit_keys_label.setMaximumWidth(_TOGGLE_CONTROLS_WIDTH)
        self._edit_keys_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._edit_keys_label.hide()
        root.addWidget(self._edit_keys_label, 0, Qt.AlignmentFlag.AlignLeft)

        self._apply_capture_option_visibility()
        self._update_size()
        # On standard (non-ultrawide) screens keep tools collapsed so the plate
        # does not cover as much of the capture area.
        if not _is_widescreen_monitor():
            self.set_collapsed(collapsed=True)

    @property
    def adjust_mode(self) -> bool:
        """Whether the next selection should stay editable until confirmed."""
        return self._mode == "selection" and self._adjust_button.isChecked()

    def apply_available_height(self, height: int) -> None:
        """Constrain the toolbar height on short screens."""
        clamped = max(TOOLBAR_BUTTON_SIZE + 2 * _PANEL_PAD, height)
        if clamped == self._available_height:
            return
        self._available_height = clamped
        self._update_size()

    @property
    def clipboard_only(self) -> bool:
        """Whether capture should skip the preview and only copy to the clipboard."""
        return self._mode == "selection" and self._clipboard_button.isChecked()

    @property
    def collapsed(self) -> bool:
        """Whether the tools list is hidden behind the expand control."""
        return self._collapsed

    @property
    def guides_mode(self) -> bool:
        """Whether the selection frame shows composition guides and measurements."""
        return self._mode == "selection" and self._guides_button.isChecked()

    @property
    def keep_windows(self) -> bool:
        """Whether Harrix Swiss Knife Windows should stay visible in the next grab."""
        return self._mode == "selection" and self._keep_windows_button.isChecked()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Drag the panel (or its top-level arrange dialog) with the left button."""
        if self._dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self._apply_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start dragging when the press is not on a button or switch."""
        if event.button() == Qt.MouseButton.LeftButton and not self._is_interactive_target(
            self.childAt(event.position().toPoint())
        ):
            self._dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self.mapToGlobal(QPoint(0, 0))
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Stop dragging."""
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    @property
    def ocr_translate(self) -> bool:
        """Whether capture should skip the preview and run OCR + translate."""
        return self._mode == "selection" and self._ocr_translate_button.isChecked()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Draw one rounded translucent plate behind all tools."""
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_PANEL_FILL)
        painter.drawRoundedRect(QRectF(self.rect()), _PANEL_RADIUS, _PANEL_RADIUS)
        painter.end()

    def set_adjust_mode(self, *, enabled: bool) -> None:
        """Set the adjust-region button without requiring a user click."""
        self._adjust_button.setChecked(enabled)

    def set_clipboard_only(self, *, enabled: bool) -> None:
        """Set the clipboard-only button without requiring a user click."""
        blocked = self._clipboard_button.blockSignals(True)  # noqa: FBT003
        try:
            self._clipboard_button.setChecked(enabled)
            if enabled:
                self._set_ocr_translate_checked(enabled=False)
        finally:
            self._clipboard_button.blockSignals(blocked)

    def set_collapsed(self, *, collapsed: bool) -> None:
        """Expand or collapse the tools list."""
        if collapsed == self._collapsed:
            return
        self._collapsed = collapsed
        self._set_row_visible(self._tools_host, visible=not collapsed)
        if collapsed:
            self.set_edit_keys_visible(visible=False)
        self._collapse_button.setIcon(
            create_lucide_icon(
                _EXPAND_ICON if collapsed else _COLLAPSE_ICON,
                TOOLBAR_ICON_SIZE,
                color=_ICON_COLOR,
            )
        )
        self._collapse_label.setText("Expand" if collapsed else "Collapse")
        self._fit_cell_label(self._collapse_label)
        hint = "Expand tools panel" if collapsed else "Collapse tools panel"
        self._collapse_button.setToolTip(hint)
        self._collapse_button.setProperty("hover_hint", hint)
        self._update_size()

    def set_edit_keys_visible(self, *, visible: bool) -> None:
        """Show or hide arrow/Shift/Ctrl hints under the shutter buttons."""
        if self._collapsed:
            visible = False
        if visible == self._edit_keys_label.isVisible():
            return
        self._set_row_visible(self._edit_keys_label, visible=visible)
        self._update_size()

    def set_guides_mode(self, *, enabled: bool) -> None:
        """Set the composition-guides button without requiring a user click."""
        self._guides_button.setChecked(enabled)

    def set_keep_windows(self, *, enabled: bool) -> None:
        """Set the show-app button without emitting `keep_windows_toggled`."""
        blocked = self._keep_windows_button.blockSignals(True)  # noqa: FBT003
        try:
            self._keep_windows_button.setChecked(enabled)
        finally:
            self._keep_windows_button.blockSignals(blocked)

    def set_mode(self, mode: ShutterMode) -> None:
        """Update the mode button for selection vs desktop interaction."""
        self._mode = mode
        if mode == "selection":
            self._mode_button.setIcon(create_lucide_icon(_ARRANGE_ICON, TOOLBAR_ICON_SIZE, color=_ICON_COLOR))
            self._mode_label.setText("Desktop")
            self._fit_cell_label(self._mode_label)
            tip = "Desktop — interact with other windows (OpenBoard-style)"
            self._mode_button.setToolTip(tip)
            self._mode_button.setProperty("hover_hint", tip)
            self._set_row_visible(self._guides_row, visible=True)
            self._apply_capture_option_visibility()
        else:
            self._mode_button.setIcon(create_lucide_icon(_CAMERA_ICON, TOOLBAR_ICON_SIZE, color=_ICON_COLOR))
            label = "Capture" if self._capture_options else "Select"
            self._mode_label.setText(label)
            self._fit_cell_label(self._mode_label)
            tip = "Capture region" if self._capture_options else "Select region"
            self._mode_button.setToolTip(tip)
            self._mode_button.setProperty("hover_hint", tip)
            self._set_row_visible(self._adjust_row, visible=False)
            self._adjust_button.setChecked(False)
            self._set_row_visible(self._guides_row, visible=False)
            self._guides_button.setChecked(False)
            self._set_row_visible(self._keep_windows_row, visible=False)
            self._set_row_visible(self._clipboard_row, visible=False)
            self._set_row_visible(self._ocr_row, visible=False)
            self.set_edit_keys_visible(visible=False)
        self._update_size()

    def set_ocr_translate(self, *, enabled: bool) -> None:
        """Set the OCR + translate button without requiring a user click."""
        blocked = self._ocr_translate_button.blockSignals(True)  # noqa: FBT003
        try:
            self._ocr_translate_button.setChecked(enabled)
            if enabled:
                self._set_clipboard_checked(enabled=False)
        finally:
            self._ocr_translate_button.blockSignals(blocked)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Recompute size after the first show — layout hints ignore hidden rows only then."""
        super().showEvent(event)
        self._update_size()

    @property
    def user_moved(self) -> bool:
        """Whether the user dragged the panel away from the default spot."""
        return self._user_moved

    def _apply_capture_option_visibility(self) -> None:
        show = self._capture_options and self._mode == "selection"
        self._set_row_visible(self._adjust_row, visible=show)
        self._set_row_visible(self._keep_windows_row, visible=show)
        self._set_row_visible(self._clipboard_row, visible=show)
        self._set_row_visible(self._ocr_row, visible=show)
        if not show:
            self._adjust_button.setChecked(False)
            self._keep_windows_button.setChecked(False)
            self._clipboard_button.setChecked(False)
            self._ocr_translate_button.setChecked(False)
            self.set_edit_keys_visible(visible=False)

    def _apply_drag(self, global_mouse: QPoint) -> None:
        self._user_moved = True
        new_global = global_mouse - self._drag_offset
        window = self.window()
        if isinstance(window, ArrangeModeDialog):
            window.move(new_global)
            return
        parent = self.parentWidget()
        if parent is not None:
            self.move(parent.mapFromGlobal(new_global))
        else:
            self.move(new_global)

    def _cell_labels(self) -> tuple[QLabel, ...]:
        names = (
            "_collapse_label",
            "_mode_label",
            "_adjust_label",
            "_guides_label",
            "_keep_windows_label",
            "_clipboard_label",
            "_ocr_label",
            "_close_label",
        )
        return tuple(label for name in names if isinstance((label := getattr(self, name, None)), QLabel))

    def _fit_all_cell_labels(self) -> None:
        """Recompute caption widths after collapse/expand or text changes."""
        column = self._label_column_width()
        for label in self._cell_labels():
            self._fit_cell_label(label, column_width=column)
        self._edit_keys_label.setMaximumWidth(column)

    def _fit_cell_label(self, text: QLabel, *, column_width: int | None = None) -> None:
        """Size a caption so painted text fits; use the tool column when expanded.

        Font size/weight live on the `QFont` (not only in a stylesheet) so
        `fontMetrics` matches what is drawn. Expanded tools share one column
        wide enough for single-word captions (e.g. Collapse); collapsed mode
        keeps a narrow natural width.

        """
        tools_host = getattr(self, "_tools_host", None)
        collapsed = getattr(self, "_collapsed", False)
        if not collapsed and tools_host is not None and not tools_host.isHidden():
            # During `__init__` not every cell label exists yet; use the toggle
            # floor until `_fit_all_cell_labels` runs with the full set.
            width = column_width if column_width is not None else _TOGGLE_CONTROLS_WIDTH
            text.setFixedWidth(width)
            return
        metrics = text.fontMetrics()
        natural = metrics.horizontalAdvance(text.text()) + _CELL_LABEL_PAD
        text.setFixedWidth(max(TOOLBAR_BUTTON_SIZE, natural))

    def _is_interactive_target(self, widget: QWidget | None) -> bool:
        current = widget
        while current is not None and current is not self:
            if isinstance(current, (QPushButton, ShutterSwitch, ShutterToggleControl)):
                return True
            current = current.parentWidget()
        return False

    def _label_column_width(self) -> int:
        """Toggle-row width, expanded so single-word captions are not clipped."""
        width = _TOGGLE_CONTROLS_WIDTH
        for label in self._cell_labels():
            caption = label.text().strip()
            if not caption or " " in caption:
                continue
            width = max(width, label.fontMetrics().horizontalAdvance(caption) + _CELL_LABEL_PAD)
        return width

    def _make_action_cell(self, icon_name: str, label: str, tooltip: str) -> tuple[QWidget, QPushButton, QLabel]:
        cell = QWidget(self)
        cell.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        cell.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        layout = QVBoxLayout(cell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        button = self._make_icon_button(icon_name, tooltip)
        text = self._make_cell_label(label, cell)
        layout.addWidget(button, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(text, 0, Qt.AlignmentFlag.AlignLeft)
        return cell, button, text

    def _make_cell_label(self, label: str, parent: QWidget) -> QLabel:
        text = QLabel(label, parent)
        font = QFont(text.font())
        font.setPointSizeF(_CELL_LABEL_POINT_SIZE)
        font.setWeight(QFont.Weight.DemiBold)
        text.setFont(font)
        text.setStyleSheet(_CELL_LABEL_STYLE)
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        text.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._fit_cell_label(text)
        return text

    def _make_icon_button(self, name: str, tooltip: str) -> QPushButton:
        button = QPushButton(self)
        button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
        button.setIcon(create_lucide_icon(name, TOOLBAR_ICON_SIZE, color=_ICON_COLOR))
        button.setIconSize(QSize(TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip(tooltip)
        button.setProperty("hover_hint", tooltip)
        button.setStyleSheet(_FLAT_BUTTON_STYLE)
        button.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
        return button

    def _make_toggle_cell(
        self, icon_name: str, label: str, tooltip: str
    ) -> tuple[QWidget, ShutterToggleControl, QLabel]:
        cell = QWidget(self)
        cell.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        cell.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        layout = QVBoxLayout(cell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        control = ShutterToggleControl(icon_name, tooltip, cell)
        text = self._make_cell_label(label, cell)
        layout.addWidget(control, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(text, 0, Qt.AlignmentFlag.AlignLeft)
        return cell, control, text

    def _on_clipboard_toggled(self, *, checked: bool) -> None:
        if checked:
            self._set_ocr_translate_checked(enabled=False)
        self.clipboard_toggled.emit(checked)

    def _on_ocr_translate_toggled(self, *, checked: bool) -> None:
        if checked:
            self._set_clipboard_checked(enabled=False)
        self.ocr_translate_toggled.emit(checked)

    def _preferred_size(self) -> QSize:
        """Size from non-hidden rows only (`isHidden`, not `isVisible`).

        Before the panel is shown, `sizeHint()` still includes rows that were only
        marked invisible via ancestors, which left empty gaps in arrange mode.
        Width follows visible content so collapse is narrow and toggle rows define
        the expanded width — no reserved empty switch column.

        """
        parts: list[QWidget] = []
        if not self._collapse_row.isHidden():
            parts.append(self._collapse_row)
        if not self._tools_host.isHidden():
            tool_rows = (
                self._mode_row,
                self._adjust_row,
                self._guides_row,
                self._keep_windows_row,
                self._clipboard_row,
                self._ocr_row,
                self._close_row,
            )
            parts.extend(row for row in tool_rows if not row.isHidden())
        if not self._edit_keys_label.isHidden():
            parts.append(self._edit_keys_label)
        if not parts:
            side = TOOLBAR_BUTTON_SIZE + 2 * _PANEL_PAD
            return QSize(side, side)
        for part in parts:
            part.adjustSize()
        width = max(part.sizeHint().width() for part in parts) + 2 * _PANEL_PAD
        height = 2 * _PANEL_PAD + sum(part.sizeHint().height() for part in parts) + _ROW_GAP * (len(parts) - 1)
        return QSize(width, height)

    def _set_clipboard_checked(self, *, enabled: bool) -> None:
        if self._clipboard_button.isChecked() == enabled:
            return
        blocked = self._clipboard_button.blockSignals(True)  # noqa: FBT003
        try:
            self._clipboard_button.setChecked(enabled)
        finally:
            self._clipboard_button.blockSignals(blocked)

    def _set_ocr_translate_checked(self, *, enabled: bool) -> None:
        if self._ocr_translate_button.isChecked() == enabled:
            return
        blocked = self._ocr_translate_button.blockSignals(True)  # noqa: FBT003
        try:
            self._ocr_translate_button.setChecked(enabled)
        finally:
            self._ocr_translate_button.blockSignals(blocked)

    def _set_row_visible(self, row: QWidget, *, visible: bool) -> None:
        """Hide a row without leaving empty layout gaps after a fixed-size shrink."""
        row.setVisible(visible)
        if visible:
            row.setMaximumSize(_QWIDGETSIZE_MAX, _QWIDGETSIZE_MAX)
        else:
            row.setMaximumSize(_QWIDGETSIZE_MAX, 0)

    def _toggle_collapsed(self) -> None:
        self.set_collapsed(collapsed=not self._collapsed)

    def _update_size(self) -> None:
        # Clearing fixed bounds is required; otherwise sizeHint keeps the old height
        # and hidden tools leave empty gaps in arrange / collapsed modes.
        self.setMinimumSize(0, 0)
        self.setMaximumSize(_QWIDGETSIZE_MAX, _QWIDGETSIZE_MAX)
        if self._tools_host.isHidden():
            self._tools_host.setMaximumSize(_QWIDGETSIZE_MAX, 0)
        else:
            self._tools_host.setMaximumSize(_QWIDGETSIZE_MAX, _QWIDGETSIZE_MAX)
        self._fit_all_cell_labels()
        hint = self._preferred_size()
        new_width = hint.width()
        new_height = min(hint.height(), self._available_height)
        if (
            self.width() == new_width
            and self.height() == new_height
            and self.minimumWidth() == new_width
            and self.maximumWidth() == new_width
            and self.minimumHeight() == new_height
            and self.maximumHeight() == new_height
        ):
            self.geometry_changed.emit()
            return
        # resize() first — on Windows setFixedSize alone may keep the old geometry.
        self.resize(new_width, new_height)
        self.setFixedSize(new_width, new_height)
        self.geometry_changed.emit()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, capture_options: bool = True) -> None
```

Create the shutter panel with desktop/adjust/close controls.

Args:

- `parent` (`QWidget | None`): Parent widget.
- `capture_options` (`bool`): When `False` (screen recording), hide Adjust /
  Show Harrix app / Clipboard / OCR — only Desktop, Guides, and Cancel remain.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, capture_options: bool = True) -> None:
        super().__init__(parent)
        self.setObjectName("ShutterPanelRoot")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._capture_options = capture_options
        self._available_height = _primary_available_height()
        self._collapsed = False
        self._mode: ShutterMode = "selection"
        self._user_moved = False
        self._dragging = False
        self._drag_offset = QPoint()

        root = QVBoxLayout(self)
        root.setContentsMargins(_PANEL_PAD, _PANEL_PAD, _PANEL_PAD, _PANEL_PAD)
        root.setSpacing(_ROW_GAP)

        self._collapse_row, self._collapse_button, self._collapse_label = self._make_action_cell(
            _COLLAPSE_ICON,
            "Collapse",
            "Collapse tools panel",
        )
        self._collapse_button.clicked.connect(self._toggle_collapsed)
        root.addWidget(self._collapse_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._tools_host = QWidget(self)
        self._tools_host.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._tools_host.setAutoFillBackground(False)
        self._tools_host.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self._tools_layout = QVBoxLayout(self._tools_host)
        self._tools_layout.setContentsMargins(0, 0, 0, 0)
        self._tools_layout.setSpacing(_ROW_GAP)

        self._mode_row, self._mode_button, self._mode_label = self._make_action_cell(
            _ARRANGE_ICON,
            "Desktop",
            "Desktop — interact with other windows (OpenBoard-style)",
        )
        self._mode_button.clicked.connect(self.triggered.emit)
        self._tools_layout.addWidget(self._mode_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._adjust_row, self._adjust_button, self._adjust_label = self._make_toggle_cell(
            _ADJUST_ICON,
            "Adjust",
            "Adjust region after select (Enter confirms)",
        )
        self._adjust_button.toggled.connect(self.adjust_toggled.emit)
        self._tools_layout.addWidget(self._adjust_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._guides_row, self._guides_button, self._guides_label = self._make_toggle_cell(
            _GUIDES_ICON,
            "Guides",
            "Composition guides: thirds, diagonal, size, and angle",
        )
        self._guides_button.toggled.connect(self.guides_toggled.emit)
        self._tools_layout.addWidget(self._guides_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._keep_windows_row, self._keep_windows_button, self._keep_windows_label = self._make_toggle_cell(
            _KEEP_WINDOWS_ICON,
            "Show Harrix app",
            "Keep Harrix Swiss Knife windows visible in the screenshot",
        )
        self._keep_windows_button.toggled.connect(self.keep_windows_toggled.emit)
        self._tools_layout.addWidget(self._keep_windows_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._clipboard_row, self._clipboard_button, self._clipboard_label = self._make_toggle_cell(
            _CLIPBOARD_ICON,
            "Clipboard only",
            "Clipboard only (skip preview)",
        )
        self._clipboard_button.toggled.connect(lambda checked: self._on_clipboard_toggled(checked=checked))
        self._tools_layout.addWidget(self._clipboard_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._ocr_row, self._ocr_translate_button, self._ocr_label = self._make_toggle_cell(
            _OCR_TRANSLATE_ICON,
            "OCR + translate",
            "OCR + translate (skip preview)",
        )
        self._ocr_translate_button.toggled.connect(lambda checked: self._on_ocr_translate_toggled(checked=checked))
        self._tools_layout.addWidget(self._ocr_row, 0, Qt.AlignmentFlag.AlignLeft)

        self._close_row, self._close_button, self._close_label = self._make_action_cell(
            _CLOSE_ICON,
            "Cancel",
            "Cancel" if not capture_options else "Cancel screenshot",
        )
        self._close_button.clicked.connect(self.cancelled.emit)
        self._tools_layout.addWidget(self._close_row, 0, Qt.AlignmentFlag.AlignLeft)

        root.addWidget(self._tools_host)

        self._edit_keys_label = QLabel(self)
        self._edit_keys_label.setStyleSheet(_HINT_STYLE)
        self._edit_keys_label.setWordWrap(True)
        self._edit_keys_label.setText(_EDIT_KEYS_TEXT)
        self._edit_keys_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._edit_keys_label.setMaximumWidth(_TOGGLE_CONTROLS_WIDTH)
        self._edit_keys_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._edit_keys_label.hide()
        root.addWidget(self._edit_keys_label, 0, Qt.AlignmentFlag.AlignLeft)

        self._apply_capture_option_visibility()
        self._update_size()
        # On standard (non-ultrawide) screens keep tools collapsed so the plate
        # does not cover as much of the capture area.
        if not _is_widescreen_monitor():
            self.set_collapsed(collapsed=True)
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
        return self._mode == "selection" and self._adjust_button.isChecked()
```

</details>

### ⚙️ Method `apply_available_height`

```python
def apply_available_height(self, height: int) -> None
```

Constrain the toolbar height on short screens.

<details>
<summary>Code:</summary>

```python
def apply_available_height(self, height: int) -> None:
        clamped = max(TOOLBAR_BUTTON_SIZE + 2 * _PANEL_PAD, height)
        if clamped == self._available_height:
            return
        self._available_height = clamped
        self._update_size()
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
        return self._mode == "selection" and self._clipboard_button.isChecked()
```

</details>

### ⚙️ Method `collapsed (property)`

```python
def collapsed(self) -> bool
```

Whether the tools list is hidden behind the expand control.

<details>
<summary>Code:</summary>

```python
def collapsed(self) -> bool:
        return self._collapsed
```

</details>

### ⚙️ Method `guides_mode (property)`

```python
def guides_mode(self) -> bool
```

Whether the selection frame shows composition guides and measurements.

<details>
<summary>Code:</summary>

```python
def guides_mode(self) -> bool:
        return self._mode == "selection" and self._guides_button.isChecked()
```

</details>

### ⚙️ Method `keep_windows (property)`

```python
def keep_windows(self) -> bool
```

Whether Harrix Swiss Knife Windows should stay visible in the next grab.

<details>
<summary>Code:</summary>

```python
def keep_windows(self) -> bool:
        return self._mode == "selection" and self._keep_windows_button.isChecked()
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Drag the panel (or its top-level arrange dialog) with the left button.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self._apply_drag(event.globalPosition().toPoint())
            event.accept()
            return
        super().mouseMoveEvent(event)
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Start dragging when the press is not on a button or switch.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and not self._is_interactive_target(
            self.childAt(event.position().toPoint())
        ):
            self._dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self.mapToGlobal(QPoint(0, 0))
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

Stop dragging.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)
```

</details>

### ⚙️ Method `ocr_translate (property)`

```python
def ocr_translate(self) -> bool
```

Whether capture should skip the preview and run OCR + translate.

<details>
<summary>Code:</summary>

```python
def ocr_translate(self) -> bool:
        return self._mode == "selection" and self._ocr_translate_button.isChecked()
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Draw one rounded translucent plate behind all tools.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(_PANEL_FILL)
        painter.drawRoundedRect(QRectF(self.rect()), _PANEL_RADIUS, _PANEL_RADIUS)
        painter.end()
```

</details>

### ⚙️ Method `set_adjust_mode`

```python
def set_adjust_mode(self, *, enabled: bool) -> None
```

Set the adjust-region button without requiring a user click.

<details>
<summary>Code:</summary>

```python
def set_adjust_mode(self, *, enabled: bool) -> None:
        self._adjust_button.setChecked(enabled)
```

</details>

### ⚙️ Method `set_clipboard_only`

```python
def set_clipboard_only(self, *, enabled: bool) -> None
```

Set the clipboard-only button without requiring a user click.

<details>
<summary>Code:</summary>

```python
def set_clipboard_only(self, *, enabled: bool) -> None:
        blocked = self._clipboard_button.blockSignals(True)  # noqa: FBT003
        try:
            self._clipboard_button.setChecked(enabled)
            if enabled:
                self._set_ocr_translate_checked(enabled=False)
        finally:
            self._clipboard_button.blockSignals(blocked)
```

</details>

### ⚙️ Method `set_collapsed`

```python
def set_collapsed(self, *, collapsed: bool) -> None
```

Expand or collapse the tools list.

<details>
<summary>Code:</summary>

```python
def set_collapsed(self, *, collapsed: bool) -> None:
        if collapsed == self._collapsed:
            return
        self._collapsed = collapsed
        self._set_row_visible(self._tools_host, visible=not collapsed)
        if collapsed:
            self.set_edit_keys_visible(visible=False)
        self._collapse_button.setIcon(
            create_lucide_icon(
                _EXPAND_ICON if collapsed else _COLLAPSE_ICON,
                TOOLBAR_ICON_SIZE,
                color=_ICON_COLOR,
            )
        )
        self._collapse_label.setText("Expand" if collapsed else "Collapse")
        self._fit_cell_label(self._collapse_label)
        hint = "Expand tools panel" if collapsed else "Collapse tools panel"
        self._collapse_button.setToolTip(hint)
        self._collapse_button.setProperty("hover_hint", hint)
        self._update_size()
```

</details>

### ⚙️ Method `set_edit_keys_visible`

```python
def set_edit_keys_visible(self, *, visible: bool) -> None
```

Show or hide arrow/Shift/Ctrl hints under the shutter buttons.

<details>
<summary>Code:</summary>

```python
def set_edit_keys_visible(self, *, visible: bool) -> None:
        if self._collapsed:
            visible = False
        if visible == self._edit_keys_label.isVisible():
            return
        self._set_row_visible(self._edit_keys_label, visible=visible)
        self._update_size()
```

</details>

### ⚙️ Method `set_guides_mode`

```python
def set_guides_mode(self, *, enabled: bool) -> None
```

Set the composition-guides button without requiring a user click.

<details>
<summary>Code:</summary>

```python
def set_guides_mode(self, *, enabled: bool) -> None:
        self._guides_button.setChecked(enabled)
```

</details>

### ⚙️ Method `set_keep_windows`

```python
def set_keep_windows(self, *, enabled: bool) -> None
```

Set the show-app button without emitting `keep_windows_toggled`.

<details>
<summary>Code:</summary>

```python
def set_keep_windows(self, *, enabled: bool) -> None:
        blocked = self._keep_windows_button.blockSignals(True)  # noqa: FBT003
        try:
            self._keep_windows_button.setChecked(enabled)
        finally:
            self._keep_windows_button.blockSignals(blocked)
```

</details>

### ⚙️ Method `set_mode`

```python
def set_mode(self, mode: ShutterMode) -> None
```

Update the mode button for selection vs desktop interaction.

<details>
<summary>Code:</summary>

```python
def set_mode(self, mode: ShutterMode) -> None:
        self._mode = mode
        if mode == "selection":
            self._mode_button.setIcon(create_lucide_icon(_ARRANGE_ICON, TOOLBAR_ICON_SIZE, color=_ICON_COLOR))
            self._mode_label.setText("Desktop")
            self._fit_cell_label(self._mode_label)
            tip = "Desktop — interact with other windows (OpenBoard-style)"
            self._mode_button.setToolTip(tip)
            self._mode_button.setProperty("hover_hint", tip)
            self._set_row_visible(self._guides_row, visible=True)
            self._apply_capture_option_visibility()
        else:
            self._mode_button.setIcon(create_lucide_icon(_CAMERA_ICON, TOOLBAR_ICON_SIZE, color=_ICON_COLOR))
            label = "Capture" if self._capture_options else "Select"
            self._mode_label.setText(label)
            self._fit_cell_label(self._mode_label)
            tip = "Capture region" if self._capture_options else "Select region"
            self._mode_button.setToolTip(tip)
            self._mode_button.setProperty("hover_hint", tip)
            self._set_row_visible(self._adjust_row, visible=False)
            self._adjust_button.setChecked(False)
            self._set_row_visible(self._guides_row, visible=False)
            self._guides_button.setChecked(False)
            self._set_row_visible(self._keep_windows_row, visible=False)
            self._set_row_visible(self._clipboard_row, visible=False)
            self._set_row_visible(self._ocr_row, visible=False)
            self.set_edit_keys_visible(visible=False)
        self._update_size()
```

</details>

### ⚙️ Method `set_ocr_translate`

```python
def set_ocr_translate(self, *, enabled: bool) -> None
```

Set the OCR + translate button without requiring a user click.

<details>
<summary>Code:</summary>

```python
def set_ocr_translate(self, *, enabled: bool) -> None:
        blocked = self._ocr_translate_button.blockSignals(True)  # noqa: FBT003
        try:
            self._ocr_translate_button.setChecked(enabled)
            if enabled:
                self._set_clipboard_checked(enabled=False)
        finally:
            self._ocr_translate_button.blockSignals(blocked)
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

Recompute size after the first show — layout hints ignore hidden rows only then.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        self._update_size()
```

</details>

### ⚙️ Method `user_moved (property)`

```python
def user_moved(self) -> bool
```

Whether the user dragged the panel away from the default spot.

<details>
<summary>Code:</summary>

```python
def user_moved(self) -> bool:
        return self._user_moved
```

</details>

## 🏛️ Class `ShutterSwitch`

```python
class ShutterSwitch(QPushButton)
```

Large standalone on/off switch track used inside toggle cells.

<details>
<summary>Code:</summary>

```python
class ShutterSwitch(QPushButton):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a large iOS-style switch control."""
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(_SWITCH_TRACK_W, _SWITCH_TRACK_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Draw a large track and knob."""
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setPen(Qt.PenStyle.NoPen)
        if self.isChecked():
            painter.setBrush(QColor("#0072CA"))
        else:
            painter.setBrush(QColor(90, 90, 95, 230))
        painter.drawRoundedRect(
            QRectF(0, 0, _SWITCH_TRACK_W, _SWITCH_TRACK_H), _SWITCH_TRACK_H / 2, _SWITCH_TRACK_H / 2
        )
        knob_y = (_SWITCH_TRACK_H - _SWITCH_KNOB) / 2
        knob_x = _SWITCH_TRACK_W - _SWITCH_KNOB - 2 if self.isChecked() else 2
        painter.setBrush(QColor("#FFFFFF") if self.isChecked() else _SWITCH_KNOB_OFF)
        painter.drawEllipse(QRectF(knob_x, knob_y, _SWITCH_KNOB, _SWITCH_KNOB))
        painter.end()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a large iOS-style switch control.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(_SWITCH_TRACK_W, _SWITCH_TRACK_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Draw a large track and knob.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, on=True)
        painter.setPen(Qt.PenStyle.NoPen)
        if self.isChecked():
            painter.setBrush(QColor("#0072CA"))
        else:
            painter.setBrush(QColor(90, 90, 95, 230))
        painter.drawRoundedRect(
            QRectF(0, 0, _SWITCH_TRACK_W, _SWITCH_TRACK_H), _SWITCH_TRACK_H / 2, _SWITCH_TRACK_H / 2
        )
        knob_y = (_SWITCH_TRACK_H - _SWITCH_KNOB) / 2
        knob_x = _SWITCH_TRACK_W - _SWITCH_KNOB - 2 if self.isChecked() else 2
        painter.setBrush(QColor("#FFFFFF") if self.isChecked() else _SWITCH_KNOB_OFF)
        painter.drawEllipse(QRectF(knob_x, knob_y, _SWITCH_KNOB, _SWITCH_KNOB))
        painter.end()
```

</details>

## 🏛️ Class `ShutterToggleControl`

```python
class ShutterToggleControl(QWidget)
```

Icon plus large switch; checkable like a single toggle button.

<details>
<summary>Code:</summary>

```python
class ShutterToggleControl(QWidget):

    toggled = Signal(bool)

    def __init__(self, icon_name: str, tooltip: str, parent: QWidget | None = None) -> None:
        """Create an icon + switch control group."""
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._icon_name = icon_name
        self._syncing = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(_CONTROL_GAP)

        self._icon_button = QPushButton(self)
        self._icon_button.setCheckable(True)
        self._icon_button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
        self._icon_button.setIconSize(QSize(TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE))
        self._icon_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._icon_button.setToolTip(tooltip)
        self._icon_button.setProperty("hover_hint", tooltip)
        self._icon_button.setProperty("lucide_name", icon_name)
        self._icon_button.setStyleSheet(_FLAT_BUTTON_STYLE)
        self._icon_button.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)

        self._switch = ShutterSwitch(self)
        self._switch.setToolTip(tooltip)

        layout.addWidget(self._icon_button)
        layout.addWidget(self._switch)

        self._icon_button.toggled.connect(self._on_part_toggled)
        self._switch.toggled.connect(self._on_part_toggled)
        self._sync_icon(checked=False)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

    def isChecked(self) -> bool:  # noqa: N802
        """Whether the toggle is on."""
        return self._switch.isChecked()

    def setChecked(self, checked: bool) -> None:  # noqa: N802, FBT001
        """Set both icon and switch; emit `toggled` unless signals are blocked."""
        if checked == self.isChecked():
            self._sync_icon(checked=checked)
            return
        self._apply_checked(checked=checked, emit_signal=not self.signalsBlocked())

    def toolTip(self) -> str:  # noqa: N802
        """Forward tooltip from the icon button for test discovery."""
        return self._icon_button.toolTip()

    def _apply_checked(self, *, checked: bool, emit_signal: bool) -> None:
        self._syncing = True
        try:
            self._icon_button.setChecked(checked)
            self._switch.setChecked(checked)
            self._sync_icon(checked=checked)
        finally:
            self._syncing = False
        if emit_signal:
            self.toggled.emit(checked)

    def _on_part_toggled(self, checked: bool) -> None:  # noqa: FBT001
        if self._syncing:
            return
        self._apply_checked(checked=checked, emit_signal=True)

    def _sync_icon(self, *, checked: bool = False) -> None:
        color = _TOGGLE_CHECKED_ICON_COLOR if checked else _ICON_COLOR
        self._icon_button.setIcon(create_lucide_icon(self._icon_name, TOOLBAR_ICON_SIZE, color=color))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, icon_name: str, tooltip: str, parent: QWidget | None = None) -> None
```

Create an icon + switch control group.

<details>
<summary>Code:</summary>

```python
def __init__(self, icon_name: str, tooltip: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._icon_name = icon_name
        self._syncing = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(_CONTROL_GAP)

        self._icon_button = QPushButton(self)
        self._icon_button.setCheckable(True)
        self._icon_button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
        self._icon_button.setIconSize(QSize(TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE))
        self._icon_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._icon_button.setToolTip(tooltip)
        self._icon_button.setProperty("hover_hint", tooltip)
        self._icon_button.setProperty("lucide_name", icon_name)
        self._icon_button.setStyleSheet(_FLAT_BUTTON_STYLE)
        self._icon_button.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)

        self._switch = ShutterSwitch(self)
        self._switch.setToolTip(tooltip)

        layout.addWidget(self._icon_button)
        layout.addWidget(self._switch)

        self._icon_button.toggled.connect(self._on_part_toggled)
        self._switch.toggled.connect(self._on_part_toggled)
        self._sync_icon(checked=False)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
```

</details>

### ⚙️ Method `isChecked`

```python
def isChecked(self) -> bool
```

Whether the toggle is on.

<details>
<summary>Code:</summary>

```python
def isChecked(self) -> bool:  # noqa: N802
        return self._switch.isChecked()
```

</details>

### ⚙️ Method `setChecked`

```python
def setChecked(self, checked: bool) -> None
```

Set both icon and switch; emit `toggled` unless signals are blocked.

<details>
<summary>Code:</summary>

```python
def setChecked(self, checked: bool) -> None:  # noqa: N802, FBT001
        if checked == self.isChecked():
            self._sync_icon(checked=checked)
            return
        self._apply_checked(checked=checked, emit_signal=not self.signalsBlocked())
```

</details>

### ⚙️ Method `toolTip`

```python
def toolTip(self) -> str
```

Forward tooltip from the icon button for test discovery.

<details>
<summary>Code:</summary>

```python
def toolTip(self) -> str:  # noqa: N802
        return self._icon_button.toolTip()
```

</details>

## 🔧 Function `position_panel_at_left_center`

```python
def position_panel_at_left_center(panel: ShutterPanel, overlay_geometry: QRect) -> None
```

Place an embedded panel at the left center of the primary screen.

Skips repositioning after the user has dragged the panel.

Args:

- `panel` ([`ShutterPanel`](#%EF%B8%8F-class-shutterpanel)): Panel that is a child of the fullscreen overlay.
- `overlay_geometry` (`QRect`): Overlay geometry in global (virtual desktop) coordinates.

<details>
<summary>Code:</summary>

```python
def position_panel_at_left_center(panel: ShutterPanel, overlay_geometry: QRect) -> None:
    if panel.user_moved:
        return
    screen = QApplication.primaryScreen()
    if screen is None:
        return
    geo = screen.availableGeometry()
    panel.apply_available_height(max(TOOLBAR_BUTTON_SIZE, geo.height() - 2 * TOOLBAR_EDGE_MARGIN))
    parent = panel.parentWidget()
    origin = parent.mapToGlobal(QPoint(0, 0)) if parent is not None else overlay_geometry.topLeft()
    x = geo.x() - origin.x() + TOOLBAR_EDGE_MARGIN
    y = geo.y() - origin.y() + (geo.height() - panel.height()) // 2
    panel.move(x, y)
    panel.raise_()
```

</details>
