---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `beautify_and_optimize_icons.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnBeautifyAndOptimizeIcons`](#%EF%B8%8F-class-onbeautifyandoptimizeicons)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnBeautifyAndOptimizeIcons`

```python
class OnBeautifyAndOptimizeIcons(ActionBase)
```

Beautify icon Markdown notes and optimize SVG files in place.

Uses the same job as Vector Icons → File → Beautify and optimize icons:
`Beautify MD` on `icons/`, then SVG optimize (the existing optimize
action) for every `.svg` under that tree.

<details>
<summary>Code:</summary>

```python
class OnBeautifyAndOptimizeIcons(ActionBase):

    icon = "💎"
    title = "Beautify and optimize icons"

    @ActionBase.handle_exceptions("beautifying and optimizing icons")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Beautify Markdown and optimize SVGs in the selected repo."""
        self.folder_path = pick_vector_icons_repo(self)
        if self.folder_path is None:
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("beautifying and optimizing icons thread")
    def in_thread(self) -> None:
        """Run Beautify MD and SVG optimize."""
        if self.folder_path is None:
            return
        self.add_line(beautify_and_optimize_icons(self.folder_path))

    @ActionBase.handle_exceptions("beautifying and optimizing icons thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and the beautify/optimize report."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Beautify Markdown and optimize SVGs in the selected repo.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = pick_vector_icons_repo(self)
        if self.folder_path is None:
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> None
```

Run Beautify MD and SVG optimize.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> None:
        if self.folder_path is None:
            return
        self.add_line(beautify_and_optimize_icons(self.folder_path))
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and the beautify/optimize report.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>
