---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `early_splash.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `close_early_splash`](#-function-close_early_splash)
- [🔧 Function `early_splash_hwnd`](#-function-early_splash_hwnd)
- [🔧 Function `ensure_early_splash`](#-function-ensure_early_splash)
- [🔧 Function `format_splash_clock`](#-function-format_splash_clock)
- [🔧 Function `splash_logo_path`](#-function-splash_logo_path)
- [🔧 Function `splash_status_lines`](#-function-splash_status_lines)

</details>

## 🔧 Function `close_early_splash`

```python
def close_early_splash() -> None
```

Close the splash if it is showing.

<details>
<summary>Code:</summary>

```python
def close_early_splash() -> None:
    _runtime.stop.set()
    with _lock:
        hwnd = _runtime.hwnd
        thread = _runtime.thread
    if hwnd:
        with contextlib.suppress(OSError):
            _user32().PostMessageW(hwnd, _WM_CLOSE, 0, 0)
    if thread is not None:
        thread.join(timeout=2.0)
    with _lock:
        _runtime.hwnd = 0
        _runtime.thread = None
```

</details>

## 🔧 Function `early_splash_hwnd`

```python
def early_splash_hwnd() -> int
```

Return the splash window handle, or `0` when it is not showing.

<details>
<summary>Code:</summary>

```python
def early_splash_hwnd() -> int:
    with _lock:
        return _runtime.hwnd
```

</details>

## 🔧 Function `ensure_early_splash`

```python
def ensure_early_splash() -> None
```

Show a topmost splash as soon as the process starts.

<details>
<summary>Code:</summary>

```python
def ensure_early_splash() -> None:
    if sys.platform != "win32" or _qt_app_exists():
        return
    _enable_dpi_awareness()
    with _lock:
        thread = _runtime.thread
        if thread is not None and thread.is_alive():
            return
    try:
        _start_thread()
    except (OSError, ValueError, AttributeError):
        close_early_splash()
```

</details>

## 🔧 Function `format_splash_clock`

```python
def format_splash_clock(seconds: int) -> str
```

Format elapsed seconds as `MM:SS`, or `HH:MM:SS` after 60 minutes.

<details>
<summary>Code:</summary>

```python
def format_splash_clock(seconds: int) -> str:
    total = max(0, int(seconds))
    if total >= _SECONDS_PER_HOUR:
        hours, rem = divmod(total, _SECONDS_PER_HOUR)
        minutes, secs = divmod(rem, _SECONDS_PER_MINUTE)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    minutes, secs = divmod(total, _SECONDS_PER_MINUTE)
    return f"{minutes:02d}:{secs:02d}"
```

</details>

## 🔧 Function `splash_logo_path`

```python
def splash_logo_path() -> Path | None
```

Return the ICO used on the splash, if the file exists.

<details>
<summary>Code:</summary>

```python
def splash_logo_path() -> Path | None:
    path = Path(__file__).resolve().parent / "assets" / "app.ico"
    return path if path.is_file() else None
```

</details>

## 🔧 Function `splash_status_lines`

```python
def splash_status_lines(seconds: int) -> tuple[str, str, str]
```

Return the three splash lines: title, status, and clock.

<details>
<summary>Code:</summary>

```python
def splash_status_lines(seconds: int) -> tuple[str, str, str]:
    return TRAY_LOADING_TITLE, _LOADING_LINE, format_splash_clock(seconds)
```

</details>
