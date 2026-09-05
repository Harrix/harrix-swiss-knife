---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `record_region.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnRecordRegion`](#%EF%B8%8F-class-onrecordregion)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnRecordRegion`

```python
class OnRecordRegion(ActionBase)
```

Record a screen region to MP4 (ShareX-like).

Select a region, adjust the frame (move/resize), choose audio, then record
immediately or after a configurable countdown. Stop saves `temp/videos`.

<details>
<summary>Code:</summary>

```python
class OnRecordRegion(ActionBase):

    icon = "🎥"
    title = "Record region"
    bold_title = False
    quick_launcher = True

    @ActionBase.handle_exceptions("record region")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open region selection, then the recording frame."""

        def on_finished(path: object) -> None:
            message = f"Recording saved: {path}"
            self.add_line(message)
            self.show_toast(message)

        started = record_region(on_finished=on_finished)
        if not started:
            self.add_line("Screen recording cancelled or unavailable")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Open region selection, then the recording frame.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002

        def on_finished(path: object) -> None:
            message = f"Recording saved: {path}"
            self.add_line(message)
            self.show_toast(message)

        started = record_region(on_finished=on_finished)
        if not started:
            self.add_line("Screen recording cancelled or unavailable")
```

</details>
