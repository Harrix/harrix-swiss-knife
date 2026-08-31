---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `screenshot_region_clipboard.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnScreenshotRegionClipboard`](#%EF%B8%8F-class-onscreenshotregionclipboard)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnScreenshotRegionClipboard`

```python
class OnScreenshotRegionClipboard(ActionBase)
```

Capture a screen region to the clipboard without opening the preview window.

Same ShareX-like selection as [`OnScreenshotRegion`](screenshot_region.g.md#%EF%B8%8F-class-onscreenshotregion), starting with the
clipboard-only shutter button on so the preview window is skipped. A
visible modal dialog stays on screen so it can be snapped. The
keep-Windows button can still show or hide app Windows and re-grab.

<details>
<summary>Code:</summary>

```python
class OnScreenshotRegionClipboard(ActionBase):

    icon = "📷"
    title = "Screenshot region (clipboard)"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("screenshot region clipboard")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Start region selection; copy to clipboard only."""
        image = capture_region(show_preview=False, show_shutter_button=True)
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

Start region selection; copy to clipboard only.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        image = capture_region(show_preview=False, show_shutter_button=True)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        message = "Screenshot copied to clipboard"
        self.add_line(message)
        self.show_toast(message)
```

</details>
