"""Actions for file operations and management of directory structures."""

from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife import action_base


class OnAllFilesToParentFolder(action_base.ActionBase):
    """Move and flatten files from nested directories.

    This action prompts the user to select a folder and then moves all files
    from its nested subdirectories directly into the selected parent folder,
    effectively flattening the directory structure while preserving all files.
    """

    icon = "🗂️"
    title = "Moves and flattens files from nested folders"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.all_to_parent_folder(folder_path)
        self.add_line(result)
        self.show_result()


class OnBlockDisks(action_base.ActionBase):
    """Lock BitLocker-encrypted drives.

    This action locks all drives specified in the configuration's `block_drives` list
    using BitLocker encryption, forcibly dismounting them if necessary to ensure
    secure protection of the drive contents.
    """

    icon = "🔒"
    title = "Block disks"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        commands = "\n".join([f"manage-bde -lock {drive}: -ForceDismount" for drive in self.config["block_drives"]])
        result = h.dev.run_powershell_script_as_admin(commands)
        self.add_line(result)
        self.show_result()


class OnCheckFeaturedImage(action_base.ActionBase):
    """Check for featured image files in a selected folder.

    This action prompts the user to select a folder and then checks for the presence
    of files named `featured_image` with any extension, which are commonly used
    as preview images or thumbnails for the folder contents.
    """

    icon = "✅"
    title = "Check featured_image in …"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        try:
            result = h.file.check_featured_image(folder_path)[1]
        except Exception as e:
            result = f"❌ Error: {e}"
        self.add_line(result)
        self.show_result()


class OnCheckFeaturedImageInFolders(action_base.ActionBase):
    """Check for featured image files in all configured folders.

    This action automatically checks all directories specified in the
    paths_with_featured_image configuration setting for the presence of
    files named `featured_image` with any extension, providing a status
    report for each directory.
    """

    icon = "✅"
    title = "Check featured_image"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        for path in self.config["paths_with_featured_image"]:
            try:
                result = h.file.check_featured_image(path)[1]
            except Exception as e:
                result = f"❌ Error: {e}"
            self.add_line(result)
        self.show_result()


class OnOpenCameraUploads(action_base.ActionBase):
    """Open all Camera Uploads folders.

    This action opens all directories specified in the `paths_camera_uploads`
    configuration setting in the system's file explorer, providing quick access
    to folders where camera photos are typically uploaded or stored.
    """

    icon = "📸"
    title = "Open Camera Uploads"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        for path in self.config["paths_camera_uploads"]:
            h.file.open_file_or_folder(Path(path))
        self.add_line('The folders from "Camera Uploads" is opened.')


class OnTreeViewFolder(action_base.ActionBase):
    """Generate a text-based tree view of a folder structure.

    This action prompts the user to select a folder and then creates
    a hierarchical text representation of its directory structure,
    similar to the output of the 'tree' command in command-line interfaces.
    """

    icon = "├"
    title = "Tree view of a folder"

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


class OnTreeViewFolderIgnoreHiddenFolders(action_base.ActionBase):
    """Generate a tree view excluding hidden folders.

    This action extends OnTreeViewFolder by automatically setting the
    is_ignore_hidden_folders flag to true, creating a cleaner tree view
    that omits hidden directories (those starting with a dot).
    """

    icon = "├"
    title = "Tree view of a folder (ignore hidden folders)"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        OnTreeViewFolder().execute(is_ignore_hidden_folders=True)


class RenameLargestImagesToFeaturedImage(action_base.ActionBase):
    """Rename the largest image in each folder to featured_image.

    This action prompts the user to select a folder and then identifies
    the largest image file in each subfolder, renaming it to `featured_image`
    while preserving its original extension. This helps standardize thumbnail
    or preview images across multiple directories.
    """

    icon = "🖲️"
    title = "Rename largest images to featured_image in …"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        try:
            result = h.file.rename_largest_images_to_featured(folder_path)
        except Exception as e:
            result = f"❌ Error: {e}"
        self.add_line(result)
        self.show_result()
