---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `list_files_simple.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnListFilesSimple`](#%EF%B8%8F-class-onlistfilessimple)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnListFilesSimple`

```python
class OnListFilesSimple(ActionBase)
```

Generate a simple list of all files in a directory structure.

This action prompts the user to select a folder and then creates
a simple text list of all files with their relative paths,
similar to a flat file listing without directory tree structure.

<details>
<summary>Code:</summary>

```python
class OnListFilesSimple(ActionBase):

    icon = "📄"
    title = "List files simple in …"

    @ActionBase.handle_exceptions("generating file list")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Generate a simple list of all files in a directory structure."""
        folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.list_files_simple(
            folder_path, is_ignore_hidden_folders=kwargs.get("is_ignore_hidden_folders", False)
        )
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Generate a simple list of all files in a directory structure.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.list_files_simple(
            folder_path, is_ignore_hidden_folders=kwargs.get("is_ignore_hidden_folders", False)
        )
        self.add_line(result)
        self.show_result()
```

</details>
