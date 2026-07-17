---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_frameless_window.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `frameless_stay_on_top_flags`](#-function-frameless_stay_on_top_flags)
- [🔧 Function `try_handle_frameless_resize_native_event`](#-function-try_handle_frameless_resize_native_event)
- [🔧 Function `_event_type_to_bytes`](#-function-_event_type_to_bytes)
- [🔧 Function `_message_address`](#-function-_message_address)

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
def try_handle_frameless_resize_native_event(widget: QWidget, event_type: bytes | bytearray | memoryview | QByteArray | str, message: Any) -> tuple[bool, int] | None
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
    local = widget.mapFromGlobal(QPoint(global_x, global_y))
    rect = widget.rect()

    on_left = local.x() < border
    on_right = local.x() >= rect.width() - border
    on_top = local.y() < border
    on_bottom = local.y() >= rect.height() - border

    if on_top and on_left:
        return True, _HTTOPLEFT
    if on_top and on_right:
        return True, _HTTOPRIGHT
    if on_bottom and on_left:
        return True, _HTBOTTOMLEFT
    if on_bottom and on_right:
        return True, _HTBOTTOMRIGHT
    if on_left:
        return True, _HTLEFT
    if on_right:
        return True, _HTRIGHT
    if on_top:
        return True, _HTTOP
    if on_bottom:
        return True, _HTBOTTOM
    return True, _HTCLIENT
```

</details>

## 🔧 Function `_event_type_to_bytes`

```python
def _event_type_to_bytes(event_type: bytes | bytearray | memoryview | QByteArray | str) -> bytes
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _event_type_to_bytes(event_type: bytes | bytearray | memoryview | QByteArray | str) -> bytes:
    if isinstance(event_type, QByteArray):
        return bytes(event_type.data())
    if isinstance(event_type, memoryview):
        return event_type.tobytes()
    if isinstance(event_type, str):
        return event_type.encode("utf-8")
    return bytes(event_type)
```

</details>

## 🔧 Function `_message_address`

```python
def _message_address(message: Any) -> int | None
```

Convert PySide6 nativeEvent message pointer to an integer address.

<details>
<summary>Code:</summary>

```python
def _message_address(message: Any) -> int | None:
    if isinstance(message, int):
        return message

    for converter in (
        int,
        lambda value: int(value.__int__()),  # Shiboken VoidPtr
        lambda value: ctypes.cast(value, ctypes.c_void_p).value,
    ):
        try:
            address = converter(message)
        except (AttributeError, TypeError, ValueError, OverflowError):
            continue
        if isinstance(address, int) and address:
            return address
    return None
```

</details>
