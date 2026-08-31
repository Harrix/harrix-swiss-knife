---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `capture.py`

## 🔧 Function `capture_region`

```python
def capture_region(*, show_preview: bool = True, show_shutter_button: bool = True, hide_app: bool | None = None) -> QImage | None
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
clipboard-only, and close buttons are embedded in the selection overlay.
Arrange removes the overlay so the desktop can be rearranged; clipboard-only
skips the preview after capture; adjust keeps the next selection editable
(move/resize) until Enter or double-click; close cancels. A floating camera
button returns to region selection with a fresh grab.

Every capture overlay runs modally via `exec()`. The optional preview window is
non-modal so later captures can add tabs to an already open preview.

Args:

- `show_preview` (`bool`): If `True`, displays the preview window after capture.
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
        show_preview=show_preview,
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

    if session.show_preview and image is not None and not image.isNull():
        window = show_screenshot_preview(image)
        bring_window_to_foreground(window, delays_ms=PREVIEW_FOREGROUND_DELAYS_MS)

    return image
```

</details>
