---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `panels.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DrawerEdge`](#%EF%B8%8F-class-draweredge)
- [🏛️ Class `FluentDockWidget`](#%EF%B8%8F-class-fluentdockwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme)
- [🏛️ Class `FluentDrawerArea`](#%EF%B8%8F-class-fluentdrawerarea)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `close_drawer`](#%EF%B8%8F-method-close_drawer)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
  - [⚙️ Method `is_open`](#%EF%B8%8F-method-is_open)
  - [⚙️ Method `open_drawer`](#%EF%B8%8F-method-open_drawer)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `toggle`](#%EF%B8%8F-method-toggle)
- [🏛️ Class `FluentSheetPanel`](#%EF%B8%8F-class-fluentsheetpanel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `close_sheet`](#%EF%B8%8F-method-close_sheet)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter-1)
  - [⚙️ Method `open_sheet`](#%EF%B8%8F-method-open_sheet)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-1)
- [🏛️ Class `FluentSplashScreen`](#%EF%B8%8F-class-fluentsplashscreen)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `finish`](#%EF%B8%8F-method-finish)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-2)
  - [⚙️ Method `set_status`](#%EF%B8%8F-method-set_status)
  - [⚙️ Method `showEvent`](#%EF%B8%8F-method-showevent)
- [🏛️ Class `FluentWatermark`](#%EF%B8%8F-class-fluentwatermark)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter-2)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-3)
  - [⚙️ Method `set_text`](#%EF%B8%8F-method-set_text)

</details>

## 🏛️ Class `DrawerEdge`

```python
class DrawerEdge(Enum)
```

Edge of the window a drawer slides from.

<details>
<summary>Code:</summary>

```python
class DrawerEdge(Enum):

    LEFT = "left"
    RIGHT = "right"
```

</details>

## 🏛️ Class `FluentDockWidget`

```python
class FluentDockWidget(QDockWidget)
```

Dock widget with a Fluent title bar and layer surface.

<details>
<summary>Code:</summary>

```python
class FluentDockWidget(QDockWidget):

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        """Create a dock widget."""
        super().__init__(title, parent)
        bind_theme(self, self.refresh_theme)

    def refresh_theme(self) -> None:
        """Re-apply chrome."""
        palette = palette_for(self)
        close = lucide_qss_url("x", palette.text_secondary, 12)
        undock = lucide_qss_url("copy", palette.text_secondary, 12)
        self.setStyleSheet(f"""
QDockWidget {{
    color: {css(palette.text_primary)}; titlebar-close-icon: url("{close}"); titlebar-normal-icon: url("{undock}");
}}
QDockWidget::title {{
    background: {css(palette.layer_alt_bg)};
    border-bottom: 1px solid {css(palette.divider)};
    padding: 6px 8px;
    text-align: left;
}}
QDockWidget::close-button, QDockWidget::float-button {{
    border: none; background: transparent; border-radius: {RADIUS_CONTROL}px; padding: 2px;
}}
QDockWidget::close-button:hover, QDockWidget::float-button:hover {{ background: {css(palette.subtle_hover)}; }}
""")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, parent: QWidget | None = None) -> None
```

Create a dock widget.

<details>
<summary>Code:</summary>

```python
def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(title, parent)
        bind_theme(self, self.refresh_theme)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply chrome.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        palette = palette_for(self)
        close = lucide_qss_url("x", palette.text_secondary, 12)
        undock = lucide_qss_url("copy", palette.text_secondary, 12)
        self.setStyleSheet(f"""
QDockWidget {{
    color: {css(palette.text_primary)}; titlebar-close-icon: url("{close}"); titlebar-normal-icon: url("{undock}");
}}
QDockWidget::title {{
    background: {css(palette.layer_alt_bg)};
    border-bottom: 1px solid {css(palette.divider)};
    padding: 6px 8px;
    text-align: left;
}}
QDockWidget::close-button, QDockWidget::float-button {{
    border: none; background: transparent; border-radius: {RADIUS_CONTROL}px; padding: 2px;
}}
QDockWidget::close-button:hover, QDockWidget::float-button:hover {{ background: {css(palette.subtle_hover)}; }}
""")
```

</details>

## 🏛️ Class `FluentDrawerArea`

```python
class FluentDrawerArea(QWidget)
```

Side drawer that slides over a window from the left or right edge.

<details>
<summary>Code:</summary>

```python
class FluentDrawerArea(QWidget):

    opened = Signal()
    closed = Signal()

    def __init__(
        self, host: QWidget, *, edge: DrawerEdge = DrawerEdge.RIGHT, title: str = "", width: int = _DRAWER_WIDTH
    ) -> None:
        """Create a drawer over `host`'s window; add widgets to `content_layout`."""
        window = host.window()
        self._overlay = _HostOverlay(window)
        super().__init__(window)
        self._window = window
        self._edge = edge
        self._open = False
        self.setFixedWidth(width)
        self.hide()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_L, SPACE_L, SPACE_L, SPACE_L)
        layout.setSpacing(SPACE_M)
        header = QHBoxLayout()
        header.addWidget(FluentText(title, self, style=TextStyle.SUBTITLE), 1)
        close = FluentIconButton("x", self, tooltip="Close")
        close.clicked.connect(self.close_drawer)
        header.addWidget(close)
        layout.addLayout(header)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(SPACE_S)
        layout.addLayout(self.content_layout, 1)
        self._overlay.clicked_outside.connect(self.close_drawer)
        self._animation = QPropertyAnimation(self, b"pos", self)
        self._animation.setDuration(ANIMATION_SLOW)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        window.installEventFilter(self)
        bind_theme(self, self.update)

    def close_drawer(self) -> None:
        """Slide out and hide."""
        if not self._open:
            return
        self._open = False
        self._animation.stop()
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(self._hidden_pos())
        self._animation.finished.connect(self._after_close)
        self._animation.start()
        self._overlay.hide()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Keep full height and the edge position on window resize."""
        if watched is self._window and event.type() == QEvent.Type.Resize:
            self.setFixedHeight(self._window.height())
            self.move(self._shown_pos() if self._open else self._hidden_pos())
        return False

    def is_open(self) -> bool:
        """Return whether the drawer is shown."""
        return self._open

    def open_drawer(self) -> None:
        """Slide in over a smoke layer."""
        if self._open:
            return
        self._open = True
        self._overlay.setGeometry(self._window.rect())
        self._overlay.show()
        self._overlay.raise_()
        self.setFixedHeight(self._window.height())
        self.move(self._hidden_pos())
        self.show()
        self.raise_()
        self._animation.stop()
        self._animation.setStartValue(self._hidden_pos())
        self._animation.setEndValue(self._shown_pos())
        self._animation.start()
        self.opened.emit()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the drawer surface with a hairline on the inner edge."""
        palette = palette_for(self)
        painter = QPainter(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        painter.fillRect(self.rect(), fill)
        x = self.width() - 1 if self._edge == DrawerEdge.LEFT else 0
        painter.fillRect(x, 0, 1, self.height(), palette.popup_stroke)
        painter.end()

    def toggle(self) -> None:
        """Open or close."""
        if self._open:
            self.close_drawer()
        else:
            self.open_drawer()

    def _after_close(self) -> None:
        self._animation.finished.disconnect(self._after_close)
        if not self._open:
            self.hide()
            self.closed.emit()

    def _hidden_pos(self) -> QPoint:
        if self._edge == DrawerEdge.LEFT:
            return QPoint(-self.width(), 0)
        return QPoint(self._window.width(), 0)

    def _shown_pos(self) -> QPoint:
        if self._edge == DrawerEdge.LEFT:
            return QPoint(0, 0)
        return QPoint(self._window.width() - self.width(), 0)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, host: QWidget, *, edge: DrawerEdge = DrawerEdge.RIGHT, title: str = '', width: int = _DRAWER_WIDTH) -> None
```

Create a drawer over `host`'s window; add widgets to `content_layout`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self, host: QWidget, *, edge: DrawerEdge = DrawerEdge.RIGHT, title: str = "", width: int = _DRAWER_WIDTH
    ) -> None:
        window = host.window()
        self._overlay = _HostOverlay(window)
        super().__init__(window)
        self._window = window
        self._edge = edge
        self._open = False
        self.setFixedWidth(width)
        self.hide()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_L, SPACE_L, SPACE_L, SPACE_L)
        layout.setSpacing(SPACE_M)
        header = QHBoxLayout()
        header.addWidget(FluentText(title, self, style=TextStyle.SUBTITLE), 1)
        close = FluentIconButton("x", self, tooltip="Close")
        close.clicked.connect(self.close_drawer)
        header.addWidget(close)
        layout.addLayout(header)
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(SPACE_S)
        layout.addLayout(self.content_layout, 1)
        self._overlay.clicked_outside.connect(self.close_drawer)
        self._animation = QPropertyAnimation(self, b"pos", self)
        self._animation.setDuration(ANIMATION_SLOW)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        window.installEventFilter(self)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `close_drawer`

```python
def close_drawer(self) -> None
```

Slide out and hide.

<details>
<summary>Code:</summary>

```python
def close_drawer(self) -> None:
        if not self._open:
            return
        self._open = False
        self._animation.stop()
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(self._hidden_pos())
        self._animation.finished.connect(self._after_close)
        self._animation.start()
        self._overlay.hide()
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Keep full height and the edge position on window resize.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._window and event.type() == QEvent.Type.Resize:
            self.setFixedHeight(self._window.height())
            self.move(self._shown_pos() if self._open else self._hidden_pos())
        return False
```

</details>

### ⚙️ Method `is_open`

```python
def is_open(self) -> bool
```

Return whether the drawer is shown.

<details>
<summary>Code:</summary>

```python
def is_open(self) -> bool:
        return self._open
```

</details>

### ⚙️ Method `open_drawer`

```python
def open_drawer(self) -> None
```

Slide in over a smoke layer.

<details>
<summary>Code:</summary>

```python
def open_drawer(self) -> None:
        if self._open:
            return
        self._open = True
        self._overlay.setGeometry(self._window.rect())
        self._overlay.show()
        self._overlay.raise_()
        self.setFixedHeight(self._window.height())
        self.move(self._hidden_pos())
        self.show()
        self.raise_()
        self._animation.stop()
        self._animation.setStartValue(self._hidden_pos())
        self._animation.setEndValue(self._shown_pos())
        self._animation.start()
        self.opened.emit()
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the drawer surface with a hairline on the inner edge.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = QPainter(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        painter.fillRect(self.rect(), fill)
        x = self.width() - 1 if self._edge == DrawerEdge.LEFT else 0
        painter.fillRect(x, 0, 1, self.height(), palette.popup_stroke)
        painter.end()
```

</details>

### ⚙️ Method `toggle`

```python
def toggle(self) -> None
```

Open or close.

<details>
<summary>Code:</summary>

```python
def toggle(self) -> None:
        if self._open:
            self.close_drawer()
        else:
            self.open_drawer()
```

</details>

## 🏛️ Class `FluentSheetPanel`

```python
class FluentSheetPanel(QWidget)
```

Bottom sheet that slides up over a window with a grab handle.

<details>
<summary>Code:</summary>

```python
class FluentSheetPanel(QWidget):

    closed = Signal()

    def __init__(self, host: QWidget, *, height: int = _SHEET_HEIGHT) -> None:
        """Create a bottom sheet over `host`'s window; add widgets to `content_layout`."""
        window = host.window()
        self._overlay = _HostOverlay(window)
        super().__init__(window)
        self._window = window
        self._open = False
        self.setFixedHeight(height)
        self.hide()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_L)
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout, 1)
        self._overlay.clicked_outside.connect(self.close_sheet)
        self._animation = QPropertyAnimation(self, b"pos", self)
        self._animation.setDuration(ANIMATION_SLOW)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        window.installEventFilter(self)
        bind_theme(self, self.update)

    def close_sheet(self) -> None:
        """Slide down and hide."""
        if not self._open:
            return
        self._open = False
        self._overlay.hide()
        self._animation.stop()
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(QPoint(0, self._window.height()))
        self._animation.start()
        self.closed.emit()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Follow window resizes."""
        if watched is self._window and event.type() == QEvent.Type.Resize:
            self.setFixedWidth(self._window.width())
            self.move(0, self._window.height() - (self.height() if self._open else 0))
        return False

    def open_sheet(self) -> None:
        """Slide up."""
        self._open = True
        self._overlay.setGeometry(self._window.rect())
        self._overlay.show()
        self._overlay.raise_()
        self.setFixedWidth(self._window.width())
        self.show()
        self.raise_()
        self._animation.stop()
        self._animation.setStartValue(QPoint(0, self._window.height()))
        self._animation.setEndValue(QPoint(0, self._window.height() - self.height()))
        self._animation.start()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the sheet with rounded top corners and a grab handle."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        paint_surface(
            painter, self.rect().adjusted(0, 0, 0, RADIUS_OVERLAY * 2), fill, palette.popup_stroke, RADIUS_OVERLAY * 2
        )
        handle = QRect((self.width() - 36) // 2, SPACE_S, 36, 4)
        paint_surface(painter, handle, palette.control_strong_stroke, None, 2)
        painter.end()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, host: QWidget, *, height: int = _SHEET_HEIGHT) -> None
```

Create a bottom sheet over `host`'s window; add widgets to `content_layout`.

<details>
<summary>Code:</summary>

```python
def __init__(self, host: QWidget, *, height: int = _SHEET_HEIGHT) -> None:
        window = host.window()
        self._overlay = _HostOverlay(window)
        super().__init__(window)
        self._window = window
        self._open = False
        self.setFixedHeight(height)
        self.hide()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_L)
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout, 1)
        self._overlay.clicked_outside.connect(self.close_sheet)
        self._animation = QPropertyAnimation(self, b"pos", self)
        self._animation.setDuration(ANIMATION_SLOW)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        window.installEventFilter(self)
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `close_sheet`

```python
def close_sheet(self) -> None
```

Slide down and hide.

<details>
<summary>Code:</summary>

```python
def close_sheet(self) -> None:
        if not self._open:
            return
        self._open = False
        self._overlay.hide()
        self._animation.stop()
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(QPoint(0, self._window.height()))
        self._animation.start()
        self.closed.emit()
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
            self.setFixedWidth(self._window.width())
            self.move(0, self._window.height() - (self.height() if self._open else 0))
        return False
```

</details>

### ⚙️ Method `open_sheet`

```python
def open_sheet(self) -> None
```

Slide up.

<details>
<summary>Code:</summary>

```python
def open_sheet(self) -> None:
        self._open = True
        self._overlay.setGeometry(self._window.rect())
        self._overlay.show()
        self._overlay.raise_()
        self.setFixedWidth(self._window.width())
        self.show()
        self.raise_()
        self._animation.stop()
        self._animation.setStartValue(QPoint(0, self._window.height()))
        self._animation.setEndValue(QPoint(0, self._window.height() - self.height()))
        self._animation.start()
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the sheet with rounded top corners and a grab handle.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        fill = palette.solid_tertiary_bg if palette.dark else palette.solid_quarternary_bg
        paint_surface(
            painter, self.rect().adjusted(0, 0, 0, RADIUS_OVERLAY * 2), fill, palette.popup_stroke, RADIUS_OVERLAY * 2
        )
        handle = QRect((self.width() - 36) // 2, SPACE_S, 36, 4)
        paint_surface(painter, handle, palette.control_strong_stroke, None, 2)
        painter.end()
```

</details>

## 🏛️ Class `FluentSplashScreen`

```python
class FluentSplashScreen(QWidget)
```

Frameless startup window: app icon, title, status text, and a busy ring.

<details>
<summary>Code:</summary>

```python
class FluentSplashScreen(QWidget):

    def __init__(self, title: str, *, icon: QIcon | None = None, subtitle: str = "") -> None:
        """Create a splash screen (`show()` centers it on the primary screen)."""
        super().__init__(
            None, Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        enable_fluent_theme(self)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setFixedSize(*_SPLASH_SIZE)
        self._icon = icon
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XL, SPACE_XL * 2 + 48, SPACE_XL, SPACE_XL)
        layout.setSpacing(SPACE_S)
        heading = FluentText(title, self, style=TextStyle.TITLE)
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(heading)
        if subtitle:
            caption = CaptionLabel(subtitle, self)
            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(caption)
        layout.addStretch(1)
        self._status = CaptionLabel("", self)
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ring = FluentProgressRing(self, size=28)
        self.ring.set_busy(busy=True)
        layout.addWidget(self.ring, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._status)

    def finish(self, window: QWidget | None = None) -> None:
        """Close the splash (after `window` is shown, if given)."""
        self.ring.set_busy(busy=False)
        if window is not None:
            window.show()
        self.close()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the rounded surface and icon."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.window_bg, palette.popup_stroke, RADIUS_OVERLAY)
        if self._icon is not None and not self._icon.isNull():
            self._icon.paint(painter, QRect((self.width() - 48) // 2, SPACE_XL * 2 - SPACE_S, 48, 48))
        painter.end()

    def set_status(self, text: str) -> None:
        """Show a status line under the ring."""
        self._status.setText(text)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Center on the primary screen."""
        screen = self.screen()
        if screen is not None:
            self.move(screen.availableGeometry().center() - self.rect().center())
        super().showEvent(event)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, *, icon: QIcon | None = None, subtitle: str = '') -> None
```

Create a splash screen (`show()` centers it on the primary screen).

<details>
<summary>Code:</summary>

```python
def __init__(self, title: str, *, icon: QIcon | None = None, subtitle: str = "") -> None:
        super().__init__(
            None, Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        enable_fluent_theme(self)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, on=True)
        self.setFixedSize(*_SPLASH_SIZE)
        self._icon = icon
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XL, SPACE_XL * 2 + 48, SPACE_XL, SPACE_XL)
        layout.setSpacing(SPACE_S)
        heading = FluentText(title, self, style=TextStyle.TITLE)
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(heading)
        if subtitle:
            caption = CaptionLabel(subtitle, self)
            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(caption)
        layout.addStretch(1)
        self._status = CaptionLabel("", self)
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ring = FluentProgressRing(self, size=28)
        self.ring.set_busy(busy=True)
        layout.addWidget(self.ring, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._status)
```

</details>

### ⚙️ Method `finish`

```python
def finish(self, window: QWidget | None = None) -> None
```

Close the splash (after `window` is shown, if given).

<details>
<summary>Code:</summary>

```python
def finish(self, window: QWidget | None = None) -> None:
        self.ring.set_busy(busy=False)
        if window is not None:
            window.show()
        self.close()
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the rounded surface and icon.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        paint_surface(painter, self.rect(), palette.window_bg, palette.popup_stroke, RADIUS_OVERLAY)
        if self._icon is not None and not self._icon.isNull():
            self._icon.paint(painter, QRect((self.width() - 48) // 2, SPACE_XL * 2 - SPACE_S, 48, 48))
        painter.end()
```

</details>

### ⚙️ Method `set_status`

```python
def set_status(self, text: str) -> None
```

Show a status line under the ring.

<details>
<summary>Code:</summary>

```python
def set_status(self, text: str) -> None:
        self._status.setText(text)
```

</details>

### ⚙️ Method `showEvent`

```python
def showEvent(self, event: QShowEvent) -> None
```

Center on the primary screen.

<details>
<summary>Code:</summary>

```python
def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        screen = self.screen()
        if screen is not None:
            self.move(screen.availableGeometry().center() - self.rect().center())
        super().showEvent(event)
```

</details>

## 🏛️ Class `FluentWatermark`

```python
class FluentWatermark(QWidget)
```

Transparent overlay that tiles a rotated text watermark over its parent.

<details>
<summary>Code:</summary>

```python
class FluentWatermark(QWidget):

    def __init__(self, text: str, parent: QWidget, *, opacity: int = 22, gap: int = 120) -> None:
        """Create a watermark over `parent` (mouse events pass through)."""
        super().__init__(parent)
        self._text = text
        self._opacity = opacity
        self._gap = gap
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        parent.installEventFilter(self)
        self.setGeometry(parent.rect())
        self.raise_()
        bind_theme(self, self.update)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Cover the parent after it resizes."""
        if watched is self.parentWidget() and event.type() == QEvent.Type.Resize:
            parent = self.parentWidget()
            if parent is not None:
                self.setGeometry(parent.rect())
                self.raise_()
        return False

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the tiled rotated text."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        font = fluent_font(self.font(), TYPE_CAPTION * 1.2, weight=QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.setPen(with_alpha(palette.text_primary, self._opacity))
        width = painter.fontMetrics().horizontalAdvance(self._text) + self._gap
        height = self._gap
        painter.rotate(_WATERMARK_ANGLE)
        span = max(self.width(), self.height()) * 2
        for y in range(-span, span, height):
            for x in range(-span, span, width):
                painter.drawText(x, y, self._text)
        painter.end()

    def set_text(self, text: str) -> None:
        """Change the watermark text."""
        self._text = text
        self.update()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str, parent: QWidget, *, opacity: int = 22, gap: int = 120) -> None
```

Create a watermark over `parent` (mouse events pass through).

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str, parent: QWidget, *, opacity: int = 22, gap: int = 120) -> None:
        super().__init__(parent)
        self._text = text
        self._opacity = opacity
        self._gap = gap
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=True)
        parent.installEventFilter(self)
        self.setGeometry(parent.rect())
        self.raise_()
        bind_theme(self, self.update)
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Cover the parent after it resizes.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self.parentWidget() and event.type() == QEvent.Type.Resize:
            parent = self.parentWidget()
            if parent is not None:
                self.setGeometry(parent.rect())
                self.raise_()
        return False
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the tiled rotated text.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        font = fluent_font(self.font(), TYPE_CAPTION * 1.2, weight=QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.setPen(with_alpha(palette.text_primary, self._opacity))
        width = painter.fontMetrics().horizontalAdvance(self._text) + self._gap
        height = self._gap
        painter.rotate(_WATERMARK_ANGLE)
        span = max(self.width(), self.height()) * 2
        for y in range(-span, span, height):
            for x in range(-span, span, width):
                painter.drawText(x, y, self._text)
        painter.end()
```

</details>

### ⚙️ Method `set_text`

```python
def set_text(self, text: str) -> None
```

Change the watermark text.

<details>
<summary>Code:</summary>

```python
def set_text(self, text: str) -> None:
        self._text = text
        self.update()
```

</details>
