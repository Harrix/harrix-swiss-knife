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

Frameless stay-on-top camera button on the left edge of the primary screen.

Emits `triggered` on click and `cancelled` on Escape. Stays modeless so it can
sit above the region overlay and toggle capture / window-management modes.

<details>
<summary>Code:</summary>

```python
class ShutterButton(QDialog):

    cancelled = Signal()
    triggered = Signal()

    def __init__(self) -> None:
        """Create the shutter button dialog."""
        super().__init__(None)
        mark_screenshot_ui(self)
        self.setWindowFlags(frameless_stay_on_top_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setFixedSize(_SHUTTER_SIZE, _SHUTTER_SIZE)

        button = QPushButton(self)
        button.setFixedSize(_SHUTTER_SIZE, _SHUTTER_SIZE)
        button.setIcon(create_emoji_icon(_CAMERA_EMOJI, 36))
        button.setIconSize(QSize(36, 36))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(40, 40, 40, 220);
                border: 2px solid rgba(255, 255, 255, 180);
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(60, 60, 60, 240);
                border-color: rgba(255, 255, 255, 230);
            }
            QPushButton:pressed {
                background-color: rgba(20, 20, 20, 240);
            }
            """
        )
        button.clicked.connect(self.triggered.emit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(button)

        self._position_on_primary_screen()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Cancel capture on Escape."""
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
            return
        super().keyPressEvent(event)

    def raise_above(self) -> None:
        """Keep the shutter visible above other screenshot UI."""
        self.show()
        self.raise_()

    def wait_for_trigger_or_cancel(self) -> bool:
        """Block until the button is clicked (`True`) or Escape is pressed (`False`)."""
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

    def _position_on_primary_screen(self) -> None:
        """Place the button on the left edge, vertically centered."""
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.x() + 12
        y = geo.y() + (geo.height() - _SHUTTER_SIZE) // 2
        self.move(x, y)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Create the shutter button dialog.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        super().__init__(None)
        mark_screenshot_ui(self)
        self.setWindowFlags(frameless_stay_on_top_flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setFixedSize(_SHUTTER_SIZE, _SHUTTER_SIZE)

        button = QPushButton(self)
        button.setFixedSize(_SHUTTER_SIZE, _SHUTTER_SIZE)
        button.setIcon(create_emoji_icon(_CAMERA_EMOJI, 36))
        button.setIconSize(QSize(36, 36))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(40, 40, 40, 220);
                border: 2px solid rgba(255, 255, 255, 180);
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(60, 60, 60, 240);
                border-color: rgba(255, 255, 255, 230);
            }
            QPushButton:pressed {
                background-color: rgba(20, 20, 20, 240);
            }
            """
        )
        button.clicked.connect(self.triggered.emit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(button)

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

Keep the shutter visible above other screenshot UI.

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

Block until the button is clicked (`True`) or Escape is pressed (`False`).

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
