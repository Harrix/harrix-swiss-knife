---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `list_files_current_folder.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnListFilesCurrentFolder`](#%EF%B8%8F-class-onlistfilescurrentfolder)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnListFilesCurrentFolder`

```python
class OnListFilesCurrentFolder(ActionBase)
```

Generate a simple list of files from the current directory only.

This action prompts the user to select a folder and then creates
a simple text list of all files in the selected directory only,
without entering any subdirectories. This provides a flat view
of files at the current level.

<details>
<summary>Code:</summary>

```python
class OnListFilesCurrentFolder(ActionBase):

    icon = "📄"
    title = "List files current folder in …"

    @ActionBase.handle_exceptions("generating current folder file list")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Generate a simple list of files from the current directory only."""
        folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.list_files_simple(
            folder_path, is_ignore_hidden_folders=kwargs.get("is_ignore_hidden_folders", False), is_only_files=True
        )
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Generate a simple list of files from the current directory only.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.list_files_simple(
            folder_path, is_ignore_hidden_folders=kwargs.get("is_ignore_hidden_folders", False), is_only_files=True
        )
        self.add_line(result)
        self.show_result()
```

</details>
