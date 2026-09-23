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

Capture a screen region while keeping Harrix Swiss Knife Windows visible.

Same ShareX-like selection as [`OnScreenshotRegion`](screenshot_region.g.md#%EF%B8%8F-class-onscreenshotregion), but starts with the
Show Harrix app shutter toggle on so application Windows are not concealed
before the grab.

<details>
<summary>Code:</summary>

```python
class OnScreenshotRegionKeepWindows(ActionBase):

    icon = "👀"
    icon_svg = "it__camera.svg"
    title = "Screenshot region (show app)"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("screenshot region show app")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Start region selection without hiding application Windows."""
        image = capture_region(show_preview=True, show_shutter_button=True, hide_app=False)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        message = "Screenshot copied to clipboard"
        self.add_line(message)
        self.show_toast(message, collapsed=True)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Start region selection without hiding application Windows.

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
        self.show_toast(message, collapsed=True)
```

</details>
