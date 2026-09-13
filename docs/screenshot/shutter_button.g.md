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
  - [⚙️ Method `ocr_translate (property)`](#%EF%B8%8F-method-ocr_translate-property)
  - [⚙️ Method `set_adjust_mode`](#%EF%B8%8F-method-set_adjust_mode)
  - [⚙️ Method `set_clipboard_only`](#%EF%B8%8F-method-set_clipboard_only)
  - [⚙️ Method `set_collapsed`](#%EF%B8%8F-method-set_collapsed)
  - [⚙️ Method `set_edit_keys_visible`](#%EF%B8%8F-method-set_edit_keys_visible)
  - [⚙️ Method `set_guides_mode`](#%EF%B8%8F-method-set_guides_mode)
  - [⚙️ Method `set_keep_windows`](#%EF%B8%8F-method-set_keep_windows)
  - [⚙️ Method `set_mode`](#%EF%B8%8F-method-set_mode)
  - [⚙️ Method `set_ocr_translate`](#%EF%B8%8F-method-set_ocr_translate)
- [🏛️ Class `ShutterToggleButton`](#%EF%B8%8F-class-shuttertogglebutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `setChecked`](#%EF%B8%8F-method-setchecked)
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
        self.setFixedSize(self._panel.sizeHint())
        self._position_on_primary_screen()

    def _position_on_primary_screen(self) -> None:
        """Place the controls at the left center of the primary screen."""
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

Left-centered vertical toolbar with labeled tools, embeddable as a child.

Being a regular child widget (not a separate native window) guarantees that
clicks reach the buttons even when the application has modal dialogs in
`exec()` — the parent (overlay or arrange dialog) owns the modal input.

Action buttons are square; checkable tools are pill toggles of the same size
with visible text labels. Clipboard-only and OCR + translate are mutually
exclusive. A collapse control hides the tool list to a single expand button.

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
        """Create the shutter panel with arrange/adjust/close controls.

        Args:

        - `parent` (`QWidget | None`): Parent widget.
        - `capture_options` (`bool`): When `False` (screen recording), hide Adjust /
          Keep Windows / Clipboard / OCR — only Arrange, Guides, and Cancel remain.

        """
        super().__init__(parent)
        self.setObjectName("ShutterPanelRoot")
        self.setStyleSheet(_PANEL_STYLE)
        self._capture_options = capture_options
        self._available_height = _primary_available_height()
        self._collapsed = False
        self._mode: ShutterMode = "selection"

        root = QVBoxLayout(self)
        root.setContentsMargins(_PANEL_PAD, _PANEL_PAD, _PANEL_PAD, _PANEL_PAD)
        root.setSpacing(_ROW_GAP)

        self._collapse_row, self._collapse_button, self._collapse_label = self._make_action_row(
            _COLLAPSE_ICON,
            "Collapse",
            "Collapse tools panel",
        )
        self._collapse_button.clicked.connect(self._toggle_collapsed)
        root.addWidget(self._collapse_row)

        self._tools_host = QWidget(self)
        self._tools_layout = QVBoxLayout(self._tools_host)
        self._tools_layout.setContentsMargins(0, 0, 0, 0)
        self._tools_layout.setSpacing(_ROW_GAP)

        self._mode_row, self._mode_button, self._mode_label = self._make_action_row(
            _ARRANGE_ICON,
            "Arrange",
            "Arrange desktop",
        )
        self._mode_button.clicked.connect(self.triggered.emit)
        self._tools_layout.addWidget(self._mode_row)

        self._adjust_row, self._adjust_button, self._adjust_label = self._make_toggle_row(
            _ADJUST_ICON,
            "Adjust",
            "Adjust region after select (Enter confirms)",
        )
        self._adjust_button.toggled.connect(self.adjust_toggled.emit)
        self._tools_layout.addWidget(self._adjust_row)

        self._guides_row, self._guides_button, self._guides_label = self._make_toggle_row(
            _GUIDES_ICON,
            "Guides",
            "Composition guides: thirds, diagonal, size, and angle",
        )
        self._guides_button.toggled.connect(self.guides_toggled.emit)
        self._tools_layout.addWidget(self._guides_row)

        self._keep_windows_row, self._keep_windows_button, self._keep_windows_label = self._make_toggle_row(
            _KEEP_WINDOWS_ICON,
            "Keep windows",
            "Keep app Windows visible in the screenshot",
        )
        self._keep_windows_button.toggled.connect(self.keep_windows_toggled.emit)
        self._tools_layout.addWidget(self._keep_windows_row)

        self._clipboard_row, self._clipboard_button, self._clipboard_label = self._make_toggle_row(
            _CLIPBOARD_ICON,
            "Clipboard only",
            "Clipboard only (skip preview)",
        )
        self._clipboard_button.toggled.connect(lambda checked: self._on_clipboard_toggled(checked=checked))
        self._tools_layout.addWidget(self._clipboard_row)

        self._ocr_row, self._ocr_translate_button, self._ocr_label = self._make_toggle_row(
            _OCR_TRANSLATE_ICON,
            "OCR + translate",
            "OCR + translate (skip preview)",
        )
        self._ocr_translate_button.toggled.connect(lambda checked: self._on_ocr_translate_toggled(checked=checked))
        self._tools_layout.addWidget(self._ocr_row)

        self._close_row, self._close_button, self._close_label = self._make_action_row(
            _CLOSE_ICON,
            "Cancel",
            "Cancel" if not capture_options else "Cancel screenshot",
        )
        self._close_button.clicked.connect(self.cancelled.emit)
        self._tools_layout.addWidget(self._close_row)

        root.addWidget(self._tools_host)

        self._edit_keys_label = QLabel(self)
        self._edit_keys_label.setStyleSheet(_HINT_STYLE)
        self._edit_keys_label.setWordWrap(True)
        self._edit_keys_label.setText(_EDIT_KEYS_TEXT)
        self._edit_keys_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._edit_keys_label.hide()
        root.addWidget(self._edit_keys_label)

        self._apply_capture_option_visibility()
        self._update_size()

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
        """Whether application Windows should stay visible in the next grab."""
        return self._mode == "selection" and self._keep_windows_button.isChecked()

    @property
    def ocr_translate(self) -> bool:
        """Whether capture should skip the preview and run OCR + translate."""
        return self._mode == "selection" and self._ocr_translate_button.isChecked()

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
        self._tools_host.setVisible(not collapsed)
        if collapsed:
            self.set_edit_keys_visible(visible=False)
        self._collapse_button.setIcon(
            create_lucide_icon(_EXPAND_ICON if collapsed else _COLLAPSE_ICON, TOOLBAR_ICON_SIZE)
        )
        self._collapse_label.setText("Expand" if collapsed else "Collapse")
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
        self._edit_keys_label.setVisible(visible)
        self._update_size()

    def set_guides_mode(self, *, enabled: bool) -> None:
        """Set the composition-guides button without requiring a user click."""
        self._guides_button.setChecked(enabled)

    def set_keep_windows(self, *, enabled: bool) -> None:
        """Set the keep-Windows button without emitting `keep_windows_toggled`."""
        blocked = self._keep_windows_button.blockSignals(True)  # noqa: FBT003
        try:
            self._keep_windows_button.setChecked(enabled)
        finally:
            self._keep_windows_button.blockSignals(blocked)

    def set_mode(self, mode: ShutterMode) -> None:
        """Update the mode button for selection vs desktop-arrangement."""
        self._mode = mode
        if mode == "selection":
            self._mode_button.setIcon(create_lucide_icon(_ARRANGE_ICON, TOOLBAR_ICON_SIZE))
            self._mode_label.setText("Arrange")
            self._mode_button.setToolTip("Arrange desktop")
            self._mode_button.setProperty("hover_hint", "Arrange desktop")
            self._guides_row.show()
            self._apply_capture_option_visibility()
        else:
            self._mode_button.setIcon(create_lucide_icon(_CAMERA_ICON, TOOLBAR_ICON_SIZE))
            label = "Capture" if self._capture_options else "Select"
            self._mode_label.setText(label)
            tip = "Capture region" if self._capture_options else "Select region"
            self._mode_button.setToolTip(tip)
            self._mode_button.setProperty("hover_hint", tip)
            self._adjust_row.hide()
            self._adjust_button.setChecked(False)
            self._guides_row.hide()
            self._guides_button.setChecked(False)
            self._keep_windows_row.hide()
            self._clipboard_row.hide()
            self._ocr_row.hide()
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

    def _apply_capture_option_visibility(self) -> None:
        show = self._capture_options and self._mode == "selection"
        self._adjust_row.setVisible(show)
        self._keep_windows_row.setVisible(show)
        self._clipboard_row.setVisible(show)
        self._ocr_row.setVisible(show)
        if not show:
            self._adjust_button.setChecked(False)
            self._keep_windows_button.setChecked(False)
            self._clipboard_button.setChecked(False)
            self._ocr_translate_button.setChecked(False)
            self.set_edit_keys_visible(visible=False)

    def _make_action_row(self, icon_name: str, label: str, tooltip: str) -> tuple[QWidget, QPushButton, QLabel]:
        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(_ROW_GAP)
        button = self._make_icon_button(icon_name, tooltip)
        text = QLabel(label, row)
        text.setStyleSheet(_ROW_LABEL_STYLE)
        text.setMinimumWidth(_LABEL_MIN_WIDTH)
        layout.addWidget(button, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(text, 1, Qt.AlignmentFlag.AlignVCenter)
        return row, button, text

    def _make_icon_button(self, name: str, tooltip: str) -> QPushButton:
        button = QPushButton(self)
        button.setFixedSize(TOOLBAR_BUTTON_SIZE, TOOLBAR_BUTTON_SIZE)
        button.setIcon(create_lucide_icon(name, TOOLBAR_ICON_SIZE))
        button.setIconSize(QSize(TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip(tooltip)
        button.setProperty("hover_hint", tooltip)
        button.setStyleSheet(TOOLBAR_BUTTON_STYLE)
        button.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
        return button

    def _make_toggle(self, name: str, tooltip: str) -> ShutterToggleButton:
        return ShutterToggleButton(name, tooltip, self)

    def _make_toggle_row(self, icon_name: str, label: str, tooltip: str) -> tuple[QWidget, ShutterToggleButton, QLabel]:
        row = QWidget(self)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(_ROW_GAP)
        button = self._make_toggle(icon_name, tooltip)
        text = QLabel(label, row)
        text.setStyleSheet(_ROW_LABEL_STYLE)
        text.setMinimumWidth(_LABEL_MIN_WIDTH)
        layout.addWidget(button, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(text, 1, Qt.AlignmentFlag.AlignVCenter)
        return row, button, text

    def _on_clipboard_toggled(self, *, checked: bool) -> None:
        if checked:
            self._set_ocr_translate_checked(enabled=False)
        self.clipboard_toggled.emit(checked)

    def _on_ocr_translate_toggled(self, *, checked: bool) -> None:
        if checked:
            self._set_clipboard_checked(enabled=False)
        self.ocr_translate_toggled.emit(checked)

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

    def _toggle_collapsed(self) -> None:
        self.set_collapsed(collapsed=not self._collapsed)

    def _update_size(self) -> None:
        self.adjustSize()
        hint = self.sizeHint()
        max_h = self._available_height
        new_width = hint.width()
        new_height = min(hint.height(), max_h)
        if self.width() == new_width and self.height() == new_height:
            self.geometry_changed.emit()
            return
        self.setFixedSize(new_width, new_height)
        self.geometry_changed.emit()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, capture_options: bool = True) -> None
```

Create the shutter panel with arrange/adjust/close controls.

Args:

- `parent` (`QWidget | None`): Parent widget.
- `capture_options` (`bool`): When `False` (screen recording), hide Adjust /
  Keep Windows / Clipboard / OCR — only Arrange, Guides, and Cancel remain.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, capture_options: bool = True) -> None:
        super().__init__(parent)
        self.setObjectName("ShutterPanelRoot")
        self.setStyleSheet(_PANEL_STYLE)
        self._capture_options = capture_options
        self._available_height = _primary_available_height()
        self._collapsed = False
        self._mode: ShutterMode = "selection"

        root = QVBoxLayout(self)
        root.setContentsMargins(_PANEL_PAD, _PANEL_PAD, _PANEL_PAD, _PANEL_PAD)
        root.setSpacing(_ROW_GAP)

        self._collapse_row, self._collapse_button, self._collapse_label = self._make_action_row(
            _COLLAPSE_ICON,
            "Collapse",
            "Collapse tools panel",
        )
        self._collapse_button.clicked.connect(self._toggle_collapsed)
        root.addWidget(self._collapse_row)

        self._tools_host = QWidget(self)
        self._tools_layout = QVBoxLayout(self._tools_host)
        self._tools_layout.setContentsMargins(0, 0, 0, 0)
        self._tools_layout.setSpacing(_ROW_GAP)

        self._mode_row, self._mode_button, self._mode_label = self._make_action_row(
            _ARRANGE_ICON,
            "Arrange",
            "Arrange desktop",
        )
        self._mode_button.clicked.connect(self.triggered.emit)
        self._tools_layout.addWidget(self._mode_row)

        self._adjust_row, self._adjust_button, self._adjust_label = self._make_toggle_row(
            _ADJUST_ICON,
            "Adjust",
            "Adjust region after select (Enter confirms)",
        )
        self._adjust_button.toggled.connect(self.adjust_toggled.emit)
        self._tools_layout.addWidget(self._adjust_row)

        self._guides_row, self._guides_button, self._guides_label = self._make_toggle_row(
            _GUIDES_ICON,
            "Guides",
            "Composition guides: thirds, diagonal, size, and angle",
        )
        self._guides_button.toggled.connect(self.guides_toggled.emit)
        self._tools_layout.addWidget(self._guides_row)

        self._keep_windows_row, self._keep_windows_button, self._keep_windows_label = self._make_toggle_row(
            _KEEP_WINDOWS_ICON,
            "Keep windows",
            "Keep app Windows visible in the screenshot",
        )
        self._keep_windows_button.toggled.connect(self.keep_windows_toggled.emit)
        self._tools_layout.addWidget(self._keep_windows_row)

        self._clipboard_row, self._clipboard_button, self._clipboard_label = self._make_toggle_row(
            _CLIPBOARD_ICON,
            "Clipboard only",
            "Clipboard only (skip preview)",
        )
        self._clipboard_button.toggled.connect(lambda checked: self._on_clipboard_toggled(checked=checked))
        self._tools_layout.addWidget(self._clipboard_row)

        self._ocr_row, self._ocr_translate_button, self._ocr_label = self._make_toggle_row(
            _OCR_TRANSLATE_ICON,
            "OCR + translate",
            "OCR + translate (skip preview)",
        )
        self._ocr_translate_button.toggled.connect(lambda checked: self._on_ocr_translate_toggled(checked=checked))
        self._tools_layout.addWidget(self._ocr_row)

        self._close_row, self._close_button, self._close_label = self._make_action_row(
            _CLOSE_ICON,
            "Cancel",
            "Cancel" if not capture_options else "Cancel screenshot",
        )
        self._close_button.clicked.connect(self.cancelled.emit)
        self._tools_layout.addWidget(self._close_row)

        root.addWidget(self._tools_host)

        self._edit_keys_label = QLabel(self)
        self._edit_keys_label.setStyleSheet(_HINT_STYLE)
        self._edit_keys_label.setWordWrap(True)
        self._edit_keys_label.setText(_EDIT_KEYS_TEXT)
        self._edit_keys_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._edit_keys_label.hide()
        root.addWidget(self._edit_keys_label)

        self._apply_capture_option_visibility()
        self._update_size()
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

Whether application Windows should stay visible in the next grab.

<details>
<summary>Code:</summary>

```python
def keep_windows(self) -> bool:
        return self._mode == "selection" and self._keep_windows_button.isChecked()
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
        self._tools_host.setVisible(not collapsed)
        if collapsed:
            self.set_edit_keys_visible(visible=False)
        self._collapse_button.setIcon(
            create_lucide_icon(_EXPAND_ICON if collapsed else _COLLAPSE_ICON, TOOLBAR_ICON_SIZE)
        )
        self._collapse_label.setText("Expand" if collapsed else "Collapse")
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
        self._edit_keys_label.setVisible(visible)
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

Set the keep-Windows button without emitting `keep_windows_toggled`.

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

Update the mode button for selection vs desktop-arrangement.

<details>
<summary>Code:</summary>

```python
def set_mode(self, mode: ShutterMode) -> None:
        self._mode = mode
        if mode == "selection":
            self._mode_button.setIcon(create_lucide_icon(_ARRANGE_ICON, TOOLBAR_ICON_SIZE))
            self._mode_label.setText("Arrange")
            self._mode_button.setToolTip("Arrange desktop")
            self._mode_button.setProperty("hover_hint", "Arrange desktop")
            self._guides_row.show()
            self._apply_capture_option_visibility()
        else:
            self._mode_button.setIcon(create_lucide_icon(_CAMERA_ICON, TOOLBAR_ICON_SIZE))
            label = "Capture" if self._capture_options else "Select"
            self._mode_label.setText(label)
            tip = "Capture region" if self._capture_options else "Select region"
            self._mode_button.setToolTip(tip)
            self._mode_button.setProperty("hover_hint", tip)
            self._adjust_row.hide()
            self._adjust_button.setChecked(False)
            self._guides_row.hide()
            self._guides_button.setChecked(False)
            self._keep_windows_row.hide()
            self._clipboard_row.hide()
            self._ocr_row.hide()
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

## 🏛️ Class `ShutterToggleButton`

```python
class ShutterToggleButton(QPushButton)
```

Pill checkable shutter tool matching the square action button size.

<details>
<summary>Code:</summary>

```python
class ShutterToggleButton(QPushButton):

    def __init__(self, icon_name: str, tooltip: str, parent: QWidget | None = None) -> None:
        """Create a modern pill toggle for shutter options."""
        super().__init__(parent)
        self._icon_name = icon_name
        self.setCheckable(True)
        self.setFixedSize(TOOLBAR_TOGGLE_WIDTH, TOOLBAR_BUTTON_SIZE)
        self.setIconSize(QSize(TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tooltip)
        self.setProperty("hover_hint", tooltip)
        self.setProperty("lucide_name", icon_name)
        self.setStyleSheet(TOOLBAR_TOGGLE_STYLE)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
        self.toggled.connect(lambda checked: self._sync_icon(checked=checked))
        self._sync_icon(checked=False)

    def setChecked(self, checked: bool) -> None:  # noqa: N802, FBT001
        """Keep the icon color in sync even when signals are blocked."""
        super().setChecked(checked)
        self._sync_icon(checked=checked)

    def _sync_icon(self, *, checked: bool = False) -> None:
        color = _TOGGLE_CHECKED_ICON_COLOR if checked else None
        self.setIcon(create_lucide_icon(self._icon_name, TOOLBAR_ICON_SIZE, color=color))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, icon_name: str, tooltip: str, parent: QWidget | None = None) -> None
```

Create a modern pill toggle for shutter options.

<details>
<summary>Code:</summary>

```python
def __init__(self, icon_name: str, tooltip: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._icon_name = icon_name
        self.setCheckable(True)
        self.setFixedSize(TOOLBAR_TOGGLE_WIDTH, TOOLBAR_BUTTON_SIZE)
        self.setIconSize(QSize(TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tooltip)
        self.setProperty("hover_hint", tooltip)
        self.setProperty("lucide_name", icon_name)
        self.setStyleSheet(TOOLBAR_TOGGLE_STYLE)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
        self.toggled.connect(lambda checked: self._sync_icon(checked=checked))
        self._sync_icon(checked=False)
```

</details>

### ⚙️ Method `setChecked`

```python
def setChecked(self, checked: bool) -> None
```

Keep the icon color in sync even when signals are blocked.

<details>
<summary>Code:</summary>

```python
def setChecked(self, checked: bool) -> None:  # noqa: N802, FBT001
        super().setChecked(checked)
        self._sync_icon(checked=checked)
```

</details>

## 🔧 Function `position_panel_at_left_center`

```python
def position_panel_at_left_center(panel: ShutterPanel, overlay_geometry: QRect) -> None
```

Place an embedded panel at the left center of the primary screen.

Args:

- `panel` ([`ShutterPanel`](#%EF%B8%8F-class-shutterpanel)): Panel that is a child of the fullscreen overlay.
- `overlay_geometry` (`QRect`): Overlay geometry in global (virtual desktop) coordinates.

<details>
<summary>Code:</summary>

```python
def position_panel_at_left_center(panel: ShutterPanel, overlay_geometry: QRect) -> None:
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
