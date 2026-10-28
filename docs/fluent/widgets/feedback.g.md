---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `feedback.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentFloatButton`](#%EF%B8%8F-class-fluentfloatbutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `enterEvent`](#%EF%B8%8F-method-enterevent)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `leaveEvent`](#%EF%B8%8F-method-leaveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
- [🏛️ Class `FluentFlyout`](#%EF%B8%8F-class-fluentflyout)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-1)
  - [⚙️ Method `popup`](#%EF%B8%8F-method-popup)
- [🏛️ Class `FluentInfoBar`](#%EF%B8%8F-class-fluentinfobar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `close_bar`](#%EF%B8%8F-method-close_bar)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-2)
  - [⚙️ Method `severity`](#%EF%B8%8F-method-severity)
- [🏛️ Class `FluentMessageBar`](#%EF%B8%8F-class-fluentmessagebar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter-1)
  - [⚙️ Method `show_bar`](#%EF%B8%8F-method-show_bar)
  - [⚙️ Method `show_message (classmethod)`](#%EF%B8%8F-method-show_message-classmethod)
- [🏛️ Class `FluentMessageButton`](#%EF%B8%8F-class-fluentmessagebutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
- [🏛️ Class `FluentNotificationCenter`](#%EF%B8%8F-class-fluentnotificationcenter)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-5)
  - [⚙️ Method `add`](#%EF%B8%8F-method-add)
  - [⚙️ Method `clear`](#%EF%B8%8F-method-clear)
  - [⚙️ Method `count`](#%EF%B8%8F-method-count)
- [🏛️ Class `FluentSnackbar`](#%EF%B8%8F-class-fluentsnackbar)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-6)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-3)
  - [⚙️ Method `show_snackbar`](#%EF%B8%8F-method-show_snackbar)
- [🏛️ Class `FluentSpotlight`](#%EF%B8%8F-class-fluentspotlight)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-7)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter-2)
  - [⚙️ Method `finish`](#%EF%B8%8F-method-finish)
  - [⚙️ Method `next_step`](#%EF%B8%8F-method-next_step)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-4)
  - [⚙️ Method `start`](#%EF%B8%8F-method-start)
- [🏛️ Class `FluentTeachingTip`](#%EF%B8%8F-class-fluentteachingtip)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-8)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-5)
  - [⚙️ Method `show_tip`](#%EF%B8%8F-method-show_tip)
- [🏛️ Class `FluentToast`](#%EF%B8%8F-class-fluenttoast)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-9)
  - [⚙️ Method `show_toast`](#%EF%B8%8F-method-show_toast)
- [🏛️ Class `FluentToolTip`](#%EF%B8%8F-class-fluenttooltip)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-10)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-6)
  - [⚙️ Method `show_text`](#%EF%B8%8F-method-show_text)
- [🏛️ Class `Notification`](#%EF%B8%8F-class-notification)
- [🏛️ Class `SpotlightStep`](#%EF%B8%8F-class-spotlightstep)
- [🔧 Function `fade_in`](#-function-fade_in)
- [🔧 Function `install_fluent_tooltip`](#-function-install_fluent_tooltip)

</details>

## 🏛️ Class `FluentFloatButton`

```python
class FluentFloatButton(QWidget)
```

Round accent action button floating at a corner of its parent.

<details>
<summary>Code:</summary>

```python
class FluentFloatButton(QWidget):

    clicked = Signal()

    def __init__(
        self, icon: str, parent: QWidget, *, tooltip: str = "", corner: Qt.Corner = Qt.Corner.BottomRightCorner
    ) -> None:
        """Create a floating action button."""
        super().__init__(parent)
        self._icon = icon
        self._corner = corner
        self._hover = False
        self._pressed = False
        self.setFixedSize(48, 48)
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.setGraphicsEffect(shadow)
        parent.installEventFilter(self)
        self._place()
        bind_theme(self, self.update)

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Show the hover color."""
        self._hover = True
        self.update()
        super().enterEvent(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Stay in the corner when the parent resizes."""
        if watched is self.parentWidget() and event.type() == QEvent.Type.Resize:
            self._place()
        return False

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        """Drop the hover color."""
        self._hover = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Show the pressed color."""
        self._pressed = event.button() == Qt.MouseButton.LeftButton
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Emit `clicked`."""
        if self._pressed and self.rect().contains(event.position().toPoint()):
            self.clicked.emit()
        self._pressed = False
        self.update()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the round accent button and icon."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        fill = palette.accent_pressed if self._pressed else palette.accent_hover if self._hover else palette.accent
        paint_surface(painter, self.rect(), fill, None, self.width() / 2)
        icon = create_lucide_icon(self._icon, 20, color=palette.text_on_accent)
        icon.paint(painter, (self.width() - 20) // 2, (self.height() - 20) // 2, 20, 20)
        painter.end()

    def _place(self) -> None:
        parent = self.parentWidget()
        if parent is None:
            return
        margin = SPACE_XL
        right = parent.width() - self.width() - margin
        bottom = parent.height() - self.height() - margin
        positions = {
            Qt.Corner.TopLeftCorner: QPoint(margin, margin),
            Qt.Corner.TopRightCorner: QPoint(right, margin),
            Qt.Corner.BottomLeftCorner: QPoint(margin, bottom),
            Qt.Corner.BottomRightCorner: QPoint(right, bottom),
        }
        self.move(positions[self._corner])
        self.raise_()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, icon: str, parent: QWidget, *, tooltip: str = '', corner: Qt.Corner = Qt.Corner.BottomRightCorner) -> None
```

Create a floating action button.

<details>
<summary>Code:</summary>

```python
def __init__(
        self, icon: str, parent: QWidget, *, tooltip: str = "", corner: Qt.Corner = Qt.Corner.BottomRightCorner
    ) -> None:
        super().__init__(parent)
        self._icon = icon
        self._corner = corner
        self._hover = False
        self._pressed = False
        self.setFixedSize(48, 48)
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.setGraphicsEffect(shadow)
        parent.installEventFilter(self)
        self._place()
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `enterEvent`

```python
def enterEvent(self, event: QEnterEvent) -> None
```

Show the hover color.

<details>
<summary>Code:</summary>

```python
def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        self._hover = True
        self.update()
        super().enterEvent(event)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Stay in the corner when the parent resizes.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self.parentWidget() and event.type() == QEvent.Type.Resize:
            self._place()
        return False
```

</details>

### ⚙️ Method `leaveEvent`

```python
def leaveEvent(self, event: QEvent) -> None
```

Drop the hover color.

<details>
<summary>Code:</summary>

```python
def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        self._hover = False
        self.update()
        super().leaveEvent(event)
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Show the pressed color.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._pressed = event.button() == Qt.MouseButton.LeftButton
        self.update()
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Emit `clicked`.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._pressed and self.rect().contains(event.position().toPoint()):
            self.clicked.emit()
        self._pressed = False
        self.update()
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the round accent button and icon.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        fill = palette.accent_pressed if self._pressed else palette.accent_hover if self._hover else palette.accent
        paint_surface(painter, self.rect(), fill, None, self.width() / 2)
        icon = create_lucide_icon(self._icon, 20, color=palette.text_on_accent)
        icon.paint(painter, (self.width() - 20) // 2, (self.height() - 20) // 2, 20, 20)
        painter.end()
```

</details>

## 🏛️ Class `FluentFlyout`

```python
class FluentFlyout(QFrame)
```

Light-dismiss popup with arbitrary content anchored to a widget.

<details>
<summary>Code:</summary>

```python
class FluentFlyout(QFrame):

    def __init__(self, anchor: QWidget, content: QWidget | None = None) -> None:
        """Create a flyout for `anchor`; add widgets to `content_layout`."""
        flags = Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        super().__init__(anchor, flags)
        self._anchor = anchor
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(SPACE_L, SPACE_L, SPACE_L, SPACE_L)
        self.content_layout.setSpacing(SPACE_S)
        if content is not None:
            self.content_layout.addWidget(content)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the popup surface."""
        palette = palette_for(self._anchor)
        painter = antialiased_painter(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        paint_surface(painter, self.rect(), fill, palette.popup_stroke, RADIUS_OVERLAY)
        painter.end()

    def popup(self) -> None:
        """Show below the anchor (above when there is no room)."""
        self.adjustSize()
        origin = self._anchor.mapToGlobal(QPoint(0, self._anchor.height() + SPACE_XS))
        screen = QApplication.screenAt(origin) or QApplication.primaryScreen()
        if screen is not None and origin.y() + self.height() > screen.availableGeometry().bottom():
            origin = self._anchor.mapToGlobal(QPoint(0, -self.height() - SPACE_XS))
        self.move(origin)
        self.show()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, anchor: QWidget, content: QWidget | None = None) -> None
```

Create a flyout for `anchor`; add widgets to `content_layout`.

<details>
<summary>Code:</summary>

```python
def __init__(self, anchor: QWidget, content: QWidget | None = None) -> None:
        flags = Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        super().__init__(anchor, flags)
        self._anchor = anchor
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(SPACE_L, SPACE_L, SPACE_L, SPACE_L)
        self.content_layout.setSpacing(SPACE_S)
        if content is not None:
            self.content_layout.addWidget(content)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the popup surface.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self._anchor)
        painter = antialiased_painter(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        paint_surface(painter, self.rect(), fill, palette.popup_stroke, RADIUS_OVERLAY)
        painter.end()
```

</details>

### ⚙️ Method `popup`

```python
def popup(self) -> None
```

Show below the anchor (above when there is no room).

<details>
<summary>Code:</summary>

```python
def popup(self) -> None:
        self.adjustSize()
        origin = self._anchor.mapToGlobal(QPoint(0, self._anchor.height() + SPACE_XS))
        screen = QApplication.screenAt(origin) or QApplication.primaryScreen()
        if screen is not None and origin.y() + self.height() > screen.availableGeometry().bottom():
            origin = self._anchor.mapToGlobal(QPoint(0, -self.height() - SPACE_XS))
        self.move(origin)
        self.show()
```

</details>

## 🏛️ Class `FluentInfoBar`

```python
class FluentInfoBar(QWidget)
```

Inline status strip: severity icon, bold title, message, optional action, and close.

<details>
<summary>Code:</summary>

```python
class FluentInfoBar(QWidget):

    closed = Signal()

    def __init__(
        self,
        title: str,
        message: str = "",
        parent: QWidget | None = None,
        *,
        severity: Severity = Severity.ACCENT,
        closable: bool = True,
        action_text: str = "",
        on_action: Callable[[], None] | None = None,
    ) -> None:
        """Create an info bar."""
        super().__init__(parent)
        self._severity = severity
        row = QHBoxLayout(self)
        row.setContentsMargins(SPACE_L, SPACE_S, SPACE_XS, SPACE_S)
        row.setSpacing(SPACE_M)
        self._icon = _SeverityIcon(severity, self)
        row.addWidget(self._icon, 0, Qt.AlignmentFlag.AlignTop)
        text = QVBoxLayout() if len(message) > 60 else QHBoxLayout()  # noqa: PLR2004
        text.setSpacing(SPACE_XS if isinstance(text, QVBoxLayout) else SPACE_M)
        self.title_label = FluentText(title, self, style=TextStyle.BODY_STRONG)
        self.message_label = FluentText(message, self, word_wrap=True)
        self.message_label.setVisible(bool(message))
        text.addWidget(self.title_label)
        text.addWidget(self.message_label, 1)
        row.addLayout(text, 1)
        if action_text:
            action = FluentPushButton(action_text, self)
            if on_action is not None:
                action.clicked.connect(on_action)
            row.addWidget(action, 0, Qt.AlignmentFlag.AlignTop)
        if closable:
            close = FluentIconButton("x", self, tooltip="Close")
            close.clicked.connect(self.close_bar)
            row.addWidget(close, 0, Qt.AlignmentFlag.AlignTop)
        self.setMinimumHeight(CONTROL_HEIGHT + 2 * SPACE_S)
        bind_theme(self, self.update)

    def close_bar(self) -> None:
        """Hide the bar and emit `closed`."""
        self.hide()
        self.closed.emit()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the tinted surface."""
        palette = palette_for(self)
        _foreground, background = severity_colors(palette, self._severity)
        if self._severity == Severity.ACCENT:
            background = palette.card_bg if palette.dark else QColor(palette.solid_quarternary_bg)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), background, palette.card_stroke, RADIUS_CONTROL)
        painter.end()

    def severity(self) -> Severity:
        """Return the bar severity."""
        return self._severity
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, message: str = '', parent: QWidget | None = None, *, severity: Severity = Severity.ACCENT, closable: bool = True, action_text: str = '', on_action: Callable[[], None] | None = None) -> None
```

Create an info bar.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        message: str = "",
        parent: QWidget | None = None,
        *,
        severity: Severity = Severity.ACCENT,
        closable: bool = True,
        action_text: str = "",
        on_action: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self._severity = severity
        row = QHBoxLayout(self)
        row.setContentsMargins(SPACE_L, SPACE_S, SPACE_XS, SPACE_S)
        row.setSpacing(SPACE_M)
        self._icon = _SeverityIcon(severity, self)
        row.addWidget(self._icon, 0, Qt.AlignmentFlag.AlignTop)
        text = QVBoxLayout() if len(message) > 60 else QHBoxLayout()  # noqa: PLR2004
        text.setSpacing(SPACE_XS if isinstance(text, QVBoxLayout) else SPACE_M)
        self.title_label = FluentText(title, self, style=TextStyle.BODY_STRONG)
        self.message_label = FluentText(message, self, word_wrap=True)
        self.message_label.setVisible(bool(message))
        text.addWidget(self.title_label)
        text.addWidget(self.message_label, 1)
        row.addLayout(text, 1)
        if action_text:
            action = FluentPushButton(action_text, self)
            if on_action is not None:
                action.clicked.connect(on_action)
            row.addWidget(action, 0, Qt.AlignmentFlag.AlignTop)
        if closable:
            close = FluentIconButton("x", self, tooltip="Close")
            close.clicked.connect(self.close_bar)
            row.addWidget(close, 0, Qt.AlignmentFlag.AlignTop)
        self.setMinimumHeight(CONTROL_HEIGHT + 2 * SPACE_S)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `close_bar`

```python
def close_bar(self) -> None
```

Hide the bar and emit `closed`.

<details>
<summary>Code:</summary>

```python
def close_bar(self) -> None:
        self.hide()
        self.closed.emit()
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the tinted surface.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        _foreground, background = severity_colors(palette, self._severity)
        if self._severity == Severity.ACCENT:
            background = palette.card_bg if palette.dark else QColor(palette.solid_quarternary_bg)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), background, palette.card_stroke, RADIUS_CONTROL)
        painter.end()
```

</details>

### ⚙️ Method `severity`

```python
def severity(self) -> Severity
```

Return the bar severity.

<details>
<summary>Code:</summary>

```python
def severity(self) -> Severity:
        return self._severity
```

</details>

## 🏛️ Class `FluentMessageBar`

```python
class FluentMessageBar(FluentInfoBar)
```

Floating info bar placed at one of eight positions of a window; auto-closes.

<details>
<summary>Code:</summary>

```python
class FluentMessageBar(FluentInfoBar):

    _stacks: dict[tuple[int, MessagePosition], list[FluentMessageBar]] = {}  # noqa: RUF012

    def __init__(
        self,
        title: str,
        message: str,
        host: QWidget,
        *,
        severity: Severity = Severity.ACCENT,
        position: MessagePosition = MessagePosition.TOP_RIGHT,
        duration_ms: int = _DEFAULT_DURATION_MS,
    ) -> None:
        """Create a floating message bar over `host`'s window (call `show_bar()`)."""
        window = host.window()
        super().__init__(title, message, window, severity=severity)
        self._window = window
        self._position = position
        self.setFixedWidth(min(_BAR_WIDTH, max(200, window.width() - 2 * SPACE_XL)))
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.close_bar)
        if duration_ms > 0:
            self._timer.setInterval(duration_ms)
        self.closed.connect(self._remove_from_stack)
        window.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Re-place the bar stack when the window resizes."""
        if watched is self._window and event.type() == QEvent.Type.Resize:
            self._relayout_stack()
        return False

    def show_bar(self) -> None:
        """Show the bar, stacking it with other bars at the same position."""
        self.adjustSize()
        stack = self._stacks.setdefault((id(self._window), self._position), [])
        stack.append(self)
        self.show()
        self.raise_()
        self._relayout_stack()
        if self._timer.interval() > 0:
            self._timer.start()

    @classmethod
    def show_message(
        cls,
        host: QWidget,
        title: str,
        message: str = "",
        *,
        severity: Severity = Severity.ACCENT,
        position: MessagePosition = MessagePosition.TOP_RIGHT,
        duration_ms: int = _DEFAULT_DURATION_MS,
    ) -> FluentMessageBar:
        """Create, show, and return a message bar."""
        bar = cls(title, message, host, severity=severity, position=position, duration_ms=duration_ms)
        bar.show_bar()
        return bar

    def _relayout_stack(self) -> None:
        stack = self._stacks.get((id(self._window), self._position), [])
        offset = SPACE_XL
        for bar in stack:
            bar.move(bar._target_point(offset))  # noqa: SLF001
            offset += bar.height() + SPACE_S

    def _remove_from_stack(self) -> None:
        stack = self._stacks.get((id(self._window), self._position), [])
        if self in stack:
            stack.remove(self)
        self._relayout_stack()
        self.deleteLater()

    def _target_point(self, offset: int) -> QPoint:
        area = self._window.rect()
        width, height = self.width(), self.height()
        margin = SPACE_XL
        center_x = (area.width() - width) // 2
        center_y = (area.height() - height) // 2
        top = offset + 32
        bottom = area.height() - offset - height
        points = {
            MessagePosition.TOP: QPoint(center_x, top),
            MessagePosition.BOTTOM: QPoint(center_x, bottom),
            MessagePosition.LEFT: QPoint(margin, center_y + offset - SPACE_XL),
            MessagePosition.RIGHT: QPoint(area.width() - width - margin, center_y + offset - SPACE_XL),
            MessagePosition.TOP_LEFT: QPoint(margin, top),
            MessagePosition.TOP_RIGHT: QPoint(area.width() - width - margin, top),
            MessagePosition.BOTTOM_LEFT: QPoint(margin, bottom),
            MessagePosition.BOTTOM_RIGHT: QPoint(area.width() - width - margin, bottom),
        }
        return points[self._position]
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, message: str, host: QWidget, *, severity: Severity = Severity.ACCENT, position: MessagePosition = MessagePosition.TOP_RIGHT, duration_ms: int = _DEFAULT_DURATION_MS) -> None
```

Create a floating message bar over `host`'s window (call `show_bar()`).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        message: str,
        host: QWidget,
        *,
        severity: Severity = Severity.ACCENT,
        position: MessagePosition = MessagePosition.TOP_RIGHT,
        duration_ms: int = _DEFAULT_DURATION_MS,
    ) -> None:
        window = host.window()
        super().__init__(title, message, window, severity=severity)
        self._window = window
        self._position = position
        self.setFixedWidth(min(_BAR_WIDTH, max(200, window.width() - 2 * SPACE_XL)))
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.close_bar)
        if duration_ms > 0:
            self._timer.setInterval(duration_ms)
        self.closed.connect(self._remove_from_stack)
        window.installEventFilter(self)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Re-place the bar stack when the window resizes.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._window and event.type() == QEvent.Type.Resize:
            self._relayout_stack()
        return False
```

</details>

### ⚙️ Method `show_bar`

```python
def show_bar(self) -> None
```

Show the bar, stacking it with other bars at the same position.

<details>
<summary>Code:</summary>

```python
def show_bar(self) -> None:
        self.adjustSize()
        stack = self._stacks.setdefault((id(self._window), self._position), [])
        stack.append(self)
        self.show()
        self.raise_()
        self._relayout_stack()
        if self._timer.interval() > 0:
            self._timer.start()
```

</details>

### ⚙️ Method `show_message (classmethod)`

```python
def show_message(cls, host: QWidget, title: str, message: str = '', *, severity: Severity = Severity.ACCENT, position: MessagePosition = MessagePosition.TOP_RIGHT, duration_ms: int = _DEFAULT_DURATION_MS) -> FluentMessageBar
```

Create, show, and return a message bar.

<details>
<summary>Code:</summary>

```python
def show_message(
        cls,
        host: QWidget,
        title: str,
        message: str = "",
        *,
        severity: Severity = Severity.ACCENT,
        position: MessagePosition = MessagePosition.TOP_RIGHT,
        duration_ms: int = _DEFAULT_DURATION_MS,
    ) -> FluentMessageBar:
        bar = cls(title, message, host, severity=severity, position=position, duration_ms=duration_ms)
        bar.show_bar()
        return bar
```

</details>

## 🏛️ Class `FluentMessageButton`

```python
class FluentMessageButton(FluentPushButton)
```

Button that shows a floating message bar when clicked (handy for demos and hints).

<details>
<summary>Code:</summary>

```python
class FluentMessageButton(FluentPushButton):

    def __init__(
        self,
        text: str,
        parent: QWidget | None = None,
        *,
        title: str = "",
        message: str = "",
        severity: Severity = Severity.ACCENT,
        position: MessagePosition = MessagePosition.TOP_RIGHT,
    ) -> None:
        """Create a message button."""
        super().__init__(text, parent)
        self._title = title or text
        self._message = message
        self._severity = severity
        self._position = position
        self.clicked.connect(self._show)

    def _show(self) -> None:
        FluentMessageBar.show_message(
            self, self._title, self._message, severity=self._severity, position=self._position
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str, parent: QWidget | None = None, *, title: str = '', message: str = '', severity: Severity = Severity.ACCENT, position: MessagePosition = MessagePosition.TOP_RIGHT) -> None
```

Create a message button.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        text: str,
        parent: QWidget | None = None,
        *,
        title: str = "",
        message: str = "",
        severity: Severity = Severity.ACCENT,
        position: MessagePosition = MessagePosition.TOP_RIGHT,
    ) -> None:
        super().__init__(text, parent)
        self._title = title or text
        self._message = message
        self._severity = severity
        self._position = position
        self.clicked.connect(self._show)
```

</details>

## 🏛️ Class `FluentNotificationCenter`

```python
class FluentNotificationCenter(QWidget)
```

Side panel listing notifications as info bars, with "Clear all".

<details>
<summary>Code:</summary>

```python
class FluentNotificationCenter(QWidget):

    count_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create an empty notification center."""
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_L, SPACE_L, SPACE_L, SPACE_L)
        layout.setSpacing(SPACE_S)
        header = QHBoxLayout()
        header.addWidget(FluentText("Notifications", self, style=TextStyle.SUBTITLE), 1)
        clear = FluentPushButton("Clear all", self)
        clear.clicked.connect(self.clear)
        header.addWidget(clear)
        layout.addLayout(header)
        self._scroll = FluentScrollArea(self)
        self._content = QWidget(self._scroll)
        self._list = QVBoxLayout(self._content)
        self._list.setContentsMargins(0, 0, 0, 0)
        self._list.setSpacing(SPACE_S)
        self._list.addStretch(1)
        self._scroll.setWidget(self._content)
        layout.addWidget(self._scroll, 1)
        self._empty = FluentText("No new notifications", self, role=TextRole.SECONDARY)
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._empty)
        self.setMinimumWidth(_BAR_WIDTH)
        self._bars: list[FluentInfoBar] = []

    def add(self, notification: Notification) -> None:
        """Append a notification at the top."""
        message = f"{notification.message}\n{notification.when}".strip() if notification.when else notification.message
        bar = FluentInfoBar(notification.title, message, self._content, severity=notification.severity)
        bar.closed.connect(lambda target=bar: self._remove(target))
        self._list.insertWidget(0, bar)
        self._bars.append(bar)
        self._sync()

    def clear(self) -> None:
        """Remove every notification."""
        for bar in list(self._bars):
            self._remove(bar)

    def count(self) -> int:
        """Return the number of notifications."""
        return len(self._bars)

    def _remove(self, bar: FluentInfoBar) -> None:
        if bar in self._bars:
            self._bars.remove(bar)
            bar.deleteLater()
        self._sync()

    def _sync(self) -> None:
        self._empty.setVisible(not self._bars)
        self.count_changed.emit(len(self._bars))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create an empty notification center.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_L, SPACE_L, SPACE_L, SPACE_L)
        layout.setSpacing(SPACE_S)
        header = QHBoxLayout()
        header.addWidget(FluentText("Notifications", self, style=TextStyle.SUBTITLE), 1)
        clear = FluentPushButton("Clear all", self)
        clear.clicked.connect(self.clear)
        header.addWidget(clear)
        layout.addLayout(header)
        self._scroll = FluentScrollArea(self)
        self._content = QWidget(self._scroll)
        self._list = QVBoxLayout(self._content)
        self._list.setContentsMargins(0, 0, 0, 0)
        self._list.setSpacing(SPACE_S)
        self._list.addStretch(1)
        self._scroll.setWidget(self._content)
        layout.addWidget(self._scroll, 1)
        self._empty = FluentText("No new notifications", self, role=TextRole.SECONDARY)
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._empty)
        self.setMinimumWidth(_BAR_WIDTH)
        self._bars: list[FluentInfoBar] = []
```

</details>

### ⚙️ Method `add`

```python
def add(self, notification: Notification) -> None
```

Append a notification at the top.

<details>
<summary>Code:</summary>

```python
def add(self, notification: Notification) -> None:
        message = f"{notification.message}\n{notification.when}".strip() if notification.when else notification.message
        bar = FluentInfoBar(notification.title, message, self._content, severity=notification.severity)
        bar.closed.connect(lambda target=bar: self._remove(target))
        self._list.insertWidget(0, bar)
        self._bars.append(bar)
        self._sync()
```

</details>

### ⚙️ Method `clear`

```python
def clear(self) -> None
```

Remove every notification.

<details>
<summary>Code:</summary>

```python
def clear(self) -> None:
        for bar in list(self._bars):
            self._remove(bar)
```

</details>

### ⚙️ Method `count`

```python
def count(self) -> int
```

Return the number of notifications.

<details>
<summary>Code:</summary>

```python
def count(self) -> int:
        return len(self._bars)
```

</details>

## 🏛️ Class `FluentSnackbar`

```python
class FluentSnackbar(QWidget)
```

Dark pill at the bottom center of a window with text and an optional action.

<details>
<summary>Code:</summary>

```python
class FluentSnackbar(QWidget):

    action_triggered = Signal()

    def __init__(
        self, text: str, host: QWidget, *, action_text: str = "", duration_ms: int = _DEFAULT_DURATION_MS
    ) -> None:
        """Create a snackbar over `host`'s window (call `show_snackbar()`)."""
        window = host.window()
        super().__init__(window)
        self._window = window
        row = QHBoxLayout(self)
        row.setContentsMargins(SPACE_L, SPACE_S, SPACE_S, SPACE_S)
        row.setSpacing(SPACE_M)
        self._label = FluentText(text, self)
        row.addWidget(self._label, 1)
        if action_text:
            action = FluentPrimaryButton(action_text, self)
            action.clicked.connect(self._on_action)
            row.addWidget(action)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(max(1, duration_ms))
        self._timer.timeout.connect(self.hide)
        bind_theme(self, self._recolor)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the inverted pill."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        fill = QColor("#f3f3f3") if palette.dark else QColor("#2b2b2b")
        paint_surface(painter, self.rect(), fill, None, RADIUS_CARD)
        painter.end()

    def show_snackbar(self) -> None:
        """Show at the bottom center of the window."""
        self.adjustSize()
        self.setFixedWidth(max(self.sizeHint().width(), 280))
        self.move((self._window.width() - self.width()) // 2, self._window.height() - self.height() - SPACE_XL)
        self.show()
        self.raise_()
        self._timer.start()

    def _on_action(self) -> None:
        self.hide()
        self.action_triggered.emit()

    def _recolor(self) -> None:
        dark = palette_for(self).dark
        color = "#1a1a1a" if dark else "#ffffff"
        self._label.setStyleSheet(f"QLabel {{ color: {color}; background: transparent; }}")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str, host: QWidget, *, action_text: str = '', duration_ms: int = _DEFAULT_DURATION_MS) -> None
```

Create a snackbar over `host`'s window (call `show_snackbar()`).

<details>
<summary>Code:</summary>

```python
def __init__(
        self, text: str, host: QWidget, *, action_text: str = "", duration_ms: int = _DEFAULT_DURATION_MS
    ) -> None:
        window = host.window()
        super().__init__(window)
        self._window = window
        row = QHBoxLayout(self)
        row.setContentsMargins(SPACE_L, SPACE_S, SPACE_S, SPACE_S)
        row.setSpacing(SPACE_M)
        self._label = FluentText(text, self)
        row.addWidget(self._label, 1)
        if action_text:
            action = FluentPrimaryButton(action_text, self)
            action.clicked.connect(self._on_action)
            row.addWidget(action)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(max(1, duration_ms))
        self._timer.timeout.connect(self.hide)
        bind_theme(self, self._recolor)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the inverted pill.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        fill = QColor("#f3f3f3") if palette.dark else QColor("#2b2b2b")
        paint_surface(painter, self.rect(), fill, None, RADIUS_CARD)
        painter.end()
```

</details>

### ⚙️ Method `show_snackbar`

```python
def show_snackbar(self) -> None
```

Show at the bottom center of the window.

<details>
<summary>Code:</summary>

```python
def show_snackbar(self) -> None:
        self.adjustSize()
        self.setFixedWidth(max(self.sizeHint().width(), 280))
        self.move((self._window.width() - self.width()) // 2, self._window.height() - self.height() - SPACE_XL)
        self.show()
        self.raise_()
        self._timer.start()
```

</details>

## 🏛️ Class `FluentSpotlight`

```python
class FluentSpotlight(QWidget)
```

Guided tour: dims the window except a rounded hole around each target.

<details>
<summary>Code:</summary>

```python
class FluentSpotlight(QWidget):

    finished = Signal()

    def __init__(self, host: QWidget, steps: list[SpotlightStep]) -> None:
        """Create a spotlight tour over `host`'s window (call `start()`)."""
        window = host.window()
        super().__init__(window)
        self._window = window
        self._steps = steps
        self._index = 0
        self._card = QFrame(self)
        self._card.setObjectName("FluentSpotlightCard")
        layout = QVBoxLayout(self._card)
        layout.setContentsMargins(SPACE_L, SPACE_L, SPACE_L, SPACE_L)
        self._title = FluentText("", self._card, style=TextStyle.BODY_STRONG)
        self._text = FluentText("", self._card, role=TextRole.SECONDARY, word_wrap=True)
        layout.addWidget(self._title)
        layout.addWidget(self._text)
        row = QHBoxLayout()
        self._counter = FluentText("", self._card, role=TextRole.TERTIARY)
        row.addWidget(self._counter, 1)
        skip = FluentPushButton("Skip", self._card)
        skip.clicked.connect(self.finish)
        self._next = FluentPrimaryButton("Next", self._card)
        self._next.clicked.connect(self.next_step)
        row.addWidget(skip)
        row.addWidget(self._next)
        layout.addLayout(row)
        self._card.setFixedWidth(300)
        window.installEventFilter(self)
        bind_theme(self, self._recolor)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Follow window resizes."""
        if watched is self._window and event.type() == QEvent.Type.Resize:
            self._sync()
        return False

    def finish(self) -> None:
        """End the tour."""
        self._window.removeEventFilter(self)
        self.hide()
        self.deleteLater()
        self.finished.emit()

    def next_step(self) -> None:
        """Go to the next step or finish."""
        if self._index >= len(self._steps) - 1:
            self.finish()
            return
        self._index += 1
        self._sync()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the smoke with a hole around the target."""
        painter = antialiased_painter(self)
        path = QPainterPath()
        path.addRect(QRectF(self.rect()))
        hole = QPainterPath()
        hole.addRoundedRect(QRectF(self._target_rect()), RADIUS_CARD, RADIUS_CARD)
        painter.fillPath(path.subtracted(hole), QColor(0, 0, 0, 120))
        painter.setPen(palette_for(self).accent)
        painter.drawRoundedRect(QRectF(self._target_rect()), RADIUS_CARD, RADIUS_CARD)
        painter.end()

    def start(self) -> None:
        """Show the first step."""
        if not self._steps:
            self.finished.emit()
            return
        self._index = 0
        self.show()
        self.raise_()
        self._sync()

    def _recolor(self) -> None:
        palette = palette_for(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        self._card.setStyleSheet(
            f"QFrame#FluentSpotlightCard {{ background: {css(fill)}; border: 1px solid {css(palette.popup_stroke)};"
            f" border-radius: {RADIUS_OVERLAY}px; }}",
        )

    def _sync(self) -> None:
        self.setGeometry(self._window.rect())
        step = self._steps[self._index]
        self._title.setText(step.title)
        self._text.setText(step.text)
        self._text.setVisible(bool(step.text))
        self._counter.setText(f"{self._index + 1} / {len(self._steps)}")
        self._next.setText("Done" if self._index == len(self._steps) - 1 else "Next")
        self._card.adjustSize()
        rect = self._target_rect()
        x = max(SPACE_L, min(rect.left(), self.width() - self._card.width() - SPACE_L))
        y = rect.bottom() + SPACE_M
        if y + self._card.height() > self.height() - SPACE_L:
            y = rect.top() - self._card.height() - SPACE_M
        self._card.move(x, max(SPACE_L, y))
        self.update()

    def _target_rect(self) -> QRect:
        if not self._steps:
            return QRect()
        target = self._steps[self._index].target
        top_left = target.mapTo(self._window, QPoint(0, 0))
        return QRect(top_left, target.size()).adjusted(-SPACE_XS, -SPACE_XS, SPACE_XS, SPACE_XS)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, host: QWidget, steps: list[SpotlightStep]) -> None
```

Create a spotlight tour over `host`'s window (call `start()`).

<details>
<summary>Code:</summary>

```python
def __init__(self, host: QWidget, steps: list[SpotlightStep]) -> None:
        window = host.window()
        super().__init__(window)
        self._window = window
        self._steps = steps
        self._index = 0
        self._card = QFrame(self)
        self._card.setObjectName("FluentSpotlightCard")
        layout = QVBoxLayout(self._card)
        layout.setContentsMargins(SPACE_L, SPACE_L, SPACE_L, SPACE_L)
        self._title = FluentText("", self._card, style=TextStyle.BODY_STRONG)
        self._text = FluentText("", self._card, role=TextRole.SECONDARY, word_wrap=True)
        layout.addWidget(self._title)
        layout.addWidget(self._text)
        row = QHBoxLayout()
        self._counter = FluentText("", self._card, role=TextRole.TERTIARY)
        row.addWidget(self._counter, 1)
        skip = FluentPushButton("Skip", self._card)
        skip.clicked.connect(self.finish)
        self._next = FluentPrimaryButton("Next", self._card)
        self._next.clicked.connect(self.next_step)
        row.addWidget(skip)
        row.addWidget(self._next)
        layout.addLayout(row)
        self._card.setFixedWidth(300)
        window.installEventFilter(self)
        bind_theme(self, self._recolor)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Follow window resizes.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._window and event.type() == QEvent.Type.Resize:
            self._sync()
        return False
```

</details>

### ⚙️ Method `finish`

```python
def finish(self) -> None
```

End the tour.

<details>
<summary>Code:</summary>

```python
def finish(self) -> None:
        self._window.removeEventFilter(self)
        self.hide()
        self.deleteLater()
        self.finished.emit()
```

</details>

### ⚙️ Method `next_step`

```python
def next_step(self) -> None
```

Go to the next step or finish.

<details>
<summary>Code:</summary>

```python
def next_step(self) -> None:
        if self._index >= len(self._steps) - 1:
            self.finish()
            return
        self._index += 1
        self._sync()
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the smoke with a hole around the target.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        painter = antialiased_painter(self)
        path = QPainterPath()
        path.addRect(QRectF(self.rect()))
        hole = QPainterPath()
        hole.addRoundedRect(QRectF(self._target_rect()), RADIUS_CARD, RADIUS_CARD)
        painter.fillPath(path.subtracted(hole), QColor(0, 0, 0, 120))
        painter.setPen(palette_for(self).accent)
        painter.drawRoundedRect(QRectF(self._target_rect()), RADIUS_CARD, RADIUS_CARD)
        painter.end()
```

</details>

### ⚙️ Method `start`

```python
def start(self) -> None
```

Show the first step.

<details>
<summary>Code:</summary>

```python
def start(self) -> None:
        if not self._steps:
            self.finished.emit()
            return
        self._index = 0
        self.show()
        self.raise_()
        self._sync()
```

</details>

## 🏛️ Class `FluentTeachingTip`

```python
class FluentTeachingTip(QFrame)
```

Callout with a tail pointing at a target: title, text, and a close button.

<details>
<summary>Code:</summary>

```python
class FluentTeachingTip(QFrame):

    closed = Signal()

    def __init__(self, target: QWidget, title: str, text: str = "", *, action_text: str = "") -> None:
        """Create a teaching tip (call `show_tip()`)."""
        flags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        super().__init__(target.window(), flags)
        self._target = target
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_L, SPACE_L + _TIP_TAIL, SPACE_S, SPACE_L)
        header = QHBoxLayout()
        header.addWidget(FluentText(title, self, style=TextStyle.BODY_STRONG), 1)
        close = FluentIconButton("x", self, tooltip="Close")
        close.clicked.connect(self._close)
        header.addWidget(close, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)
        if text:
            label = FluentText(text, self, role=TextRole.SECONDARY, word_wrap=True)
            label.setContentsMargins(0, 0, SPACE_S, 0)
            layout.addWidget(label)
        if action_text:
            button = FluentPrimaryButton(action_text, self)
            button.clicked.connect(self._close)
            layout.addWidget(button, 0, Qt.AlignmentFlag.AlignRight)
        self.setFixedWidth(320)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the bubble with a tail on top."""
        palette = palette_for(self._target)
        painter = antialiased_painter(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        body = QRectF(self.rect()).adjusted(0.5, _TIP_TAIL + 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(body, RADIUS_OVERLAY, RADIUS_OVERLAY)
        tail_x = SPACE_XL + _TIP_TAIL
        tail = QPolygonF(
            [QPoint(tail_x - _TIP_TAIL, _TIP_TAIL + 1), QPoint(tail_x, 1), QPoint(tail_x + _TIP_TAIL, _TIP_TAIL + 1)]
        )
        tail_path = QPainterPath()
        tail_path.addPolygon(tail)
        path = path.united(tail_path)
        painter.setPen(palette.popup_stroke)
        painter.setBrush(fill)
        painter.drawPath(path)
        painter.end()

    def show_tip(self) -> None:
        """Show below the target with the tail pointing at its center."""
        self.adjustSize()
        anchor = self._target.mapToGlobal(QPoint(self._target.width() // 2, self._target.height()))
        self.move(anchor.x() - SPACE_XL - _TIP_TAIL, anchor.y() + SPACE_XS)
        self.show()

    def _close(self) -> None:
        self.close()
        self.closed.emit()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, target: QWidget, title: str, text: str = '', *, action_text: str = '') -> None
```

Create a teaching tip (call `show_tip()`).

<details>
<summary>Code:</summary>

```python
def __init__(self, target: QWidget, title: str, text: str = "", *, action_text: str = "") -> None:
        flags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        super().__init__(target.window(), flags)
        self._target = target
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_L, SPACE_L + _TIP_TAIL, SPACE_S, SPACE_L)
        header = QHBoxLayout()
        header.addWidget(FluentText(title, self, style=TextStyle.BODY_STRONG), 1)
        close = FluentIconButton("x", self, tooltip="Close")
        close.clicked.connect(self._close)
        header.addWidget(close, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)
        if text:
            label = FluentText(text, self, role=TextRole.SECONDARY, word_wrap=True)
            label.setContentsMargins(0, 0, SPACE_S, 0)
            layout.addWidget(label)
        if action_text:
            button = FluentPrimaryButton(action_text, self)
            button.clicked.connect(self._close)
            layout.addWidget(button, 0, Qt.AlignmentFlag.AlignRight)
        self.setFixedWidth(320)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the bubble with a tail on top.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self._target)
        painter = antialiased_painter(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        body = QRectF(self.rect()).adjusted(0.5, _TIP_TAIL + 0.5, -0.5, -0.5)
        path = QPainterPath()
        path.addRoundedRect(body, RADIUS_OVERLAY, RADIUS_OVERLAY)
        tail_x = SPACE_XL + _TIP_TAIL
        tail = QPolygonF(
            [QPoint(tail_x - _TIP_TAIL, _TIP_TAIL + 1), QPoint(tail_x, 1), QPoint(tail_x + _TIP_TAIL, _TIP_TAIL + 1)]
        )
        tail_path = QPainterPath()
        tail_path.addPolygon(tail)
        path = path.united(tail_path)
        painter.setPen(palette.popup_stroke)
        painter.setBrush(fill)
        painter.drawPath(path)
        painter.end()
```

</details>

### ⚙️ Method `show_tip`

```python
def show_tip(self) -> None
```

Show below the target with the tail pointing at its center.

<details>
<summary>Code:</summary>

```python
def show_tip(self) -> None:
        self.adjustSize()
        anchor = self._target.mapToGlobal(QPoint(self._target.width() // 2, self._target.height()))
        self.move(anchor.x() - SPACE_XL - _TIP_TAIL, anchor.y() + SPACE_XS)
        self.show()
```

</details>

## 🏛️ Class `FluentToast`

```python
class FluentToast(QFrame)
```

Top-level notification near the bottom-right of the screen that fades out.

<details>
<summary>Code:</summary>

```python
class FluentToast(QFrame):

    def __init__(
        self,
        title: str,
        message: str = "",
        *,
        severity: Severity = Severity.ACCENT,
        duration_ms: int = _DEFAULT_DURATION_MS,
    ) -> None:
        """Create a toast (call `show_toast()`)."""
        flags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        super().__init__(None, flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)
        self.bar = FluentInfoBar(title, message, self, severity=severity)
        self.bar.closed.connect(self.close)
        self.bar.setFixedWidth(_BAR_WIDTH)
        layout.addWidget(self.bar)
        self._duration = duration_ms
        self._opacity = QGraphicsOpacityEffect(self.bar)
        self.bar.setGraphicsEffect(self._opacity)
        self._fade = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade.setDuration(ANIMATION_SLOW)

    def show_toast(self) -> None:
        """Show at the bottom-right of the screen under the cursor and start the timer."""
        self.adjustSize()
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        if screen is not None:
            area = screen.availableGeometry()
            self.move(area.right() - self.width() - SPACE_L, area.bottom() - self.height() - SPACE_L)
        self.show()
        if self._duration > 0:
            QTimer.singleShot(self._duration, self._fade_out)

    def _fade_out(self) -> None:
        self._fade.setStartValue(1.0)
        self._fade.setEndValue(0.0)
        self._fade.finished.connect(self.close)
        self._fade.start()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, message: str = '', *, severity: Severity = Severity.ACCENT, duration_ms: int = _DEFAULT_DURATION_MS) -> None
```

Create a toast (call `show_toast()`).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        message: str = "",
        *,
        severity: Severity = Severity.ACCENT,
        duration_ms: int = _DEFAULT_DURATION_MS,
    ) -> None:
        flags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        super().__init__(None, flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_S, SPACE_S, SPACE_S, SPACE_S)
        self.bar = FluentInfoBar(title, message, self, severity=severity)
        self.bar.closed.connect(self.close)
        self.bar.setFixedWidth(_BAR_WIDTH)
        layout.addWidget(self.bar)
        self._duration = duration_ms
        self._opacity = QGraphicsOpacityEffect(self.bar)
        self.bar.setGraphicsEffect(self._opacity)
        self._fade = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade.setDuration(ANIMATION_SLOW)
```

</details>

### ⚙️ Method `show_toast`

```python
def show_toast(self) -> None
```

Show at the bottom-right of the screen under the cursor and start the timer.

<details>
<summary>Code:</summary>

```python
def show_toast(self) -> None:
        self.adjustSize()
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        if screen is not None:
            area = screen.availableGeometry()
            self.move(area.right() - self.width() - SPACE_L, area.bottom() - self.height() - SPACE_L)
        self.show()
        if self._duration > 0:
            QTimer.singleShot(self._duration, self._fade_out)
```

</details>

## 🏛️ Class `FluentToolTip`

```python
class FluentToolTip(QFrame)
```

Fluent tooltip window; use `install_fluent_tooltip(widget)` to replace native tips.

<details>
<summary>Code:</summary>

```python
class FluentToolTip(QFrame):

    def __init__(self) -> None:
        """Create the (shared) tooltip window."""
        flags = Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        super().__init__(None, flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_S + 1, SPACE_XS + 2, SPACE_S + 1, SPACE_XS + 3)
        self._label = FluentText("", self, word_wrap=True)
        self._label.setMaximumWidth(320)
        layout.addWidget(self._label)
        self._source: QWidget | None = None

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the tooltip surface."""
        palette = palette_for(self._source)
        painter = antialiased_painter(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        paint_surface(painter, self.rect(), fill, palette.popup_stroke, RADIUS_CONTROL)
        painter.end()

    def show_text(self, source: QWidget, text: str, position: QPoint) -> None:
        """Show `text` for `source` near `position` (global)."""
        self._source = source
        self._label.setText(text)
        palette = palette_for(source)
        self._label.setStyleSheet(f"QLabel {{ color: {css(palette.text_primary)}; background: transparent; }}")
        self.adjustSize()
        self.move(position + QPoint(SPACE_S, SPACE_L + SPACE_XS))
        self.show()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Create the (shared) tooltip window.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        flags = Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint
        super().__init__(None, flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, on=True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_S + 1, SPACE_XS + 2, SPACE_S + 1, SPACE_XS + 3)
        self._label = FluentText("", self, word_wrap=True)
        self._label.setMaximumWidth(320)
        layout.addWidget(self._label)
        self._source: QWidget | None = None
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the tooltip surface.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self._source)
        painter = antialiased_painter(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        paint_surface(painter, self.rect(), fill, palette.popup_stroke, RADIUS_CONTROL)
        painter.end()
```

</details>

### ⚙️ Method `show_text`

```python
def show_text(self, source: QWidget, text: str, position: QPoint) -> None
```

Show `text` for `source` near `position` (global).

<details>
<summary>Code:</summary>

```python
def show_text(self, source: QWidget, text: str, position: QPoint) -> None:
        self._source = source
        self._label.setText(text)
        palette = palette_for(source)
        self._label.setStyleSheet(f"QLabel {{ color: {css(palette.text_primary)}; background: transparent; }}")
        self.adjustSize()
        self.move(position + QPoint(SPACE_S, SPACE_L + SPACE_XS))
        self.show()
```

</details>

## 🏛️ Class `Notification`

```python
class Notification
```

One entry in [`FluentNotificationCenter`](#%EF%B8%8F-class-fluentnotificationcenter).

<details>
<summary>Code:</summary>

```python
class Notification:

    title: str
    message: str = ""
    severity: Severity = Severity.ACCENT
    when: str = ""
```

</details>

## 🏛️ Class `SpotlightStep`

```python
class SpotlightStep
```

One step of a [`FluentSpotlight`](#%EF%B8%8F-class-fluentspotlight) tour.

<details>
<summary>Code:</summary>

```python
class SpotlightStep:

    target: QWidget
    title: str
    text: str = ""
```

</details>

## 🔧 Function `fade_in`

```python
def fade_in(widget: QWidget, duration_ms: int = ANIMATION_NORMAL) -> None
```

Fade `widget` in with a temporary opacity effect.

<details>
<summary>Code:</summary>

```python
def fade_in(widget: QWidget, duration_ms: int = ANIMATION_NORMAL) -> None:
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity", widget)
    animation.setDuration(duration_ms)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    animation.finished.connect(lambda: widget.setGraphicsEffect(None))  # ty: ignore[invalid-argument-type]
    animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
```

</details>

## 🔧 Function `install_fluent_tooltip`

```python
def install_fluent_tooltip(widget: QWidget) -> None
```

Show `widget.toolTip()` in a Fluent tooltip instead of the native one.

<details>
<summary>Code:</summary>

```python
def install_fluent_tooltip(widget: QWidget) -> None:
    _ToolTipFilter(widget)
```

</details>
