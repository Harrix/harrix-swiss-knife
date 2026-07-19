---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `tree_view_folder_ignore_hidden_folders.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnTreeViewFolderIgnoreHiddenFolders`](#️-class-ontreeviewfolderignorehiddenfolders)
  - [⚙️ Method `execute`](#️-method-execute)

</details>

## 🏛️ Class `OnTreeViewFolderIgnoreHiddenFolders`

```python
class OnTreeViewFolderIgnoreHiddenFolders(OnTreeViewFolder)
```

Generate a tree view excluding hidden folders.

This action extends `OnTreeViewFolder` by automatically setting the
`is_ignore_hidden_folders` flag to `True`, creating a cleaner tree view
that omits hidden directories (those starting with a dot).

<details>
<summary>Code:</summary>

```python
class OnTreeViewFolderIgnoreHiddenFolders(OnTreeViewFolder):

    icon = "├"
    title = "Tree view in … (ignore hidden folders)"

    @ActionBase.handle_exceptions("generating tree view ignoring hidden folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:
        """Generate a tree view excluding hidden folders."""
        super().execute(*args, is_ignore_hidden_folders=True, **kwargs)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Generate a tree view excluding hidden folders.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:
        super().execute(*args, is_ignore_hidden_folders=True, **kwargs)
```

</details>
