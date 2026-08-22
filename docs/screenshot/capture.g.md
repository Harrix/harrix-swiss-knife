---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `capture.py`

## 🔧 Function `capture_region`

```python
def capture_region(*, show_preview: bool = True, show_shutter_button: bool = True) -> QImage | None
```

Capture a screen region with a ShareX-like workflow.

Hides application Windows for the whole session, freezes the desktop for region
selection, copies the cropped region to the clipboard, restores Windows, and
optionally shows a preview in the foreground.

When `show_shutter_button` is `True`, arrange and close buttons are embedded in
the selection overlay. Clicking the arrange button removes the overlay so the
desktop can be arranged while the app stays hidden; a floating camera button
returns to region selection with a fresh grab. Escape during a drag clears
that selection; Escape with no active drag (or Close) cancels capture.

Every window shown here runs modally via `exec()`, so capture works even when
it is started from nested modal dialogs (e.g. New Markdown → Fill with AI).

Args:

- `show_preview` (`bool`): If `True`, displays the preview dialog after capture.
- `show_shutter_button` (`bool`): If `True`, shows the mode-toggle shutter controls.

Returns:

- `QImage | None`: Cropped image if captured, or `None` if the user cancelled.

<details>
<summary>Code:</summary>

```python
def capture_region(
    *,
    show_preview: bool = True,
    show_shutter_button: bool = True,
) -> QImage | None:
    app = QApplication.instance()
    if app is None:
        return None

    hidden = hide_app_windows()
    image: QImage | None = None
    try:
        _wait_ms(_HIDE_SETTLE_MS)
        image = _capture_loop(with_controls=show_shutter_button)
    finally:
        show_preview_now = show_preview and image is not None and not image.isNull()
        restore_app_windows(hidden, activate=not show_preview_now)

    if show_preview and image is not None and not image.isNull():
        dialog = ScreenshotPreviewDialog(image)
        dialog.show()
        bring_window_to_foreground(dialog, delays_ms=PREVIEW_FOREGROUND_DELAYS_MS)
        dialog.exec()

    return image
```

</details>
