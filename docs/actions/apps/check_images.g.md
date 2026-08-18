---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `check_images.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnCheckImages`](#%EF%B8%8F-class-oncheckimages)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnCheckImages`

```python
class OnCheckImages(ActionBase)
```

Check icon filenames, folder/category match, and Markdown notes.

Uses the same checks as Vector Icons → File → Check images: file names
must match the family ID, category folders must match the family-id
prefix and YAML `categories`, then `Check MD` runs on `icons/`.

<details>
<summary>Code:</summary>

```python
class OnCheckImages(ActionBase):

    icon = "🚧"
    title = "Check images"

    @ActionBase.handle_exceptions("checking images")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Check the selected Vector Icons repository."""
        self.folder_path = pick_vector_icons_repo(self)
        if self.folder_path is None:
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("checking images thread")
    def in_thread(self) -> None:
        """Run filename, folder, category, and Markdown checks."""
        if self.folder_path is None:
            return
        self.add_line(check_icon_repo(self.folder_path))

    @ActionBase.handle_exceptions("checking images thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and the check report."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Check the selected Vector Icons repository.

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

Run filename, folder, category, and Markdown checks.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> None:
        if self.folder_path is None:
            return
        self.add_line(check_icon_repo(self.folder_path))
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and the check report.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>
