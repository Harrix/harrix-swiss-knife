---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `rename_largest_images_to_featured_image.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnRenameLargestImagesToFeaturedImage`](#️-class-onrenamelargestimagestofeaturedimage)
  - [⚙️ Method `execute`](#️-method-execute)

</details>

## 🏛️ Class `OnRenameLargestImagesToFeaturedImage`

```python
class OnRenameLargestImagesToFeaturedImage(ActionBase)
```

Rename the largest image in each folder to featured_image.

This action prompts the user to select a folder and then identifies
the largest image file in each subfolder, renaming it to `featured_image`
while preserving its original extension. This helps standardize thumbnail
or preview images across multiple directories.

<details>
<summary>Code:</summary>

```python
class OnRenameLargestImagesToFeaturedImage(ActionBase):

    icon = "🖲️"
    title = "Rename largest images to featured_image in …"

    @ActionBase.handle_exceptions("renaming largest images")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Rename the largest image in each folder to featured_image."""
        if not self.show_rename_preview(
            """In each subfolder, finds the largest image file and renames it to featured_image,
preserving the original extension. The main selected folder itself is not processed.
Existing featured_image files are not overwritten.

Example:

  photos/vacation/IMG_1234.jpg  (largest in folder)
→ photos/vacation/featured_image.jpg"""
        ):
            return

        folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.rename_largest_images_to_featured(folder_path)
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Rename the largest image in each folder to featured_image.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if not self.show_rename_preview(
            """In each subfolder, finds the largest image file and renames it to featured_image,
preserving the original extension. The main selected folder itself is not processed.
Existing featured_image files are not overwritten.

Example:

  photos/vacation/IMG_1234.jpg  (largest in folder)
→ photos/vacation/featured_image.jpg"""
        ):
            return

        folder_path = self.dialogs.get_existing_directory("Select folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.rename_largest_images_to_featured(folder_path)
        self.add_line(result)
        self.show_result()
```

</details>
