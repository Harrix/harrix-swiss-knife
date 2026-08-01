---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `optimize_single_image.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOptimizeSingleImage`](#%EF%B8%8F-class-onoptimizesingleimage)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnOptimizeSingleImage`

```python
class OnOptimizeSingleImage(OnOptimize)
```

Optimize a single image file and replace the original in place.

<details>
<summary>Code:</summary>

```python
class OnOptimizeSingleImage(OnOptimize):

    icon = "🖼️"
    title = "Optimize one image in …"
    bold_title = False

    @ActionBase.handle_exceptions("single file optimization")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Optimize a single image file and replace the original in place."""
        filename = self.dialogs.get_open_filename(
            "Select an Image File",
            self.config["path_articles"],
            "Image Files (*.jpg *.jpeg *.webp *.png *.svg *.avif *.mp4);;All Files (*)",
        )
        if not filename:
            return

        self._source_image = Path(filename)
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("single file optimization thread")
    def in_thread(self) -> str | None:
        """Optimize the selected image in a worker thread."""
        filename = self._source_image
        target_dir = filename.parent
        stem = filename.stem
        project_root = h.dev.get_project_root()

        with TemporaryDirectory() as temp_folder:
            temp_path = Path(temp_folder)
            shutil.copy(filename, temp_path / filename.name)
            output_folder = project_root / "temp/optimized_images"
            result = self.run_optimize_images(
                temp_path,
                output_folder,
            )

            for ext in (".avif", ".png", ".svg"):
                output_file = output_folder / (stem + ext)
                if output_file.exists():
                    target_path = target_dir / (stem + ext)
                    shutil.copy2(output_file, target_path)
                    if target_path != filename and filename.exists():
                        filename.unlink()
                    self.result_folder = target_dir
                    break

        return result

    @ActionBase.handle_exceptions("single file optimization thread completion")
    def thread_after(self, result: Any) -> None:
        """Show toast and result dialog after a single-image optimize."""
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Optimize a single image file and replace the original in place.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        filename = self.dialogs.get_open_filename(
            "Select an Image File",
            self.config["path_articles"],
            "Image Files (*.jpg *.jpeg *.webp *.png *.svg *.avif *.mp4);;All Files (*)",
        )
        if not filename:
            return

        self._source_image = Path(filename)
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Optimize the selected image in a worker thread.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        filename = self._source_image
        target_dir = filename.parent
        stem = filename.stem
        project_root = h.dev.get_project_root()

        with TemporaryDirectory() as temp_folder:
            temp_path = Path(temp_folder)
            shutil.copy(filename, temp_path / filename.name)
            output_folder = project_root / "temp/optimized_images"
            result = self.run_optimize_images(
                temp_path,
                output_folder,
            )

            for ext in (".avif", ".png", ".svg"):
                output_file = output_folder / (stem + ext)
                if output_file.exists():
                    target_path = target_dir / (stem + ext)
                    shutil.copy2(output_file, target_path)
                    if target_path != filename and filename.exists():
                        filename.unlink()
                    self.result_folder = target_dir
                    break

        return result
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and result dialog after a single-image optimize.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>
