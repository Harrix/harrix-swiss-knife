---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `extract_zip_archives.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnExtractZipArchives`](#%EF%B8%8F-class-onextractziparchives)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnExtractZipArchives`

```python
class OnExtractZipArchives(ActionBase)
```

Extract all ZIP archives from a selected folder.

This action prompts the user to select a folder and then processes all ZIP files
within it, extracting their contents directly to the same directory where each
archive is located. After successful extraction, the original archive files
are deleted.

The extraction process handles nested directory structures and preserves the
original file organization from within the archives. Each ZIP file is processed
independently, so if one archive fails to extract, others will still be processed.

This provides a one-click solution for bulk extraction of ZIP archives while
maintaining clean folder organization by removing the original archive files.

<details>
<summary>Code:</summary>

```python
class OnExtractZipArchives(ActionBase):

    icon = "📦"
    title = "Extract ZIP archives in …"

    @ActionBase.handle_exceptions("extracting ZIP archives")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Extract all ZIP archives from a selected folder."""
        self.folder_path = self.dialogs.get_existing_directory(
            "Select folder with ZIP archives", self.config["path_3d"]
        )
        if self.folder_path is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("extracting ZIP archives thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return

        self.add_line(f"🔵 Starting ZIP archive extraction for path: {self.folder_path}")
        self.add_line(h.file.apply_func(self.folder_path, ".zip", h.file.extract_zip_archive))

    @ActionBase.handle_exceptions("extracting ZIP archives thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Extract all ZIP archives from a selected folder.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.dialogs.get_existing_directory(
            "Select folder with ZIP archives", self.config["path_3d"]
        )
        if self.folder_path is None:
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
            return

        self.add_line(f"🔵 Starting ZIP archive extraction for path: {self.folder_path}")
        self.add_line(h.file.apply_func(self.folder_path, ".zip", h.file.extract_zip_archive))
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
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>
