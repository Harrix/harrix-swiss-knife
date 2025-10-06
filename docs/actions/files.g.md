---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `files.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnAllFilesToParentFolder`](#%EF%B8%8F-class-onallfilestoparentfolder)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
- [🏛️ Class `OnBlockDisks`](#%EF%B8%8F-class-onblockdisks)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-1)
- [🏛️ Class `OnCheckFeaturedImage`](#%EF%B8%8F-class-oncheckfeaturedimage)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-2)
- [🏛️ Class `OnCheckFeaturedImageInFolders`](#%EF%B8%8F-class-oncheckfeaturedimageinfolders)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-3)
- [🏛️ Class `OnCombineForAI`](#%EF%B8%8F-class-oncombineforai)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-4)
  - [⚙️ Method `_handle_folder_selection`](#%EF%B8%8F-method-_handle_folder_selection)
- [🏛️ Class `OnExtractZipArchives`](#%EF%B8%8F-class-onextractziparchives)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-5)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)
- [🏛️ Class `OnListFilesCurrentFolder`](#%EF%B8%8F-class-onlistfilescurrentfolder)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-6)
- [🏛️ Class `OnListFilesSimple`](#%EF%B8%8F-class-onlistfilessimple)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-7)
- [🏛️ Class `OnListFilesSimpleIgnoreHiddenFolders`](#%EF%B8%8F-class-onlistfilessimpleignorehiddenfolders)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-8)
- [🏛️ Class `OnRemoveEmptyFolders`](#%EF%B8%8F-class-onremoveemptyfolders)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-9)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-1)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-1)
- [🏛️ Class `OnRenameFb2EpubPdfFiles`](#%EF%B8%8F-class-onrenamefb2epubpdffiles)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-10)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-2)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-2)
- [🏛️ Class `OnRenameFilesByMapping`](#%EF%B8%8F-class-onrenamefilesbymapping)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-11)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread-3)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after-3)
  - [⚙️ Method `_parse_mapping_text`](#%EF%B8%8F-method-_parse_mapping_text)
- [🏛️ Class `OnRenameLargestImagesToFeaturedImage`](#%EF%B8%8F-class-onrenamelargestimagestofeaturedimage)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-12)
- [🏛️ Class `OnRenameLastGitCommitWithEmoji`](#%EF%B8%8F-class-onrenamelastgitcommitwithemoji)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-13)
- [🏛️ Class `OnTreeViewFolder`](#%EF%B8%8F-class-ontreeviewfolder)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-14)
- [🏛️ Class `OnTreeViewFolderIgnoreHiddenFolders`](#%EF%B8%8F-class-ontreeviewfolderignorehiddenfolders)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-15)
- [🔧 Function `_expand_path_patterns`](#-function-_expand_path_patterns)
- [🔧 Function `_filter_files_by_extension`](#-function-_filter_files_by_extension)
- [🔧 Function `_safe_collect_text_files_to_markdown`](#-function-_safe_collect_text_files_to_markdown)

</details>

## 🏛️ Class `OnAllFilesToParentFolder`

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

### ⚙️ Method `execute`

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

## 🏛️ Class `OnBlockDisks`

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

### ⚙️ Method `execute`

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

## 🏛️ Class `OnCheckFeaturedImage`

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

### ⚙️ Method `execute`

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
        """Execute the code. Main method for the action."""
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

## 🏛️ Class `OnCombineForAI`

```python
class OnCombineForAI(ActionBase)
```

Combine multiple text files into a single markdown document for AI processing.

This action allows users to select from predefined file combinations configured
in paths_combine_for_ai. It combines multiple files into a single markdown
document with proper code fencing, making it suitable for AI analysis and processing.

Now supports:

- Direct file paths (as before)
- Directory paths (all files recursively)
- Glob patterns (e.g., _.py, \*\*/_.py)
- File extension filtering

<details>
<summary>Code:</summary>

```python
class OnCombineForAI(ActionBase):

    icon = "🤖"
    title = "Combine files for AI"
    bold_title = True

    @ActionBase.handle_exceptions("combining files for AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        # Get list of available combinations from config
        combinations = self.config.get("paths_combine_for_ai", [])

        # Add folder selection option
        folder_selection_option = "📁 Choose folder"
        combination_names = [combo["name"] for combo in combinations] + [folder_selection_option]

        # Let user select a combination or folder
        selected_name = self.get_choice_from_list(
            "Select file combination", "Choose a file combination to combine:", combination_names
        )

        if not selected_name:
            return

        # Handle folder selection
        if selected_name == folder_selection_option:
            self._handle_folder_selection()
            return

        # Find the selected combination
        selected_combo = next((combo for combo in combinations if combo["name"] == selected_name), None)
        if not selected_combo:
            self.add_line(f"❌ Could not find combination: {selected_name}")
            return

        # Get files and base folder from the selected combination
        input_paths = selected_combo["files"]
        base_folder = selected_combo["base_folder"]

        # Check if there are file extensions to filter by
        file_extensions = selected_combo.get("extensions", None)

        # Expand paths (handle directories, glob patterns, etc.)
        all_files = _expand_path_patterns(input_paths)

        if not all_files:
            self.add_line("❌ No files found matching the specified paths/patterns")
            return

        # Filter by extensions if specified
        if file_extensions:
            all_files = _filter_files_by_extension(all_files, file_extensions)

        if not all_files:
            self.add_line(f"❌ No files found with extensions: {', '.join(file_extensions)}")
            return

        # Show file selection dialog with checkboxes (all files selected by default)
        selected_files = self.get_checkbox_selection(
            "Select files to combine",
            f"Choose files from '{selected_name}' to combine:",
            all_files,
            default_selected=all_files,  # All files selected by default
        )

        if not selected_files:
            return

        self.add_line(_safe_collect_text_files_to_markdown(selected_files, base_folder))
        self.show_result()

    def _handle_folder_selection(self) -> None:
        """Handle folder selection and process all files in the selected folder."""
        # Get default path from config or use current directory
        default_path = self.config.get("path_github", str(Path.cwd()))

        # Let user select a folder
        selected_folder = self.get_existing_directory("Выбрать папку", default_path)
        if not selected_folder:
            return

        # Find all files recursively in the selected folder, filtering ignored paths
        all_files = []
        for root, dirs, files in os.walk(selected_folder):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not h.file.should_ignore_path(Path(root) / d)]

            for file in files:
                file_path = Path(root) / file
                # Check if the file should be ignored
                if not h.file.should_ignore_path(file_path):
                    all_files.append(str(file_path))

        if not all_files:
            self.add_line("❌ No files found in the selected folder (after filtering ignored paths)")
            return

        # Show file selection dialog with checkboxes (all files selected by default)
        selected_files = self.get_checkbox_selection(
            "Select files to combine",
            f"Choose files from '{selected_folder}' to combine:",
            all_files,
            default_selected=all_files,  # All files selected by default
        )

        if not selected_files:
            return

        # Use the selected folder as base folder
        self.add_line(_safe_collect_text_files_to_markdown(selected_files, str(selected_folder)))
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        # Get list of available combinations from config
        combinations = self.config.get("paths_combine_for_ai", [])

        # Add folder selection option
        folder_selection_option = "📁 Choose folder"
        combination_names = [combo["name"] for combo in combinations] + [folder_selection_option]

        # Let user select a combination or folder
        selected_name = self.get_choice_from_list(
            "Select file combination", "Choose a file combination to combine:", combination_names
        )

        if not selected_name:
            return

        # Handle folder selection
        if selected_name == folder_selection_option:
            self._handle_folder_selection()
            return

        # Find the selected combination
        selected_combo = next((combo for combo in combinations if combo["name"] == selected_name), None)
        if not selected_combo:
            self.add_line(f"❌ Could not find combination: {selected_name}")
            return

        # Get files and base folder from the selected combination
        input_paths = selected_combo["files"]
        base_folder = selected_combo["base_folder"]

        # Check if there are file extensions to filter by
        file_extensions = selected_combo.get("extensions", None)

        # Expand paths (handle directories, glob patterns, etc.)
        all_files = _expand_path_patterns(input_paths)

        if not all_files:
            self.add_line("❌ No files found matching the specified paths/patterns")
            return

        # Filter by extensions if specified
        if file_extensions:
            all_files = _filter_files_by_extension(all_files, file_extensions)

        if not all_files:
            self.add_line(f"❌ No files found with extensions: {', '.join(file_extensions)}")
            return

        # Show file selection dialog with checkboxes (all files selected by default)
        selected_files = self.get_checkbox_selection(
            "Select files to combine",
            f"Choose files from '{selected_name}' to combine:",
            all_files,
            default_selected=all_files,  # All files selected by default
        )

        if not selected_files:
            return

        self.add_line(_safe_collect_text_files_to_markdown(selected_files, base_folder))
        self.show_result()
```

</details>

### ⚙️ Method `_handle_folder_selection`

```python
def _handle_folder_selection(self) -> None
```

Handle folder selection and process all files in the selected folder.

<details>
<summary>Code:</summary>

```python
def _handle_folder_selection(self) -> None:
        # Get default path from config or use current directory
        default_path = self.config.get("path_github", str(Path.cwd()))

        # Let user select a folder
        selected_folder = self.get_existing_directory("Выбрать папку", default_path)
        if not selected_folder:
            return

        # Find all files recursively in the selected folder, filtering ignored paths
        all_files = []
        for root, dirs, files in os.walk(selected_folder):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not h.file.should_ignore_path(Path(root) / d)]

            for file in files:
                file_path = Path(root) / file
                # Check if the file should be ignored
                if not h.file.should_ignore_path(file_path):
                    all_files.append(str(file_path))

        if not all_files:
            self.add_line("❌ No files found in the selected folder (after filtering ignored paths)")
            return

        # Show file selection dialog with checkboxes (all files selected by default)
        selected_files = self.get_checkbox_selection(
            "Select files to combine",
            f"Choose files from '{selected_folder}' to combine:",
            all_files,
            default_selected=all_files,  # All files selected by default
        )

        if not selected_files:
            return

        # Use the selected folder as base folder
        self.add_line(_safe_collect_text_files_to_markdown(selected_files, str(selected_folder)))
        self.show_result()
```

</details>

## 🏛️ Class `OnExtractZipArchives`

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

### ⚙️ Method `execute`

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

### ⚙️ Method `in_thread`

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

### ⚙️ Method `thread_after`

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
    title = "List files current folder"

    @ActionBase.handle_exceptions("generating current folder file list")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
        if folder_path is None:
            return

        result = h.file.list_files_simple(
            folder_path, is_ignore_hidden_folders=kwargs.get("is_ignore_hidden_folders", False), is_only_files=True
        )
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

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
            folder_path, is_ignore_hidden_folders=kwargs.get("is_ignore_hidden_folders", False), is_only_files=True
        )
        self.add_line(result)
        self.show_result()
```

</details>

## 🏛️ Class `OnListFilesSimple`

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

### ⚙️ Method `execute`

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

## 🏛️ Class `OnListFilesSimpleIgnoreHiddenFolders`

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

### ⚙️ Method `execute`

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

## 🏛️ Class `OnRemoveEmptyFolders`

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

### ⚙️ Method `execute`

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

### ⚙️ Method `in_thread`

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

### ⚙️ Method `thread_after`

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

## 🏛️ Class `OnRenameFb2EpubPdfFiles`

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

### ⚙️ Method `execute`

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

### ⚙️ Method `in_thread`

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

### ⚙️ Method `thread_after`

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

## 🏛️ Class `OnRenameFilesByMapping`

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
                line_new = line.strip()
                if not line_new:  # Skip empty lines
                    continue

                # Split by tab character
                parts = line_new.split("\t")
                count_parts = 2
                if len(parts) != count_parts:
                    self.add_line(
                        f"❌ Invalid format on line {line_num}: '{line_new}'. Expected: old_filename<TAB>new_filename"
                    )
                    return None

                old_name, new_name = parts[0].strip(), parts[1].strip()

                if not old_name or not new_name:
                    self.add_line(f"❌ Empty filename on line {line_num}: '{line_new}'")
                    return None

                mapping_dict[old_name] = new_name

            if not mapping_dict:
                self.add_line("❌ No valid mappings found in the text")
                return None

        except Exception as e:
            self.add_line(f"❌ Error parsing mapping text: {e}")
            return None
        else:
            self.add_line(f"✅ Parsed {len(mapping_dict)} file mappings")
            return mapping_dict
```

</details>

### ⚙️ Method `execute`

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

### ⚙️ Method `in_thread`

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

### ⚙️ Method `thread_after`

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

### ⚙️ Method `_parse_mapping_text`

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
                line_new = line.strip()
                if not line_new:  # Skip empty lines
                    continue

                # Split by tab character
                parts = line_new.split("\t")
                count_parts = 2
                if len(parts) != count_parts:
                    self.add_line(
                        f"❌ Invalid format on line {line_num}: '{line_new}'. Expected: old_filename<TAB>new_filename"
                    )
                    return None

                old_name, new_name = parts[0].strip(), parts[1].strip()

                if not old_name or not new_name:
                    self.add_line(f"❌ Empty filename on line {line_num}: '{line_new}'")
                    return None

                mapping_dict[old_name] = new_name

            if not mapping_dict:
                self.add_line("❌ No valid mappings found in the text")
                return None

        except Exception as e:
            self.add_line(f"❌ Error parsing mapping text: {e}")
            return None
        else:
            self.add_line(f"✅ Parsed {len(mapping_dict)} file mappings")
            return mapping_dict
```

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
        """Execute the code. Main method for the action."""
        folder_path = self.get_existing_directory("Select a folder", self.config["path_3d"])
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

## 🏛️ Class `OnRenameLastGitCommitWithEmoji`

```python
class OnRenameLastGitCommitWithEmoji(ActionBase)
```

Rename the last git commit by adding emoji if missing.

This action checks the last git commit message and adds an appropriate emoji
if the message starts with specific keywords like Add, Create, Build, etc.
It uses git commit --amend to modify the last commit.

<details>
<summary>Code:</summary>

```python
class OnRenameLastGitCommitWithEmoji(ActionBase):

    icon = "🎯"
    title = "Rename last Git commit with emoji"

    # Mapping of keywords to emojis

    EMOJI_MAPPING: ClassVar[dict[str, str]] = {
        "Add": "➕",  # noqa: RUF001
        "Create": "➕",  # noqa: RUF001
        "Build": "🚀",
        "Delete": "🗑️",
        "Remove": "🗑️",
        "Docs": "📚",
        "Experiment": "🧪",
        "Fix": "🐞",
        "Modify": "🔧",
        "Move": "🚚",
        "Refactor": "♻️",
        "Rename": "✒️",
        "Replace": "🔄",
        "Style": "✨",
        "Test": "⚗️",
        "Update": "⬆️",
        "Revert": "🔙",
        "Publish": "🚀",
        "Merge": "🔀",
    }

    @ActionBase.handle_exceptions("renaming last git commit with emoji")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        # Select git folder
        self.folder_path = self.get_folder_with_choice_option(
            "Select Git folder", self.config["paths_git"], self.config["path_github"]
        )
        if not self.folder_path:
            return

        self.add_line(f"🔵 Processing git repository: {self.folder_path}")

        # Change to the selected directory
        original_cwd = Path.cwd()
        os.chdir(self.folder_path)

        try:
            # Get the last commit message
            result = h.dev.run_command("git log -1 --pretty=format:%s", cwd=str(self.folder_path))
            if not result.strip():
                self.add_line("❌ No git commits found or not a git repository")
                return

            last_commit_message = result.strip()
            self.add_line(f"📝 Last commit message: {last_commit_message}")

            # Check if emoji is already present
            if any(emoji in last_commit_message for emoji in self.EMOJI_MAPPING.values()):
                self.add_line("✅ Emoji already present in commit message")
                return

            # Find matching keyword and emoji
            new_message = None
            for keyword, emoji in self.EMOJI_MAPPING.items():
                if last_commit_message.startswith(keyword):
                    new_message = f"{emoji} {last_commit_message}"
                    self.add_line(f"🎯 Found keyword '{keyword}', adding emoji {emoji}")
                    break

            if not new_message:
                self.add_line("ℹ️ No matching keyword found, no changes needed")  # noqa: RUF001
                return

            # Amend the commit with new message
            self.add_line(f"🔄 Amending commit with new message: {new_message}")

            # Handle quotes in commit message by escaping them properly
            escaped_message = new_message.replace('"', '\\"')
            command = f'git commit --amend -m "{escaped_message}" && git push origin main --force'

            result = h.dev.run_command(command, cwd=str(self.folder_path))
            self.add_line("✅ Commit amended successfully")
            self.add_line(f"📊 Git output: {result}")

        finally:
            # Restore original working directory
            os.chdir(original_cwd)

        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Execute the code. Main method for the action.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        # Select git folder
        self.folder_path = self.get_folder_with_choice_option(
            "Select Git folder", self.config["paths_git"], self.config["path_github"]
        )
        if not self.folder_path:
            return

        self.add_line(f"🔵 Processing git repository: {self.folder_path}")

        # Change to the selected directory
        original_cwd = Path.cwd()
        os.chdir(self.folder_path)

        try:
            # Get the last commit message
            result = h.dev.run_command("git log -1 --pretty=format:%s", cwd=str(self.folder_path))
            if not result.strip():
                self.add_line("❌ No git commits found or not a git repository")
                return

            last_commit_message = result.strip()
            self.add_line(f"📝 Last commit message: {last_commit_message}")

            # Check if emoji is already present
            if any(emoji in last_commit_message for emoji in self.EMOJI_MAPPING.values()):
                self.add_line("✅ Emoji already present in commit message")
                return

            # Find matching keyword and emoji
            new_message = None
            for keyword, emoji in self.EMOJI_MAPPING.items():
                if last_commit_message.startswith(keyword):
                    new_message = f"{emoji} {last_commit_message}"
                    self.add_line(f"🎯 Found keyword '{keyword}', adding emoji {emoji}")
                    break

            if not new_message:
                self.add_line("ℹ️ No matching keyword found, no changes needed")  # noqa: RUF001
                return

            # Amend the commit with new message
            self.add_line(f"🔄 Amending commit with new message: {new_message}")

            # Handle quotes in commit message by escaping them properly
            escaped_message = new_message.replace('"', '\\"')
            command = f'git commit --amend -m "{escaped_message}" && git push origin main --force'

            result = h.dev.run_command(command, cwd=str(self.folder_path))
            self.add_line("✅ Commit amended successfully")
            self.add_line(f"📊 Git output: {result}")

        finally:
            # Restore original working directory
            os.chdir(original_cwd)

        self.show_result()
```

</details>

## 🏛️ Class `OnTreeViewFolder`

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

### ⚙️ Method `execute`

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

## 🏛️ Class `OnTreeViewFolderIgnoreHiddenFolders`

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

### ⚙️ Method `execute`

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

## 🔧 Function `_expand_path_patterns`

```python
def _expand_path_patterns(paths: list[str]) -> list[str]
```

Expand path patterns to actual file paths.

This function processes a list of paths that may contain:

- Direct file paths (returned as-is)
- Directory paths (all files recursively)
- Glob patterns (e.g., _.py, \*\*/_.py)

Args:
paths: List of paths that may be files, directories, or glob patterns

Returns:
List of actual file paths (filtered to exclude ignored paths)

<details>
<summary>Code:</summary>

```python
def _expand_path_patterns(paths: list[str]) -> list[str]:
    expanded_paths = []

    for path in paths:
        path = path.strip()
        if not path:
            continue

        # Check if it's a glob pattern (contains * or ?)
        if "*" in path or "?" in path:
            # Use Path.glob or Path.rglob to find matching files (PTH207)
            p = Path(path)
            matches = p.parent.rglob(p.name) if "**" in path else p.parent.glob(p.name)
            expanded_paths.extend(str(match) for match in matches if not h.file.should_ignore_path(match))
        elif Path(path).is_file():
            # It's a direct file path - check if it should be ignored
            if not h.file.should_ignore_path(Path(path)):
                expanded_paths.append(path)
        elif Path(path).is_dir():
            # It's a directory, find all files recursively
            for root, dirs, files in os.walk(path):
                # Filter out ignored directories
                dirs[:] = [d for d in dirs if not h.file.should_ignore_path(Path(root) / d)]

                for file in files:
                    file_path = Path(root) / file
                    # Check if the file should be ignored
                    if not h.file.should_ignore_path(file_path):
                        expanded_paths.append(str(file_path))
        else:
            # Path doesn't exist, but might be a glob pattern that didn't match
            # Try Path.glob or Path.rglob in case it's a pattern
            p = Path(path)
            matches = p.parent.rglob(p.name) if "**" in path else p.parent.glob(p.name)
            expanded_paths.extend(str(match) for match in matches if not h.file.should_ignore_path(match))

    return expanded_paths
```

</details>

## 🔧 Function `_filter_files_by_extension`

```python
def _filter_files_by_extension(files: list[str], extensions: list[str] | None = None) -> list[str]
```

Filter files by extension.

Args:
files: List of file paths
extensions: List of extensions to include (e.g., ['.py', '.md']). If None, includes all files.

Returns:
Filtered list of file paths

<details>
<summary>Code:</summary>

```python
def _filter_files_by_extension(files: list[str], extensions: list[str] | None = None) -> list[str]:
    if not extensions:
        return files

    filtered_files = []
    for file_path in files:
        file_ext = Path(file_path).suffix.lower()
        if file_ext in [ext.lower() for ext in extensions]:
            filtered_files.append(file_path)

    return filtered_files
```

</details>

## 🔧 Function `_safe_collect_text_files_to_markdown`

```python
def _safe_collect_text_files_to_markdown(file_paths: list[str], base_folder: str) -> str
```

Safely collect text files to markdown, skipping files that can't be decoded as text.

This function wraps h.file.collect_text_files_to_markdown and handles UnicodeDecodeError
exceptions by skipping files that can't be decoded as text (e.g., binary files).

Args:
file_paths: List of file paths to process
base_folder: Base folder path for relative path calculation

Returns:
Markdown string with successfully processed files

<details>
<summary>Code:</summary>

```python
def _safe_collect_text_files_to_markdown(file_paths: list[str], base_folder: str) -> str:
    try:
        return h.file.collect_text_files_to_markdown(file_paths, base_folder)
    except UnicodeDecodeError:
        # If we get a UnicodeDecodeError, it means one of the files is not a text file
        # We need to process files one by one and skip the problematic ones
        result_lines = []
        processed_files = []
        skipped_files = []

        for file_path in file_paths:
            try:
                # Try to read the file to check if it's a text file
                with Path.open(file_path, encoding="utf-8") as f:
                    f.read(1)  # Try to read at least one character
                processed_files.append(file_path)
            except UnicodeDecodeError:
                # This file is not a text file, skip it
                skipped_files.append(file_path)
                continue
            except Exception:
                # Other errors, also skip
                skipped_files.append(file_path)
                continue

        if skipped_files:
            result_lines.append(f"⚠️ Skipped {len(skipped_files)} non-text files: {', '.join(skipped_files)}")

        if processed_files:
            # Process only the text files
            result_lines.append(h.file.collect_text_files_to_markdown(processed_files, base_folder))
        else:
            result_lines.append("❌ No text files found to process")

        return "\n".join(result_lines)
```

</details>
