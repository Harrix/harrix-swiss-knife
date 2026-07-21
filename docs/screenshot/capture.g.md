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

Capture a screen region with a ShareX-like flow.

Hides application Windows, optionally shows a floating shutter button, freezes
the desktop for region selection, copies the crop to the clipboard, restores
Windows, and optionally shows a preview dialog.

Args:
show_preview: If `True`, show the preview dialog after capture.
show_shutter_button: If `True`, wait for the floating camera button click
before starting region selection.

Returns:
Cropped `QImage`, or `None` if the user cancelled.

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

        if show_shutter_button:
            shutter = ShutterButton()
            if shutter.exec() != QDialog.DialogCode.Accepted:
                return None
            shutter.close()
            QApplication.processEvents()
            _wait_ms(50)

        frozen, geometry = _grab_virtual_desktop()
        if frozen.isNull():
            return None

        overlay = RegionOverlay(frozen, geometry)
        if overlay.exec() != QDialog.DialogCode.Accepted:
            return None

        image = overlay.cropped_image
        if image is None or image.isNull():
            return None

        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setImage(image)
    finally:
        restore_app_windows(hidden)

    if show_preview and image is not None and not image.isNull():
        dialog = ScreenshotPreviewDialog(image)
        dialog.exec()

    return image
```

</details>
