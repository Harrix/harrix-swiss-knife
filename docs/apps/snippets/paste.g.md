---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `paste.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `clone_clipboard_mime`](#-function-clone_clipboard_mime)
- [🔧 Function `paste_text_then_restore_clipboard`](#-function-paste_text_then_restore_clipboard)
- [🔧 Function `restore_clipboard_mime`](#-function-restore_clipboard_mime)
- [🔧 Function `send_ctrl_v`](#-function-send_ctrl_v)

</details>

## 🔧 Function `clone_clipboard_mime`

```python
def clone_clipboard_mime() -> QMimeData
```

Return a copy of the current clipboard contents.

<details>
<summary>Code:</summary>

```python
def clone_clipboard_mime() -> QMimeData:
    clone = QMimeData()
    clipboard = QApplication.clipboard()
    if clipboard is None:
        return clone
    source = clipboard.mimeData()
    if source is None:
        return clone
    for fmt in source.formats():
        clone.setData(fmt, source.data(fmt))
    return clone
```

</details>

## 🔧 Function `paste_text_then_restore_clipboard`

```python
def paste_text_then_restore_clipboard(text: str, saved: QMimeData, *, on_finished: Callable[[], None] | None = None, paste_delay_ms: int = _PASTE_DELAY_MS, restore_delay_ms: int = _RESTORE_DELAY_MS) -> None
```

Set clipboard to `text`, paste, then restore `saved`.

<details>
<summary>Code:</summary>

```python
def paste_text_then_restore_clipboard(
    text: str,
    saved: QMimeData,
    *,
    on_finished: Callable[[], None] | None = None,
    paste_delay_ms: int = _PASTE_DELAY_MS,
    restore_delay_ms: int = _RESTORE_DELAY_MS,
) -> None:

    def restore() -> None:
        restore_clipboard_mime(saved)
        if on_finished is not None:
            on_finished()

    def paste() -> None:
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text)
        send_ctrl_v()
        QTimer.singleShot(restore_delay_ms, restore)

    app = QApplication.instance()
    if app is not None:
        app.processEvents()
    QTimer.singleShot(paste_delay_ms, paste)
```

</details>

## 🔧 Function `restore_clipboard_mime`

```python
def restore_clipboard_mime(mime: QMimeData) -> None
```

Replace the clipboard with a previously cloned `QMimeData`.

<details>
<summary>Code:</summary>

```python
def restore_clipboard_mime(mime: QMimeData) -> None:
    clipboard = QApplication.clipboard()
    if clipboard is None:
        return
    clipboard.setMimeData(mime)
```

</details>

## 🔧 Function `send_ctrl_v`

```python
def send_ctrl_v() -> bool
```

Send Ctrl+V to the focused window on Windows.

<details>
<summary>Code:</summary>

```python
def send_ctrl_v() -> bool:
    if sys.platform != "win32":
        return False
    send_input, keybd_input = _send_input_types()
    extra = ctypes.c_ulong(0)
    extra_ptr = ctypes.pointer(extra)

    def key_event(vk: int, flags: int = 0) -> Any:
        event = send_input()
        event.type = _INPUT_KEYBOARD
        event.union.ki = keybd_input(vk, 0, flags, 0, extra_ptr)
        return event

    events = (send_input * _CTRL_V_EVENT_COUNT)(
        key_event(_VK_CONTROL),
        key_event(_VK_V),
        key_event(_VK_V, _KEYEVENTF_KEYUP),
        key_event(_VK_CONTROL, _KEYEVENTF_KEYUP),
    )
    sent = ctypes.windll.user32.SendInput(_CTRL_V_EVENT_COUNT, ctypes.byref(events), ctypes.sizeof(send_input))
    return sent == _CTRL_V_EVENT_COUNT
```

</details>
