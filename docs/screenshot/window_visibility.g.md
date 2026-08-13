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

Owners of those dialogs are also faded (not `hide()` / `show()`), so Windows
does not reshuffle Z-order and leave a `WindowModal` box behind its parent.

Modality is also set to NonModal and mouse events are ignored on faded
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

    candidates = [widget for widget in app.topLevelWidgets() if widget.isVisible() and not is_screenshot_ui(widget)]
    opacity_targets = _opacity_conceal_targets(candidates)

    concealed: list[ConcealedWindow] = []
    for widget in candidates:
        if widget in opacity_targets:
            concealed.append(_conceal_with_opacity(widget))
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

Non-modal (`hide`) Windows are restored first; opacity-concealed modals and
their owners are restored afterward so they stay above the owner chain.

<details>
<summary>Code:</summary>

```python
def restore_app_windows(widgets: list[ConcealedWindow]) -> None:
    hide_items = [item for item in widgets if item.mode == "hide"]
    opacity_items = [item for item in widgets if item.mode == "opacity"]

    for item in hide_items:
        item.widget.show()
        item.widget.raise_()

    for item in opacity_items:
        item.widget.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            item.transparent_for_mouse,
        )
        item.widget.setWindowModality(item.modality)
        item.widget.setWindowOpacity(item.opacity)
        item.widget.raise_()

    QApplication.processEvents()

    focus_target = _pick_focus_target(widgets)
    if focus_target is not None:
        _bring_to_foreground(focus_target)
        QApplication.processEvents()
        # Show/raise of owners can land after the first raise; pin the modal again.
        _bring_to_foreground(focus_target)

    QApplication.processEvents()
```

</details>
