"""Actions for file operations and management of directory structures."""

from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnAllFilesToParentFolder(ActionBase):
    """Move and flatten files from nested directories.

    This action prompts the user to select a folder and then moves all files
    from its nested subdirectories directly into the selected parent folder,
    effectively flattening the directory structure while preserving all files.
    """

    icon = "🗂️"
    title = "Moves and flattens files from nested folders"

    @ActionBase.handle_exceptions("moving files to parent folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.all_to_parent_folder(folder_path)
        self.add_line(result)
        self.show_result()


class OnBlockDisks(ActionBase):
    """Lock BitLocker-encrypted drives.

    This action locks all drives specified in the configuration's `block_drives` list
    using BitLocker encryption, forcibly dismounting them if necessary to ensure
    secure protection of the drive contents.
    """

    icon = "🔒"
    title = "Block disks"

    @ActionBase.handle_exceptions("blocking disks")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        commands = "\n".join([f"manage-bde -lock {drive}: -ForceDismount" for drive in self.config["block_drives"]])
        result = h.dev.run_powershell_script_as_admin(commands)
        self.add_line(result)
        self.show_result()


class OnCheckFeaturedImage(ActionBase):
    """Check for featured image files in a selected folder.

    This action prompts the user to select a folder and then checks for the presence
    of files named `featured_image` with any extension, which are commonly used
    as preview images or thumbnails for the folder contents.
    """

    icon = "✅"
    title = "Check featured_image in …"

    @ActionBase.handle_exceptions("checking featured image")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.check_featured_image(folder_path)[1]
        self.add_line(result)
        self.show_result()


class OnCheckFeaturedImageInFolders(ActionBase):
    """Check for featured image files in all configured folders.

    This action automatically checks all directories specified in the
    paths_with_featured_image configuration setting for the presence of
    files named `featured_image` with any extension, providing a status
    report for each directory.
    """

    icon = "✅"
    title = "Check featured_image"

    @ActionBase.handle_exceptions("checking featured image in folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        for path in self.config["paths_with_featured_image"]:
            result = h.file.check_featured_image(path)[1]
            self.add_line(result)
        self.show_result()


class OnExtractZipArchives(ActionBase):
    """Extract all ZIP archives from a selected folder.

    This action prompts the user to select a folder and then processes all ZIP files
    within it, extracting their contents directly to the same directory where each
    archive is located. After successful extraction, the original archive files
    are deleted.

    The extraction process handles nested directory structures and preserves the
    original file organization from within the archives. Each ZIP file is processed
    independently, so if one archive fails to extract, others will still be processed.

    This provides a one-click solution for bulk extraction of ZIP archives while
    maintaining clean folder organization by removing the original archive files.
    """

    icon = "📦"
    title = "Extract ZIP archives in …"

    @ActionBase.handle_exceptions("extracting ZIP archives")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory("Select a folder with ZIP archives", self.config["path_3d"])
        if self.folder_path is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("extracting ZIP archives thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return

        self.add_line(f"🔵 Starting ZIP archive extraction for path: {self.folder_path}")
        self.add_line(h.file.apply_func(self.folder_path, ".zip", h.file.extract_zip_archive))

    @ActionBase.handle_exceptions("extracting ZIP archives thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnRemoveEmptyFoldersThreaded(ActionBase):
    """Remove all empty folders recursively with threading support.

    This action provides the same functionality as OnRemoveEmptyFolders but
    executes the operation in a separate thread to prevent UI blocking when
    processing large directory structures. A progress toast notification is
    shown upon completion.

    This is recommended for cleaning large directory trees where the operation
    might take several seconds or more to complete.
    """

    icon = "🗑️"
    title = "Remove empty folders in …"

    @ActionBase.handle_exceptions("removing empty folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory("Select a folder to clean empty folders", self.config["path_3d"])
        if self.folder_path is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("removing empty folders thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return

        self.add_line(f"🔵 Starting empty folder cleanup for path: {self.folder_path}")
        result = h.file.remove_empty_folders(self.folder_path)
        self.add_line(result)

    @ActionBase.handle_exceptions("removing empty folders thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnRenameFb2EpubPdfFiles(ActionBase):
    """Rename FB2, Epub, PDF files based on metadata from file content.

    This action prompts the user to select a folder and then processes all FB2, Epub, PDF files
    within it, extracting author, title, and year information from the metadata.
    Files are renamed according to the pattern: "Author - Title - Year.ext" (year is optional).

    If metadata extraction fails, the action attempts to transliterate the filename
    from English to Russian, assuming it might be a transliterated Russian title.
    If transliteration doesn't improve the filename, it remains unchanged.

    This provides a one-click solution for organizing and standardizing FB2, Epub, PDF book collections
    with proper naming conventions based on actual book metadata.
    """

    icon = "📚"
    title = "Rename FB2, Epub, PDF files in …"

    @ActionBase.handle_exceptions("renaming FB2, Epub, PDF files")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with FB2, Epub, PDF files", self.config["path_3d"]
        )
        if self.folder_path is None:
            return

        # Define available operations
        operations = [
            "📖 Rename FB2 files by metadata",
            "📖 Rename Epub files by metadata",
            "📖 Rename PDF files by metadata",
            "🔄 Transliterate filenames (FB2, Epub, PDF)",
        ]

        # Get user selection for operations
        selected_operations = self.get_checkbox_selection(
            "Select Operations",
            "Choose which operations to perform:",
            operations,
            default_selected=operations,  # All selected by default
        )

        if selected_operations is None:
            return

        self.selected_operations = selected_operations
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("renaming FB2, Epub, PDF files thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return

        # Execute selected operations
        if "📖 Rename FB2 files by metadata" in self.selected_operations:
            self.add_line(f"🔵 Starting FB2 file processing for path: {self.folder_path}")
            self.add_line(h.file.apply_func(self.folder_path, ".fb2", h.file.rename_fb2_file))

        if "📖 Rename Epub files by metadata" in self.selected_operations:
            self.add_line(f"🔵 Starting Epub file processing for path: {self.folder_path}")
            self.add_line(h.file.apply_func(self.folder_path, ".epub", h.file.rename_epub_file))

        if "📖 Rename PDF files by metadata" in self.selected_operations:
            self.add_line(f"🔵 Starting PDF file processing for path: {self.folder_path}")
            self.add_line(h.file.apply_func(self.folder_path, ".pdf", h.file.rename_pdf_file))

        if "🔄 Transliterate filenames (FB2, Epub, PDF)" in self.selected_operations:
            self.add_line(f"🔵 Starting transliteration for path: {self.folder_path}")
            self.add_line(h.file.apply_func(self.folder_path, ".fb2", h.file.rename_transliterated_file))
            self.add_line(h.file.apply_func(self.folder_path, ".epub", h.file.rename_transliterated_file))
            self.add_line(h.file.apply_func(self.folder_path, ".pdf", h.file.rename_transliterated_file))

    @ActionBase.handle_exceptions("renaming FB2, Epub, PDF files thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


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
        """Execute the code. Main method for the action."""
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.rename_largest_images_to_featured(folder_path)
        self.add_line(result)
        self.show_result()


class OnTreeViewFolder(ActionBase):
    """Generate a text-based tree view of a folder structure.

    This action prompts the user to select a folder and then creates
    a hierarchical text representation of its directory structure,
    similar to the output of the 'tree' command in command-line interfaces.
    """

    icon = "├"
    title = "Tree view of a folder"

    @ActionBase.handle_exceptions("generating tree view")
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


class OnTreeViewFolderIgnoreHiddenFolders(ActionBase):
    """Generate a tree view excluding hidden folders.

    This action extends OnTreeViewFolder by automatically setting the
    is_ignore_hidden_folders flag to true, creating a cleaner tree view
    that omits hidden directories (those starting with a dot).
    """

    icon = "├"
    title = "Tree view of a folder (ignore hidden folders)"

    @ActionBase.handle_exceptions("generating tree view ignoring hidden folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        OnTreeViewFolder().execute(is_ignore_hidden_folders=True)
