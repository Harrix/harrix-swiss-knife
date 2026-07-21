---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `window_visibility.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `hide_app_windows`](#-function-hide_app_windows)
- [🔧 Function `is_screenshot_ui`](#-function-is_screenshot_ui)
- [🔧 Function `mark_screenshot_ui`](#-function-mark_screenshot_ui)
- [🔧 Function `restore_app_windows`](#-function-restore_app_windows)

</details>

## 🔧 Function `hide_app_windows`

```python
def hide_app_windows() -> list[QWidget]
```

Hide all visible top-level application Windows except screenshot UI.

Returns:
Widgets that were hidden and should be restored later.

<details>
<summary>Code:</summary>

```python
def hide_app_windows() -> list[QWidget]:
    app = QApplication.instance()
    if app is None:
        return []

    hidden: list[QWidget] = []
    for widget in app.topLevelWidgets():
        if not widget.isVisible():
            continue
        if is_screenshot_ui(widget):
            continue
        widget.hide()
        hidden.append(widget)

    QApplication.processEvents()
    return hidden
```

</details>

## 🔧 Function `is_screenshot_ui`

```python
def is_screenshot_ui(widget: QWidget) -> bool
```

Return whether the widget belongs to the screenshot capture UI.

<details>
<summary>Code:</summary>

```python
def is_screenshot_ui(widget: QWidget) -> bool:
    return bool(widget.property(HSK_SCREENSHOT_UI_PROP))
```

</details>

## 🔧 Function `mark_screenshot_ui`

```python
def mark_screenshot_ui(widget: QWidget) -> None
```

Mark a widget so it is not hidden with the rest of the application.

<details>
<summary>Code:</summary>

```python
def mark_screenshot_ui(widget: QWidget) -> None:
    widget.setProperty(HSK_SCREENSHOT_UI_PROP, True)  # noqa: FBT003
```

</details>

## 🔧 Function `restore_app_windows`

```python
def restore_app_windows(widgets: list[QWidget]) -> None
```

Show Windows previously hidden by `hide_app_windows`.

<details>
<summary>Code:</summary>

```python
def restore_app_windows(widgets: list[QWidget]) -> None:
    for widget in widgets:
        widget.show()
    QApplication.processEvents()
```

</details>
