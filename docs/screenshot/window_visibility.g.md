---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `window_visibility.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ConcealedWindow`](#%EF%B8%8F-class-concealedwindow)
- [🔧 Function `hide_app_windows`](#-function-hide_app_windows)
- [🔧 Function `is_screenshot_ui`](#-function-is_screenshot_ui)
- [🔧 Function `mark_screenshot_ui`](#-function-mark_screenshot_ui)
- [🔧 Function `restore_app_windows`](#-function-restore_app_windows)

</details>

## 🏛️ Class `ConcealedWindow`

```python
class ConcealedWindow
```

State needed to restore a window after screenshot capture.

<details>
<summary>Code:</summary>

```python
class ConcealedWindow:

    widget: QWidget
    mode: ConcealMode
    opacity: float = 1.0
    modality: Qt.WindowModality = Qt.WindowModality.NonModal
    transparent_for_mouse: bool = False
```

</details>

## 🔧 Function `hide_app_windows`

```python
def hide_app_windows() -> list[ConcealedWindow]
```

Conceal visible top-level application Windows except screenshot UI.

Modal dialogs are faded with opacity `0` instead of `hide()`, because
hiding a modal `QDialog` ends its `exec()` loop as Rejected (e.g. Fill
with AI source dialog while capturing a screenshot).

Modality is also set to NonModal and mouse events are ignored on those
dialogs. Note: Qt does not fully drop ApplicationModal blocking for a
window that stays visible, so screenshot UI must still present itself as
ApplicationModal on top (see `capture._capture_loop`).

Returns:

- `list[ConcealedWindow]`: Windows that were concealed and should be restored.

<details>
<summary>Code:</summary>

```python
def hide_app_windows() -> list[ConcealedWindow]:
    app = QApplication.instance()
    if app is None:
        return []

    concealed: list[ConcealedWindow] = []
    for widget in app.topLevelWidgets():
        if not widget.isVisible():
            continue
        if is_screenshot_ui(widget):
            continue
        if isinstance(widget, QDialog) and widget.isModal():
            opacity = widget.windowOpacity()
            modality = widget.windowModality()
            was_transparent = bool(widget.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents))
            widget.setWindowOpacity(0.0)
            # Keep exec() alive, but do not leave an ApplicationModal blocker.
            widget.setWindowModality(Qt.WindowModality.NonModal)
            widget.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents,
                True,  # noqa: FBT003
            )
            concealed.append(
                ConcealedWindow(
                    widget,
                    "opacity",
                    opacity,
                    modality=modality,
                    transparent_for_mouse=was_transparent,
                )
            )
        else:
            widget.hide()
            concealed.append(ConcealedWindow(widget, "hide"))

    QApplication.processEvents()
    return concealed
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
def restore_app_windows(widgets: list[ConcealedWindow]) -> None
```

Restore Windows previously concealed by [`hide_app_windows`](#-function-hide_app_windows) and bring them forward.

After a fullscreen capture overlay, other apps may sit on top of the Z-order.
Restored widgets are raised and the topmost modal dialog is activated so the
user returns to Fill with AI / New Markdown without hunting the taskbar.

<details>
<summary>Code:</summary>

```python
def restore_app_windows(widgets: list[ConcealedWindow]) -> None:
    for item in widgets:
        if item.mode == "opacity":
            item.widget.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents,
                item.transparent_for_mouse,
            )
            item.widget.setWindowModality(item.modality)
            item.widget.setWindowOpacity(item.opacity)
        else:
            item.widget.show()
        item.widget.raise_()

    focus_target = _pick_focus_target(widgets)
    if focus_target is not None:
        focus_target.show()
        focus_target.raise_()
        focus_target.activateWindow()
        _force_foreground(focus_target)

    QApplication.processEvents()
```

</details>
