---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `exercise_avif_lightbox.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ExerciseAvifLightboxDialog`](#%EF%B8%8F-class-exerciseaviflightboxdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `closeEvent`](#%EF%B8%8F-method-closeevent)
  - [⚙️ Method `done`](#%EF%B8%8F-method-done)
  - [⚙️ Method `empty_caption`](#%EF%B8%8F-method-empty_caption)
  - [⚙️ Method `resizeEvent`](#%EF%B8%8F-method-resizeevent)
  - [⚙️ Method `show_item`](#%EF%B8%8F-method-show_item)
- [🏛️ Class `LightboxAvifLabel`](#%EF%B8%8F-class-lightboxaviflabel)
  - [⚙️ Method `mouseDoubleClickEvent`](#%EF%B8%8F-method-mousedoubleclickevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)

</details>

## 🏛️ Class `ExerciseAvifLightboxDialog`

```python
class ExerciseAvifLightboxDialog(AppWindowLightboxDialog)
```

Browse exercise AVIF animations with the shared window lightbox chrome.

<details>
<summary>Code:</summary>

```python
class ExerciseAvifLightboxDialog(AppWindowLightboxDialog):

    def __init__(
        self,
        exercises: Sequence[str],
        *,
        avif_manager: AvifManager,
        current_index: int = 0,
        parent: QWidget | None = None,
        show_speed_slider: bool = False,
    ) -> None:
        """Build a lightbox for `exercises` that have media.

        Args:

        - `exercises` (`Sequence[str]`): Exercise names in navigation order.
        - `avif_manager` (`AvifManager`): Loader for static and animated AVIF files.
        - `current_index` (`int`): Initial exercise index. Defaults to `0`.
        - `parent` (`QWidget | None`): Widget whose top-level window is covered.
        - `show_speed_slider` (`bool`): When `True`, show a speed slider for
          animated AVIFs (Fitness lightbox only). Defaults to `False`.

        """
        names = [name for name in exercises if name]
        super().__init__(parent, item_count=len(names), current_index=current_index)
        self._exercises = names
        self._avif_manager = avif_manager
        self._loaded_size = QSize()
        self._reload_timer = QTimer(self)
        self._reload_timer.setSingleShot(True)
        self._reload_timer.timeout.connect(self._reload_current)
        self._speed_bar: QWidget | None = None
        self._speed_slider: QSlider | None = None
        self._speed_value_label: QLabel | None = None

        self._label = LightboxAvifLabel(self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet("background: transparent; border: none;")
        self.attach_content(self._label)
        if show_speed_slider:
            self._build_speed_controls()
        self.finish_setup()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Stop the lightbox animation when the dialog is closed."""
        self._stop_avif()
        super().closeEvent(event)

    def done(self, result: int) -> None:
        """Stop the lightbox animation when `exec` finishes."""
        self._stop_avif()
        super().done(result)

    def empty_caption(self) -> str:
        """Caption when there are no exercises."""
        return "No exercise image to display"

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Reload AVIF frames after the overlay is resized."""
        super().resizeEvent(event)
        self._schedule_avif_reload()

    def show_item(self, index: int) -> None:
        """Load the exercise AVIF at `index`."""
        name = self._exercises[index]
        self.setWindowTitle(name)
        self.set_caption(f"{name}  ·  {index + 1} / {len(self._exercises)}")
        self._reload_current()

    def _build_speed_controls(self) -> None:
        bar = QWidget(self)
        bar.setObjectName("lightboxSpeedBar")
        bar.setStyleSheet(
            "QWidget#lightboxSpeedBar { background: rgba(20, 20, 20, 180); border-radius: 7px; }"
            "QLabel { color: white; background: transparent; }"
            "QSlider::groove:horizontal { height: 6px; background: rgba(255, 255, 255, 80);"
            "border-radius: 3px; }"
            "QSlider::handle:horizontal { width: 16px; height: 16px; margin: -5px 0;"
            "background: white; border-radius: 8px; }"
        )
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)
        title = QLabel("Speed", bar)
        slider = QSlider(Qt.Orientation.Horizontal, bar)
        slider.setRange(_SPEED_MIN_PERCENT, _SPEED_MAX_PERCENT)
        slider.setValue(_SPEED_DEFAULT_PERCENT)
        slider.setSingleStep(25)
        slider.setPageStep(25)
        slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        slider.setFixedHeight(22)
        slider.setToolTip("Slow down or speed up the animation")
        slider.valueChanged.connect(self._on_speed_changed)
        value = QLabel(self._format_speed(_SPEED_DEFAULT_PERCENT / 100.0), bar)
        value.setMinimumWidth(44)
        value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title)
        layout.addWidget(slider, stretch=1)
        layout.addWidget(value)
        bar.hide()
        self._speed_bar = bar
        self._speed_slider = slider
        self._speed_value_label = value

    def _format_speed(self, speed: float) -> str:
        return f"{speed:.2f}x"

    def _on_speed_changed(self, percent: int) -> None:
        speed = percent / 100.0
        if self._speed_value_label is not None:
            self._speed_value_label.setText(self._format_speed(speed))
        self._avif_manager.set_animation_speed(AvifLabelKey.LIGHTBOX, speed)

    def _position_controls(self) -> None:
        super()._position_controls()
        if self._speed_bar is None or self._speed_bar.isHidden():
            return
        bar_width = min(360, max(220, self.width() - 280))
        self._speed_bar.setFixedWidth(bar_width)
        self._speed_bar.adjustSize()
        y = self._caption.y() - self._speed_bar.height() - 10
        self._speed_bar.move((self.width() - bar_width) // 2, max(_SPEED_SIDE_MARGIN, y))
        self._speed_bar.raise_()

    def _reload_current(self) -> None:
        if not self._exercises:
            return
        name = self._exercises[self._index]
        self._avif_manager.load_exercise_avif(name, self._label, AvifLabelKey.LIGHTBOX)
        self._loaded_size = self._label.size()
        self._sync_speed_controls()

    def _schedule_avif_reload(self) -> None:
        if self._label.width() < _MIN_RELOAD_EDGE or self._label.height() < _MIN_RELOAD_EDGE:
            return
        if self._loaded_size == self._label.size():
            return
        self._reload_timer.start(_RELOAD_DELAY_MS)

    def _stop_avif(self) -> None:
        if self._reload_timer.isActive():
            self._reload_timer.stop()
        self._avif_manager.stop_animation(AvifLabelKey.LIGHTBOX)

    def _sync_speed_controls(self) -> None:
        if self._speed_bar is None:
            return
        visible = self._avif_manager.is_animation_active(AvifLabelKey.LIGHTBOX)
        self._speed_bar.setVisible(visible)
        if visible and self._speed_slider is not None:
            self._avif_manager.set_animation_speed(
                AvifLabelKey.LIGHTBOX,
                self._speed_slider.value() / 100.0,
            )
        self._position_controls()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, exercises: Sequence[str], *, avif_manager: AvifManager, current_index: int = 0, parent: QWidget | None = None, show_speed_slider: bool = False) -> None
```

Build a lightbox for `exercises` that have media.

Args:

- `exercises` (`Sequence[str]`): Exercise names in navigation order.
- `avif_manager` ([`AvifManager`](../avif_manager.g.md#%EF%B8%8F-class-avifmanager)): Loader for static and animated AVIF files.
- [`current_index`](app_window_lightbox.g.md#%EF%B8%8F-method-current_index-property) (`int`): Initial exercise index. Defaults to `0`.
- `parent` (`QWidget | None`): Widget whose top-level window is covered.
- `show_speed_slider` (`bool`): When `True`, show a speed slider for
  animated AVIFs (Fitness lightbox only). Defaults to `False`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        exercises: Sequence[str],
        *,
        avif_manager: AvifManager,
        current_index: int = 0,
        parent: QWidget | None = None,
        show_speed_slider: bool = False,
    ) -> None:
        names = [name for name in exercises if name]
        super().__init__(parent, item_count=len(names), current_index=current_index)
        self._exercises = names
        self._avif_manager = avif_manager
        self._loaded_size = QSize()
        self._reload_timer = QTimer(self)
        self._reload_timer.setSingleShot(True)
        self._reload_timer.timeout.connect(self._reload_current)
        self._speed_bar: QWidget | None = None
        self._speed_slider: QSlider | None = None
        self._speed_value_label: QLabel | None = None

        self._label = LightboxAvifLabel(self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet("background: transparent; border: none;")
        self.attach_content(self._label)
        if show_speed_slider:
            self._build_speed_controls()
        self.finish_setup()
```

</details>

### ⚙️ Method `closeEvent`

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Stop the lightbox animation when the dialog is closed.

<details>
<summary>Code:</summary>

```python
def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._stop_avif()
        super().closeEvent(event)
```

</details>

### ⚙️ Method `done`

```python
def done(self, result: int) -> None
```

Stop the lightbox animation when `exec` finishes.

<details>
<summary>Code:</summary>

```python
def done(self, result: int) -> None:
        self._stop_avif()
        super().done(result)
```

</details>

### ⚙️ Method `empty_caption`

```python
def empty_caption(self) -> str
```

Caption when there are no exercises.

<details>
<summary>Code:</summary>

```python
def empty_caption(self) -> str:
        return "No exercise image to display"
```

</details>

### ⚙️ Method `resizeEvent`

```python
def resizeEvent(self, event: QResizeEvent) -> None
```

Reload AVIF frames after the overlay is resized.

<details>
<summary>Code:</summary>

```python
def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._schedule_avif_reload()
```

</details>

### ⚙️ Method `show_item`

```python
def show_item(self, index: int) -> None
```

Load the exercise AVIF at `index`.

<details>
<summary>Code:</summary>

```python
def show_item(self, index: int) -> None:
        name = self._exercises[index]
        self.setWindowTitle(name)
        self.set_caption(f"{name}  ·  {index + 1} / {len(self._exercises)}")
        self._reload_current()
```

</details>

## 🏛️ Class `LightboxAvifLabel`

```python
class LightboxAvifLabel(QLabel)
```

Centered AVIF surface that closes the lightbox on backdrop or double-click.

<details>
<summary>Code:</summary>

```python
class LightboxAvifLabel(QLabel):

    backdrop_clicked = Signal()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Close the lightbox on a left double-click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.backdrop_clicked.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Close after a click outside the displayed pixmap."""
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            return
        pixmap_rect = self._pixmap_rect()
        if pixmap_rect.isNull() or not pixmap_rect.contains(event.position().toPoint()):
            self.backdrop_clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _pixmap_rect(self) -> QRect:
        pixmap = self.pixmap()
        if pixmap is None or pixmap.isNull():
            return QRect()
        dpr = pixmap.devicePixelRatio() or 1.0
        width = max(1, int(pixmap.width() / dpr))
        height = max(1, int(pixmap.height() / dpr))
        x = (self.width() - width) // 2
        y = (self.height() - height) // 2
        return QRect(x, y, width, height)
```

</details>

### ⚙️ Method `mouseDoubleClickEvent`

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None
```

Close the lightbox on a left double-click.

<details>
<summary>Code:</summary>

```python
def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.backdrop_clicked.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Close after a click outside the displayed pixmap.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            return
        pixmap_rect = self._pixmap_rect()
        if pixmap_rect.isNull() or not pixmap_rect.contains(event.position().toPoint()):
            self.backdrop_clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)
```

</details>
