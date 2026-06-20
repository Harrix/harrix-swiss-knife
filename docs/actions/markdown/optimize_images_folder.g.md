---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `optimize_images_folder.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOptimizeImagesFolder`](#️-class-onoptimizeimagesfolder)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `in_thread`](#️-method-in_thread)

</details>

## 🏛️ Class `OnOptimizeImagesFolder`

```python
class OnOptimizeImagesFolder(ActionBase)
```

Optimize images in Markdown files with PNG/AVIF size comparison.

<details>
<summary>Code:</summary>

```python
class OnOptimizeImagesFolder(ActionBase):

    icon = "🖼️"
    title = "Optimize images in MD in …"

    @ActionBase.handle_exceptions("optimizing images with size comparison")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Optimize images in Markdown files with PNG/AVIF size comparison."""
        self.folder_path = self.dialogs.get_existing_directory(
            "Select folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after_show_result, self.title)

    @ActionBase.handle_exceptions("optimizing images with size comparison thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        results = []
        for md_file in sorted(Path(self.folder_path).rglob("*.md")):
            if md_file.name.endswith(".g.md"):
                continue
            results.append(
                optimize_images_in_md_file(md_file, is_convert_png_to_avif=False, is_compare_png_avif_sizes=True)
            )
        self.add_line("\n".join(results))
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Optimize images in Markdown files with PNG/AVIF size comparison.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.dialogs.get_existing_directory(
            "Select folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after_show_result, self.title)
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
        if self.folder_path is None:
            return
        results = []
        for md_file in sorted(Path(self.folder_path).rglob("*.md")):
            if md_file.name.endswith(".g.md"):
                continue
            results.append(
                optimize_images_in_md_file(md_file, is_convert_png_to_avif=False, is_compare_png_avif_sizes=True)
            )
        self.add_line("\n".join(results))
```

</details>
