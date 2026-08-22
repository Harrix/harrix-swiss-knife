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
- [🔧 Function `bring_window_to_foreground`](#-function-bring_window_to_foreground)
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
    was_active: bool = False
    stay_on_top: bool = False
```

</details>

## 🔧 Function `bring_window_to_foreground`

```python
def bring_window_to_foreground(widget: QWidget, *, delays_ms: tuple[int, ...] | None = None) -> None
```

Raise `widget` now and again after Windows focus races.

Args:

- `widget` (`QWidget`): Window that should stay in front.
- `delays_ms` (`tuple[int, ...] | None`): Extra pin delays. Defaults to
  `_REPIN_MODAL_DELAYS_MS`. Pass `()` to raise once without a timer.

<details>
<summary>Code:</summary>

```python
def bring_window_to_foreground(widget: QWidget, *, delays_ms: tuple[int, ...] | None = None) -> None:
    _bring_to_foreground(widget)
    if delays_ms is None:
        delays_ms = _REPIN_MODAL_DELAYS_MS
    if delays_ms:
        _schedule_foreground(widget, delays_ms=delays_ms)
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

When any modal dialog is visible, every other visible top-level window is
also faded (not `hide()` / `show()`). `hide()` of a sibling such as
Fitness, then `show()` after capture, often puts that window above a
still-living `WindowModal` `QMessageBox`, which then blocks clicks while
staying invisible.

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
    active = _active_top_level()

    concealed: list[ConcealedWindow] = []
    for widget in candidates:
        was_active = widget is active
        stay_on_top = _has_stay_on_top(widget)
        if widget in opacity_targets:
            concealed.append(
                replace(_conceal_with_opacity(widget), was_active=was_active, stay_on_top=stay_on_top),
            )
        else:
            widget.hide()
            concealed.append(ConcealedWindow(widget, "hide", was_active=was_active, stay_on_top=stay_on_top))

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
def restore_app_windows(widgets: list[ConcealedWindow], *, activate: bool = True) -> None
```

Restore Windows previously concealed by [`hide_app_windows`](#-function-hide_app_windows) and bring them forward.

After a fullscreen capture overlay, other apps may sit on top of the Z-order.
Restored widgets are raised and the window that started the capture (or its
modal dialog) is activated so the user returns to Finance / Fill with AI /
an error `QMessageBox` — not a stay-on-top sibling such as the command cards.

Non-modal (`hide`) Windows are restored first; opacity-concealed owners
next; modal dialogs last so they stay above the owner chain. Stay-on-top
is cleared on siblings of the focus target so they cannot cover it.

When `activate` is `False`, Windows are shown again but not focused. Use that
when a screenshot preview will take the foreground next.

Args:

- `widgets` (`list[ConcealedWindow]`): Concealed Windows from [`hide_app_windows`](#-function-hide_app_windows).
- `activate` (`bool`): If `True`, focus the window that started capture.
  Defaults to `True`.

<details>
<summary>Code:</summary>

```python
def restore_app_windows(widgets: list[ConcealedWindow], *, activate: bool = True) -> None:
    hide_items = [item for item in widgets if item.mode == "hide"]
    opacity_owners, opacity_modals = _split_opacity_items(widgets)

    for item in hide_items:
        item.widget.show()
        item.widget.raise_()

    for item in [*opacity_owners, *opacity_modals]:
        _restore_opacity_item(item)

    for item in opacity_owners:
        item.widget.raise_()
    for item in opacity_modals:
        item.widget.raise_()

    QApplication.processEvents()

    if not activate:
        _drop_stay_on_top_except(widgets, None)
        QApplication.processEvents()
        return

    focus_target = _pick_focus_target(widgets)
    if focus_target is not None:
        _drop_stay_on_top_except(widgets, focus_target)
        _bring_to_foreground(focus_target)
        QApplication.processEvents()
        # Show/raise of owners can land after the first raise; pin the modal again.
        _bring_to_foreground(focus_target)
        _schedule_foreground(focus_target)

    QApplication.processEvents()
```

</details>
