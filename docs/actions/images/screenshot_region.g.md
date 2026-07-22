---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `screenshot_region.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnScreenshotRegion`](#%EF%B8%8F-class-onscreenshotregion)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnScreenshotRegion`

```python
class OnScreenshotRegion(ActionBase)
```

Capture a screen region to the clipboard (ShareX-like flow).

<details>
<summary>Code:</summary>

```python
class OnScreenshotRegion(ActionBase):

    icon = "📷"
    title = "Screenshot region"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("screenshot region")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Hide app Windows, select a region, copy it, and show a preview dialog."""
        image = capture_region(show_preview=True, show_shutter_button=True)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        self.add_line("Screenshot copied to clipboard")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Hide app Windows, select a region, copy it, and show a preview dialog.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        image = capture_region(show_preview=True, show_shutter_button=True)
        if image is None:
            self.add_line("Screenshot cancelled")
            return
        self.add_line("Screenshot copied to clipboard")
```

</details>
