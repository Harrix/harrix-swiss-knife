---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `files.py`

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
- [Class `OnExtractZipArchives`](#class-onextractziparchives)
  - [Method `execute`](#method-execute-4)
  - [Method `in_thread`](#method-in_thread)
  - [Method `thread_after`](#method-thread_after)
- [Class `OnListFilesSimple`](#class-onlistfilessimple)
  - [Method `execute`](#method-execute-5)
- [Class `OnListFilesSimpleIgnoreHiddenFolders`](#class-onlistfilessimpleignorehiddenfolders)
  - [Method `execute`](#method-execute-6)
- [Class `OnRemoveEmptyFolders`](#class-onremoveemptyfolders)
  - [Method `execute`](#method-execute-7)
  - [Method `in_thread`](#method-in_thread-1)
  - [Method `thread_after`](#method-thread_after-1)
- [Class `OnRenameFb2EpubPdfFiles`](#class-onrenamefb2epubpdffiles)
  - [Method `execute`](#method-execute-8)
  - [Method `in_thread`](#method-in_thread-2)
  - [Method `thread_after`](#method-thread_after-2)
- [Class `OnRenameFilesByMapping`](#class-onrenamefilesbymapping)
  - [Method `execute`](#method-execute-9)
  - [Method `in_thread`](#method-in_thread-3)
  - [Method `thread_after`](#method-thread_after-3)
  - [Method `_parse_mapping_text`](#method-_parse_mapping_text)
- [Class `OnRenameLargestImagesToFeaturedImage`](#class-onrenamelargestimagestofeaturedimage)
  - [Method `execute`](#method-execute-10)
- [Class `OnTreeViewFolder`](#class-ontreeviewfolder)
  - [Method `execute`](#method-execute-11)
- [Class `OnTreeViewFolderIgnoreHiddenFolders`](#class-ontreeviewfolderignorehiddenfolders)
  - [Method `execute`](#method-execute-12)

</details>

## Class `OnAllFilesToParentFolder`

```python
class OnAllFilesToParentFolder(ActionBase)
```

Move and flatten files from nested directories.

This action prompts the user to select a folder and then moves all files
from its nested subdirectories directly into the selected parent folder,
effectively flattening the directory structure while preserving all files.

<details>
<summary>Code:</summary>

```python
class OnAllFilesToParentFolder(ActionBase):

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
class OnBlockDisks(ActionBase)
```

Lock BitLocker-encrypted drives.

This action locks all drives specified in the configuration's `block_drives` list
using BitLocker encryption, forcibly dismounting them if necessary to ensure
secure protection of the drive contents.

<details>
<summary>Code:</summary>

```python
class OnBlockDisks(ActionBase):

    icon = "🔒"
    title = "Block disks"

    @ActionBase.handle_exceptions("blocking disks")
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
class OnCheckFeaturedImage(ActionBase)
```

Check for featured image files in a selected folder.

This action prompts the user to select a folder and then checks for the presence
of files named `featured_image` with any extension, which are commonly used
as preview images or thumbnails for the folder contents.

<details>
<summary>Code:</summary>

```python
class OnCheckFeaturedImage(ActionBase):

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

## Class `OnExtractZipArchives`

```python
class OnExtractZipArchives(ActionBase)
```

Extract all ZIP archives from a selected folder.

This action prompts the user to select a folder and then processes all ZIP files
within it, extracting their contents directly to the same directory where each
archive is located. After successful extraction, the original archive files
are deleted.

The extraction process handles nested directory structures and preserves the
original file organization from within the archives. Each ZIP file is processed
independently, so if one archive fails to extract, others will still be processed.

This provides a one-click solution for bulk extraction of ZIP archives while
maintaining clean folder organization by removing the original archive files.

<details>
<summary>Code:</summary>

```python
class OnExtractZipArchives(ActionBase):

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
        self.folder_path = self.get_existing_directory("Select a folder with ZIP archives", self.config["path_3d"])
        if self.folder_path is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        if self.folder_path is None:
            return

        self.add_line(f"🔵 Starting ZIP archive extraction for path: {self.folder_path}")
        self.add_line(h.file.apply_func(self.folder_path, ".zip", h.file.extract_zip_archive))
```

</details>

### Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

## Class `OnListFilesSimple`

```python
class OnListFilesSimple(ActionBase)
```

Generate a simple list of all files in a directory structure.

This action prompts the user to select a folder and then creates
a simple text list of all files with their relative paths,
similar to a flat file listing without directory tree structure.

<details>
<summary>Code:</summary>

```python
class OnListFilesSimple(ActionBase):

    icon = "📄"
    title = "List files simple"

    @ActionBase.handle_exceptions("generating file list")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.list_files_simple(
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

        result = h.file.list_files_simple(
            folder_path, is_ignore_hidden_folders=kwargs.get("is_ignore_hidden_folders", False)
        )
        self.add_line(result)
        self.show_result()
```

</details>

## Class `OnListFilesSimpleIgnoreHiddenFolders`

```python
class OnListFilesSimpleIgnoreHiddenFolders(ActionBase)
```

Generate a simple file list excluding hidden folders.

This action extends OnListFilesSimple by automatically setting the
is_ignore_hidden_folders flag to true, creating a cleaner file list
that omits hidden directories and files (those starting with a dot
or matching common ignore patterns like .git, **pycache**, etc.).

<details>
<summary>Code:</summary>

```python
class OnListFilesSimpleIgnoreHiddenFolders(ActionBase):

    icon = "📄"
    title = "List files simple (ignore hidden folders)"

    @ActionBase.handle_exceptions("generating file list ignoring hidden folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        OnListFilesSimple().execute(is_ignore_hidden_folders=True)
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
        OnListFilesSimple().execute(is_ignore_hidden_folders=True)
```

</details>

## Class `OnRemoveEmptyFolders`

```python
class OnRemoveEmptyFolders(ActionBase)
```

Remove all empty folders recursively.

This action prompts the user to select a folder and then removes all empty
folders recursively from the selected directory.

<details>
<summary>Code:</summary>

```python
class OnRemoveEmptyFolders(ActionBase):

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
        self.folder_path = self.get_existing_directory("Select a folder to clean empty folders", self.config["path_3d"])
        if self.folder_path is None:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        if self.folder_path is None:
            return

        self.add_line(f"🔵 Starting empty folder cleanup for path: {self.folder_path}")
        result = h.file.remove_empty_folders(self.folder_path)
        self.add_line(result)
```

</details>

### Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

## Class `OnRenameFb2EpubPdfFiles`

```python
class OnRenameFb2EpubPdfFiles(ActionBase)
```

Rename FB2, Epub, PDF files based on metadata from file content.

This action prompts the user to select a folder and then processes all FB2, Epub, PDF files
within it, extracting author, title, and year information from the metadata.
Files are renamed according to the pattern: "Author - Title - Year.ext" (year is optional).

If metadata extraction fails, the action attempts to transliterate the filename
from English to Russian, assuming it might be a transliterated Russian title.
If transliteration doesn't improve the filename, it remains unchanged.

This provides a one-click solution for organizing and standardizing FB2, Epub, PDF book collections
with proper naming conventions based on actual book metadata.

<details>
<summary>Code:</summary>

```python
class OnRenameFb2EpubPdfFiles(ActionBase):

    icon = "📚"
    title = "Rename FB2, Epub, PDF files in …"

    @ActionBase.handle_exceptions("renaming FB2, Epub, PDF files")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with FB2, Epub, PDF files", self.config["path_books"]
        )
        if self.folder_path is None:
            return

        # Define available operations
        operations = [
            "📖 Rename FB2 files by metadata",
            "📖 Rename Epub files by metadata",
            "📖 Rename PDF files by metadata",
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

    @ActionBase.handle_exceptions("renaming FB2, Epub, PDF files thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
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
        self.folder_path = self.get_existing_directory(
            "Select a folder with FB2, Epub, PDF files", self.config["path_books"]
        )
        if self.folder_path is None:
            return

        # Define available operations
        operations = [
            "📖 Rename FB2 files by metadata",
            "📖 Rename Epub files by metadata",
            "📖 Rename PDF files by metadata",
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
```

</details>

### Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
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
```

</details>

### Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

## Class `OnRenameFilesByMapping`

```python
class OnRenameFilesByMapping(ActionBase)
```

Rename files recursively based on a mapping dictionary.

This action prompts the user to select a folder and provide a mapping text
(old filename TAB new filename per line), then renames files recursively
from the selected directory according to the mapping.

<details>
<summary>Code:</summary>

```python
class OnRenameFilesByMapping(ActionBase):

    icon = "📝"
    title = "Rename files by mapping in …"

    @ActionBase.handle_exceptions("renaming files by mapping")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory("Select a folder to rename files", self.config["path_3d"])
        if self.folder_path is None:
            return

        # Get mapping text from user
        mapping_text = self.get_text_textarea(
            "File Rename Mapping",
            "Enter file rename mapping (one per line):\nold_filename.ext<TAB>new_filename.ext",
            "old_file.txt\tnew_file.txt\nconfig.json\tsettings.json",
        )
        if mapping_text is None:
            return

        # Parse mapping text into dictionary
        self.rename_mapping = self._parse_mapping_text(mapping_text)
        if not self.rename_mapping:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("renaming files by mapping thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None or not self.rename_mapping:
            return

        self.add_line(f"🔵 Starting file renaming for path: {self.folder_path}")
        self.add_line(f"🔵 Renaming {len(self.rename_mapping)} file mappings")
        result = h.file.rename_files_by_mapping(self.folder_path, self.rename_mapping)
        self.add_line(result)

    @ActionBase.handle_exceptions("renaming files by mapping thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()

    def _parse_mapping_text(self, mapping_text: str) -> dict[str, str] | None:
        """Parse mapping text into a dictionary.

        Args:
            mapping_text (str): Text with old_filename<TAB>new_filename per line

        Returns:
            dict[str, str] | None: Dictionary mapping old names to new names, or None if error
        """
        try:
            mapping_dict = {}
            lines = mapping_text.strip().split("\n")

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue

                # Split by tab character
                parts = line.split("\t")
                if len(parts) != 2:
                    self.add_line(
                        f"❌ Invalid format on line {line_num}: '{line}'. Expected: old_filename<TAB>new_filename"
                    )
                    return None

                old_name, new_name = parts[0].strip(), parts[1].strip()

                if not old_name or not new_name:
                    self.add_line(f"❌ Empty filename on line {line_num}: '{line}'")
                    return None

                mapping_dict[old_name] = new_name

            if not mapping_dict:
                self.add_line("❌ No valid mappings found in the text")
                return None

            self.add_line(f"✅ Parsed {len(mapping_dict)} file mappings")
            return mapping_dict

        except Exception as e:
            self.add_line(f"❌ Error parsing mapping text: {e}")
            return None
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
        self.folder_path = self.get_existing_directory("Select a folder to rename files", self.config["path_3d"])
        if self.folder_path is None:
            return

        # Get mapping text from user
        mapping_text = self.get_text_textarea(
            "File Rename Mapping",
            "Enter file rename mapping (one per line):\nold_filename.ext<TAB>new_filename.ext",
            "old_file.txt\tnew_file.txt\nconfig.json\tsettings.json",
        )
        if mapping_text is None:
            return

        # Parse mapping text into dictionary
        self.rename_mapping = self._parse_mapping_text(mapping_text)
        if not self.rename_mapping:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        if self.folder_path is None or not self.rename_mapping:
            return

        self.add_line(f"🔵 Starting file renaming for path: {self.folder_path}")
        self.add_line(f"🔵 Renaming {len(self.rename_mapping)} file mappings")
        result = h.file.rename_files_by_mapping(self.folder_path, self.rename_mapping)
        self.add_line(result)
```

</details>

### Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### Method `_parse_mapping_text`

```python
def _parse_mapping_text(self, mapping_text: str) -> dict[str, str] | None
```

Parse mapping text into a dictionary.

Args:
mapping_text (str): Text with old_filename<TAB>new_filename per line

Returns:
dict[str, str] | None: Dictionary mapping old names to new names, or None if error

<details>
<summary>Code:</summary>

```python
def _parse_mapping_text(self, mapping_text: str) -> dict[str, str] | None:
        try:
            mapping_dict = {}
            lines = mapping_text.strip().split("\n")

            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue

                # Split by tab character
                parts = line.split("\t")
                if len(parts) != 2:
                    self.add_line(
                        f"❌ Invalid format on line {line_num}: '{line}'. Expected: old_filename<TAB>new_filename"
                    )
                    return None

                old_name, new_name = parts[0].strip(), parts[1].strip()

                if not old_name or not new_name:
                    self.add_line(f"❌ Empty filename on line {line_num}: '{line}'")
                    return None

                mapping_dict[old_name] = new_name

            if not mapping_dict:
                self.add_line("❌ No valid mappings found in the text")
                return None

            self.add_line(f"✅ Parsed {len(mapping_dict)} file mappings")
            return mapping_dict

        except Exception as e:
            self.add_line(f"❌ Error parsing mapping text: {e}")
            return None
```

</details>

## Class `OnRenameLargestImagesToFeaturedImage`

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

## Class `OnTreeViewFolder`

```python
class OnTreeViewFolder(ActionBase)
```

Generate a text-based tree view of a folder structure.

This action prompts the user to select a folder and then creates
a hierarchical text representation of its directory structure,
similar to the output of the 'tree' command in command-line interfaces.

<details>
<summary>Code:</summary>

```python
class OnTreeViewFolder(ActionBase):

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
class OnTreeViewFolderIgnoreHiddenFolders(ActionBase)
```

Generate a tree view excluding hidden folders.

This action extends OnTreeViewFolder by automatically setting the
is_ignore_hidden_folders flag to true, creating a cleaner tree view
that omits hidden directories (those starting with a dot).

<details>
<summary>Code:</summary>

```python
class OnTreeViewFolderIgnoreHiddenFolders(ActionBase):

    icon = "├"
    title = "Tree view of a folder (ignore hidden folders)"

    @ActionBase.handle_exceptions("generating tree view ignoring hidden folders")
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
