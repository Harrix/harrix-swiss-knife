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
  - [⚙️ Method `_expand_path_patterns`](#%EF%B8%8F-method-_expand_path_patterns)
  - [⚙️ Method `_file_contains_nul`](#%EF%B8%8F-method-_file_contains_nul)
  - [⚙️ Method `_filter_files_by_extension`](#%EF%B8%8F-method-_filter_files_by_extension)
  - [⚙️ Method `_get_default_selected_for_combine`](#%EF%B8%8F-method-_get_default_selected_for_combine)
  - [⚙️ Method `_handle_folder_selection`](#%EF%B8%8F-method-_handle_folder_selection)
  - [⚙️ Method `_has_glob_wildcards`](#%EF%B8%8F-method-_has_glob_wildcards)
  - [⚙️ Method `_is_binary_for_combine`](#%EF%B8%8F-method-_is_binary_for_combine)
  - [⚙️ Method `_matches_any_unchecked_pattern`](#%EF%B8%8F-method-_matches_any_unchecked_pattern)
  - [⚙️ Method `_matches_path_pattern`](#%EF%B8%8F-method-_matches_path_pattern)
  - [⚙️ Method `_normalize_extension`](#%EF%B8%8F-method-_normalize_extension)
  - [⚙️ Method `_normalize_path_for_compare`](#%EF%B8%8F-method-_normalize_path_for_compare)
  - [⚙️ Method `_relative_path_for_combine`](#%EF%B8%8F-method-_relative_path_for_combine)
  - [⚙️ Method `_safe_collect_text_files_to_markdown`](#%EF%B8%8F-method-_safe_collect_text_files_to_markdown)
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
  - [⚙️ Method `_amend_with_message`](#%EF%B8%8F-method-_amend_with_message)
  - [⚙️ Method `_apply_keyword_emoji_prefix`](#%EF%B8%8F-method-_apply_keyword_emoji_prefix)
  - [⚙️ Method `_git_out`](#%EF%B8%8F-method-_git_out)
  - [⚙️ Method `_git_subprocess`](#%EF%B8%8F-method-_git_subprocess)
  - [⚙️ Method `_mapped_emojis_sorted`](#%EF%B8%8F-method-_mapped_emojis_sorted)
  - [⚙️ Method `_mode_add_emoji_last`](#%EF%B8%8F-method-_mode_add_emoji_last)
  - [⚙️ Method `_mode_rename_by_hash`](#%EF%B8%8F-method-_mode_rename_by_hash)
  - [⚙️ Method `_mode_rename_last`](#%EF%B8%8F-method-_mode_rename_last)
  - [⚙️ Method `_push_current_branch`](#%EF%B8%8F-method-_push_current_branch)
  - [⚙️ Method `_run_rebase_reword`](#%EF%B8%8F-method-_run_rebase_reword)
  - [⚙️ Method `_subject_has_mapped_emoji_prefix`](#%EF%B8%8F-method-_subject_has_mapped_emoji_prefix)
  - [⚙️ Method `_write_temp_editor`](#%EF%B8%8F-method-_write_temp_editor)
- [🏛️ Class `OnTreeViewFolder`](#%EF%B8%8F-class-ontreeviewfolder)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-14)
- [🏛️ Class `OnTreeViewFolderIgnoreHiddenFolders`](#%EF%B8%8F-class-ontreeviewfolderignorehiddenfolders)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute-15)

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
        folder_path = self.get_existing_directory("Select folder", self.config["path_3d"])
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
        folder_path = self.get_existing_directory("Select folder", self.config["path_3d"])
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
        folder_path = self.get_existing_directory("Select folder", self.config["path_3d"])
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
        folder_path = self.get_existing_directory("Select folder", self.config["path_3d"])
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

Combine multiple text files into a single Markdown document for AI processing.

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

        # Add folder selection option first (same text as in get_folder_with_choice_option)
        folder_selection_option = "📁 Select folder …"
        combination_names = [folder_selection_option] + [f"📁 {combo['name']}" for combo in combinations]

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

        # List items use 📁 prefix for presets; map back to config name
        lookup_name = (
            selected_name.removeprefix("📁 ")
            if selected_name.startswith("📁 ") and selected_name != folder_selection_option
            else selected_name
        )

        # Find the selected combination
        selected_combo = next((combo for combo in combinations if combo["name"] == lookup_name), None)
        if not selected_combo:
            self.add_line(f"❌ Could not find combination: {selected_name}")
            return

        # Get files and base folder from the selected combination
        input_paths = selected_combo["files"]
        base_folder = selected_combo["base_folder"]

        # Check if there are file extensions to filter by
        file_extensions = selected_combo.get("extensions", None)

        # Expand paths (handle directories, glob patterns, etc.)
        all_files = self._expand_path_patterns(input_paths)

        if not all_files:
            self.add_line("❌ No files found matching the specified paths/patterns")
            return

        # Filter by extensions if specified
        if file_extensions:
            all_files = self._filter_files_by_extension(all_files, file_extensions)

        if not all_files:
            self.add_line(f"❌ No files found with extensions: {', '.join(file_extensions)}")
            return

        default_selected = self._get_default_selected_for_combine(all_files, base_folder)

        # Show file selection dialog with checkboxes (all files selected by default)
        selected_files = self.get_checkbox_selection(
            "Select files to combine",
            f"Choose files from '{selected_name}' to combine:",
            all_files,
            default_selected=default_selected,
            enable_extension_filter=True,
        )

        if not selected_files:
            return

        self.add_line(self._safe_collect_text_files_to_markdown(cast("list[str | Path]", selected_files), base_folder))
        self.show_result()

    def _expand_path_patterns(self, paths: list[str]) -> list[str]:
        """Expand path patterns to actual file paths.

        Processes paths that may be direct files, directories, or glob patterns.
        """
        expanded_paths = []

        for original_path in paths:
            path = original_path.strip()
            if not path:
                continue

            # Check if it's a glob pattern (contains * or ?)
            if "*" in path or "?" in path:
                # Find the base directory (before any wildcards) and the pattern
                # Split path at the first wildcard occurrence
                parts = path.replace("\\", "/").split("/")
                base_parts = []
                pattern_parts = []
                found_wildcard = False

                for part in parts:
                    if not found_wildcard and "*" not in part and "?" not in part:
                        base_parts.append(part)
                    else:
                        found_wildcard = True
                        pattern_parts.append(part)

                # Reconstruct base directory and pattern
                base_dir = "/".join(base_parts) if base_parts else "."
                pattern = "/".join(pattern_parts) if pattern_parts else "*"

                # Use rglob if pattern contains ** or glob otherwise
                base_path = Path(base_dir)
                if base_path.exists() and base_path.is_dir():
                    matches = (
                        base_path.rglob(pattern.replace("**/", "")) if "**" in pattern else base_path.glob(pattern)
                    )
                    expanded_paths.extend(
                        str(match) for match in matches if match.is_file() and not h.file.should_ignore_path(match)
                    )
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
                # Try to find base directory and pattern
                parts = path.replace("\\", "/").split("/")
                base_parts = []
                pattern_parts = []
                found_wildcard = False

                for part in parts:
                    if not found_wildcard and "*" not in part and "?" not in part:
                        base_parts.append(part)
                    else:
                        found_wildcard = True
                        pattern_parts.append(part)

                base_dir = "/".join(base_parts) if base_parts else "."
                pattern = "/".join(pattern_parts) if pattern_parts else "*"

                base_path = Path(base_dir)
                if base_path.exists() and base_path.is_dir():
                    matches = (
                        base_path.rglob(pattern.replace("**/", "")) if "**" in pattern else base_path.glob(pattern)
                    )
                    expanded_paths.extend(
                        str(match) for match in matches if match.is_file() and not h.file.should_ignore_path(match)
                    )

        return expanded_paths

    def _file_contains_nul(self, path: Path) -> bool:
        """Return True if the file contains a null byte (streamed read, no full-file load)."""
        with path.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    return False
                if b"\x00" in chunk:
                    return True

    def _filter_files_by_extension(self, files: list[str], extensions: list[str] | None = None) -> list[str]:
        """Filter files by extension."""
        if not extensions:
            return files

        filtered_files = []
        for file_path in files:
            file_ext = Path(file_path).suffix.lower()
            if file_ext in [ext.lower() for ext in extensions]:
                filtered_files.append(file_path)

        return filtered_files

    def _get_default_selected_for_combine(self, all_files: list[str], base_folder: str) -> list[str]:
        """Return default selected files after applying pre-uncheck config rules."""
        unchecked_extensions = {
            self._normalize_extension(ext)
            for ext in cast("list[str]", self.config.get("combine_for_ai_unchecked_extensions", []))
            if self._normalize_extension(ext)
        }

        unchecked_file_patterns = {
            self._normalize_path_for_compare(path)
            for path in cast("list[str]", self.config.get("combine_for_ai_unchecked_files", []))
            if str(path).strip()
        }

        base_path = Path(base_folder).resolve()
        selected_files: list[str] = []

        for file_path in all_files:
            candidate = Path(file_path).resolve()
            candidate_ext = candidate.suffix.lower()
            candidate_abs = self._normalize_path_for_compare(candidate)

            candidate_rel = ""
            if base_path in candidate.parents:
                candidate_rel = self._normalize_path_for_compare(candidate.relative_to(base_path))

            should_uncheck = candidate_ext in unchecked_extensions
            if self._matches_any_unchecked_pattern(candidate_rel, candidate_abs, unchecked_file_patterns):
                should_uncheck = True

            if not should_uncheck:
                selected_files.append(file_path)

        return selected_files

    def _handle_folder_selection(self) -> None:
        """Handle folder selection and process all files in the selected folder."""
        # Get default path from config or use current directory
        default_path = self.config.get("path_github", str(Path.cwd()))

        # Let user select a folder
        selected_folder = self.get_existing_directory("Select folder", default_path)
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

        default_selected = self._get_default_selected_for_combine(all_files, str(selected_folder))

        # Show file selection dialog with checkboxes (all files selected by default)
        selected_files = self.get_checkbox_selection(
            "Select files to combine",
            f"Choose files from '{selected_folder}' to combine:",
            all_files,
            default_selected=default_selected,
            enable_extension_filter=True,
        )

        if not selected_files:
            return

        # Use the selected folder as base folder
        self.add_line(
            self._safe_collect_text_files_to_markdown(cast("list[str | Path]", selected_files), str(selected_folder))
        )
        self.show_result()

    def _has_glob_wildcards(self, pattern: str) -> bool:
        """Return whether pattern contains glob wildcard tokens."""
        return any(token in pattern for token in ("*", "?", "["))

    def _is_binary_for_combine(self, path: Path) -> bool:
        """Return whether the file is binary (path-only line), not combined as text.

        Uses presence of NUL bytes; text without NUL may still be decoded via UTF-8 or cp1251 in harrix-pylib.
        """
        return self._file_contains_nul(path)

    def _matches_any_unchecked_pattern(self, candidate_rel: str, candidate_abs: str, patterns: set[str]) -> bool:
        """Return True if candidate path matches any unchecked path or glob pattern."""
        return any(
            self._matches_path_pattern(candidate_abs, pattern)
            or (candidate_rel and self._matches_path_pattern(candidate_rel, pattern))
            for pattern in patterns
        )

    def _matches_path_pattern(self, candidate_path: str, pattern: str) -> bool:
        """Match candidate path against exact path or glob pattern."""
        if not self._has_glob_wildcards(pattern):
            return candidate_path == pattern
        return PurePosixPath(candidate_path).match(pattern)

    def _normalize_extension(self, value: str) -> str:
        """Normalize extension to lowercase '.ext' format."""
        ext = value.strip().lower()
        if not ext:
            return ""
        return ext if ext.startswith(".") else f".{ext}"

    def _normalize_path_for_compare(self, path: str | Path) -> str:
        """Normalize path for case-insensitive compare."""
        return str(path).replace("\\", "/").lower()

    def _relative_path_for_combine(self, file_path: str | Path, base_folder: str | Path | None) -> str:
        """Compute display path for combine output (same rules as harrix-pylib `collect_text_files_to_markdown`)."""
        path_resolve = Path(file_path).resolve()
        base_resolved = Path(base_folder).resolve() if base_folder else None
        if base_resolved and base_resolved in path_resolve.parents:
            rel_path = str(path_resolve.relative_to(base_resolved))
        else:
            rel_path = str(path_resolve)
        return rel_path.replace("\\", "/")

    def _safe_collect_text_files_to_markdown(self, file_paths: list[str | Path], base_folder: str) -> str:
        """Collect files to markdown: full fenced content for text, single `File `path`.` line for binary.

        Binary detection is done before `h.file.collect_text_files_to_markdown` so harrix-pylib does not
        mis-decode binaries as cp1251.
        """
        markdown_parts: list[str] = []
        for file_path in file_paths:
            path_resolve = Path(file_path).resolve()
            rel = self._relative_path_for_combine(file_path, base_folder)
            if self._is_binary_for_combine(path_resolve):
                markdown_parts.append(f"File `{rel}`.")
            else:
                markdown_parts.append(h.file.collect_text_files_to_markdown([file_path], base_folder))
        return "\n".join(markdown_parts)
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

        # Add folder selection option first (same text as in get_folder_with_choice_option)
        folder_selection_option = "📁 Select folder …"
        combination_names = [folder_selection_option] + [f"📁 {combo['name']}" for combo in combinations]

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

        # List items use 📁 prefix for presets; map back to config name
        lookup_name = (
            selected_name.removeprefix("📁 ")
            if selected_name.startswith("📁 ") and selected_name != folder_selection_option
            else selected_name
        )

        # Find the selected combination
        selected_combo = next((combo for combo in combinations if combo["name"] == lookup_name), None)
        if not selected_combo:
            self.add_line(f"❌ Could not find combination: {selected_name}")
            return

        # Get files and base folder from the selected combination
        input_paths = selected_combo["files"]
        base_folder = selected_combo["base_folder"]

        # Check if there are file extensions to filter by
        file_extensions = selected_combo.get("extensions", None)

        # Expand paths (handle directories, glob patterns, etc.)
        all_files = self._expand_path_patterns(input_paths)

        if not all_files:
            self.add_line("❌ No files found matching the specified paths/patterns")
            return

        # Filter by extensions if specified
        if file_extensions:
            all_files = self._filter_files_by_extension(all_files, file_extensions)

        if not all_files:
            self.add_line(f"❌ No files found with extensions: {', '.join(file_extensions)}")
            return

        default_selected = self._get_default_selected_for_combine(all_files, base_folder)

        # Show file selection dialog with checkboxes (all files selected by default)
        selected_files = self.get_checkbox_selection(
            "Select files to combine",
            f"Choose files from '{selected_name}' to combine:",
            all_files,
            default_selected=default_selected,
            enable_extension_filter=True,
        )

        if not selected_files:
            return

        self.add_line(self._safe_collect_text_files_to_markdown(cast("list[str | Path]", selected_files), base_folder))
        self.show_result()
```

</details>

### ⚙️ Method `_expand_path_patterns`

```python
def _expand_path_patterns(self, paths: list[str]) -> list[str]
```

Expand path patterns to actual file paths.

Processes paths that may be direct files, directories, or glob patterns.

<details>
<summary>Code:</summary>

```python
def _expand_path_patterns(self, paths: list[str]) -> list[str]:
        expanded_paths = []

        for original_path in paths:
            path = original_path.strip()
            if not path:
                continue

            # Check if it's a glob pattern (contains * or ?)
            if "*" in path or "?" in path:
                # Find the base directory (before any wildcards) and the pattern
                # Split path at the first wildcard occurrence
                parts = path.replace("\\", "/").split("/")
                base_parts = []
                pattern_parts = []
                found_wildcard = False

                for part in parts:
                    if not found_wildcard and "*" not in part and "?" not in part:
                        base_parts.append(part)
                    else:
                        found_wildcard = True
                        pattern_parts.append(part)

                # Reconstruct base directory and pattern
                base_dir = "/".join(base_parts) if base_parts else "."
                pattern = "/".join(pattern_parts) if pattern_parts else "*"

                # Use rglob if pattern contains ** or glob otherwise
                base_path = Path(base_dir)
                if base_path.exists() and base_path.is_dir():
                    matches = (
                        base_path.rglob(pattern.replace("**/", "")) if "**" in pattern else base_path.glob(pattern)
                    )
                    expanded_paths.extend(
                        str(match) for match in matches if match.is_file() and not h.file.should_ignore_path(match)
                    )
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
                # Try to find base directory and pattern
                parts = path.replace("\\", "/").split("/")
                base_parts = []
                pattern_parts = []
                found_wildcard = False

                for part in parts:
                    if not found_wildcard and "*" not in part and "?" not in part:
                        base_parts.append(part)
                    else:
                        found_wildcard = True
                        pattern_parts.append(part)

                base_dir = "/".join(base_parts) if base_parts else "."
                pattern = "/".join(pattern_parts) if pattern_parts else "*"

                base_path = Path(base_dir)
                if base_path.exists() and base_path.is_dir():
                    matches = (
                        base_path.rglob(pattern.replace("**/", "")) if "**" in pattern else base_path.glob(pattern)
                    )
                    expanded_paths.extend(
                        str(match) for match in matches if match.is_file() and not h.file.should_ignore_path(match)
                    )

        return expanded_paths
```

</details>

### ⚙️ Method `_file_contains_nul`

```python
def _file_contains_nul(self, path: Path) -> bool
```

Return True if the file contains a null byte (streamed read, no full-file load).

<details>
<summary>Code:</summary>

```python
def _file_contains_nul(self, path: Path) -> bool:
        with path.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    return False
                if b"\x00" in chunk:
                    return True
```

</details>

### ⚙️ Method `_filter_files_by_extension`

```python
def _filter_files_by_extension(self, files: list[str], extensions: list[str] | None = None) -> list[str]
```

Filter files by extension.

<details>
<summary>Code:</summary>

```python
def _filter_files_by_extension(self, files: list[str], extensions: list[str] | None = None) -> list[str]:
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

### ⚙️ Method `_get_default_selected_for_combine`

```python
def _get_default_selected_for_combine(self, all_files: list[str], base_folder: str) -> list[str]
```

Return default selected files after applying pre-uncheck config rules.

<details>
<summary>Code:</summary>

```python
def _get_default_selected_for_combine(self, all_files: list[str], base_folder: str) -> list[str]:
        unchecked_extensions = {
            self._normalize_extension(ext)
            for ext in cast("list[str]", self.config.get("combine_for_ai_unchecked_extensions", []))
            if self._normalize_extension(ext)
        }

        unchecked_file_patterns = {
            self._normalize_path_for_compare(path)
            for path in cast("list[str]", self.config.get("combine_for_ai_unchecked_files", []))
            if str(path).strip()
        }

        base_path = Path(base_folder).resolve()
        selected_files: list[str] = []

        for file_path in all_files:
            candidate = Path(file_path).resolve()
            candidate_ext = candidate.suffix.lower()
            candidate_abs = self._normalize_path_for_compare(candidate)

            candidate_rel = ""
            if base_path in candidate.parents:
                candidate_rel = self._normalize_path_for_compare(candidate.relative_to(base_path))

            should_uncheck = candidate_ext in unchecked_extensions
            if self._matches_any_unchecked_pattern(candidate_rel, candidate_abs, unchecked_file_patterns):
                should_uncheck = True

            if not should_uncheck:
                selected_files.append(file_path)

        return selected_files
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
        selected_folder = self.get_existing_directory("Select folder", default_path)
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

        default_selected = self._get_default_selected_for_combine(all_files, str(selected_folder))

        # Show file selection dialog with checkboxes (all files selected by default)
        selected_files = self.get_checkbox_selection(
            "Select files to combine",
            f"Choose files from '{selected_folder}' to combine:",
            all_files,
            default_selected=default_selected,
            enable_extension_filter=True,
        )

        if not selected_files:
            return

        # Use the selected folder as base folder
        self.add_line(
            self._safe_collect_text_files_to_markdown(cast("list[str | Path]", selected_files), str(selected_folder))
        )
        self.show_result()
```

</details>

### ⚙️ Method `_has_glob_wildcards`

```python
def _has_glob_wildcards(self, pattern: str) -> bool
```

Return whether pattern contains glob wildcard tokens.

<details>
<summary>Code:</summary>

```python
def _has_glob_wildcards(self, pattern: str) -> bool:
        return any(token in pattern for token in ("*", "?", "["))
```

</details>

### ⚙️ Method `_is_binary_for_combine`

```python
def _is_binary_for_combine(self, path: Path) -> bool
```

Return whether the file is binary (path-only line), not combined as text.

Uses presence of NUL bytes; text without NUL may still be decoded via UTF-8 or cp1251 in harrix-pylib.

<details>
<summary>Code:</summary>

```python
def _is_binary_for_combine(self, path: Path) -> bool:
        return self._file_contains_nul(path)
```

</details>

### ⚙️ Method `_matches_any_unchecked_pattern`

```python
def _matches_any_unchecked_pattern(self, candidate_rel: str, candidate_abs: str, patterns: set[str]) -> bool
```

Return True if candidate path matches any unchecked path or glob pattern.

<details>
<summary>Code:</summary>

```python
def _matches_any_unchecked_pattern(self, candidate_rel: str, candidate_abs: str, patterns: set[str]) -> bool:
        return any(
            self._matches_path_pattern(candidate_abs, pattern)
            or (candidate_rel and self._matches_path_pattern(candidate_rel, pattern))
            for pattern in patterns
        )
```

</details>

### ⚙️ Method `_matches_path_pattern`

```python
def _matches_path_pattern(self, candidate_path: str, pattern: str) -> bool
```

Match candidate path against exact path or glob pattern.

<details>
<summary>Code:</summary>

```python
def _matches_path_pattern(self, candidate_path: str, pattern: str) -> bool:
        if not self._has_glob_wildcards(pattern):
            return candidate_path == pattern
        return PurePosixPath(candidate_path).match(pattern)
```

</details>

### ⚙️ Method `_normalize_extension`

```python
def _normalize_extension(self, value: str) -> str
```

Normalize extension to lowercase '.ext' format.

<details>
<summary>Code:</summary>

```python
def _normalize_extension(self, value: str) -> str:
        ext = value.strip().lower()
        if not ext:
            return ""
        return ext if ext.startswith(".") else f".{ext}"
```

</details>

### ⚙️ Method `_normalize_path_for_compare`

```python
def _normalize_path_for_compare(self, path: str | Path) -> str
```

Normalize path for case-insensitive compare.

<details>
<summary>Code:</summary>

```python
def _normalize_path_for_compare(self, path: str | Path) -> str:
        return str(path).replace("\\", "/").lower()
```

</details>

### ⚙️ Method `_relative_path_for_combine`

```python
def _relative_path_for_combine(self, file_path: str | Path, base_folder: str | Path | None) -> str
```

Compute display path for combine output (same rules as harrix-pylib `collect_text_files_to_markdown`).

<details>
<summary>Code:</summary>

```python
def _relative_path_for_combine(self, file_path: str | Path, base_folder: str | Path | None) -> str:
        path_resolve = Path(file_path).resolve()
        base_resolved = Path(base_folder).resolve() if base_folder else None
        if base_resolved and base_resolved in path_resolve.parents:
            rel_path = str(path_resolve.relative_to(base_resolved))
        else:
            rel_path = str(path_resolve)
        return rel_path.replace("\\", "/")
```

</details>

### ⚙️ Method `_safe_collect_text_files_to_markdown`

```python
def _safe_collect_text_files_to_markdown(self, file_paths: list[str | Path], base_folder: str) -> str
```

Collect files to markdown: full fenced content for text, single `File `path`.` line for binary.

Binary detection is done before `h.file.collect_text_files_to_markdown` so harrix-pylib does not
mis-decode binaries as cp1251.

<details>
<summary>Code:</summary>

```python
def _safe_collect_text_files_to_markdown(self, file_paths: list[str | Path], base_folder: str) -> str:
        markdown_parts: list[str] = []
        for file_path in file_paths:
            path_resolve = Path(file_path).resolve()
            rel = self._relative_path_for_combine(file_path, base_folder)
            if self._is_binary_for_combine(path_resolve):
                markdown_parts.append(f"File `{rel}`.")
            else:
                markdown_parts.append(h.file.collect_text_files_to_markdown([file_path], base_folder))
        return "\n".join(markdown_parts)
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
        self.folder_path = self.get_existing_directory("Select folder with ZIP archives", self.config["path_3d"])
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
        self.folder_path = self.get_existing_directory("Select folder with ZIP archives", self.config["path_3d"])
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
        folder_path = self.get_existing_directory("Select folder", self.config["path_3d"])
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
        folder_path = self.get_existing_directory("Select folder", self.config["path_3d"])
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
        folder_path = self.get_existing_directory("Select folder", self.config["path_3d"])
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
        folder_path = self.get_existing_directory("Select folder", self.config["path_3d"])
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
        self.folder_path = self.get_existing_directory("Select folder to clean empty folders", self.config["path_3d"])
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
        self.folder_path = self.get_existing_directory("Select folder to clean empty folders", self.config["path_3d"])
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
            "Select folder with FB2, Epub, PDF files", self.config["path_books"]
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
            "Select folder with FB2, Epub, PDF files", self.config["path_books"]
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
        self.folder_path = self.get_existing_directory("Select folder to rename files", self.config["path_3d"])
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

        -`mapping_text` (`str`): Text with `old_filename<TAB>new_filename` per line.

        Returns:

        - `dict[str, str] | None`: Dictionary mapping old names to new names, or None if error.

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
        self.folder_path = self.get_existing_directory("Select folder to rename files", self.config["path_3d"])
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

-`mapping_text` (`str`): Text with `old_filename<TAB>new_filename` per line.

Returns:

- `dict[str, str] | None`: Dictionary mapping old names to new names, or None if error.

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
        folder_path = self.get_existing_directory("Select folder", self.config["path_3d"])
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
        folder_path = self.get_existing_directory("Select folder", self.config["path_3d"])
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

Git commit subject: add emoji by keyword, rename last commit, or rename by hash.

Offers three modes after choosing a repository: append emoji to the latest commit only
(unchanged text), set a new message for HEAD (with optional emoji), or reword a commit
by hash via interactive rebase (with optional emoji). Emoji rules match keyword prefixes
in `EMOJI_MAPPING` when the subject does not already start with a mapped emoji.

<details>
<summary>Code:</summary>

```python
class OnRenameLastGitCommitWithEmoji(ActionBase):

    icon = "🎯"
    title = "Git commit message (emoji / rename)"

    _MODE_CHOICES: ClassVar[list[tuple[str, str, str]]] = [
        ("➕", "Add emoji (last commit)", "_mode_add_emoji_last"),  # noqa: RUF001
        ("✒️", "Rename last commit", "_mode_rename_last"),
        ("🔑", "Rename by hash", "_mode_rename_by_hash"),
    ]

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

    _SEQUENCE_EDITOR_SCRIPT = r"""import os
import subprocess
import sys
from pathlib import Path


def _resolve(repo: str, ref: str) -> str:
    r = subprocess.run(
        ["git", "-C", repo, "rev-parse", ref],
        capture_output=True,
        text=True,
        check=False,
    )
    return r.stdout.strip() if r.returncode == 0 else ""


def main() -> None:
    repo = os.environ["HARRIX_GIT_REPO"]
    target = os.environ["HARRIX_TARGET_FULL"]
    todo_path = sys.argv[1]
    lines = Path(todo_path).read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    changed = False
    for line in lines:
        parts = line.split(None, 2)
        if len(parts) >= 2 and parts[0] == "pick" and _resolve(repo, parts[1]) == target:
            line = line.replace("pick ", "reword ", 1)
            changed = True
        out.append(line)
    if not changed:
        sys.stderr.write("harrix: could not find pick line for target commit\n")
        raise SystemExit(1)
    Path(todo_path).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
"""

    _MSG_EDITOR_SOURCE = r"""import os
import sys
from pathlib import Path

Path(sys.argv[1]).write_text(os.environ["HARRIX_NEW_SUBJECT"] + "\n", encoding="utf-8")
"""

    @ActionBase.handle_exceptions("Git commit message (emoji / rename)")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(self.config["paths_git"], self.config["path_github"])
        if not self.folder_path:
            return

        self.add_line(f"🔵 Processing git repository: {self.folder_path}")

        choices = [(icon, title) for icon, title, _ in self._MODE_CHOICES]
        selected = self.get_choice_from_icons("Git commit message", "Choose an action:", choices)
        if not selected:
            return

        method_name = next((m for _, t, m in self._MODE_CHOICES if t == selected), None)
        if not method_name:
            self.add_line(f"❌ Unknown choice: {selected}")
            self.show_result()
            return

        original_cwd = Path.cwd()
        os.chdir(self.folder_path)

        try:
            getattr(self, method_name)(self.folder_path)
        finally:
            os.chdir(original_cwd)

        self.show_result()

    def _amend_with_message(self, folder_path: Path, new_message: str) -> None:
        self.add_line(f"🔄 Amending commit with new message: {new_message}")
        escaped = new_message.replace('"', '\\"')
        out = self._git_out(f'git commit --amend -m "{escaped}"', folder_path)
        self.add_line("✅ Commit amended successfully")
        self.add_line(f"📊 Git output: {out}")

    def _apply_keyword_emoji_prefix(self, subject: str) -> str:
        if self._subject_has_mapped_emoji_prefix(subject):
            return subject
        for keyword, emoji in self.EMOJI_MAPPING.items():
            if subject.startswith(keyword):
                self.add_line(f"🎯 Found keyword '{keyword}', adding emoji {emoji}")
                return f"{emoji} {subject}"
        return subject

    def _git_out(self, cmd: str, cwd: Path) -> str:
        return h.dev.run_command(cmd, cwd=str(cwd))

    @staticmethod
    def _git_subprocess(
        args: list[str],
        cwd: Path,
        *,
        env: dict[str, str] | None = None,
        capture_output: bool = False,
        text: bool = False,
        check: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],  # noqa: S607
            cwd=cwd,
            env=env,
            capture_output=capture_output,
            text=text,
            check=check,
        )

    def _mapped_emojis_sorted(self) -> list[str]:
        emojis: set[str] = set(self.EMOJI_MAPPING.values())

        def _len_str(s: str) -> int:
            return len(s)

        return sorted(emojis, key=_len_str, reverse=True)

    def _mode_add_emoji_last(self, folder_path: Path) -> None:
        result = self._git_out("git log -1 --pretty=format:%s", folder_path)
        if not result.strip():
            self.add_line("❌ No git commits found or not a git repository")
            return

        last_commit_message = result.strip()
        self.add_line(f"📝 Last commit message: {last_commit_message}")

        if self._subject_has_mapped_emoji_prefix(last_commit_message):
            self.add_line("✅ Emoji already present in commit message")
            return

        new_message = None
        for keyword, emoji in self.EMOJI_MAPPING.items():
            if last_commit_message.startswith(keyword):
                new_message = f"{emoji} {last_commit_message}"
                self.add_line(f"🎯 Found keyword '{keyword}', adding emoji {emoji}")
                break

        if not new_message:
            self.add_line("ℹ️ No matching keyword found, no changes needed")  # noqa: RUF001
            return

        self._amend_with_message(folder_path, new_message)
        self._push_current_branch(folder_path)

    def _mode_rename_by_hash(self, folder_path: Path) -> None:
        hash_raw = self.get_text_input("Commit hash", "Enter commit hash to reword:", "")
        if hash_raw is None:
            return

        commit_ref = f"{hash_raw}^{{commit}}"
        verify_p = self._git_subprocess(
            ["rev-parse", "--verify", commit_ref],
            folder_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if verify_p.returncode != 0:
            self.add_line(f"❌ Invalid commit: {hash_raw}")
            return

        full_p = self._git_subprocess(
            ["rev-parse", hash_raw],
            folder_path,
            capture_output=True,
            text=True,
            check=False,
        )
        full_hash = full_p.stdout.strip()
        if not full_hash:
            self.add_line("❌ Could not resolve commit hash")
            return

        anc = self._git_subprocess(
            ["merge-base", "--is-ancestor", full_hash, "HEAD"],
            folder_path,
            capture_output=True,
            check=False,
        )
        if anc.returncode != 0:
            self.add_line("❌ That commit is not an ancestor of HEAD on this branch")
            return

        parent_check = self._git_subprocess(
            ["rev-parse", "--verify", f"{full_hash}^"],
            folder_path,
            capture_output=True,
            check=False,
        )
        if parent_check.returncode != 0:
            self.add_line("❌ Cannot reword root commit with this flow (no parent). Use another Git workflow.")
            return

        old_subject = self._git_out(f"git log -1 {full_hash} --pretty=format:%s", folder_path).strip()
        if not old_subject:
            self.add_line("❌ Could not read commit message")
            return

        self.add_line(f"📝 Current message for {full_hash[:7]}: {old_subject}")
        raw = self.get_text_input("New message", "New commit message (subject line):", old_subject)
        if raw is None:
            return

        final_subject = self._apply_keyword_emoji_prefix(raw)
        if final_subject != raw:
            self.add_line(f"📝 Message after emoji rule: {final_subject}")

        if not self._run_rebase_reword(folder_path, full_hash, final_subject):
            return
        self._push_current_branch(folder_path)

    def _mode_rename_last(self, folder_path: Path) -> None:
        result = self._git_out("git log -1 --pretty=format:%s", folder_path)
        if not result.strip():
            self.add_line("❌ No git commits found or not a git repository")
            return

        default_subject = result.strip()
        self.add_line(f"📝 Current last commit message: {default_subject}")
        raw = self.get_text_input("Rename last commit", "New commit message (subject line):", default_subject)
        if raw is None:
            return

        final_subject = self._apply_keyword_emoji_prefix(raw)
        if final_subject != raw:
            self.add_line(f"📝 Message after emoji rule: {final_subject}")

        self._amend_with_message(folder_path, final_subject)
        self._push_current_branch(folder_path)

    def _push_current_branch(self, folder_path: Path) -> None:
        branch = self._git_out("git rev-parse --abbrev-ref HEAD", folder_path).strip()
        if branch == "HEAD":
            self.add_line("❌ Detached HEAD: cannot push (no current branch name)")
            return
        escaped_branch = branch.replace('"', '\\"')
        out = self._git_out(f'git push origin "{escaped_branch}" --force', folder_path)
        self.add_line(f"✅ Push finished: {out}")

    def _run_rebase_reword(self, folder_path: Path, full_hash: str, new_subject: str) -> bool:
        repo = str(folder_path.resolve())
        seq_script: Path | None = None
        msg_script: Path | None = None
        env = os.environ.copy()
        env["HARRIX_GIT_REPO"] = repo
        env["HARRIX_TARGET_FULL"] = full_hash
        env["HARRIX_NEW_SUBJECT"] = new_subject
        completed: subprocess.CompletedProcess[str] | None = None
        try:
            seq_script = self._write_temp_editor(self._SEQUENCE_EDITOR_SCRIPT)
            msg_script = self._write_temp_editor(self._MSG_EDITOR_SOURCE)
            seq_q = shlex.quote(str(seq_script))
            exe_q = shlex.quote(sys.executable)
            env["GIT_SEQUENCE_EDITOR"] = f"{exe_q} {seq_q}"
            env["GIT_EDITOR"] = f"{exe_q} {shlex.quote(str(msg_script))}"
            parent = f"{full_hash}^"
            completed = self._git_subprocess(
                ["rebase", "-i", parent],
                folder_path,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            if seq_script is not None:
                seq_script.unlink(missing_ok=True)
            if msg_script is not None:
                msg_script.unlink(missing_ok=True)
        if completed is None:
            return False
        if completed.stdout:
            self.add_line(completed.stdout.rstrip())
        if completed.stderr:
            self.add_line(completed.stderr.rstrip())
        if completed.returncode != 0:
            msg = f"❌ git rebase failed (exit {completed.returncode}). Run `git rebase --abort` in the repo if needed."
            self.add_line(msg)
            return False
        self.add_line("✅ Rebase finished; commit message updated")
        return True

    def _subject_has_mapped_emoji_prefix(self, subject: str) -> bool:
        stripped = subject.lstrip()
        return any(stripped.startswith(emoji) for emoji in self._mapped_emojis_sorted())

    def _write_temp_editor(self, source: str) -> Path:
        root = h.dev.get_project_root() / "temp"
        root.mkdir(parents=True, exist_ok=True)
        fd, str_path = tempfile.mkstemp(suffix=".py", prefix="hsk_git_", dir=root)
        os.close(fd)
        path = Path(str_path)
        path.write_text(source, encoding="utf-8")
        return path
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
        self.folder_path = self.get_folder_with_choice_option(self.config["paths_git"], self.config["path_github"])
        if not self.folder_path:
            return

        self.add_line(f"🔵 Processing git repository: {self.folder_path}")

        choices = [(icon, title) for icon, title, _ in self._MODE_CHOICES]
        selected = self.get_choice_from_icons("Git commit message", "Choose an action:", choices)
        if not selected:
            return

        method_name = next((m for _, t, m in self._MODE_CHOICES if t == selected), None)
        if not method_name:
            self.add_line(f"❌ Unknown choice: {selected}")
            self.show_result()
            return

        original_cwd = Path.cwd()
        os.chdir(self.folder_path)

        try:
            getattr(self, method_name)(self.folder_path)
        finally:
            os.chdir(original_cwd)

        self.show_result()
```

</details>

### ⚙️ Method `_amend_with_message`

```python
def _amend_with_message(self, folder_path: Path, new_message: str) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _amend_with_message(self, folder_path: Path, new_message: str) -> None:
        self.add_line(f"🔄 Amending commit with new message: {new_message}")
        escaped = new_message.replace('"', '\\"')
        out = self._git_out(f'git commit --amend -m "{escaped}"', folder_path)
        self.add_line("✅ Commit amended successfully")
        self.add_line(f"📊 Git output: {out}")
```

</details>

### ⚙️ Method `_apply_keyword_emoji_prefix`

```python
def _apply_keyword_emoji_prefix(self, subject: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _apply_keyword_emoji_prefix(self, subject: str) -> str:
        if self._subject_has_mapped_emoji_prefix(subject):
            return subject
        for keyword, emoji in self.EMOJI_MAPPING.items():
            if subject.startswith(keyword):
                self.add_line(f"🎯 Found keyword '{keyword}', adding emoji {emoji}")
                return f"{emoji} {subject}"
        return subject
```

</details>

### ⚙️ Method `_git_out`

```python
def _git_out(self, cmd: str, cwd: Path) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _git_out(self, cmd: str, cwd: Path) -> str:
        return h.dev.run_command(cmd, cwd=str(cwd))
```

</details>

### ⚙️ Method `_git_subprocess`

```python
def _git_subprocess(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _git_subprocess(
        args: list[str],
        cwd: Path,
        *,
        env: dict[str, str] | None = None,
        capture_output: bool = False,
        text: bool = False,
        check: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],  # noqa: S607
            cwd=cwd,
            env=env,
            capture_output=capture_output,
            text=text,
            check=check,
        )
```

</details>

### ⚙️ Method `_mapped_emojis_sorted`

```python
def _mapped_emojis_sorted(self) -> list[str]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _mapped_emojis_sorted(self) -> list[str]:
        emojis: set[str] = set(self.EMOJI_MAPPING.values())

        def _len_str(s: str) -> int:
            return len(s)

        return sorted(emojis, key=_len_str, reverse=True)
```

</details>

### ⚙️ Method `_mode_add_emoji_last`

```python
def _mode_add_emoji_last(self, folder_path: Path) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _mode_add_emoji_last(self, folder_path: Path) -> None:
        result = self._git_out("git log -1 --pretty=format:%s", folder_path)
        if not result.strip():
            self.add_line("❌ No git commits found or not a git repository")
            return

        last_commit_message = result.strip()
        self.add_line(f"📝 Last commit message: {last_commit_message}")

        if self._subject_has_mapped_emoji_prefix(last_commit_message):
            self.add_line("✅ Emoji already present in commit message")
            return

        new_message = None
        for keyword, emoji in self.EMOJI_MAPPING.items():
            if last_commit_message.startswith(keyword):
                new_message = f"{emoji} {last_commit_message}"
                self.add_line(f"🎯 Found keyword '{keyword}', adding emoji {emoji}")
                break

        if not new_message:
            self.add_line("ℹ️ No matching keyword found, no changes needed")  # noqa: RUF001
            return

        self._amend_with_message(folder_path, new_message)
        self._push_current_branch(folder_path)
```

</details>

### ⚙️ Method `_mode_rename_by_hash`

```python
def _mode_rename_by_hash(self, folder_path: Path) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _mode_rename_by_hash(self, folder_path: Path) -> None:
        hash_raw = self.get_text_input("Commit hash", "Enter commit hash to reword:", "")
        if hash_raw is None:
            return

        commit_ref = f"{hash_raw}^{{commit}}"
        verify_p = self._git_subprocess(
            ["rev-parse", "--verify", commit_ref],
            folder_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if verify_p.returncode != 0:
            self.add_line(f"❌ Invalid commit: {hash_raw}")
            return

        full_p = self._git_subprocess(
            ["rev-parse", hash_raw],
            folder_path,
            capture_output=True,
            text=True,
            check=False,
        )
        full_hash = full_p.stdout.strip()
        if not full_hash:
            self.add_line("❌ Could not resolve commit hash")
            return

        anc = self._git_subprocess(
            ["merge-base", "--is-ancestor", full_hash, "HEAD"],
            folder_path,
            capture_output=True,
            check=False,
        )
        if anc.returncode != 0:
            self.add_line("❌ That commit is not an ancestor of HEAD on this branch")
            return

        parent_check = self._git_subprocess(
            ["rev-parse", "--verify", f"{full_hash}^"],
            folder_path,
            capture_output=True,
            check=False,
        )
        if parent_check.returncode != 0:
            self.add_line("❌ Cannot reword root commit with this flow (no parent). Use another Git workflow.")
            return

        old_subject = self._git_out(f"git log -1 {full_hash} --pretty=format:%s", folder_path).strip()
        if not old_subject:
            self.add_line("❌ Could not read commit message")
            return

        self.add_line(f"📝 Current message for {full_hash[:7]}: {old_subject}")
        raw = self.get_text_input("New message", "New commit message (subject line):", old_subject)
        if raw is None:
            return

        final_subject = self._apply_keyword_emoji_prefix(raw)
        if final_subject != raw:
            self.add_line(f"📝 Message after emoji rule: {final_subject}")

        if not self._run_rebase_reword(folder_path, full_hash, final_subject):
            return
        self._push_current_branch(folder_path)
```

</details>

### ⚙️ Method `_mode_rename_last`

```python
def _mode_rename_last(self, folder_path: Path) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _mode_rename_last(self, folder_path: Path) -> None:
        result = self._git_out("git log -1 --pretty=format:%s", folder_path)
        if not result.strip():
            self.add_line("❌ No git commits found or not a git repository")
            return

        default_subject = result.strip()
        self.add_line(f"📝 Current last commit message: {default_subject}")
        raw = self.get_text_input("Rename last commit", "New commit message (subject line):", default_subject)
        if raw is None:
            return

        final_subject = self._apply_keyword_emoji_prefix(raw)
        if final_subject != raw:
            self.add_line(f"📝 Message after emoji rule: {final_subject}")

        self._amend_with_message(folder_path, final_subject)
        self._push_current_branch(folder_path)
```

</details>

### ⚙️ Method `_push_current_branch`

```python
def _push_current_branch(self, folder_path: Path) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _push_current_branch(self, folder_path: Path) -> None:
        branch = self._git_out("git rev-parse --abbrev-ref HEAD", folder_path).strip()
        if branch == "HEAD":
            self.add_line("❌ Detached HEAD: cannot push (no current branch name)")
            return
        escaped_branch = branch.replace('"', '\\"')
        out = self._git_out(f'git push origin "{escaped_branch}" --force', folder_path)
        self.add_line(f"✅ Push finished: {out}")
```

</details>

### ⚙️ Method `_run_rebase_reword`

```python
def _run_rebase_reword(self, folder_path: Path, full_hash: str, new_subject: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _run_rebase_reword(self, folder_path: Path, full_hash: str, new_subject: str) -> bool:
        repo = str(folder_path.resolve())
        seq_script: Path | None = None
        msg_script: Path | None = None
        env = os.environ.copy()
        env["HARRIX_GIT_REPO"] = repo
        env["HARRIX_TARGET_FULL"] = full_hash
        env["HARRIX_NEW_SUBJECT"] = new_subject
        completed: subprocess.CompletedProcess[str] | None = None
        try:
            seq_script = self._write_temp_editor(self._SEQUENCE_EDITOR_SCRIPT)
            msg_script = self._write_temp_editor(self._MSG_EDITOR_SOURCE)
            seq_q = shlex.quote(str(seq_script))
            exe_q = shlex.quote(sys.executable)
            env["GIT_SEQUENCE_EDITOR"] = f"{exe_q} {seq_q}"
            env["GIT_EDITOR"] = f"{exe_q} {shlex.quote(str(msg_script))}"
            parent = f"{full_hash}^"
            completed = self._git_subprocess(
                ["rebase", "-i", parent],
                folder_path,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            if seq_script is not None:
                seq_script.unlink(missing_ok=True)
            if msg_script is not None:
                msg_script.unlink(missing_ok=True)
        if completed is None:
            return False
        if completed.stdout:
            self.add_line(completed.stdout.rstrip())
        if completed.stderr:
            self.add_line(completed.stderr.rstrip())
        if completed.returncode != 0:
            msg = f"❌ git rebase failed (exit {completed.returncode}). Run `git rebase --abort` in the repo if needed."
            self.add_line(msg)
            return False
        self.add_line("✅ Rebase finished; commit message updated")
        return True
```

</details>

### ⚙️ Method `_subject_has_mapped_emoji_prefix`

```python
def _subject_has_mapped_emoji_prefix(self, subject: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _subject_has_mapped_emoji_prefix(self, subject: str) -> bool:
        stripped = subject.lstrip()
        return any(stripped.startswith(emoji) for emoji in self._mapped_emojis_sorted())
```

</details>

### ⚙️ Method `_write_temp_editor`

```python
def _write_temp_editor(self, source: str) -> Path
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _write_temp_editor(self, source: str) -> Path:
        root = h.dev.get_project_root() / "temp"
        root.mkdir(parents=True, exist_ok=True)
        fd, str_path = tempfile.mkstemp(suffix=".py", prefix="hsk_git_", dir=root)
        os.close(fd)
        path = Path(str_path)
        path.write_text(source, encoding="utf-8")
        return path
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
        folder_path = self.get_existing_directory("Select folder", self.config["path_3d"])
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
        folder_path = self.get_existing_directory("Select folder", self.config["path_3d"])
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
