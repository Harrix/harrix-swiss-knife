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
- [🏛️ Class `ShutterPanel`](#%EF%B8%8F-class-shutterpanel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
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
        panel = ShutterPanel(self)
        panel.set_mode("arrange")
        panel.triggered.connect(self.accept)
        panel.cancelled.connect(self.reject)
        self.setFixedSize(panel.size())
        self._position_on_primary_screen()

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
        panel = ShutterPanel(self)
        panel.set_mode("arrange")
        panel.triggered.connect(self.accept)
        panel.cancelled.connect(self.reject)
        self.setFixedSize(panel.size())
        self._position_on_primary_screen()
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

<details>
<summary>Code:</summary>

```python
class ShutterPanel(QWidget):

    cancelled = Signal()
    triggered = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create the two-button shutter panel."""
        super().__init__(parent)
        total_height = _BUTTON_SIZE * 2 + _BUTTON_GAP
        self.setFixedSize(_BUTTON_SIZE, total_height)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(_BUTTON_GAP)

        self._mode_button = self._make_emoji_button(_ARRANGE_EMOJI, "Arrange desktop")
        self._mode_button.clicked.connect(self.triggered.emit)
        layout.addWidget(self._mode_button)

        close_button = self._make_emoji_button(_CLOSE_EMOJI, "Cancel screenshot")
        close_button.clicked.connect(self.cancelled.emit)
        layout.addWidget(close_button)

        self._mode: ShutterMode = "selection"

    def set_mode(self, mode: ShutterMode) -> None:
        """Update the mode button emoji for selection vs desktop-arrangement."""
        self._mode = mode
        if mode == "selection":
            # In region selection, click leaves capture to arrange other Windows.
            self._mode_button.setIcon(create_emoji_icon(_ARRANGE_EMOJI, _ICON_SIZE))
            self._mode_button.setToolTip("Arrange desktop")
        else:
            # In arrange mode, click returns to region capture.
            self._mode_button.setIcon(create_emoji_icon(_CAMERA_EMOJI, _ICON_SIZE))
            self._mode_button.setToolTip("Capture region")

    def _make_emoji_button(self, emoji: str, tooltip: str) -> QPushButton:
        button = QPushButton(self)
        button.setFixedSize(_BUTTON_SIZE, _BUTTON_SIZE)
        button.setIcon(create_emoji_icon(emoji, _ICON_SIZE))
        button.setIconSize(QSize(_ICON_SIZE, _ICON_SIZE))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip(tooltip)
        button.setStyleSheet(_BUTTON_STYLE)
        return button
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create the two-button shutter panel.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        total_height = _BUTTON_SIZE * 2 + _BUTTON_GAP
        self.setFixedSize(_BUTTON_SIZE, total_height)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(_BUTTON_GAP)

        self._mode_button = self._make_emoji_button(_ARRANGE_EMOJI, "Arrange desktop")
        self._mode_button.clicked.connect(self.triggered.emit)
        layout.addWidget(self._mode_button)

        close_button = self._make_emoji_button(_CLOSE_EMOJI, "Cancel screenshot")
        close_button.clicked.connect(self.cancelled.emit)
        layout.addWidget(close_button)

        self._mode: ShutterMode = "selection"
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
        else:
            # In arrange mode, click returns to region capture.
            self._mode_button.setIcon(create_emoji_icon(_CAMERA_EMOJI, _ICON_SIZE))
            self._mode_button.setToolTip("Capture region")
```

</details>

## 🔧 Function `position_panel_on_left_edge`

```python
def position_panel_on_left_edge(panel: ShutterPanel, overlay_geometry: QRect) -> None
```

Place an embedded panel at the primary screen's left edge inside the overlay.

Args:

- `panel` (`ShutterPanel`): Panel that is a child of the fullscreen overlay.
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
