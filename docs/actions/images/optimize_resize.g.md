---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `optimize_resize.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOptimizeResize`](#%EF%B8%8F-class-onoptimizeresize)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)

</details>

## 🏛️ Class `OnOptimizeResize`

```python
class OnOptimizeResize(OnOptimize)
```

Resize and optimize images (asks for max size in pixels).

<details>
<summary>Code:</summary>

```python
class OnOptimizeResize(OnOptimize):

    icon = "↔️"
    title = "Resize and optimize images"

    @ActionBase.handle_exceptions("resize and optimize")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Resize and optimize images (asks for max size in pixels)."""
        self.max_size = self.dialogs.get_text_input("Max size", "Input max image size in pixels", "1024")

        if self.max_size is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("resize and optimize thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return self.optimize_images_common(
            f"npm run optimize convertPngToAvif=compare maxSize={self.max_size}",
            h.dev.get_project_root() / "temp/optimized_images",
        )
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Resize and optimize images (asks for max size in pixels).

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.max_size = self.dialogs.get_text_input("Max size", "Input max image size in pixels", "1024")

        if self.max_size is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        return self.optimize_images_common(
            f"npm run optimize convertPngToAvif=compare maxSize={self.max_size}",
            h.dev.get_project_root() / "temp/optimized_images",
        )
```

</details>
