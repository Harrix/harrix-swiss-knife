---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `optimize.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOptimize`](#%EF%B8%8F-class-onoptimize)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `optimize_images_common`](#%EF%B8%8F-method-optimize_images_common)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnOptimize`

```python
class OnOptimize(ActionBase)
```

Run standard image optimization on all images in the temp folder.

This action executes the npm optimize script to process all images
in the temporary `images` directory using default optimization settings,
creating compressed versions in the `optimized_images` directory.

<details>
<summary>Code:</summary>

```python
class OnOptimize(ActionBase):

    icon = "🚀"
    title = "Optimize images"
    bold_title = True

    @ActionBase.handle_exceptions("image optimization")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Run standard image optimization on all images in the temp folder."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("optimization thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        return self.optimize_images_common(
            "npm run optimize convertPngToAvif=compare", h.dev.get_project_root() / "temp/optimized_images"
        )

    def optimize_images_common(self, command: str, output_folder: str | Path | None = None) -> str | None:
        """Perform common image optimization operations.

        Args:

        - `command` (`str`): The npm command to execute for optimization.
        - `output_folder` (`str | Path | None`): Optional output folder to open after optimization.

        Returns:

        - `str | None`: The result of the command execution

        """
        result = h.dev.run_command(command)

        if output_folder:
            h.file.open_file_or_folder(output_folder)

        return result

    @ActionBase.handle_exceptions("optimization thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Run standard image optimization on all images in the temp folder.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
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
            "npm run optimize convertPngToAvif=compare", h.dev.get_project_root() / "temp/optimized_images"
        )
```

</details>

### ⚙️ Method `optimize_images_common`

```python
def optimize_images_common(self, command: str, output_folder: str | Path | None = None) -> str | None
```

Perform common image optimization operations.

Args:

- `command` (`str`): The npm command to execute for optimization.
- `output_folder` (`str | Path | None`): Optional output folder to open after optimization.

Returns:

- `str | None`: The result of the command execution

<details>
<summary>Code:</summary>

```python
def optimize_images_common(self, command: str, output_folder: str | Path | None = None) -> str | None:
        result = h.dev.run_command(command)

        if output_folder:
            h.file.open_file_or_folder(output_folder)

        return result
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>
