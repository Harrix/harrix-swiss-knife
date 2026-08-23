---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `app_startup_toast.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `app_loading_title`](#-function-app_loading_title)
- [🔧 Function `start_app_loading_toast`](#-function-start_app_loading_toast)
- [🔧 Function `stop_app_loading_toast`](#-function-stop_app_loading_toast)

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
