---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `win11_caption.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `CaptionButton`](#%EF%B8%8F-class-captionbutton)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `enterEvent`](#%EF%B8%8F-method-enterevent)
  - [⚙️ Method `glyph_name`](#%EF%B8%8F-method-glyph_name)
  - [⚙️ Method `hover_background`](#%EF%B8%8F-method-hover_background)
  - [⚙️ Method `leaveEvent`](#%EF%B8%8F-method-leaveevent)
  - [⚙️ Method `mousePressEvent`](#%EF%B8%8F-method-mousepressevent)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `pressed_background`](#%EF%B8%8F-method-pressed_background)
  - [⚙️ Method `set_glyph`](#%EF%B8%8F-method-set_glyph)
  - [⚙️ Method `set_light`](#%EF%B8%8F-method-set_light)
  - [⚙️ Method `set_window_active`](#%EF%B8%8F-method-set_window_active)
- [🔧 Function `caption_glyph_icon`](#-function-caption_glyph_icon)
- [🔧 Function `caption_hit_test`](#-function-caption_hit_test)
- [🔧 Function `install_win11_caption`](#-function-install_win11_caption)
- [🔧 Function `try_handle_win11_caption_native_event`](#-function-try_handle_win11_caption_native_event)
- [🔧 Function `write_nccalcsize_client_rect`](#-function-write_nccalcsize_client_rect)

</details>

## 🏛️ Class `CaptionButton`

```python
class CaptionButton(QToolButton)
```

One Windows 11 caption button painted with a Fluent glyph.

<details>
<summary>Code:</summary>

```python
class CaptionButton(QToolButton):

    def __init__(self, *, kind: str, light: bool, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        glyph, object_name, tooltip = _BUTTON_KINDS[kind]
        self._kind = kind
        self._glyph = glyph
        self._light = light
        self._window_active = True
        self.setObjectName(object_name)
        self.setToolTip(tooltip)
        self.setAccessibleName(tooltip)
        self.setFixedSize(CAPTION_BUTTON_WIDTH, CAPTION_BUTTON_HEIGHT)
        self.setAutoRaise(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        """Repaint so the Windows hover fill appears."""
        super().enterEvent(event)
        self.update()

    def glyph_name(self) -> str:
        """Return the Fluent glyph stem currently painted on this button."""
        return self._glyph

    def hover_background(self) -> QColor:
        """Return the Windows 11 hover fill for this button."""
        if self._kind == "close":
            return CLOSE_HOVER_COLOR
        if self._light:
            return MINMAX_HOVER_LIGHT
        return MINMAX_HOVER_DARK

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        """Repaint after the pointer leaves the button."""
        super().leaveEvent(event)
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Repaint the pressed fill, then let the button emit `clicked`."""
        super().mousePressEvent(event)
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Repaint once the pressed fill should clear."""
        super().mouseReleaseEvent(event)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        """Fill the button and draw a 16 px glyph centered in it."""
        painter = QPainter(self)
        if self.isDown():
            fill = self.pressed_background()
        elif self.underMouse():
            fill = self.hover_background()
        else:
            fill = self._rest_background()
        painter.fillRect(self.rect(), fill)
        icon = caption_glyph_icon(self._glyph, self._glyph_color(), self.devicePixelRatioF())
        if icon.isNull():
            painter.end()
            return
        side = CAPTION_GLYPH_SIZE
        x = (self.width() - side) // 2
        y = (self.height() - side) // 2
        icon.paint(painter, QRect(x, y, side, side))
        painter.end()

    def pressed_background(self) -> QColor:
        """Return the Windows 11 pressed fill for this button."""
        if self._kind == "close":
            return CLOSE_PRESSED_COLOR
        if self._light:
            return MINMAX_PRESSED_LIGHT
        return MINMAX_PRESSED_DARK

    def set_glyph(self, name: str) -> None:
        """Switch the centered Fluent glyph.

        Args:

        - `name` (`str`): Stem such as `maximize` or `square_multiple`.

        """
        if self._glyph == name:
            return
        self._glyph = name
        if name == "square_multiple":
            self.setToolTip("Restore")
            self.setAccessibleName("Restore")
        elif name == "maximize":
            self.setToolTip("Maximize")
            self.setAccessibleName("Maximize")
        self.update()

    def set_light(self, *, light: bool) -> None:
        """Use light or dark caption colors.

        Args:

        - `light` (`bool`): `True` when the window background is light.

        """
        if self._light == light:
            return
        self._light = light
        self.update()

    def set_window_active(self, *, active: bool) -> None:
        """Dim the glyph while the window is inactive.

        Args:

        - `active` (`bool`): Whether the top-level window is active.

        """
        if self._window_active == active:
            return
        self._window_active = active
        self.update()

    def _glyph_color(self) -> QColor:
        if self._kind == "close" and (self.underMouse() or self.isDown()):
            return CLOSE_GLYPH_COLOR
        if not self._window_active:
            return INACTIVE_GLYPH_LIGHT if self._light else INACTIVE_GLYPH_DARK
        return REST_GLYPH_LIGHT if self._light else REST_GLYPH_DARK

    def _rest_background(self) -> QColor:
        parent = self.parentWidget()
        source = parent if parent is not None else self
        return source.palette().color(QPalette.ColorRole.Window)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, *, kind: str, light: bool, parent: QWidget | None = None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, *, kind: str, light: bool, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        glyph, object_name, tooltip = _BUTTON_KINDS[kind]
        self._kind = kind
        self._glyph = glyph
        self._light = light
        self._window_active = True
        self.setObjectName(object_name)
        self.setToolTip(tooltip)
        self.setAccessibleName(tooltip)
        self.setFixedSize(CAPTION_BUTTON_WIDTH, CAPTION_BUTTON_HEIGHT)
        self.setAutoRaise(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, on=True)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
```

</details>

### ⚙️ Method `enterEvent`

```python
def enterEvent(self, event: QEnterEvent) -> None
```

Repaint so the Windows hover fill appears.

<details>
<summary>Code:</summary>

```python
def enterEvent(self, event: QEnterEvent) -> None:  # noqa: N802
        super().enterEvent(event)
        self.update()
```

</details>

### ⚙️ Method `glyph_name`

```python
def glyph_name(self) -> str
```

Return the Fluent glyph stem currently painted on this button.

<details>
<summary>Code:</summary>

```python
def glyph_name(self) -> str:
        return self._glyph
```

</details>

### ⚙️ Method `hover_background`

```python
def hover_background(self) -> QColor
```

Return the Windows 11 hover fill for this button.

<details>
<summary>Code:</summary>

```python
def hover_background(self) -> QColor:
        if self._kind == "close":
            return CLOSE_HOVER_COLOR
        if self._light:
            return MINMAX_HOVER_LIGHT
        return MINMAX_HOVER_DARK
```

</details>

### ⚙️ Method `leaveEvent`

```python
def leaveEvent(self, event: QEvent) -> None
```

Repaint after the pointer leaves the button.

<details>
<summary>Code:</summary>

```python
def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        super().leaveEvent(event)
        self.update()
```

</details>

### ⚙️ Method `mousePressEvent`

```python
def mousePressEvent(self, event: QMouseEvent) -> None
```

Repaint the pressed fill, then let the button emit `clicked`.

<details>
<summary>Code:</summary>

```python
def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        super().mousePressEvent(event)
        self.update()
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None
```

Repaint once the pressed fill should clear.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        super().mouseReleaseEvent(event)
        self.update()
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, event: QPaintEvent) -> None
```

Fill the button and draw a 16 px glyph centered in it.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802, ARG002
        painter = QPainter(self)
        if self.isDown():
            fill = self.pressed_background()
        elif self.underMouse():
            fill = self.hover_background()
        else:
            fill = self._rest_background()
        painter.fillRect(self.rect(), fill)
        icon = caption_glyph_icon(self._glyph, self._glyph_color(), self.devicePixelRatioF())
        if icon.isNull():
            painter.end()
            return
        side = CAPTION_GLYPH_SIZE
        x = (self.width() - side) // 2
        y = (self.height() - side) // 2
        icon.paint(painter, QRect(x, y, side, side))
        painter.end()
```

</details>

### ⚙️ Method `pressed_background`

```python
def pressed_background(self) -> QColor
```

Return the Windows 11 pressed fill for this button.

<details>
<summary>Code:</summary>

```python
def pressed_background(self) -> QColor:
        if self._kind == "close":
            return CLOSE_PRESSED_COLOR
        if self._light:
            return MINMAX_PRESSED_LIGHT
        return MINMAX_PRESSED_DARK
```

</details>

### ⚙️ Method `set_glyph`

```python
def set_glyph(self, name: str) -> None
```

Switch the centered Fluent glyph.

Args:

- `name` (`str`): Stem such as `maximize` or `square_multiple`.

<details>
<summary>Code:</summary>

```python
def set_glyph(self, name: str) -> None:
        if self._glyph == name:
            return
        self._glyph = name
        if name == "square_multiple":
            self.setToolTip("Restore")
            self.setAccessibleName("Restore")
        elif name == "maximize":
            self.setToolTip("Maximize")
            self.setAccessibleName("Maximize")
        self.update()
```

</details>

### ⚙️ Method `set_light`

```python
def set_light(self, *, light: bool) -> None
```

Use light or dark caption colors.

Args:

- `light` (`bool`): `True` when the window background is light.

<details>
<summary>Code:</summary>

```python
def set_light(self, *, light: bool) -> None:
        if self._light == light:
            return
        self._light = light
        self.update()
```

</details>

### ⚙️ Method `set_window_active`

```python
def set_window_active(self, *, active: bool) -> None
```

Dim the glyph while the window is inactive.

Args:

- `active` (`bool`): Whether the top-level window is active.

<details>
<summary>Code:</summary>

```python
def set_window_active(self, *, active: bool) -> None:
        if self._window_active == active:
            return
        self._window_active = active
        self.update()
```

</details>

## 🔧 Function `caption_glyph_icon`

```python
def caption_glyph_icon(name: str, color: QColor, dpr: float) -> QIcon
```

Paint one Fluent caption glyph.

Args:

- `name` (`str`): Glyph stem (`dismiss`, `subtract`, `maximize`, `square_multiple`).
- `color` (`QColor`): Fill color, including alpha.
- `dpr` (`float`): Device pixel ratio of the button.

Returns:

- `QIcon`: A 16 px icon, or a null icon when the SVG is missing.

<details>
<summary>Code:</summary>

```python
def caption_glyph_icon(name: str, color: QColor, dpr: float) -> QIcon:
    ratio = dpr if dpr > 0 else 1.0
    key = (name, color.rgba(), round(ratio, 2))
    cached = _ICON_CACHE.get(key)
    if cached is not None:
        return cached
    svg_bytes = _svg_bytes(name, color)
    if svg_bytes is None:
        return QIcon()
    icon = _icon_from_svg(svg_bytes, ratio, label=name)
    if not icon.isNull():
        _ICON_CACHE[key] = icon
    return icon
```

</details>

## 🔧 Function `caption_hit_test`

```python
def caption_hit_test(local: QPoint, size: QSize, *, caption: QRect, interactive: list[QRect], maximized: bool) -> int
```

Return the Win32 hit code for a point on a custom-caption window.

Edges resize, except over a caption control. Empty caption space drags the
window. A maximized window does not resize from its edges.

Args:

- `local` (`QPoint`): Point in the window's logical coordinates.
- [`size`](apps/icons/lightbox_cache.g.md#%EF%B8%8F-method-size-property) (`QSize`): Window size in logical pixels.
- `caption` (`QRect`): The icon/menu/tab/button row.
- `interactive` (`list[QRect]`): Buttons, menu items, and tabs that must stay clickable.
- `maximized` (`bool`): Whether the window is maximized or full screen.

Returns:

- `int`: `HTCLIENT`, `HTCAPTION`, or an edge code.

<details>
<summary>Code:</summary>

```python
def caption_hit_test(
    local: QPoint,
    size: QSize,
    *,
    caption: QRect,
    interactive: list[QRect],
    maximized: bool,
) -> int:
    on_control = any(rect.contains(local) for rect in interactive)
    if not maximized:
        edge = frameless_hit_test(local, size)
        if edge != HTCLIENT:
            if on_control:
                return HTCLIENT
            return edge
    if caption.isValid() and not caption.isEmpty() and caption.contains(local) and not on_control:
        return HTCAPTION
    return HTCLIENT
```

</details>

## 🔧 Function `install_win11_caption`

```python
def install_win11_caption(window: QWidget) -> bool
```

Replace the native title bar with the tab row plus Windows 11 buttons.

No-op outside Windows. The window title string is left in place for the taskbar.

Args:

- `window` (`QWidget`): Main window that already has `tabWidget`.

Returns:

- `bool`: `True` when the caption row was installed.

<details>
<summary>Code:</summary>

```python
def install_win11_caption(window: QWidget) -> bool:
    if sys.platform != "win32" or getattr(window, _INSTALLED_ATTR, False):
        return False
    tab_widget = getattr(window, "tabWidget", None)
    if not isinstance(tab_widget, QTabWidget):
        logger.warning("Win11 caption needs a tabWidget")
        return False

    light = _palette_is_light(window)
    controller = _Win11CaptionController(window)
    setattr(window, _CONTROLLER_ATTR, controller)
    _build_caption_row(window, tab_widget, controller, light=light)
    _flush_caption_to_frame(window)
    _fit_caption_fonts(window)
    _sync_caption_palette(window)
    window.installEventFilter(controller)
    setattr(window, _INSTALLED_ATTR, True)
    _set_frameless_window_flags(window)
    _collapse_native_menu_bar(window)
    _sync_caption_icon(window)
    _sync_zoom_glyph(window)
    return True
```

</details>

## 🔧 Function `try_handle_win11_caption_native_event`

```python
def try_handle_win11_caption_native_event(window: QWidget, event_type: bytes | bytearray | memoryview | QByteArray | str, message: Any) -> tuple[bool, int] | None
```

Handle caption drag, edge resize, and the borderless client area.

Args:

- `window` (`QWidget`): Window that installed the caption.
- `event_type`: Qt native-event type tag.
- `message` (`Any`): Platform message pointer.

Returns:

- `tuple[bool, int] | None`: Qt `nativeEvent` result, or `None` to keep the default.

<details>
<summary>Code:</summary>

```python
def try_handle_win11_caption_native_event(
    window: QWidget,
    event_type: bytes | bytearray | memoryview | QByteArray | str,
    message: Any,
) -> tuple[bool, int] | None:
    if sys.platform != "win32" or not getattr(window, _INSTALLED_ATTR, False):
        return None
    msg = read_native_windows_message(event_type, message)
    if msg is None:
        return None
    if msg.message == _WM_NCCALCSIZE and msg.wParam:
        _apply_maximized_nccalcsize(window, int(msg.lParam))
        return True, 0
    if msg.message != _WM_NCHITTEST:
        return None
    global_x = ctypes.c_short(msg.lParam & 0xFFFF).value
    global_y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
    local = native_local_point(window, global_x, global_y)
    if local is None:
        return None
    return True, _live_caption_hit_test(window, local)
```

</details>

## 🔧 Function `write_nccalcsize_client_rect`

```python
def write_nccalcsize_client_rect(address: int, left: int, top: int, right: int, bottom: int) -> None
```

Overwrite `NCCALCSIZE_PARAMS.rgrc[0]` at `address`.

Args:

- `address` (`int`): Address of an `NCCALCSIZE_PARAMS` block.
- `left` / `top` / `right` / `bottom` (`int`): Client rectangle in native pixels.

<details>
<summary>Code:</summary>

```python
def write_nccalcsize_client_rect(address: int, left: int, top: int, right: int, bottom: int) -> None:
    rect = wintypes.RECT(left, top, right, bottom)
    ctypes.memmove(address, ctypes.byref(rect), ctypes.sizeof(rect))
```

</details>
