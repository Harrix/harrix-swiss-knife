---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `app_startup_toast.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `AppLoadingToastPumper`](#%EF%B8%8F-class-apploadingtoastpumper)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `refresh_display`](#%EF%B8%8F-method-refresh_display)
  - [⚙️ Method `start`](#%EF%B8%8F-method-start)
  - [⚙️ Method `stop`](#%EF%B8%8F-method-stop)
- [🔧 Function `app_loading_title`](#-function-app_loading_title)
- [🔧 Function `app_loading_toast_scope`](#-function-app_loading_toast_scope)
- [🔧 Function `start_app_loading_toast`](#-function-start_app_loading_toast)
- [🔧 Function `stop_app_loading_toast`](#-function-stop_app_loading_toast)

</details>

## 🏛️ Class `AppLoadingToastPumper`

```python
class AppLoadingToastPumper
```

Refresh the loading toast clock while the UI thread is busy.

`QTimer` does not fire during `MainWindow` construction. A per-thread
`sys.setprofile` hook refreshes the clock without `processEvents`, so
other Qt timers cannot run re-entrantly. The window is repainted only
when the displayed second changes, so a translucent toast does not flicker.

<details>
<summary>Code:</summary>

```python
class AppLoadingToastPumper:

    def __init__(self, toast: ToastCountdownNotification, *, interval_s: float = _PUMP_INTERVAL_S) -> None:
        """Store the toast and how often to refresh the clock."""
        self._toast = toast
        self._interval_s = interval_s
        self._last = 0.0
        self._previous: Any = None
        self._active = False

    def refresh_display(self) -> None:
        """Read `QElapsedTimer` and paint the clock without processing Qt events."""
        toast = self._toast
        previous = toast.elapsed_seconds
        toast.update_time()
        if toast.elapsed_seconds == previous:
            return
        toast.repaint()

    def start(self) -> None:
        """Install the profile hook and paint the first clock value."""
        if self._active:
            return
        self._active = True
        self._last = 0.0
        self._previous = sys.getprofile()
        sys.setprofile(self._on_profile)
        self.refresh_display()

    def stop(self) -> None:
        """Restore the previous profile hook and paint the final clock value."""
        if not self._active:
            return
        self._active = False
        sys.setprofile(self._previous)
        self._previous = None
        self.refresh_display()

    def _on_profile(self, _frame: object, event: str, _arg: object) -> object:
        if event == "call":
            now = time.monotonic()
            if now - self._last >= self._interval_s:
                self._last = now
                self.refresh_display()
        return self._on_profile
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, toast: ToastCountdownNotification, *, interval_s: float = _PUMP_INTERVAL_S) -> None
```

Store the toast and how often to refresh the clock.

<details>
<summary>Code:</summary>

```python
def __init__(self, toast: ToastCountdownNotification, *, interval_s: float = _PUMP_INTERVAL_S) -> None:
        self._toast = toast
        self._interval_s = interval_s
        self._last = 0.0
        self._previous: Any = None
        self._active = False
```

</details>

### ⚙️ Method `refresh_display`

```python
def refresh_display(self) -> None
```

Read `QElapsedTimer` and paint the clock without processing Qt events.

<details>
<summary>Code:</summary>

```python
def refresh_display(self) -> None:
        toast = self._toast
        previous = toast.elapsed_seconds
        toast.update_time()
        if toast.elapsed_seconds == previous:
            return
        toast.repaint()
```

</details>

### ⚙️ Method `start`

```python
def start(self) -> None
```

Install the profile hook and paint the first clock value.

<details>
<summary>Code:</summary>

```python
def start(self) -> None:
        if self._active:
            return
        self._active = True
        self._last = 0.0
        self._previous = sys.getprofile()
        sys.setprofile(self._on_profile)
        self.refresh_display()
```

</details>

### ⚙️ Method `stop`

```python
def stop(self) -> None
```

Restore the previous profile hook and paint the final clock value.

<details>
<summary>Code:</summary>

```python
def stop(self) -> None:
        if not self._active:
            return
        self._active = False
        sys.setprofile(self._previous)
        self._previous = None
        self.refresh_display()
```

</details>

## 🔧 Function `app_loading_title`

```python
def app_loading_title(source: object) -> str
```

Return a short app name for the loading toast.

Prefers `about_app_name` (window class), then `title` (launcher action).

<details>
<summary>Code:</summary>

```python
def app_loading_title(source: object) -> str:
    about = getattr(source, "about_app_name", None)
    if isinstance(about, str):
        text = about.strip()
        if text:
            return text
    title = getattr(source, "title", None)
    if isinstance(title, str):
        text = title.strip()
        if text:
            return text
    return DEFAULT_APP_LOADING_TITLE
```

</details>

## 🔧 Function `app_loading_toast_scope`

```python
def app_loading_toast_scope(app_title: str) -> Iterator[ToastCountdownNotification]
```

Show a loading toast and keep its elapsed clock updating until exit.

<details>
<summary>Code:</summary>

```python
def app_loading_toast_scope(app_title: str) -> Iterator[ToastCountdownNotification]:
    toast = start_app_loading_toast(app_title)
    pumper = AppLoadingToastPumper(toast)
    pumper.start()
    try:
        yield toast
    finally:
        pumper.stop()
        stop_app_loading_toast(toast)
```

</details>

## 🔧 Function `start_app_loading_toast`

```python
def start_app_loading_toast(app_title: str) -> ToastCountdownNotification
```

Show a countdown toast for `Loading {app_title}…`.

<details>
<summary>Code:</summary>

```python
def start_app_loading_toast(app_title: str) -> ToastCountdownNotification:
    text = app_title.strip() or DEFAULT_APP_LOADING_TITLE
    toast = ToastCountdownNotification(f"Loading {text}…")
    toast.start_countdown()
    toast.pump_events()
    return toast
```

</details>

## 🔧 Function `stop_app_loading_toast`

```python
def stop_app_loading_toast(toast: ToastCountdownNotification | None) -> None
```

Refresh elapsed time once, then close the loading toast.

<details>
<summary>Code:</summary>

```python
def stop_app_loading_toast(toast: ToastCountdownNotification | None) -> None:
    if toast is None:
        return
    toast.update_time()
    toast.pump_events()
    toast.close()
```

</details>
