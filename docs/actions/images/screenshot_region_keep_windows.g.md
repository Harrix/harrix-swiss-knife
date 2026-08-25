---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `screenshot_region_keep_windows.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnScreenshotRegionKeepWindows`](#%EF%B8%8F-class-onscreenshotregionkeepwindows)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnScreenshotRegionKeepWindows`

```python
class OnScreenshotRegionKeepWindows(ActionBase)
```

Capture a screen region without hiding this application's Windows.

Same ShareX-like flow as [`OnScreenshotRegion`](screenshot_region.g.md#%EF%B8%8F-class-onscreenshotregion), but tracker and other app
Windows stay on screen so they can be included in the screenshot.

<details>
<summary>Code:</summary>

```python
class OnScreenshotRegionKeepWindows(ActionBase):

    icon = "📷"
    title = "Screenshot region (keep Windows)"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("screenshot region keep Windows")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Start region selection without concealing application Windows."""
        image = capture_region(show_preview=True, show_shutter_button=True, hide_app=False)
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

Start region selection without concealing application Windows.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        image = capture_region(show_preview=True, show_shutter_button=True, hide_app=False)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        message = "Screenshot copied to clipboard"
        self.add_line(message)
        self.show_toast(message)
```

</details>
