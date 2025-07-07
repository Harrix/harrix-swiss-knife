---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `funcs_md.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Function `beautify_markdown_common`](#function-beautify_markdown_common)
- [Function `optimize_images_in_md`](#function-optimize_images_in_md)
- [Function `optimize_images_in_md_content`](#function-optimize_images_in_md_content)
- [Function `optimize_images_in_md_png_to_avif`](#function-optimize_images_in_md_png_to_avif)

</details>

## Function `beautify_markdown_common`

```python
def beautify_markdown_common(self: action_base.ActionBase, folder_path: str) -> None
```

Perform common beautification operations on Markdown files in a folder.

This method applies a series of enhancement operations to all Markdown files
in the specified folder, including image caption generation, table of contents
creation, YAML formatting, and Prettier formatting. Optionally includes
summary generation and file combination operations.

Args:

- `folder_path` (`str`): Path to the folder containing Markdown files to process.
- `is_include_summaries_and_combine` (`bool`): Whether to include summary generation
  and file combination steps. Defaults to `False`.

Returns:

- `None`: This method performs operations and logs results but returns nothing.

Note:

- The method preserves the exact execution order of operations for consistency.
- All operations are logged using `self.add_line()` for user feedback.
- If `is_include_summaries_and_combine` is `True`, the method will first delete
  existing `*.g.md` files, then generate summaries and combine files.

<details>
<summary>Code:</summary>

```python
def beautify_markdown_common(
    self: action_base.ActionBase, folder_path: str, *, is_include_summaries_and_combine: bool = False
) -> None:
    if is_include_summaries_and_combine:
        # Delete *.g.md files
        self.add_line("🔵 Delete *.g.md files")
        self.add_line(h.file.apply_func(folder_path, ".md", h.md.delete_g_md_files_recursively))

    # Generate image captions
    self.add_line("🔵 Generate image captions")
    self.add_line(h.file.apply_func(folder_path, ".md", h.md.generate_image_captions))

    # Generate TOC
    self.add_line("🔵 Generate TOC")
    self.add_line(h.file.apply_func(folder_path, ".md", h.md.generate_toc_with_links))

    if is_include_summaries_and_combine:
        # Generate summaries
        self.add_line("🔵 Generate summaries")
        for path_notes_for_summaries in self.config["paths_notes_for_summaries"]:
            if (Path(path_notes_for_summaries).resolve()).is_relative_to(Path(folder_path).resolve()):
                self.add_line(h.md.generate_summaries(path_notes_for_summaries))

        # Combine MD files
        self.add_line("🔵 Combine MD files")
        self.add_line(h.md.combine_markdown_files_recursively(folder_path, is_delete_g_md_files=False))

    # Format YAML
    self.add_line("🔵 Format YAML")
    self.add_line(h.file.apply_func(folder_path, ".md", h.md.format_yaml))

    # Prettier
    self.add_line("🔵 Prettier")
    commands = f"cd {folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
    result = h.dev.run_powershell_script(commands)
    self.add_line(result)
```

</details>

## Function `optimize_images_in_md`

```python
def optimize_images_in_md(filename: Path | str) -> str
```

Optimize images in a Markdown file by converting them to more efficient formats.

This function reads a Markdown file, processes any local images referenced in it,
optimizes them, and updates the Markdown content to reference the optimized images.

Args:

- `filename` (`Path | str`): Path to the Markdown file to process.

Returns:

- `str`: A status message indicating whether the file was modified.

<details>
<summary>Code:</summary>

```python
def optimize_images_in_md(filename: Path | str) -> str:
    filename = Path(filename)
    with Path.open(filename, encoding="utf-8") as f:
        document = f.read()

    document_new = optimize_images_in_md_content(document, filename.parent, is_convert_png_to_avif=False)

    if document != document_new:
        with Path.open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} applied."
    return "File is not changed."
```

</details>

## Function `optimize_images_in_md_content`

```python
def optimize_images_in_md_content(markdown_text: str, path_md: Path | str, image_folder: str = "img") -> str
```

Optimize images referenced in Markdown content by converting them to more efficient formats.

This function processes Markdown content to find local image references, optimizes those images,
and updates the Markdown content to reference the optimized versions. Remote images (URLs)
are left unchanged.

Args:

- `markdown_text` (`str`): The Markdown content to process.
- `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
- `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.
- `is_convert_png_to_avif` (`bool`): Flag for converting PNG to AVIF. Defaults to `False`.

Returns:

- `str`: The updated Markdown content with references to optimized images.

Notes:

- Images with extensions .jpg, .jpeg, .webp, .gif, and .mp4 will be converted to .avif
- PNG and SVG files keep their original format but may still be optimized
- The optimization process uses an external npm script
- Code blocks in the Markdown are preserved without changes

<details>
<summary>Code:</summary>

```python
def optimize_images_in_md_content(
    markdown_text: str,
    path_md: Path | str,
    image_folder: str = "img",
    *,
    is_convert_png_to_avif: bool = False,
) -> str:

    def optimize_images_content_line(markdown_line: str, path_md: Path | str, image_folder: str = "img") -> str:
        """Process a single line of Markdown to optimize any image reference it contains.

        Args:

        - `markdown_line` (`str`): A single line from the Markdown document.
        - `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
        - `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.

        Returns:

        - `str`: The processed Markdown line, with image references updated if needed.

        """
        result_line = markdown_line
        should_process = True

        # Regular expression to match Markdown image with remote URL (http or https)
        pattern = r"^\!\[(.*?)\]\((http.*?)\)$"
        match = re.search(pattern, markdown_line.strip())

        # If the line contains a remote image, don't process it
        if match:
            should_process = False

        # Regular expression to match Markdown image with local path
        local_pattern = r"^\!\[(.*?)\]\((.*?)\)$"
        local_match = re.search(local_pattern, markdown_line.strip())

        if should_process and local_match:
            alt_text = local_match.group(1)
            image_path = local_match.group(2)

            # Check if this is a local image (not a remote URL)
            if not image_path.startswith("http"):
                # Convert path_md to Path object if it's a string
                if isinstance(path_md, str):
                    path_md = Path(path_md)

                # Get the directory containing the Markdown file
                md_dir = path_md.parent if path_md.is_file() else path_md

                # Determine the complete path to the image
                image_filename = Path(image_path) if Path(image_path).is_absolute() else md_dir / image_path

                # Check if the image exists and has a supported extension
                if image_filename.exists():
                    # Get the extension
                    ext = image_filename.suffix.lower()
                    supported_extensions = [".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".png", ".svg"]

                    if ext in supported_extensions:
                        # Determine the new extension based on the current one
                        new_ext = ext
                        if ext in [".jpg", ".jpeg", ".webp", ".gif", ".mp4"] or (
                            ext == ".png" and is_convert_png_to_avif
                        ):
                            new_ext = ".avif"
                        # For .png and .svg, keep the original extension

                        # Create temporary directory for optimization
                        with TemporaryDirectory() as temp_folder:
                            temp_folder_path = Path(temp_folder)
                            temp_image_filename = temp_folder_path / image_filename.name
                            shutil.copy(image_filename, temp_image_filename)

                            # Run the optimization command
                            commands = f'npm run optimize imagesFolder="{temp_folder}"'
                            if is_convert_png_to_avif:
                                commands += " convertPngToAvif=true"
                            h.dev.run_powershell_script(commands)

                            # Path to the optimized image
                            optimized_images_dir = temp_folder_path / "temp"
                            optimized_image = optimized_images_dir / f"{image_filename.stem}{new_ext}"

                            # Check if the optimization was successful
                            if optimized_image.exists():
                                # Determine the target path for the new image
                                if Path(image_path).is_absolute():
                                    # If it was an absolute path, maintain that structure
                                    new_image_path = image_filename.with_suffix(new_ext)
                                    new_image_rel_path = str(new_image_path)
                                else:
                                    # For relative paths, ensure the image goes to the image_folder
                                    img_folder_path = md_dir / image_folder
                                    img_folder_path.mkdir(exist_ok=True)

                                    # Create the new image path
                                    new_image_path = img_folder_path / f"{image_filename.stem}{new_ext}"
                                    new_image_rel_path = f"{image_folder}/{image_filename.stem}{new_ext}"

                                # Remove the original image if we're replacing it
                                if image_filename.exists():
                                    image_filename.unlink()

                                # Copy the optimized image to the target location
                                shutil.copy(optimized_image, new_image_path)

                                # Create the new Markdown line with updated path
                                result_line = f"![{alt_text}]({new_image_rel_path})"

        return result_line

    yaml_md, content_md = h.md.split_yaml_content(markdown_text)

    new_lines = []
    lines = content_md.split("\n")
    for line_content, is_code_block in h.md.identify_code_blocks(lines):
        if is_code_block:
            new_lines.append(line_content)
            continue

        processed_line = optimize_images_content_line(line_content, path_md, image_folder)
        new_lines.append(processed_line)
    content_md = "\n".join(new_lines)

    return yaml_md + "\n\n" + content_md
```

</details>

## Function `optimize_images_in_md_png_to_avif`

```python
def optimize_images_in_md_png_to_avif(filename: Path | str) -> str
```

Optimize images in a Markdown file by converting them to more efficient formats. PNG converts to AVIF too.

This function reads a Markdown file, processes any local images referenced in it,
optimizes them, and updates the Markdown content to reference the optimized images.

Args:

- `filename` (`Path | str`): Path to the Markdown file to process.

Returns:

- `str`: A status message indicating whether the file was modified.

<details>
<summary>Code:</summary>

```python
def optimize_images_in_md_png_to_avif(filename: Path | str) -> str:
    filename = Path(filename)
    with Path.open(filename, encoding="utf-8") as f:
        document = f.read()

    document_new = optimize_images_in_md_content(document, filename.parent, is_convert_png_to_avif=True)

    if document != document_new:
        with Path.open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} applied."
    return "File is not changed."
```

</details>
