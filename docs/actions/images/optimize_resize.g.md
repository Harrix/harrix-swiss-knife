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
    title = "Resize and optimize images…"
    max_size: int

    @ActionBase.handle_exceptions("resize and optimize")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Resize and optimize images (asks for max size in pixels)."""
        max_size_text = self.dialogs.get_text_input("Max size", "Input max image size in pixels", "1024")

        if max_size_text is None:
            return

        self.max_size = int(max_size_text)
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("resize and optimize thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        project_root = h.dev.get_project_root()
        return self.run_optimize_images(
            project_root / "temp/images",
            project_root / "temp/optimized_images",
            max_size=self.max_size,
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
        max_size_text = self.dialogs.get_text_input("Max size", "Input max image size in pixels", "1024")

        if max_size_text is None:
            return

        self.max_size = int(max_size_text)
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
        project_root = h.dev.get_project_root()
        return self.run_optimize_images(
            project_root / "temp/images",
            project_root / "temp/optimized_images",
            max_size=self.max_size,
        )
```

</details>
