---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_frameless_window.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `frameless_hit_test`](#-function-frameless_hit_test)
- [🔧 Function `frameless_local_from_native`](#-function-frameless_local_from_native)
- [🔧 Function `frameless_stay_on_top_flags`](#-function-frameless_stay_on_top_flags)
- [🔧 Function `try_handle_frameless_resize_native_event`](#-function-try_handle_frameless_resize_native_event)

</details>

## 🔧 Function `frameless_hit_test`

```python
def frameless_hit_test(local: QPoint, size: QSize, *, border: int = _FRAMELESS_BORDER) -> int
```

Return a Win32 `HT*` code for a local point on a frameless window.

Args:

- `local` (`QPoint`): Position in the window's logical coordinates.
- `size` (`QSize`): Window size in logical pixels.
- `border` (`int`): Resize strip thickness in logical pixels. Defaults to `8`.

Returns:

- `int`: `HTCLIENT` or an edge/corner `HT*` value.

<details>
<summary>Code:</summary>

```python
def frameless_hit_test(local: QPoint, size: QSize, *, border: int = _FRAMELESS_BORDER) -> int:
    on_left = local.x() < border
    on_right = local.x() >= size.width() - border
    on_top = local.y() < border
    on_bottom = local.y() >= size.height() - border

    if on_top and on_left:
        return _HTTOPLEFT
    if on_top and on_right:
        return _HTTOPRIGHT
    if on_bottom and on_left:
        return _HTBOTTOMLEFT
    if on_bottom and on_right:
        return _HTBOTTOMRIGHT
    if on_left:
        return _HTLEFT
    if on_right:
        return _HTRIGHT
    if on_top:
        return _HTTOP
    if on_bottom:
        return _HTBOTTOM
    return _HTCLIENT
```

</details>

## 🔧 Function `frameless_local_from_native`

```python
def frameless_local_from_native(*, native_x: int, native_y: int, window_left: int, window_top: int, device_pixel_ratio: float) -> QPoint
```

Convert a native screen point to logical coordinates inside the window.

`WM_NCHITTEST` gives physical pixels. Qt layouts and `childAt` use logical
pixels. Passing native coordinates into `mapFromGlobal` on a scaled display
inflates the resize strip so it covers the close button.

<details>
<summary>Code:</summary>

```python
def frameless_local_from_native(
    *,
    native_x: int,
    native_y: int,
    window_left: int,
    window_top: int,
    device_pixel_ratio: float,
) -> QPoint:
    dpr = device_pixel_ratio if device_pixel_ratio > 0 else 1.0
    return QPoint(
        round((native_x - window_left) / dpr),
        round((native_y - window_top) / dpr),
    )
```

</details>

## 🔧 Function `frameless_stay_on_top_flags`

```python
def frameless_stay_on_top_flags() -> Qt.WindowType
```

Return window flags for a frameless stay-on-top tool window.

<details>
<summary>Code:</summary>

```python
def frameless_stay_on_top_flags() -> Qt.WindowType:
    return Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
```

</details>

## 🔧 Function `try_handle_frameless_resize_native_event`

```python
def try_handle_frameless_resize_native_event(widget: QWidget, event_type: bytes | bytearray | memoryview | QByteArray | str, message: Any, *, border: int = _FRAMELESS_BORDER) -> tuple[bool, int] | None
```

Handle WM_NCHITTEST so a frameless window can be resized from edges on Windows.

<details>
<summary>Code:</summary>

```python
def try_handle_frameless_resize_native_event(
    widget: QWidget,
    event_type: bytes | bytearray | memoryview | QByteArray | str,
    message: Any,
    *,
    border: int = _FRAMELESS_BORDER,
) -> tuple[bool, int] | None:
    if sys.platform != "win32" or _event_type_to_bytes(event_type) != b"windows_generic_MSG":
        return None

    address = _message_address(message)
    if address is None:
        return None

    try:
        msg = wintypes.MSG.from_address(address)
    except (TypeError, ValueError, OverflowError):
        return None

    if msg.message != _WM_NCHITTEST:
        return None

    global_x = ctypes.c_short(msg.lParam & 0xFFFF).value
    global_y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
    local = _nchittest_local_point(widget, global_x, global_y)
    if local is None:
        return None
    if _blocks_frameless_resize(widget, local):
        return True, _HTCLIENT
    return True, frameless_hit_test(local, widget.size(), border=border)
```

</details>
