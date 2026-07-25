---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `shutter_button.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ShutterButton`](#%EF%B8%8F-class-shutterbutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `raise_above`](#%EF%B8%8F-method-raise_above)
  - [⚙️ Method `set_mode`](#%EF%B8%8F-method-set_mode)
  - [⚙️ Method `wait_for_trigger_or_cancel`](#%EF%B8%8F-method-wait_for_trigger_or_cancel)

</details>

## 🏛️ Class `ShutterButton`

```python
class ShutterButton(QDialog)
```

Frameless stay-on-top camera + close controls on the left edge of the primary screen.

Emits `triggered` on the mode button click and `cancelled` on close click or Escape.
Stays modeless so it can sit above the region overlay and toggle capture /
desktop-arrangement modes while the app stays hidden.

<details>
<summary>Code:</summary>

```python
class ShutterButton(QDialog):

    cancelled = Signal()
    triggered = Signal()

    def __init__(self) -> None:
        """Create the shutter control dialog."""
        super().__init__(None)
        mark_screenshot_ui(self)
        self.setWindowFlags(frameless_stay_on_top_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.NonModal)
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
        self._position_on_primary_screen()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Cancel capture on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
            return
        super().keyPressEvent(event)

    def raise_above(self) -> None:
        """Keep the controls visible above other screenshot UI."""
        self.show()
        self.raise_()

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

    def wait_for_trigger_or_cancel(self) -> bool:
        """Block until the mode button is clicked (`True`) or cancel/Escape (`False`)."""
        loop = QEventLoop()
        accepted = {"value": False}

        def on_triggered() -> None:
            accepted["value"] = True
            loop.quit()

        def on_cancelled() -> None:
            accepted["value"] = False
            loop.quit()

        self.triggered.connect(on_triggered)
        self.cancelled.connect(on_cancelled)
        try:
            self.set_mode("arrange")
            self.raise_above()
            self.activateWindow()
            loop.exec()
        finally:
            self.triggered.disconnect(on_triggered)
            self.cancelled.disconnect(on_cancelled)
        return accepted["value"]

    def _make_emoji_button(self, emoji: str, tooltip: str) -> QPushButton:
        button = QPushButton(self)
        button.setFixedSize(_BUTTON_SIZE, _BUTTON_SIZE)
        button.setIcon(create_emoji_icon(emoji, _ICON_SIZE))
        button.setIconSize(QSize(_ICON_SIZE, _ICON_SIZE))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip(tooltip)
        button.setStyleSheet(_BUTTON_STYLE)
        return button

    def _position_on_primary_screen(self) -> None:
        """Place the controls on the left edge, vertically centered."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.x() + 12
        y = geo.y() + (geo.height() - self.height()) // 2
        self.move(x, y)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Create the shutter control dialog.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        super().__init__(None)
        mark_screenshot_ui(self)
        self.setWindowFlags(frameless_stay_on_top_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.NonModal)
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
        self._position_on_primary_screen()
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Cancel capture on Escape.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `raise_above`

```python
def raise_above(self) -> None
```

Keep the controls visible above other screenshot UI.

<details>
<summary>Code:</summary>

```python
def raise_above(self) -> None:
        self.show()
        self.raise_()
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

### ⚙️ Method `wait_for_trigger_or_cancel`

```python
def wait_for_trigger_or_cancel(self) -> bool
```

Block until the mode button is clicked (`True`) or cancel/Escape (`False`).

<details>
<summary>Code:</summary>

```python
def wait_for_trigger_or_cancel(self) -> bool:
        loop = QEventLoop()
        accepted = {"value": False}

        def on_triggered() -> None:
            accepted["value"] = True
            loop.quit()

        def on_cancelled() -> None:
            accepted["value"] = False
            loop.quit()

        self.triggered.connect(on_triggered)
        self.cancelled.connect(on_cancelled)
        try:
            self.set_mode("arrange")
            self.raise_above()
            self.activateWindow()
            loop.exec()
        finally:
            self.triggered.disconnect(on_triggered)
            self.cancelled.disconnect(on_cancelled)
        return accepted["value"]
```

</details>
