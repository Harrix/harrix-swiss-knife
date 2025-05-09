import re
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import harrix_pylib as h


def optimize_images_in_md(filename: Path | str) -> str:
    """Optimizes images in a markdown file by converting them to more efficient formats.

    This function reads a markdown file, processes any local images referenced in it,
    optimizes them, and updates the markdown content to reference the optimized images.

    Args:

    - `filename` (`Path | str`): Path to the markdown file to process.

    Returns:

    - `str`: A status message indicating whether the file was modified.

    """
    filename = Path(filename)
    with Path.open(filename, encoding="utf-8") as f:
        document = f.read()

    document_new = optimize_images_in_md_content(document, filename.parent, convert_png_to_avif=False)

    if document != document_new:
        with Path.open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} applied."
    return "File is not changed."


def optimize_images_in_md_content(
    markdown_text: str, path_md: Path | str, image_folder: str = "img", convert_png_to_avif: bool = False,
) -> str:
    """Optimizes images referenced in markdown content by converting them to more efficient formats.

    This function processes markdown content to find local image references, optimizes those images,
    and updates the markdown content to reference the optimized versions. Remote images (URLs)
    are left unchanged.

    Args:

    - `markdown_text` (`str`): The markdown content to process.
    - `path_md` (`Path | str`): Path to the markdown file or its containing directory.
    - `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.
    - `convert_png_to_avif` (`bool`): Flag for converting PNG to AVIF. Defaults to `False`.

    Returns:

    - `str`: The updated markdown content with references to optimized images.

    Notes:

    - Images with extensions .jpg, .jpeg, .webp, .gif, and .mp4 will be converted to .avif
    - PNG and SVG files keep their original format but may still be optimized
    - The optimization process uses an external npm script
    - Code blocks in the markdown are preserved without changes

    """

    def optimize_images_content_line(markdown_line, path_md, image_folder="img"):
        # Regular expression to match markdown image with remote URL (http or https)
        pattern = r"^\!\[(.*?)\]\((http.*?)\)$"
        match = re.search(pattern, markdown_line.strip())

        # If the line contains a remote image, return the line unchanged.
        if match:
            return markdown_line

        # Regular expression to match markdown image with local path
        local_pattern = r"^\!\[(.*?)\]\((.*?)\)$"
        local_match = re.search(local_pattern, markdown_line.strip())

        if not local_match:
            return markdown_line

        alt_text = local_match.group(1)
        image_path = local_match.group(2)

        # Check if this is a local image (not a remote URL)
        if image_path.startswith("http"):
            return markdown_line

        # Convert path_md to Path object if it's a string
        if isinstance(path_md, str):
            path_md = Path(path_md)

        # Get the directory containing the markdown file
        md_dir = path_md.parent if path_md.is_file() else path_md

        # Determine the complete path to the image
        if Path(image_path).is_absolute():
            image_filename = Path(image_path)
        else:
            # Relative path - join with markdown directory
            image_filename = md_dir / image_path

        # Check if the image exists
        if not image_filename.exists():
            return markdown_line

        # Get the extension
        ext = image_filename.suffix.lower()
        supported_extensions = [".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".png", ".svg"]

        if ext not in supported_extensions:
            return markdown_line

        # Determine the new extension based on the current one
        new_ext = ext
        if ext in [".jpg", ".jpeg", ".webp", ".gif", ".mp4"] or (ext == ".png" and convert_png_to_avif):
            new_ext = ".avif"
        # For .png and .svg, keep the original extension

        # Create temporary directory for optimization
        with TemporaryDirectory() as temp_folder:
            temp_folder_path = Path(temp_folder)
            temp_image_filename = temp_folder_path / image_filename.name
            shutil.copy(image_filename, temp_image_filename)

            # Run the optimization command
            commands = f'npm run optimize imagesFolder="{temp_folder}"'
            if convert_png_to_avif:
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
                else:
                    # For relative paths, ensure the image goes to the image_folder
                    img_folder_path = md_dir / image_folder
                    img_folder_path.mkdir(exist_ok=True)

                    # Create the new image path
                    new_image_path = img_folder_path / f"{image_filename.stem}{new_ext}"

                    # Update the markdown link to point to the new location
                    new_image_rel_path = f"{image_folder}/{image_filename.stem}{new_ext}"

                # Remove the original image if we're replacing it
                if image_filename.exists():
                    image_filename.unlink()

                # Copy the optimized image to the target location
                shutil.copy(optimized_image, new_image_path)

                # Create the new markdown line with updated path
                if Path(image_path).is_absolute():
                    new_line = f"![{alt_text}]({new_image_path})"
                else:
                    new_line = f"![{alt_text}]({new_image_rel_path})"

                return new_line

        # If we get here, optimization failed, return the original line
        return markdown_line

    yaml_md, content_md = h.md.split_yaml_content(markdown_text)

    new_lines = []
    lines = content_md.split("\n")
    for line, is_code_block in h.md.identify_code_blocks(lines):
        if is_code_block:
            new_lines.append(line)
            continue

        line = optimize_images_content_line(line, path_md, image_folder)
        new_lines.append(line)
    content_md = "\n".join(new_lines)

    return yaml_md + "\n\n" + content_md


def optimize_images_in_md_png_to_avif(filename: Path | str) -> str:
    """Optimizes images in a markdown file by converting them to more efficient formats. PNG converts to AVIF too.

    This function reads a markdown file, processes any local images referenced in it,
    optimizes them, and updates the markdown content to reference the optimized images.

    Args:

    - `filename` (`Path | str`): Path to the markdown file to process.

    Returns:

    - `str`: A status message indicating whether the file was modified.

    """
    filename = Path(filename)
    with Path.open(filename, encoding="utf-8") as f:
        document = f.read()

    document_new = optimize_images_in_md_content(document, filename.parent, convert_png_to_avif=True)

    if document != document_new:
        with Path.open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} applied."
    return "File is not changed."
