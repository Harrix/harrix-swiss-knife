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
  - [⚙️ Method `wait_for_trigger_or_cancel`](#%EF%B8%8F-method-wait_for_trigger_or_cancel)

</details>

## 🏛️ Class `ShutterButton`

```python
class ShutterButton(QDialog)
```

Frameless stay-on-top camera + close controls on the left edge of the primary screen.

Emits `triggered` on camera click and `cancelled` on close click or Escape.
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

        shutter = self._make_emoji_button(_CAMERA_EMOJI, "Capture / arrange desktop")
        shutter.clicked.connect(self.triggered.emit)
        layout.addWidget(shutter)

        close_button = self._make_emoji_button(_CLOSE_EMOJI, "Cancel screenshot")
        close_button.clicked.connect(self.cancelled.emit)
        layout.addWidget(close_button)

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

    def wait_for_trigger_or_cancel(self) -> bool:
        """Block until the camera is clicked (`True`) or cancel/Escape (`False`)."""
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
        button.setIcon(create_emoji_icon(emoji, 36))
        button.setIconSize(QSize(36, 36))
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

        shutter = self._make_emoji_button(_CAMERA_EMOJI, "Capture / arrange desktop")
        shutter.clicked.connect(self.triggered.emit)
        layout.addWidget(shutter)

        close_button = self._make_emoji_button(_CLOSE_EMOJI, "Cancel screenshot")
        close_button.clicked.connect(self.cancelled.emit)
        layout.addWidget(close_button)

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

### ⚙️ Method `wait_for_trigger_or_cancel`

```python
def wait_for_trigger_or_cancel(self) -> bool
```

Block until the camera is clicked (`True`) or cancel/Escape (`False`).

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
            self.raise_above()
            self.activateWindow()
            loop.exec()
        finally:
            self.triggered.disconnect(on_triggered)
            self.cancelled.disconnect(on_cancelled)
        return accepted["value"]
```

</details>
