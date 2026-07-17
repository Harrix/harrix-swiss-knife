---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `list_files_simple_ignore_hidden_folders.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnListFilesSimpleIgnoreHiddenFolders`](#️-class-onlistfilessimpleignorehiddenfolders)
  - [⚙️ Method `execute`](#️-method-execute)

</details>

## 🏛️ Class `OnListFilesSimpleIgnoreHiddenFolders`

```python
class OnListFilesSimpleIgnoreHiddenFolders(OnListFilesSimple)
```

Generate a simple file list excluding hidden folders.

This action extends OnListFilesSimple by automatically setting the
is_ignore_hidden_folders flag to true, creating a cleaner file list
that omits hidden directories and files (those starting with a dot
or matching common ignore patterns like `.git`, `__pycache__`, etc.).

<details>
<summary>Code:</summary>

```python
class OnListFilesSimpleIgnoreHiddenFolders(OnListFilesSimple):

    icon = "📄"
    title = "List files simple in … (ignore hidden folders)"

    @ActionBase.handle_exceptions("generating file list ignoring hidden folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Generate a simple file list excluding hidden folders."""
        super().execute(*args, is_ignore_hidden_folders=True, **kwargs)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Generate a simple file list excluding hidden folders.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:
        super().execute(*args, is_ignore_hidden_folders=True, **kwargs)
```

</details>
