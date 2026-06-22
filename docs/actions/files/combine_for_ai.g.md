---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `combine_for_ai.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnCombineForAI`](#️-class-oncombineforai)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `_expand_path_patterns`](#️-method-_expand_path_patterns)
  - [⚙️ Method `_file_contains_nul`](#️-method-_file_contains_nul)
  - [⚙️ Method `_filter_files_by_extension`](#️-method-_filter_files_by_extension)
  - [⚙️ Method `_get_default_selected_for_combine`](#️-method-_get_default_selected_for_combine)
  - [⚙️ Method `_handle_folder_selection`](#️-method-_handle_folder_selection)
  - [⚙️ Method `_has_glob_wildcards`](#️-method-_has_glob_wildcards)
  - [⚙️ Method `_is_binary_for_combine`](#️-method-_is_binary_for_combine)
  - [⚙️ Method `_matches_any_unchecked_pattern`](#️-method-_matches_any_unchecked_pattern)
  - [⚙️ Method `_matches_path_pattern`](#️-method-_matches_path_pattern)
  - [⚙️ Method `_normalize_extension`](#️-method-_normalize_extension)
  - [⚙️ Method `_normalize_path_for_compare`](#️-method-_normalize_path_for_compare)
  - [⚙️ Method `_relative_path_for_combine`](#️-method-_relative_path_for_combine)
  - [⚙️ Method `_safe_collect_text_files_to_markdown`](#️-method-_safe_collect_text_files_to_markdown)
  - [⚙️ Method `_should_ignore_path`](#️-method-_should_ignore_path)

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
    title = "Combine files for AI…"
    bold_title = True

    @ActionBase.handle_exceptions("combining files for AI")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Combine multiple text files into a single Markdown document for AI processing."""
        # Get list of available combinations from config
        combinations = self.config.get("paths_combine_for_ai", [])

        # Add folder selection option first (same text as in get_folder_with_choice_option)
        folder_selection_option = "📁 Select folder …"
        combination_names = [folder_selection_option] + [f"📁 {combo['name']}" for combo in combinations]

        # Let user select a combination or folder
        selected_name = self.dialogs.get_choice_from_list(
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
        selected_files = self.dialogs.get_checkbox_selection(
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
                    walk_base = base_path.resolve()
                    matches = (
                        base_path.rglob(pattern.replace("**/", "")) if "**" in pattern else base_path.glob(pattern)
                    )
                    expanded_paths.extend(
                        str(match)
                        for match in matches
                        if match.is_file() and not self._should_ignore_path(match, base=walk_base)
                    )
            elif Path(path).is_file():
                # It's a direct file path - check if it should be ignored
                if not self._should_ignore_path(Path(path)):
                    expanded_paths.append(path)
            elif Path(path).is_dir():
                # It's a directory, find all files recursively
                walk_base = Path(path).resolve()
                for root, dirs, files in os.walk(path):
                    # Filter out ignored directories
                    dirs[:] = [d for d in dirs if not self._should_ignore_path(Path(root) / d, base=walk_base)]

                    for file in files:
                        file_path = Path(root) / file
                        # Check if the file should be ignored
                        if not self._should_ignore_path(file_path, base=walk_base):
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
                    walk_base = base_path.resolve()
                    matches = (
                        base_path.rglob(pattern.replace("**/", "")) if "**" in pattern else base_path.glob(pattern)
                    )
                    expanded_paths.extend(
                        str(match)
                        for match in matches
                        if match.is_file() and not self._should_ignore_path(match, base=walk_base)
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
        selected_folder = self.dialogs.get_existing_directory("Select folder", default_path)
        if not selected_folder:
            return

        # Find all files recursively in the selected folder, filtering ignored paths
        walk_base = Path(selected_folder).resolve()
        all_files = []
        for root, dirs, files in os.walk(selected_folder):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore_path(Path(root) / d, base=walk_base)]

            for file in files:
                file_path = Path(root) / file
                # Check if the file should be ignored
                if not self._should_ignore_path(file_path, base=walk_base):
                    all_files.append(str(file_path))

        if not all_files:
            self.add_line("❌ No files found in the selected folder (after filtering ignored paths)")
            return

        default_selected = self._get_default_selected_for_combine(all_files, str(selected_folder))

        # Show file selection dialog with checkboxes (all files selected by default)
        selected_files = self.dialogs.get_checkbox_selection(
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

    @staticmethod
    def _should_ignore_path(path: Path | str, *, base: Path | str | None = None) -> bool:
        """Return whether *path* should be skipped (relative to *base* when given)."""
        path_obj = Path(path).resolve()
        if base is not None:
            with contextlib.suppress(ValueError):
                path_obj = path_obj.relative_to(Path(base).resolve())
        return h.file.should_ignore_path(path_obj)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Combine multiple text files into a single Markdown document for AI processing.

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
        selected_name = self.dialogs.get_choice_from_list(
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
        selected_files = self.dialogs.get_checkbox_selection(
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
                    walk_base = base_path.resolve()
                    matches = (
                        base_path.rglob(pattern.replace("**/", "")) if "**" in pattern else base_path.glob(pattern)
                    )
                    expanded_paths.extend(
                        str(match)
                        for match in matches
                        if match.is_file() and not self._should_ignore_path(match, base=walk_base)
                    )
            elif Path(path).is_file():
                # It's a direct file path - check if it should be ignored
                if not self._should_ignore_path(Path(path)):
                    expanded_paths.append(path)
            elif Path(path).is_dir():
                # It's a directory, find all files recursively
                walk_base = Path(path).resolve()
                for root, dirs, files in os.walk(path):
                    # Filter out ignored directories
                    dirs[:] = [d for d in dirs if not self._should_ignore_path(Path(root) / d, base=walk_base)]

                    for file in files:
                        file_path = Path(root) / file
                        # Check if the file should be ignored
                        if not self._should_ignore_path(file_path, base=walk_base):
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
                    walk_base = base_path.resolve()
                    matches = (
                        base_path.rglob(pattern.replace("**/", "")) if "**" in pattern else base_path.glob(pattern)
                    )
                    expanded_paths.extend(
                        str(match)
                        for match in matches
                        if match.is_file() and not self._should_ignore_path(match, base=walk_base)
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
        selected_folder = self.dialogs.get_existing_directory("Select folder", default_path)
        if not selected_folder:
            return

        # Find all files recursively in the selected folder, filtering ignored paths
        walk_base = Path(selected_folder).resolve()
        all_files = []
        for root, dirs, files in os.walk(selected_folder):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore_path(Path(root) / d, base=walk_base)]

            for file in files:
                file_path = Path(root) / file
                # Check if the file should be ignored
                if not self._should_ignore_path(file_path, base=walk_base):
                    all_files.append(str(file_path))

        if not all_files:
            self.add_line("❌ No files found in the selected folder (after filtering ignored paths)")
            return

        default_selected = self._get_default_selected_for_combine(all_files, str(selected_folder))

        # Show file selection dialog with checkboxes (all files selected by default)
        selected_files = self.dialogs.get_checkbox_selection(
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

### ⚙️ Method `_should_ignore_path`

```python
def _should_ignore_path(path: Path | str) -> bool
```

Return whether _path_ should be skipped (relative to _base_ when given).

<details>
<summary>Code:</summary>

```python
def _should_ignore_path(path: Path | str, *, base: Path | str | None = None) -> bool:
        path_obj = Path(path).resolve()
        if base is not None:
            with contextlib.suppress(ValueError):
                path_obj = path_obj.relative_to(Path(base).resolve())
        return h.file.should_ignore_path(path_obj)
```

</details>
