---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `picker_base.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentRoller`](#%EF%B8%8F-class-fluentroller)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `current_index`](#%EF%B8%8F-method-current_index)
  - [⚙️ Method `current_text`](#%EF%B8%8F-method-current_text)
  - [⚙️ Method `mouseMoveEvent`](#%EF%B8%8F-method-mousemoveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `set_current`](#%EF%B8%8F-method-set_current)
  - [⚙️ Method `set_items`](#%EF%B8%8F-method-set_items)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
  - [⚙️ Method `wheelEvent`](#%EF%B8%8F-method-wheelevent)
- [🏛️ Class `FluentRollerPicker`](#%EF%B8%8F-class-fluentrollerpicker)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `format_values`](#%EF%B8%8F-method-format_values)
  - [⚙️ Method `open_popup`](#%EF%B8%8F-method-open_popup)
  - [⚙️ Method `values`](#%EF%B8%8F-method-values)

</details>

## 🏛️ Class `FluentRoller`

```python
class FluentRoller(QWidget)
```

Vertical scroll wheel of values that snaps to the middle row.

<details>
<summary>Code:</summary>

```python
class FluentRoller(QWidget):

    current_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None, *, items: Sequence[str] = (), looping: bool = False) -> None:
        """Create a roller."""
        super().__init__(parent)
        self._items = list(items)
        self._looping = looping
        self._offset = 0.0
        self._current = 0
        self._drag_y: float | None = None
        self._press_y = 0.0
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._on_animation)
        self.setFixedSize(_ROLLER_WIDTH, _ROLLER_ROW_HEIGHT * _ROLLER_VISIBLE_ROWS)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        bind_theme(self, self.update)

    def current_index(self) -> int:
        """Return the selected index."""
        return self._current

    def current_text(self) -> str:
        """Return the selected item."""
        return self._items[self._current] if self._items else ""

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Drag the wheel."""
        if self._drag_y is None:
            return
        delta = event.position().y() - self._drag_y
        self._drag_y = event.position().y()
        self._offset -= delta / _ROLLER_ROW_HEIGHT
        self._clamp()
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start dragging."""
        self._drag_y = event.position().y()
        self._press_y = event.position().y()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Snap after a drag, or select the clicked row."""
        moved = abs(event.position().y() - self._press_y) > _CLICK_SLOP_PX
        self._drag_y = None
        if not moved:
            row = int(event.position().y() // _ROLLER_ROW_HEIGHT) - _ROLLER_VISIBLE_ROWS // 2
            self.set_current(self._normalize(round(self._offset) + row))
            return
        self.set_current(self._normalize(round(self._offset)))

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint rows around the highlighted middle row."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        middle = QRectF(
            SPACE_XS,
            (_ROLLER_VISIBLE_ROWS // 2) * _ROLLER_ROW_HEIGHT + 2,
            self.width() - 2 * SPACE_XS,
            _ROLLER_ROW_HEIGHT - 4,
        )
        paint_surface(painter, middle, palette.accent, None, RADIUS_CONTROL)
        painter.setFont(fluent_font(self.font(), TYPE_BODY))
        if not self._items:
            painter.end()
            return
        base = int(self._offset // 1)
        fraction = self._offset - base
        half = _ROLLER_VISIBLE_ROWS // 2
        for row in range(-half - 1, half + 2):
            index = base + row
            if not self._looping and not 0 <= index < len(self._items):
                continue
            text = self._items[index % len(self._items)]
            y = (row + half - fraction) * _ROLLER_ROW_HEIGHT
            rect = QRectF(0, y, self.width(), _ROLLER_ROW_HEIGHT)
            selected = abs(row - fraction) < 0.5  # noqa: PLR2004
            painter.setPen(palette.text_on_accent if selected else palette.text_primary)
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), text)
        painter.end()

    def set_current(self, index: int) -> None:
        """Select `index` with a snap animation."""
        if not self._items:
            return
        index = self._normalize(index)
        target = float(index)
        if self._looping:
            base = round(self._offset) - self._normalize(round(self._offset))
            target = base + index
        self._animation.stop()
        self._animation.setStartValue(self._offset)
        self._animation.setEndValue(target)
        self._animation.start()
        changed = index != self._current
        self._current = index
        if changed:
            self.current_changed.emit(index)

    def set_items(self, items: Sequence[str]) -> None:
        """Replace the values."""
        self._items = list(items)
        self._current = min(self._current, max(0, len(self._items) - 1))
        self._offset = float(self._current)
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the fixed roller size."""
        return QSize(_ROLLER_WIDTH, _ROLLER_ROW_HEIGHT * _ROLLER_VISIBLE_ROWS)

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        """Step one row per wheel notch."""
        step = -1 if event.angleDelta().y() > 0 else 1
        self.set_current(self._current + step)
        event.accept()

    def _clamp(self) -> None:
        if not self._looping:
            self._offset = max(0.0, min(float(len(self._items) - 1), self._offset))

    def _normalize(self, index: int) -> int:
        if not self._items:
            return 0
        if self._looping:
            return index % len(self._items)
        return max(0, min(len(self._items) - 1, index))

    def _on_animation(self, value: object) -> None:
        self._offset = float(value)  # ty: ignore[invalid-argument-type]
        self.update()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, items: Sequence[str] = (), looping: bool = False) -> None
```

Create a roller.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, items: Sequence[str] = (), looping: bool = False) -> None:
        super().__init__(parent)
        self._items = list(items)
        self._looping = looping
        self._offset = 0.0
        self._current = 0
        self._drag_y: float | None = None
        self._press_y = 0.0
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._on_animation)
        self.setFixedSize(_ROLLER_WIDTH, _ROLLER_ROW_HEIGHT * _ROLLER_VISIBLE_ROWS)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `current_index`

```python
def current_index(self) -> int
```

Return the selected index.

<details>
<summary>Code:</summary>

```python
def current_index(self) -> int:
        return self._current
```

</details>

### ⚙️ Method `current_text`

```python
def current_text(self) -> str
```

Return the selected item.

<details>
<summary>Code:</summary>

```python
def current_text(self) -> str:
        return self._items[self._current] if self._items else ""
```

</details>

### ⚙️ Method `mouseMoveEvent`

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None
```

Drag the wheel.

<details>
<summary>Code:</summary>

```python
def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._drag_y is None:
            return
        delta = event.position().y() - self._drag_y
        self._drag_y = event.position().y()
        self._offset -= delta / _ROLLER_ROW_HEIGHT
        self._clamp()
        self.update()
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Start dragging.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._drag_y = event.position().y()
        self._press_y = event.position().y()
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Snap after a drag, or select the clicked row.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        moved = abs(event.position().y() - self._press_y) > _CLICK_SLOP_PX
        self._drag_y = None
        if not moved:
            row = int(event.position().y() // _ROLLER_ROW_HEIGHT) - _ROLLER_VISIBLE_ROWS // 2
            self.set_current(self._normalize(round(self._offset) + row))
            return
        self.set_current(self._normalize(round(self._offset)))
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint rows around the highlighted middle row.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        middle = QRectF(
            SPACE_XS,
            (_ROLLER_VISIBLE_ROWS // 2) * _ROLLER_ROW_HEIGHT + 2,
            self.width() - 2 * SPACE_XS,
            _ROLLER_ROW_HEIGHT - 4,
        )
        paint_surface(painter, middle, palette.accent, None, RADIUS_CONTROL)
        painter.setFont(fluent_font(self.font(), TYPE_BODY))
        if not self._items:
            painter.end()
            return
        base = int(self._offset // 1)
        fraction = self._offset - base
        half = _ROLLER_VISIBLE_ROWS // 2
        for row in range(-half - 1, half + 2):
            index = base + row
            if not self._looping and not 0 <= index < len(self._items):
                continue
            text = self._items[index % len(self._items)]
            y = (row + half - fraction) * _ROLLER_ROW_HEIGHT
            rect = QRectF(0, y, self.width(), _ROLLER_ROW_HEIGHT)
            selected = abs(row - fraction) < 0.5  # noqa: PLR2004
            painter.setPen(palette.text_on_accent if selected else palette.text_primary)
            painter.drawText(rect, int(Qt.AlignmentFlag.AlignCenter), text)
        painter.end()
```

</details>

### ⚙️ Method `set_current`

```python
def set_current(self, index: int) -> None
```

Select `index` with a snap animation.

<details>
<summary>Code:</summary>

```python
def set_current(self, index: int) -> None:
        if not self._items:
            return
        index = self._normalize(index)
        target = float(index)
        if self._looping:
            base = round(self._offset) - self._normalize(round(self._offset))
            target = base + index
        self._animation.stop()
        self._animation.setStartValue(self._offset)
        self._animation.setEndValue(target)
        self._animation.start()
        changed = index != self._current
        self._current = index
        if changed:
            self.current_changed.emit(index)
```

</details>

### ⚙️ Method `set_items`

```python
def set_items(self, items: Sequence[str]) -> None
```

Replace the values.

<details>
<summary>Code:</summary>

```python
def set_items(self, items: Sequence[str]) -> None:
        self._items = list(items)
        self._current = min(self._current, max(0, len(self._items) - 1))
        self._offset = float(self._current)
        self.update()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self) -> QSize
```

Return the fixed roller size.

<details>
<summary>Code:</summary>

```python
def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(_ROLLER_WIDTH, _ROLLER_ROW_HEIGHT * _ROLLER_VISIBLE_ROWS)
```

</details>

### ⚙️ Method `wheelEvent`

```python
def wheelEvent(self, event: QWheelEvent) -> None
```

Step one row per wheel notch.

<details>
<summary>Code:</summary>

```python
def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        step = -1 if event.angleDelta().y() > 0 else 1
        self.set_current(self._current + step)
        event.accept()
```

</details>

## 🏛️ Class `FluentRollerPicker`

```python
class FluentRollerPicker(FluentPushButton)
```

Button that opens a flyout of side-by-side rollers with Accept / Cancel.

<details>
<summary>Code:</summary>

```python
class FluentRollerPicker(FluentPushButton):

    accepted = Signal(list)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        columns: Sequence[Sequence[str]] = (),
        looping: bool = True,
        placeholder: str = "Select",
    ) -> None:
        """Create a roller picker with one roller per column."""
        super().__init__(placeholder, parent)
        self._placeholder = placeholder
        self._separator = " "
        self._popup = QFrame(
            self, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        )
        self._popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self._popup.setObjectName("FluentRollerPopup")
        outer = QVBoxLayout(self._popup)
        outer.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        row = QHBoxLayout()
        row.setSpacing(0)
        self.rollers: list[FluentRoller] = []
        for column in columns:
            roller = FluentRoller(self._popup, items=column, looping=looping)
            self.rollers.append(roller)
            row.addWidget(roller)
        outer.addLayout(row)
        buttons = QHBoxLayout()
        buttons.setContentsMargins(SPACE_S, SPACE_XS, SPACE_S, SPACE_XS)
        accept = FluentPrimaryButton("OK", self._popup)
        cancel = FluentPushButton("Cancel", self._popup)
        accept.clicked.connect(self._accept)
        cancel.clicked.connect(self._popup.hide)
        buttons.addWidget(accept, 1)
        buttons.addWidget(cancel, 1)
        outer.addLayout(buttons)
        self.clicked.connect(self.open_popup)
        self._values: list[str] = []
        bind_theme(self._popup, self._recolor_popup)

    def format_values(self, values: list[str]) -> str:
        """Return the button caption for accepted values."""
        return self._separator.join(values)

    def open_popup(self) -> None:
        """Show the rollers centered under the button."""
        self._popup.adjustSize()
        x = self.width() // 2 - self._popup.width() // 2
        self._popup.move(self.mapToGlobal(QPoint(max(0, x), self.height() + SPACE_XS)))
        self._popup.show()

    def values(self) -> list[str]:
        """Return the accepted values (one per roller)."""
        return list(self._values)

    def _accept(self) -> None:
        self._values = [roller.current_text() for roller in self.rollers]
        self.setText(self.format_values(self._values))
        self._popup.hide()
        self.accepted.emit(self.values())

    def _recolor_popup(self) -> None:
        palette = palette_for(self)
        surface = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        self._popup.setStyleSheet(
            f"QFrame#FluentRollerPopup {{ background: {css(surface)}; border: 1px solid {css(palette.popup_stroke)};"
            f" border-radius: {RADIUS_OVERLAY}px; }}\n{scroll_bar_qss(palette)}",
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, columns: Sequence[Sequence[str]] = (), looping: bool = True, placeholder: str = 'Select') -> None
```

Create a roller picker with one roller per column.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None = None,
        *,
        columns: Sequence[Sequence[str]] = (),
        looping: bool = True,
        placeholder: str = "Select",
    ) -> None:
        super().__init__(placeholder, parent)
        self._placeholder = placeholder
        self._separator = " "
        self._popup = QFrame(
            self, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        )
        self._popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self._popup.setObjectName("FluentRollerPopup")
        outer = QVBoxLayout(self._popup)
        outer.setContentsMargins(SPACE_XS, SPACE_XS, SPACE_XS, SPACE_XS)
        row = QHBoxLayout()
        row.setSpacing(0)
        self.rollers: list[FluentRoller] = []
        for column in columns:
            roller = FluentRoller(self._popup, items=column, looping=looping)
            self.rollers.append(roller)
            row.addWidget(roller)
        outer.addLayout(row)
        buttons = QHBoxLayout()
        buttons.setContentsMargins(SPACE_S, SPACE_XS, SPACE_S, SPACE_XS)
        accept = FluentPrimaryButton("OK", self._popup)
        cancel = FluentPushButton("Cancel", self._popup)
        accept.clicked.connect(self._accept)
        cancel.clicked.connect(self._popup.hide)
        buttons.addWidget(accept, 1)
        buttons.addWidget(cancel, 1)
        outer.addLayout(buttons)
        self.clicked.connect(self.open_popup)
        self._values: list[str] = []
        bind_theme(self._popup, self._recolor_popup)
```

</details>

### ⚙️ Method `format_values`

```python
def format_values(self, values: list[str]) -> str
```

Return the button caption for accepted values.

<details>
<summary>Code:</summary>

```python
def format_values(self, values: list[str]) -> str:
        return self._separator.join(values)
```

</details>

### ⚙️ Method `open_popup`

```python
def open_popup(self) -> None
```

Show the rollers centered under the button.

<details>
<summary>Code:</summary>

```python
def open_popup(self) -> None:
        self._popup.adjustSize()
        x = self.width() // 2 - self._popup.width() // 2
        self._popup.move(self.mapToGlobal(QPoint(max(0, x), self.height() + SPACE_XS)))
        self._popup.show()
```

</details>

### ⚙️ Method `values`

```python
def values(self) -> list[str]
```

Return the accepted values (one per roller).

<details>
<summary>Code:</summary>

```python
def values(self) -> list[str]:
        return list(self._values)
```

</details>
