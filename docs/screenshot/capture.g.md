---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `capture.py`

## 🔧 Function `capture_region`

```python
def capture_region() -> QImage | None
```

Capture a screen region with a ShareX-like workflow.

Hides application Windows, freezes the desktop for region selection, copies the
cropped region to the clipboard, restores Windows, and optionally shows a preview.

When `show_shutter_button` is `True`, a floating camera button stays visible on the
left. Capture starts immediately in region-selection mode. Clicking the button
switches to window-management mode (app Windows restored); clicking again returns
to region selection with a fresh desktop grab.

Args:

- `show_preview` (`bool`): If `True`, displays the preview dialog after capture.
- `show_shutter_button` (`bool`): If `True`, shows the mode-toggle shutter button.

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
    shutter: ShutterButton | None = None
    try:
        _wait_ms(_HIDE_SETTLE_MS)

        if show_shutter_button:
            shutter = ShutterButton()
            shutter.show()
            image = _capture_with_shutter_toggle(shutter, hidden)
        else:
            image = _capture_once()
            if image is None:
                return None
    finally:
        if shutter is not None:
            shutter.close()
        restore_app_windows(hidden)

    if show_preview and image is not None and not image.isNull():
        dialog = ScreenshotPreviewDialog(image)
        dialog.exec()

    return image
```

</details>
