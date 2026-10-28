---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `card_base.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentCard`](#%EF%B8%8F-class-fluentcard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
- [🏛️ Class `FluentInteractiveCard`](#%EF%B8%8F-class-fluentinteractivecard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `contextMenuEvent`](#%EF%B8%8F-method-contextmenuevent)
  - [⚙️ Method `enterEvent`](#%EF%B8%8F-method-enterevent)
  - [⚙️ Method `focusInEvent`](#%EF%B8%8F-method-focusinevent)
  - [⚙️ Method `focusOutEvent`](#%EF%B8%8F-method-focusoutevent)
  - [⚙️ Method `is_selected`](#%EF%B8%8F-method-is_selected)
  - [⚙️ Method `keyPressEvent`](#%EF%B8%8F-method-keypressevent)
  - [⚙️ Method `leaveEvent`](#%EF%B8%8F-method-leaveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-1)
  - [⚙️ Method `paint_background`](#%EF%B8%8F-method-paint_background)
  - [⚙️ Method `set_selected`](#%EF%B8%8F-method-set_selected)

</details>

## 🏛️ Class `FluentCard`

```python
class FluentCard(QWidget)
```

Static card surface (`card_bg` + `card_stroke`, 8 px corners) for any content.

<details>
<summary>Code:</summary>

```python
class FluentCard(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty card; add content through `layout()` or your own layout."""
        super().__init__(parent)
        bind_theme(self, self.update)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the card surface."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        painter.end()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create an empty card; add content through `layout()` or your own layout.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the card surface.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.card_bg, palette.card_stroke, RADIUS_CARD)
        painter.end()
```

</details>

## 🏛️ Class `FluentInteractiveCard`

```python
class FluentInteractiveCard(FluentCard)
```

Clickable card with hover/pressed fills, keyboard activation, and a context menu signal.

<details>
<summary>Code:</summary>

```python
class FluentInteractiveCard(FluentCard):

    clicked = Signal()
    context_menu_requested = Signal(QPoint)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a clickable card."""
        self._hovered = False
        self._pressed = False
        self._selected = False
        self._focus_reason = Qt.FocusReason.OtherFocusReason
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # noqa: N802
        """Emit `context_menu_requested` with the global cursor position."""
        self.context_menu_requested.emit(event.globalPos())
        event.accept()

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Show the hover fill."""
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def focusInEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        """Remember why focus arrived (keyboard focus draws the ring)."""
        self._focus_reason = event.reason()
        self.update()
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        """Hide the focus ring."""
        self.update()
        super().focusOutEvent(event)

    def is_selected(self) -> bool:
        """Return whether the card shows the selected (accent) state."""
        return self._selected

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Activate on Enter or Space."""
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space}:
            self.clicked.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        """Drop the hover fill."""
        self._hovered = False
        self._pressed = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Show the pressed fill."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Emit `clicked` when released inside the card."""
        was_pressed = self._pressed
        self._pressed = False
        self.update()
        if (
            event.button() == Qt.MouseButton.LeftButton
            and was_pressed
            and self.rect().contains(event.position().toPoint())
        ):
            self.clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the card with hover, pressed, selected, and focus states."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        painter.end()

    def paint_background(self, painter: QPainter, palette: FluentPalette) -> None:
        """Paint the state-dependent card surface (subclasses paint content on top)."""
        fill = palette.card_bg
        if self._pressed:
            fill = palette.card_bg_pressed
        elif self._hovered:
            fill = palette.card_bg_hover
        stroke = palette.accent if self._selected else palette.card_stroke
        paint_surface(painter, self.rect(), fill, stroke, RADIUS_CARD)
        if self.hasFocus() and self.focusPolicy() != Qt.FocusPolicy.NoFocus and self._focus_visible():
            paint_surface(painter, self.rect(), None, palette.focus_stroke_outer, RADIUS_CARD, stroke_width=2)

    def set_selected(self, *, selected: bool) -> None:
        """Show or hide the selected (accent border) state."""
        self._selected = selected
        self.update()

    def _focus_visible(self) -> bool:
        return self._focus_reason in {Qt.FocusReason.TabFocusReason, Qt.FocusReason.BacktabFocusReason}
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a clickable card.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        self._hovered = False
        self._pressed = False
        self._selected = False
        self._focus_reason = Qt.FocusReason.OtherFocusReason
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
```

</details>

### ⚙️ Method `contextMenuEvent`

```python
def contextMenuEvent(self, event: QContextMenuEvent) -> None
```

Emit `context_menu_requested` with the global cursor position.

<details>
<summary>Code:</summary>

```python
def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # noqa: N802
        self.context_menu_requested.emit(event.globalPos())
        event.accept()
```

</details>

### ⚙️ Method `enterEvent`

```python
def enterEvent(self, event: QEnterEvent) -> None
```

Show the hover fill.

<details>
<summary>Code:</summary>

```python
def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        self._hovered = True
        self.update()
        super().enterEvent(event)
```

</details>

### ⚙️ Method `focusInEvent`

```python
def focusInEvent(self, event: QFocusEvent) -> None
```

Remember why focus arrived (keyboard focus draws the ring).

<details>
<summary>Code:</summary>

```python
def focusInEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        self._focus_reason = event.reason()
        self.update()
        super().focusInEvent(event)
```

</details>

### ⚙️ Method `focusOutEvent`

```python
def focusOutEvent(self, event: QFocusEvent) -> None
```

Hide the focus ring.

<details>
<summary>Code:</summary>

```python
def focusOutEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        self.update()
        super().focusOutEvent(event)
```

</details>

### ⚙️ Method `is_selected`

```python
def is_selected(self) -> bool
```

Return whether the card shows the selected (accent) state.

<details>
<summary>Code:</summary>

```python
def is_selected(self) -> bool:
        return self._selected
```

</details>

### ⚙️ Method `keyPressEvent`

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

Activate on Enter or Space.

<details>
<summary>Code:</summary>

```python
def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space}:
            self.clicked.emit()
            event.accept()
            return
        super().keyPressEvent(event)
```

</details>

### ⚙️ Method `leaveEvent`

```python
def leaveEvent(self, event: QEvent) -> None
```

Drop the hover fill.

<details>
<summary>Code:</summary>

```python
def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        self._hovered = False
        self._pressed = False
        self.update()
        super().leaveEvent(event)
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Show the pressed fill.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Emit `clicked` when released inside the card.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        was_pressed = self._pressed
        self._pressed = False
        self.update()
        if (
            event.button() == Qt.MouseButton.LeftButton
            and was_pressed
            and self.rect().contains(event.position().toPoint())
        ):
            self.clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the card with hover, pressed, selected, and focus states.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        painter.end()
```

</details>

### ⚙️ Method `paint_background`

```python
def paint_background(self, painter: QPainter, palette: FluentPalette) -> None
```

Paint the state-dependent card surface (subclasses paint content on top).

<details>
<summary>Code:</summary>

```python
def paint_background(self, painter: QPainter, palette: FluentPalette) -> None:
        fill = palette.card_bg
        if self._pressed:
            fill = palette.card_bg_pressed
        elif self._hovered:
            fill = palette.card_bg_hover
        stroke = palette.accent if self._selected else palette.card_stroke
        paint_surface(painter, self.rect(), fill, stroke, RADIUS_CARD)
        if self.hasFocus() and self.focusPolicy() != Qt.FocusPolicy.NoFocus and self._focus_visible():
            paint_surface(painter, self.rect(), None, palette.focus_stroke_outer, RADIUS_CARD, stroke_width=2)
```

</details>

### ⚙️ Method `set_selected`

```python
def set_selected(self, *, selected: bool) -> None
```

Show or hide the selected (accent border) state.

<details>
<summary>Code:</summary>

```python
def set_selected(self, *, selected: bool) -> None:
        self._selected = selected
        self.update()
```

</details>
