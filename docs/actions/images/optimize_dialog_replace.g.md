---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `optimize_dialog_replace.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOptimizeDialogReplace`](#️-class-onoptimizedialogreplace)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `in_thread`](#️-method-in_thread)
  - [⚙️ Method `thread_after`](#️-method-thread_after)

</details>

## 🏛️ Class `OnOptimizeDialogReplace`

```python
class OnOptimizeDialogReplace(OnOptimize)
```

Optimize images in a selected folder and replace the originals.

Allows the user to select a folder containing images, optimizes all images,
and replaces the original files with their optimized versions.

<details>
<summary>Code:</summary>

```python
class OnOptimizeDialogReplace(OnOptimize):

    icon = "⬆️"
    title = "Optimize images in … and replace"
    bold_title = False

    @ActionBase.handle_exceptions("folder image optimization with replacement")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Optimize images in a selected folder and replace the originals."""
        self.folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("folder optimization thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return None

        output_folder = self.folder_path / "temp"
        result = self.run_optimize_images(
            self.folder_path,
            output_folder,
            open_output=False,
        )

        for item in self.folder_path.iterdir():
            if item.is_file():
                item.unlink()

        for item in output_folder.iterdir():
            if item.is_file() or item.is_symlink():
                shutil.copy2(item, self.folder_path / item.name)

        shutil.rmtree(output_folder)

        return result

    @ActionBase.handle_exceptions("folder optimization thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        if self.folder_path is None:
            return
        h.file.open_file_or_folder(self.folder_path)
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Optimize images in a selected folder and replace the originals.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_articles"])
        if not self.folder_path:
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
        if self.folder_path is None:
            return None

        output_folder = self.folder_path / "temp"
        result = self.run_optimize_images(
            self.folder_path,
            output_folder,
            open_output=False,
        )

        for item in self.folder_path.iterdir():
            if item.is_file():
                item.unlink()

        for item in output_folder.iterdir():
            if item.is_file() or item.is_symlink():
                shutil.copy2(item, self.folder_path / item.name)

        shutil.rmtree(output_folder)

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
        if self.folder_path is None:
            return
        h.file.open_file_or_folder(self.folder_path)
        self.show_toast("Optimize completed")
        self.add_line(result)
        self.show_result()
```

</details>
