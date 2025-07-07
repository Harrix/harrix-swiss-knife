---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `actions_file.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Class `OnAllFilesToParentFolder`](#class-onallfilestoparentfolder)
  - [Method `execute`](#method-execute)
- [Class `OnBlockDisks`](#class-onblockdisks)
  - [Method `execute`](#method-execute-1)
- [Class `OnCheckFeaturedImage`](#class-oncheckfeaturedimage)
  - [Method `execute`](#method-execute-2)
- [Class `OnCheckFeaturedImageInFolders`](#class-oncheckfeaturedimageinfolders)
  - [Method `execute`](#method-execute-3)
- [Class `OnOpenCameraUploads`](#class-onopencamerauploads)
  - [Method `execute`](#method-execute-4)
- [Class `OnTreeViewFolder`](#class-ontreeviewfolder)
  - [Method `execute`](#method-execute-5)
- [Class `OnTreeViewFolderIgnoreHiddenFolders`](#class-ontreeviewfolderignorehiddenfolders)
  - [Method `execute`](#method-execute-6)
- [Class `RenameLargestImagesToFeaturedImage`](#class-renamelargestimagestofeaturedimage)
  - [Method `execute`](#method-execute-7)

</details>

## Class `OnAllFilesToParentFolder`

```python
class OnAllFilesToParentFolder(action_base.ActionBase)
```

Move and flatten files from nested directories.

This action prompts the user to select a folder and then moves all files
from its nested subdirectories directly into the selected parent folder,
effectively flattening the directory structure while preserving all files.

<details>
<summary>Code:</summary>

```python
class OnAllFilesToParentFolder(action_base.ActionBase):

    icon = "🗂️"
    title = "Moves and flattens files from nested folders"

    @action_base.ActionBase.handle_exceptions("moving files to parent folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.all_to_parent_folder(folder_path)
        self.add_line(result)
        self.show_result()
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.all_to_parent_folder(folder_path)
        self.add_line(result)
        self.show_result()
```

</details>

## Class `OnBlockDisks`

```python
class OnBlockDisks(action_base.ActionBase)
```

Lock BitLocker-encrypted drives.

This action locks all drives specified in the configuration's `block_drives` list
using BitLocker encryption, forcibly dismounting them if necessary to ensure
secure protection of the drive contents.

<details>
<summary>Code:</summary>

```python
class OnBlockDisks(action_base.ActionBase):

    icon = "🔒"
    title = "Block disks"

    @action_base.ActionBase.handle_exceptions("blocking disks")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        commands = "\n".join([f"manage-bde -lock {drive}: -ForceDismount" for drive in self.config["block_drives"]])
        result = h.dev.run_powershell_script_as_admin(commands)
        self.add_line(result)
        self.show_result()
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        commands = "\n".join([f"manage-bde -lock {drive}: -ForceDismount" for drive in self.config["block_drives"]])
        result = h.dev.run_powershell_script_as_admin(commands)
        self.add_line(result)
        self.show_result()
```

</details>

## Class `OnCheckFeaturedImage`

```python
class OnCheckFeaturedImage(action_base.ActionBase)
```

Check for featured image files in a selected folder.

This action prompts the user to select a folder and then checks for the presence
of files named `featured_image` with any extension, which are commonly used
as preview images or thumbnails for the folder contents.

<details>
<summary>Code:</summary>

```python
class OnCheckFeaturedImage(action_base.ActionBase):

    icon = "✅"
    title = "Check featured_image in …"

    @action_base.ActionBase.handle_exceptions("checking featured image")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.check_featured_image(folder_path)[1]
        self.add_line(result)
        self.show_result()
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.check_featured_image(folder_path)[1]
        self.add_line(result)
        self.show_result()
```

</details>

## Class `OnCheckFeaturedImageInFolders`

```python
class OnCheckFeaturedImageInFolders(action_base.ActionBase)
```

Check for featured image files in all configured folders.

This action automatically checks all directories specified in the
paths_with_featured_image configuration setting for the presence of
files named `featured_image` with any extension, providing a status
report for each directory.

<details>
<summary>Code:</summary>

```python
class OnCheckFeaturedImageInFolders(action_base.ActionBase):

    icon = "✅"
    title = "Check featured_image"

    @action_base.ActionBase.handle_exceptions("checking featured image in folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        for path in self.config["paths_with_featured_image"]:
            result = h.file.check_featured_image(path)[1]
            self.add_line(result)
        self.show_result()
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

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

## Class `OnOpenCameraUploads`

```python
class OnOpenCameraUploads(action_base.ActionBase)
```

Open all Camera Uploads folders.

This action opens all directories specified in the `paths_camera_uploads`
configuration setting in the system's file explorer, providing quick access
to folders where camera photos are typically uploaded or stored.

<details>
<summary>Code:</summary>

```python
class OnOpenCameraUploads(action_base.ActionBase):

    icon = "📸"
    title = "Open Camera Uploads"

    @action_base.ActionBase.handle_exceptions("opening camera uploads")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        for path in self.config["paths_camera_uploads"]:
            h.file.open_file_or_folder(Path(path))
        self.add_line('The folders from "Camera Uploads" is opened.')
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        for path in self.config["paths_camera_uploads"]:
            h.file.open_file_or_folder(Path(path))
        self.add_line('The folders from "Camera Uploads" is opened.')
```

</details>

## Class `OnTreeViewFolder`

```python
class OnTreeViewFolder(action_base.ActionBase)
```

Generate a text-based tree view of a folder structure.

This action prompts the user to select a folder and then creates
a hierarchical text representation of its directory structure,
similar to the output of the 'tree' command in command-line interfaces.

<details>
<summary>Code:</summary>

```python
class OnTreeViewFolder(action_base.ActionBase):

    icon = "├"
    title = "Tree view of a folder"

    @action_base.ActionBase.handle_exceptions("generating tree view")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.tree_view_folder(
            folder_path, is_ignore_hidden_folders=kwargs.get("is_ignore_hidden_folders", False)
        )
        self.add_line(result)
        self.show_result()
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.tree_view_folder(
            folder_path, is_ignore_hidden_folders=kwargs.get("is_ignore_hidden_folders", False)
        )
        self.add_line(result)
        self.show_result()
```

</details>

## Class `OnTreeViewFolderIgnoreHiddenFolders`

```python
class OnTreeViewFolderIgnoreHiddenFolders(action_base.ActionBase)
```

Generate a tree view excluding hidden folders.

This action extends OnTreeViewFolder by automatically setting the
is_ignore_hidden_folders flag to true, creating a cleaner tree view
that omits hidden directories (those starting with a dot).

<details>
<summary>Code:</summary>

```python
class OnTreeViewFolderIgnoreHiddenFolders(action_base.ActionBase):

    icon = "├"
    title = "Tree view of a folder (ignore hidden folders)"

    @action_base.ActionBase.handle_exceptions("generating tree view ignoring hidden folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        OnTreeViewFolder().execute(is_ignore_hidden_folders=True)
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        OnTreeViewFolder().execute(is_ignore_hidden_folders=True)
```

</details>

## Class `RenameLargestImagesToFeaturedImage`

```python
class RenameLargestImagesToFeaturedImage(action_base.ActionBase)
```

Rename the largest image in each folder to featured_image.

This action prompts the user to select a folder and then identifies
the largest image file in each subfolder, renaming it to `featured_image`
while preserving its original extension. This helps standardize thumbnail
or preview images across multiple directories.

<details>
<summary>Code:</summary>

```python
class RenameLargestImagesToFeaturedImage(action_base.ActionBase):

    icon = "🖲️"
    title = "Rename largest images to featured_image in …"

    @action_base.ActionBase.handle_exceptions("renaming largest images")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.rename_largest_images_to_featured(folder_path)
        self.add_line(result)
        self.show_result()
```

</details>

### Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.rename_largest_images_to_featured(folder_path)
        self.add_line(result)
        self.show_result()
```

</details>
