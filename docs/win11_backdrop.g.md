---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `win11_backdrop.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `SystemBackdrop`](#%EF%B8%8F-class-systembackdrop)
- [🔧 Function `ensure_windows_app_user_model_id`](#-function-ensure_windows_app_user_model_id)
- [🔧 Function `try_apply_system_backdrop`](#-function-try_apply_system_backdrop)

</details>

## 🏛️ Class `SystemBackdrop`

```python
class SystemBackdrop(IntEnum)
```

Values for DWMWA_SYSTEMBACKDROP_TYPE (Windows 11).

<details>
<summary>Code:</summary>

```python
class SystemBackdrop(IntEnum):

    AUTO = 0
    NONE = 1
    MICA = 2
    ACRYLIC = 3
    TABBED = 4
```

</details>

## 🔧 Function `ensure_windows_app_user_model_id`

```python
def ensure_windows_app_user_model_id() -> None
```

Tell the Windows taskbar this process is Harrix Swiss Knife, not `python.exe`.

Without an explicit ID, taskbar buttons sometimes take the Python icon and
sometimes a blank window glyph, depending on which top-level window Windows
groups the process under. Call this before the first window is created.

<details>
<summary>Code:</summary>

```python
def ensure_windows_app_user_model_id() -> None:
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(_APP_USER_MODEL_ID)
    except Exception:
        logger.debug("SetCurrentProcessExplicitAppUserModelID failed", exc_info=True)
```

</details>

## 🔧 Function `try_apply_system_backdrop`

```python
def try_apply_system_backdrop(window: Any, *, backdrop: SystemBackdrop = SystemBackdrop.MICA) -> bool
```

Try to apply Windows 11 backdrop to a top-level Qt window.

The frame is not extended over the whole client area. Full-window
`DwmExtendFrameIntoClientArea` margins make the taskbar drop the window icon
until the next time Windows redraws the button.

Args:

- `window`: A top-level Qt widget (e.g., QMainWindow, QDialog).
- `backdrop`: Requested backdrop type.

Returns:

- `bool`: `True` if we called DWM successfully, `False` otherwise.

<details>
<summary>Code:</summary>

```python
def try_apply_system_backdrop(window: Any, *, backdrop: SystemBackdrop = SystemBackdrop.MICA) -> bool:
    if not _is_windows_11_or_newer():
        return False

    try:
        hwnd = int(window.winId())  # Qt: sip.voidptr -> int
    except Exception:
        return False

    try:
        dwmapi = ctypes.WinDLL("dwmapi")
    except Exception:
        return False

    # HRESULT DwmSetWindowAttribute(HWND, DWORD, LPCVOID, DWORD)
    dwm_set_window_attribute = dwmapi.DwmSetWindowAttribute
    dwm_set_window_attribute.argtypes = [wintypes.HWND, wintypes.DWORD, wintypes.LPCVOID, wintypes.DWORD]
    dwm_set_window_attribute.restype = ctypes.c_long

    dwmwa_system_backdrop_type = 38
    value = ctypes.c_int(int(backdrop))
    hr = dwm_set_window_attribute(hwnd, dwmwa_system_backdrop_type, ctypes.byref(value), ctypes.sizeof(value))
    if hr == 0:
        _reapply_taskbar_icon(window)
    return hr == 0
```

</details>
