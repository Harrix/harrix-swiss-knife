---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `capture.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `capture_region`](#-function-capture_region)
- [🔧 Function `clear_pending_screen_freeze`](#-function-clear_pending_screen_freeze)
- [🔧 Function `grab_all_screens`](#-function-grab_all_screens)
- [🔧 Function `prepare_capture_long_press_freeze`](#-function-prepare_capture_long_press_freeze)
- [🔧 Function `select_region`](#-function-select_region)
- [🔧 Function `set_pending_screen_freeze`](#-function-set_pending_screen_freeze)
- [🔧 Function `take_pending_screen_freeze`](#-function-take_pending_screen_freeze)

</details>

## 🔧 Function `capture_region`

```python
def capture_region(*, show_preview: bool = True, ocr_translate: bool = False, show_shutter_button: bool = True, hide_app: bool | None = None) -> QImage | None
```

Capture a screen region with a ShareX-like workflow.

Optionally hides application Windows for the whole session, freezes the desktop
for region selection, copies the cropped region to the clipboard, restores
Windows, and optionally shows a preview in the foreground.

When `hide_app` is `None` (the default), application Windows are hidden unless
a modal dialog is visible (for example Finance Balance check). Hiding that
dialog would drop it from the snap list so hover highlights the owner instead.

When `hide_app` is `False`, application Windows stay visible so they can be
included in the capture (for example a tracker window). The keep-Windows
shutter button can flip this during selection: the overlay closes, Windows
are hidden or restored, and a fresh grab opens a new overlay.

When `show_shutter_button` is `True`, arrange, adjust, guides, keep-Windows,
clipboard-only, OCR + translate, and close buttons are embedded in the
selection overlay. Arrange removes the overlay so the desktop can be
rearranged; clipboard-only skips the preview after capture; OCR + translate
skips the preview and starts OCR/translate; adjust keeps the next selection
editable (move/resize) until Enter or double-click; close cancels. A floating
camera button returns to region selection with a fresh grab.

Every capture overlay runs modally via `exec()`. The optional preview window is
non-modal so later captures can add tabs to an already open preview.

Args:

- `show_preview` (`bool`): If `True`, displays the preview window after capture
  unless clipboard-only or OCR + translate is selected on the shutter bar.
- `ocr_translate` (`bool`): If `True`, starts with OCR + translate enabled
  (implies skipping the preview when left on).
- `show_shutter_button` (`bool`): If `True`, shows the mode-toggle shutter controls.
- `hide_app` (`bool | None`): If `True`, conceals application Windows before
  the grab. If `False`, they stay visible. If `None`, conceal unless a modal
  dialog is visible.

Returns:

- `QImage | None`: Cropped image if captured, or `None` if the user cancelled.

<details>
<summary>Code:</summary>

```python
def capture_region(
    *,
    show_preview: bool = True,
    ocr_translate: bool = False,
    show_shutter_button: bool = True,
    hide_app: bool | None = None,
) -> QImage | None:
    app = QApplication.instance()
    if app is None:
        return None

    if hide_app is None:
        hide_app = not has_visible_modal_dialog()

    session = _HideSession(
        hide_app=hide_app,
        show_preview=show_preview and not ocr_translate,
        ocr_translate=ocr_translate,
        hidden=hide_app_windows() if hide_app else [],
    )
    image: QImage | None = None
    try:
        if session.hide_app:
            _wait_ms(_HIDE_SETTLE_MS)
        image = _capture_loop(with_controls=show_shutter_button, session=session)
    finally:
        show_preview_now = session.show_preview and image is not None and not image.isNull()
        if session.hide_app:
            restore_app_windows(session.hidden, activate=not show_preview_now)

    if session.ocr_translate and image is not None and not image.isNull():
        _start_ocr_translate(image)
    elif session.show_preview and image is not None and not image.isNull():
        window = show_screenshot_preview(image)
        bring_window_to_foreground(window, delays_ms=PREVIEW_FOREGROUND_DELAYS_MS)

    return image
```

</details>

## 🔧 Function `clear_pending_screen_freeze`

```python
def clear_pending_screen_freeze() -> None
```

Drop any unused long-press freeze.

<details>
<summary>Code:</summary>

```python
def clear_pending_screen_freeze() -> None:
    global _pending_screen_freeze  # noqa: PLW0603
    _pending_screen_freeze = None
```

</details>

## 🔧 Function `grab_all_screens`

```python
def grab_all_screens() -> tuple[list[ScreenGrab], QRect]
```

Grab each monitor at native resolution.

A single overlay HWND uses the primary screen's DPI, so a 200% 4K monitor
next to a 100% ultrawide would only cover part of the 4K display. Each grab
is shown on its own fullscreen pane instead.

<details>
<summary>Code:</summary>

```python
def grab_all_screens() -> tuple[list[ScreenGrab], QRect]:
    app = QApplication.instance()
    if app is None:
        return [], QRect()

    screens = app.screens()
    primary = app.primaryScreen()
    if not screens or primary is None:
        return [], QRect()

    grabs: list[ScreenGrab] = []
    for screen in screens:
        grab = screen.grabWindow(0)
        if grab.isNull():
            continue
        dpr = screen.devicePixelRatio()
        grabs.append(
            ScreenGrab(
                geometry=screen.geometry(),
                dpr=dpr if dpr > 0 else 1.0,
                pixmap=grab,
            ),
        )
    return grabs, primary.virtualGeometry()
```

</details>

## 🔧 Function `prepare_capture_long_press_freeze`

```python
def prepare_capture_long_press_freeze() -> bool
```

Grab all screens now and store them for the next capture overlay pass.

Call this before opening the capture-action picker so foreign UI (for example
a VS Code context menu) is frozen before focus changes dismiss it.

Returns:

- `bool`: `True` when at least one screen was frozen.

<details>
<summary>Code:</summary>

```python
def prepare_capture_long_press_freeze() -> bool:
    grabs, geometry = grab_all_screens()
    if not grabs:
        clear_pending_screen_freeze()
        return False
    set_pending_screen_freeze(grabs, geometry)
    return True
```

</details>

## 🔧 Function `select_region`

```python
def select_region(*, show_shutter_button: bool = True, hide_app: bool | None = None) -> QRect | None
```

Select a screen region and return its global logical rectangle.

Same overlay workflow as [`capture_region`](#-function-capture_region), but does not crop an image or copy
to the clipboard. Used before screen recording.

<details>
<summary>Code:</summary>

```python
def select_region(
    *,
    show_shutter_button: bool = True,
    hide_app: bool | None = None,
) -> QRect | None:
    app = QApplication.instance()
    if app is None:
        return None

    if hide_app is None:
        hide_app = not has_visible_modal_dialog()

    session = _HideSession(
        hide_app=hide_app,
        show_preview=False,
        hidden=hide_app_windows() if hide_app else [],
    )
    rect: QRect | None = None
    try:
        if session.hide_app:
            _wait_ms(_HIDE_SETTLE_MS)
        rect = _select_loop(with_controls=show_shutter_button, session=session)
    finally:
        if session.hide_app:
            restore_app_windows(session.hidden, activate=True)

    return rect
```

</details>

## 🔧 Function `set_pending_screen_freeze`

```python
def set_pending_screen_freeze(grabs: Sequence[ScreenGrab], geometry: QRect) -> None
```

Store a desktop freeze for the next `_capture_loop` / `_select_loop` pass.

<details>
<summary>Code:</summary>

```python
def set_pending_screen_freeze(grabs: Sequence[ScreenGrab], geometry: QRect) -> None:
    global _pending_screen_freeze  # noqa: PLW0603
    _pending_screen_freeze = (list(grabs), QRect(geometry))
```

</details>

## 🔧 Function `take_pending_screen_freeze`

```python
def take_pending_screen_freeze() -> tuple[list[ScreenGrab], QRect] | None
```

Return and clear the pending freeze, or `None` when empty.

<details>
<summary>Code:</summary>

```python
def take_pending_screen_freeze() -> tuple[list[ScreenGrab], QRect] | None:
    global _pending_screen_freeze  # noqa: PLW0603
    pending = _pending_screen_freeze
    _pending_screen_freeze = None
    return pending
```

</details>
