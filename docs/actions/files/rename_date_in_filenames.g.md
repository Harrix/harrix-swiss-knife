---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `rename_date_in_filenames.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnRenameDateInFilenames`](#%EF%B8%8F-class-onrenamedateinfilenames)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnRenameDateInFilenames`

```python
class OnRenameDateInFilenames(ActionBase)
```

Rename DD.MM.YYYY date fragments in filenames to YYYY.MM.DD.

This action prompts the user to select a folder and recursively renames files
whose names contain a valid date in DD.MM.YYYY format. Files without such a date
or already using YYYY.MM.DD are left unchanged.

<details>
<summary>Code:</summary>

```python
class OnRenameDateInFilenames(ActionBase):

    icon = "📅"
    title = "Rename date in filenames DD.MM.YYYY → YYYY.MM.DD in …"

    @ActionBase.handle_exceptions("renaming date in filenames")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Rename DD.MM.YYYY date fragments in filenames to YYYY.MM.DD."""
        if not self.show_rename_preview(
            """Recursively renames files whose names contain a valid date in DD.MM.YYYY format.
Files without such a date or already using YYYY.MM.DD are left unchanged.
Skips rename when the target filename already exists.

Example:

  CamScanner 31.07.2025 21.23_485.jpg
→ CamScanner 2025.07.31 21.23_485.jpg"""
        ):
            return

        self.folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if self.folder_path is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("renaming date in filenames thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return

        self.add_line(f"🔵 Starting date rename for path: {self.folder_path}")
        result = h.file.rename_files_date_dd_mm_yyyy_to_yyyy_mm_dd(self.folder_path)
        self.add_line(result)

    @ActionBase.handle_exceptions("renaming date in filenames thread completion")
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

Rename DD.MM.YYYY date fragments in filenames to YYYY.MM.DD.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if not self.show_rename_preview(
            """Recursively renames files whose names contain a valid date in DD.MM.YYYY format.
Files without such a date or already using YYYY.MM.DD are left unchanged.
Skips rename when the target filename already exists.

Example:

  CamScanner 31.07.2025 21.23_485.jpg
→ CamScanner 2025.07.31 21.23_485.jpg"""
        ):
            return

        self.folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
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

        self.add_line(f"🔵 Starting date rename for path: {self.folder_path}")
        result = h.file.rename_files_date_dd_mm_yyyy_to_yyyy_mm_dd(self.folder_path)
        self.add_line(result)
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
