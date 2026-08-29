---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `screenshot_region_clipboard_keep_windows.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnScreenshotRegionClipboardKeepWindows`](#%EF%B8%8F-class-onscreenshotregionclipboardkeepwindows)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnScreenshotRegionClipboardKeepWindows`

```python
class OnScreenshotRegionClipboardKeepWindows(ActionBase)
```

Capture a region to the clipboard without preview, keeping app Windows visible.

Same flow as [`OnScreenshotRegionClipboard`](screenshot_region_clipboard.g.md#%EF%B8%8F-class-onscreenshotregionclipboard), but tracker and other app Windows
stay on screen so they can be included in the screenshot.

<details>
<summary>Code:</summary>

```python
class OnScreenshotRegionClipboardKeepWindows(ActionBase):

    icon = "📷"
    title = "Screenshot region (clipboard, keep Windows)"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("screenshot region clipboard keep Windows")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Start region selection without concealing Windows; no preview."""
        image = capture_region(show_preview=False, show_shutter_button=True, hide_app=False)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        message = "Screenshot copied to clipboard"
        self.add_line(message)
        self.show_toast(message)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Start region selection without concealing Windows; no preview.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        image = capture_region(show_preview=False, show_shutter_button=True, hide_app=False)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        message = "Screenshot copied to clipboard"
        self.add_line(message)
        self.show_toast(message)
```

</details>
