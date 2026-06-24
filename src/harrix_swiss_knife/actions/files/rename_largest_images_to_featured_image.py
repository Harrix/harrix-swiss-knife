"""Actions for file operations and management of directory structures."""

from __future__ import annotations

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnRenameLargestImagesToFeaturedImage(ActionBase):
    """Rename the largest image in each folder to featured_image.

    This action prompts the user to select a folder and then identifies
    the largest image file in each subfolder, renaming it to `featured_image`
    while preserving its original extension. This helps standardize thumbnail
    or preview images across multiple directories.
    """

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
