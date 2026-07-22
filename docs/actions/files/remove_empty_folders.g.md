---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `remove_empty_folders.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnRemoveEmptyFolders`](#%EF%B8%8F-class-onremoveemptyfolders)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnRemoveEmptyFolders`

```python
class OnRemoveEmptyFolders(ActionBase)
```

Remove all empty folders recursively.

This action prompts the user to select a folder and then removes all empty
folders recursively from the selected directory.

<details>
<summary>Code:</summary>

```python
class OnRemoveEmptyFolders(ActionBase):

    icon = "🗑️"
    title = "Remove empty folders in …"

    @ActionBase.handle_exceptions("removing empty folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Remove all empty folders recursively."""
        self.folder_path = self.dialogs.get_existing_directory(
            "Select folder to clean empty folders", self.config["path_3d"]
        )
        if self.folder_path is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("removing empty folders thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return

        self.add_line(f"🔵 Starting empty folder cleanup for path: {self.folder_path}")
        result = h.file.remove_empty_folders(self.folder_path)
        self.add_line(result)

    @ActionBase.handle_exceptions("removing empty folders thread completion")
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

Remove all empty folders recursively.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.dialogs.get_existing_directory(
            "Select folder to clean empty folders", self.config["path_3d"]
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

        self.add_line(f"🔵 Starting empty folder cleanup for path: {self.folder_path}")
        result = h.file.remove_empty_folders(self.folder_path)
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
