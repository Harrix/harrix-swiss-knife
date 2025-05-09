import re
from datetime import datetime
from pathlib import Path

import harrix_pylib as h

config = h.dev.load_config("config/config.json")


def generate_summaries(folder: Path | str) -> str:
    """Create two summary files for a directory of year-based Markdown files:

    1. Table.md - A statistical table showing the count of book entries by year
    2. _[directory_name].short.g.md - A hierarchical list of all book entries organized by year

    Args:

    - `folder` (`Path | str`): Path to the directory containing Markdown files named after years

    Returns:

    - `str`: Success message with paths to the created files

    Notes:

    - The function expects Markdown files named with 4-digit years (e.g., "2023.md")
    - Book entries are identified by second-level headings (## Title)
    - Ratings are extracted from headings in format "## Title: N" where N is a number
    - YAML frontmatter from the first processed file will be copied to the summary files

    Example:

    ```python
    import harrix_pylib as h
    from pathlib import Path

    result = h.create_markdown_summaries(Path("C:/Notes/books"))
    print(result)
    # Output: ✅ File ./books/Table.md is created.
    #         ✅ File ./books/_books.short.g.md is created.
    ```

    """
    # Convert input to Path object if it's a string
    path = Path(folder) if isinstance(folder, str) else folder

    # Make sure path is a directory, not a file
    if not path.is_dir():
        path = path.parent

    # Get the directory name for the short summary file title
    dir_name = path.name

    # Get the current year
    current_year = datetime.now(tz=datetime.now().astimezone().tzinfo).year

    # Dictionary to store counts and entries by year
    year_counts = {}
    year_entries = {}

    # Regular expressions
    heading_pattern = re.compile(r"^## (.+?)(?:: (\d+))?$", re.MULTILINE)

    # YAML frontmatter to use for both files
    yaml_frontmatter = ""

    # Scan the directory for year-named Markdown files
    for file_path in path.glob("*.md"):
        # Check if the filename is a 4-digit year
        if file_path.stem.isdigit() and len(file_path.stem) == 4:
            year = int(file_path.stem)

            # Read the file content
            content = file_path.read_text(encoding="utf-8")

            # If we haven't extracted the YAML frontmatter yet, extract it from this file
            if not yaml_frontmatter and "---" in content:
                yaml_end = content.find("---", content.find("---") + 3) + 3
                yaml_frontmatter = content[:yaml_end]

            # Find all second-level headings
            matches = heading_pattern.findall(content)

            # Process valid entries (exclude "Содержание" and "Contents")
            valid_entries = []
            for heading, rating in matches:
                if heading.strip() not in ["Содержание", "Contents"]:
                    # If there's no explicit rating in the heading, look for a rating in the section
                    if not rating:
                        # Try to find a rating in the book entry text
                        section_start = content.find(f"## {heading}")
                        if section_start != -1:
                            section_end = content.find("##", section_start + 1)
                            if section_end == -1:  # Last section
                                section_end = len(content)
                            section_text = content[section_start:section_end]

                            # Look for rating in format ": N" at the end of the heading
                            rating_match = re.search(r": (\d+)$", section_text.split("\n")[0])
                            if rating_match:
                                rating = rating_match.group(1)

                    valid_entries.append((heading, rating if rating else ""))

            # Store count and entries
            year_counts[year] = len(valid_entries)
            if valid_entries:
                year_entries[year] = valid_entries

    # If no year files were found, use the current year as min_year
    if not year_counts:
        min_year = current_year
    else:
        # Find the minimum year that has a file
        min_year = min(year_counts.keys())

    # --- Create Table.md ---
    table_content = "\n# Table <!-- top-section -->\n\n"
    table_content += "| Year | Count |\n"
    table_content += "| ---- | ----- |\n"

    # Add rows for each year from current to min_year
    for year in range(current_year, min_year - 1, -1):
        count = year_counts.get(year, 0)
        # For the current year, use a dash instead of 0
        display_count = str(count)
        table_content += f"| {year} | {display_count} |\n"

    # Write the table to Table.md
    table_file = path / "Table.md"
    table_content_with_yaml = f"{yaml_frontmatter}\n{table_content}" if yaml_frontmatter else table_content
    table_file.write_text(table_content_with_yaml, encoding="utf-8")

    # --- Create short summary file ---
    summary_content = f"\n# {dir_name}: short\n\n"

    # Add entries for each year, sorted in descending order
    for year in sorted(year_entries.keys(), reverse=True):
        summary_content += f"- {year}\n"
        for heading, rating in year_entries[year]:
            rating_text = f": {rating}" if rating else ""
            summary_content += f"  - {heading}{rating_text}\n"

    # Create the filename
    short_file_name = f"_{dir_name}.short.g.md"
    short_file = path / short_file_name

    # If we have YAML frontmatter, include it
    summary_content_with_yaml = f"{yaml_frontmatter}\n{summary_content}" if yaml_frontmatter else summary_content

    # Write the file
    short_file.write_text(summary_content_with_yaml, encoding="utf-8")

    return f"✅ File {table_file} is created\n✅ File {short_file} is created"


folder = "D:/Dropbox/Notes/Notes/Diary-Lists/Books-of-non--fiction"
print(generate_summaries(folder))
