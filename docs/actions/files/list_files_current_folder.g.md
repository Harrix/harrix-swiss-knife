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
- [🔧 Function `format_current_folder_listing`](#-function-format_current_folder_listing)

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
    title = "List files in … (only current folder)"

    @ActionBase.handle_exceptions("generating current folder file list")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Generate a simple list of files from the current directory only."""
        folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = format_current_folder_listing(folder_path)
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

        result = format_current_folder_listing(folder_path)
        self.add_line(result)
        self.show_result()
```

</details>

## 🔧 Function `format_current_folder_listing`

```python
def format_current_folder_listing(folder: Path) -> str
```

Return names in `folder` only: directories first (`name/`), then files.

<details>
<summary>Code:</summary>

```python
def format_current_folder_listing(folder: Path) -> str:
    try:
        items = list(folder.iterdir())
    except OSError as exc:
        return f"{folder}\n\nFailed to read folder:\n{exc}"

    lines: list[str] = []
    for item in sorted(items, key=lambda path: (not path.is_dir(), path.name.casefold())):
        if item.is_dir():
            lines.append(f"{item.name}/")
        elif item.is_file():
            lines.append(item.name)

    body = "\n".join(lines) if lines else "(empty folder)"
    return f"{folder}\n\n{body}"
```

</details>
