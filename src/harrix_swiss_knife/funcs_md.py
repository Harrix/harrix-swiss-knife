import re
from pathlib import Path

import yaml


def add_author_book(filename: Path | str) -> str:
    """
    Adds the author and the title of the book to the quotes and formats them as Markdown quotes.

    Args:

    - `filename` (`Path` | `str`): The filename of the Markdown file.

    Returns:

    - `str`: A string indicating whether changes were made to the file or not.

    Example:

    Given a file like `C:/test/Name_Surname/Title_of_book.md` with content:

    ```markdown
    # Title of book

    Line 1.

    Line 2.

    ---

    Line 3.

    Line 4.

    -- Modified title of book
    ```

    After processing:

    ```markdown
    # Title of book

    > Line 1.
    >
    > Line 2.
    >
    > _Name Surname - Title of book_

    ---

    > Line 3.
    >
    > Line 4.
    >
    > _Name Surname - Modified title of book_
    ```

    Note:

    - If the file does not exist or is not a Markdown file, the function will return `None`.
    - If the file has been modified, it returns a message indicating the changes; otherwise,
      it indicates no changes were made.
    """
    lines_list = []
    file = Path(filename)
    if not file.is_file():
        return
    if file.suffix.lower() != ".md":
        return
    note_initial = file.read_text(encoding="utf8")

    parts = note_initial.split("---", 2)
    yaml_content, main_content = f"---{parts[1]}---", parts[2].lstrip()

    lines = main_content.splitlines()

    author = file.parts[-2].replace("-", " ")
    title = lines[0].replace("# ", "")

    lines = lines[1:] if lines and lines[0].startswith("# ") else lines
    lines = lines[:-1] if lines[-1].strip() == "---" else lines

    note = f"{yaml_content}\n\n# {title}\n\n"
    quotes = list(map(str.strip, filter(None, "\n".join(lines).split("\n---\n"))))

    quotes_fix = []
    for quote in quotes:
        lines_quote = quote.splitlines()
        if lines_quote[-1].startswith("> -- _"):
            quotes_fix.append(quote)  # The quote has already been processed
            continue
        if lines_quote[-1].startswith("-- "):
            title = lines_quote[-1][3:]
            del lines_quote[-2:]
        quote_fix = "\n".join([f"> {line}".rstrip() for line in lines_quote])
        quotes_fix.append(f"{quote_fix}\n>\n> -- _{author}, {title}_")
    note += "\n\n---\n\n".join(quotes_fix) + "\n"
    if note_initial != note:
        file.write_text(note, encoding="utf8")
        lines_list.append(f"Fix {filename}")
    else:
        lines_list.append(f"No changes in {filename}")
    return "\n".join(lines_list)


def add_image_captions(filename: Path | str) -> str:
    """
    Processes a markdown file to add captions to images based on their alt text.

    This function reads a markdown file, processes its content to:
    - Recognize images by their markdown syntax.
    - Add automatic captions with sequential numbering, localized for Russian or English.
    - Skip image captions that already exist in italic format.
    - Ensure proper handling within and outside of code blocks.

    Args:

    - `filename` (`Path | str`): The path to the markdown file to be processed.

    Returns:

    - `str`: A status message indicating whether the file was modified or not.

    Note:

    - The function modifies the file in place if changes are made.
    - The first argument of the function can be either a `Path` object or a string representing the file path.
    """
    with open(filename, "r", encoding="utf-8") as f:
        document = f.read()
    yaml_md, content_md = split_yaml_content(document)
    data_yaml = yaml.safe_load(yaml_md.strip("---\n"))
    lang = data_yaml.get("lang")

    def process_lines(lines):
        code_block_delimiter = None
        for line in lines:
            match = re.match(r"^(`{3,})(.*)", line)
            if match:
                delimiter = match.group(1)
                if code_block_delimiter is None:
                    code_block_delimiter = delimiter
                elif code_block_delimiter == delimiter:
                    code_block_delimiter = None
                yield line, True
                continue
            if code_block_delimiter:
                yield line, True
            else:
                yield line, False

    # Remove captions
    is_caption = False
    new_lines = []
    lines = content_md.split("\n")
    for i, (line, is_code_block) in enumerate(process_lines(lines)):
        if is_code_block:
            new_lines.append(line)
            continue
        if is_caption:
            is_caption = False
            if line.strip() == "":
                continue
        if re.match(r"^_.*_$", line):
            if i > 0 and lines[i - 1].strip() == "":
                if i > 1 and re.match(r"^\!\[(.*?)\]\((.*?)\.(.*?)\)$", lines[i - 2].strip()):
                    is_caption = True
                    continue
        new_lines.append(line)
    content_md = "\n".join(new_lines)

    # Add captions
    image_count = 0
    new_lines = []
    lines = content_md.split("\n")
    for line, is_code_block in process_lines(lines):
        if is_code_block:
            new_lines.append(line)
            continue
        match = re.match(r"^\!\[(.*?)\]\((.*?)\.(.*?)\)$", line)
        if match and not line.startswith("![Featured image](featured-image"):
            image_count += 1
            alt_text = match.group(1)
            new_lines.append(line)
            caption = f"_Рисунок {image_count} — {alt_text}_" if lang == "ru" else f"_Figure {image_count}: {alt_text}_"
            new_lines.append("\n" + caption)
        else:
            new_lines.append(line)
    content_md = "\n".join(new_lines)

    document_new = yaml_md + "\n\n" + content_md
    if document != document_new:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        return f"✅ File {filename} applied."
    return "File is not changed."


def add_note(base_path: str | Path, name: str, text: str, is_with_images: bool) -> str | Path:
    """
    Adds a note to the specified base path.

    Args:

    - `base_path` (`str | Path`): The path where the note will be added.
    - `name` (`str`): The name for the note file or folder.
    - `text` (`str`): The text content for the note.
    - `is_with_images` (`bool`): If true, creates folders for images.

    Returns:

    - `str | Path`: A tuple containing a message about file creation and the path to the file.
    """
    base_path = Path(base_path)

    if is_with_images:
        (base_path / name).mkdir(exist_ok=True)
        (base_path / name / "img").mkdir(exist_ok=True)
        file_path = base_path / name / f"{name}.md"
    else:
        file_path = base_path / f"{name}.md"

    with file_path.open(mode="w", encoding="utf-8") as file:
        file.write(text)

    return f"File {file_path} created.", file_path


def split_yaml_content(note: str) -> tuple[str, str]:
    """
    Splits a markdown note into YAML front matter and the main content.

    This function assumes that the note starts with YAML front matter separated by '---' from the rest of the content.

    Args:

    - `note` (`str`): The markdown note string to be split.

    Returns:

    - `tuple[str, str]`: A tuple containing:
        - The YAML front matter as a string, prefixed and suffixed with '---'.
        - The remaining markdown content after the YAML front matter, with leading whitespace removed.

    Note:

    - If there is no '---' or only one '---' in the note, the function returns an empty string for YAML content and the entire note for the content part.
    - The function does not validate if the YAML content is properly formatted YAML.
    """
    parts = note.split("---", 2)
    if len(parts) < 3:
        return "", note
    return f"---{parts[1]}---", parts[2].lstrip()
