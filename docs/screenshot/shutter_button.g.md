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
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `set_mode`](#%EF%B8%8F-method-set_mode)
- [🔧 Function `position_panel_on_left_edge`](#-function-position_panel_on_left_edge)

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
        self._position_on_primary_screen()

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
        self.setFixedSize(self._panel.sizeHint())

    def _position_on_primary_screen(self) -> None:
        """Place the controls on the left edge, vertically centered."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.x() + _EDGE_MARGIN
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
        self._position_on_primary_screen()
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

Column with mode and close buttons, embeddable as a plain child widget.

Being a regular child widget (not a separate native window) guarantees that
clicks reach the buttons even when the application has modal dialogs in
`exec()` — the parent (overlay or arrange dialog) owns the modal input.

Hover captions are drawn as an in-panel label (not `QToolTip`), so they stay
visible above the stay-on-top screenshot overlay.

In selection mode an extra checkable button enables “adjust region”: the next
selection is kept editable (move/resize) until Enter confirms.

<details>
<summary>Code:</summary>

```python
class ShutterPanel(QWidget):

    adjust_toggled = Signal(bool)
    cancelled = Signal()
    geometry_changed = Signal()
    triggered = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the shutter panel with arrange/adjust/close controls."""
        super().__init__(parent)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(_HINT_GAP)

        buttons = QWidget(self)
        buttons_layout = QVBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(_BUTTON_GAP)

        self._mode_button = self._make_emoji_button(_ARRANGE_EMOJI, "Arrange desktop")
        self._mode_button.clicked.connect(self.triggered.emit)
        buttons_layout.addWidget(self._mode_button)

        self._adjust_button = self._make_emoji_button(
            _ADJUST_EMOJI,
            "Adjust region after select (Enter confirms)",
        )
        self._adjust_button.setCheckable(True)
        self._adjust_button.toggled.connect(self.adjust_toggled.emit)
        buttons_layout.addWidget(self._adjust_button)

        close_button = self._make_emoji_button(_CLOSE_EMOJI, "Cancel screenshot")
        close_button.clicked.connect(self.cancelled.emit)
        buttons_layout.addWidget(close_button)

        root.addWidget(buttons, 0, Qt.AlignmentFlag.AlignTop)

        self._hint_label = QLabel(self)
        self._hint_label.setStyleSheet(_HINT_STYLE)
        self._hint_label.setWordWrap(True)
        self._hint_label.setFixedWidth(_HINT_WIDTH)
        self._hint_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self._hint_label.hide()
        root.addWidget(self._hint_label, 0, Qt.AlignmentFlag.AlignVCenter)

        self._mode: ShutterMode = "selection"
        self._hovered_button: QPushButton | None = None
        self._update_size()

    @property
    def adjust_mode(self) -> bool:
        """Whether the next selection should stay editable until confirmed."""
        return self._mode == "selection" and self._adjust_button.isChecked()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Show an in-panel caption while the pointer is over a shutter button."""
        if isinstance(watched, QPushButton):
            if event.type() == QEvent.Type.Enter:
                self._hovered_button = watched
                self._show_hint(str(watched.property("hover_hint") or watched.toolTip()))
            elif event.type() == QEvent.Type.Leave and self._hovered_button is watched:
                self._hovered_button = None
                self._hide_hint()
        return super().eventFilter(watched, event)

    def set_mode(self, mode: ShutterMode) -> None:
        """Update the mode button emoji for selection vs desktop-arrangement."""
        self._mode = mode
        if mode == "selection":
            # In region selection, click leaves capture to arrange other Windows.
            self._mode_button.setIcon(create_emoji_icon(_ARRANGE_EMOJI, _ICON_SIZE))
            self._mode_button.setToolTip("Arrange desktop")
            self._mode_button.setProperty("hover_hint", "Arrange desktop")
            self._adjust_button.show()
        else:
            # In arrange mode, click returns to region capture.
            self._mode_button.setIcon(create_emoji_icon(_CAMERA_EMOJI, _ICON_SIZE))
            self._mode_button.setToolTip("Capture region")
            self._mode_button.setProperty("hover_hint", "Capture region")
            self._adjust_button.hide()
            self._adjust_button.setChecked(False)
        if self._hovered_button is self._mode_button:
            self._show_hint(str(self._mode_button.property("hover_hint") or ""))
        self._update_size()

    def _hide_hint(self) -> None:
        if not self._hint_label.isVisible():
            return
        self._hint_label.hide()
        self._hint_label.clear()
        self._update_size()

    def _make_emoji_button(self, emoji: str, tooltip: str) -> QPushButton:
        button = QPushButton(self)
        button.setFixedSize(_BUTTON_SIZE, _BUTTON_SIZE)
        button.setIcon(create_emoji_icon(emoji, _ICON_SIZE))
        button.setIconSize(QSize(_ICON_SIZE, _ICON_SIZE))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip(tooltip)
        button.setProperty("hover_hint", tooltip)
        button.setStyleSheet(_BUTTON_STYLE)
        button.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
        button.installEventFilter(self)
        return button

    def _show_hint(self, text: str) -> None:
        if not text:
            self._hide_hint()
            return
        self._hint_label.setText(text)
        self._hint_label.show()
        self._update_size()

    def _update_size(self) -> None:
        button_count = 3 if self._mode == "selection" else 2
        total_height = _BUTTON_SIZE * button_count + _BUTTON_GAP * (button_count - 1)
        width = _BUTTON_SIZE
        if self._hint_label.isVisible():
            width += _HINT_GAP + _HINT_WIDTH
        self.setFixedSize(width, total_height)
        self.geometry_changed.emit()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create the shutter panel with arrange/adjust/close controls.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(_HINT_GAP)

        buttons = QWidget(self)
        buttons_layout = QVBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(_BUTTON_GAP)

        self._mode_button = self._make_emoji_button(_ARRANGE_EMOJI, "Arrange desktop")
        self._mode_button.clicked.connect(self.triggered.emit)
        buttons_layout.addWidget(self._mode_button)

        self._adjust_button = self._make_emoji_button(
            _ADJUST_EMOJI,
            "Adjust region after select (Enter confirms)",
        )
        self._adjust_button.setCheckable(True)
        self._adjust_button.toggled.connect(self.adjust_toggled.emit)
        buttons_layout.addWidget(self._adjust_button)

        close_button = self._make_emoji_button(_CLOSE_EMOJI, "Cancel screenshot")
        close_button.clicked.connect(self.cancelled.emit)
        buttons_layout.addWidget(close_button)

        root.addWidget(buttons, 0, Qt.AlignmentFlag.AlignTop)

        self._hint_label = QLabel(self)
        self._hint_label.setStyleSheet(_HINT_STYLE)
        self._hint_label.setWordWrap(True)
        self._hint_label.setFixedWidth(_HINT_WIDTH)
        self._hint_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self._hint_label.hide()
        root.addWidget(self._hint_label, 0, Qt.AlignmentFlag.AlignVCenter)

        self._mode: ShutterMode = "selection"
        self._hovered_button: QPushButton | None = None
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

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Show an in-panel caption while the pointer is over a shutter button.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if isinstance(watched, QPushButton):
            if event.type() == QEvent.Type.Enter:
                self._hovered_button = watched
                self._show_hint(str(watched.property("hover_hint") or watched.toolTip()))
            elif event.type() == QEvent.Type.Leave and self._hovered_button is watched:
                self._hovered_button = None
                self._hide_hint()
        return super().eventFilter(watched, event)
```

</details>

### ⚙️ Method `set_mode`

```python
def set_mode(self, mode: ShutterMode) -> None
```

Update the mode button emoji for selection vs desktop-arrangement.

<details>
<summary>Code:</summary>

```python
def set_mode(self, mode: ShutterMode) -> None:
        self._mode = mode
        if mode == "selection":
            # In region selection, click leaves capture to arrange other Windows.
            self._mode_button.setIcon(create_emoji_icon(_ARRANGE_EMOJI, _ICON_SIZE))
            self._mode_button.setToolTip("Arrange desktop")
            self._mode_button.setProperty("hover_hint", "Arrange desktop")
            self._adjust_button.show()
        else:
            # In arrange mode, click returns to region capture.
            self._mode_button.setIcon(create_emoji_icon(_CAMERA_EMOJI, _ICON_SIZE))
            self._mode_button.setToolTip("Capture region")
            self._mode_button.setProperty("hover_hint", "Capture region")
            self._adjust_button.hide()
            self._adjust_button.setChecked(False)
        if self._hovered_button is self._mode_button:
            self._show_hint(str(self._mode_button.property("hover_hint") or ""))
        self._update_size()
```

</details>

## 🔧 Function `position_panel_on_left_edge`

```python
def position_panel_on_left_edge(panel: ShutterPanel, overlay_geometry: QRect) -> None
```

Place an embedded panel at the primary screen's left edge inside the overlay.

Args:

- `panel` ([`ShutterPanel`](#%EF%B8%8F-class-shutterpanel)): Panel that is a child of the fullscreen overlay.
- `overlay_geometry` (`QRect`): Overlay geometry in global (virtual desktop) coordinates.

<details>
<summary>Code:</summary>

```python
def position_panel_on_left_edge(panel: ShutterPanel, overlay_geometry: QRect) -> None:
    screen = QApplication.primaryScreen()
    if screen is None:
        return
    geo = screen.availableGeometry()
    x = geo.x() - overlay_geometry.x() + _EDGE_MARGIN
    y = geo.y() - overlay_geometry.y() + (geo.height() - panel.height()) // 2
    panel.move(x, y)
```

</details>
