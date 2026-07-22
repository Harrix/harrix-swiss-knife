---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `check_featured_image_in_folders.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnCheckFeaturedImageInFolders`](#%EF%B8%8F-class-oncheckfeaturedimageinfolders)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnCheckFeaturedImageInFolders`

```python
class OnCheckFeaturedImageInFolders(ActionBase)
```

Check for featured image files in all configured folders.

This action automatically checks all directories specified in the
paths_with_featured_image configuration setting for the presence of
files named `featured_image` with any extension, providing a status
report for each directory.

<details>
<summary>Code:</summary>

```python
class OnCheckFeaturedImageInFolders(ActionBase):

    icon = "✅"
    title = "Check featured_image"

    @ActionBase.handle_exceptions("checking featured image in folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Check for featured image files in all configured folders."""
        for path in self.config["paths_with_featured_image"]:
            result = h.file.check_featured_image(path)[1]
            self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Check for featured image files in all configured folders.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        for path in self.config["paths_with_featured_image"]:
            result = h.file.check_featured_image(path)[1]
            self.add_line(result)
        self.show_result()
```

</details>
