"""Actions for Python development and Markdown file management."""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase
from harrix_swiss_knife.template_dialog import TemplateDialog, TemplateField, TemplateParser
from harrix_swiss_knife.filtered_combobox import apply_smart_filtering


class OnAddMarkdownFromTemplate(ActionBase):
    """Add markdown content using template-based forms.

    This action provides a flexible template system for adding structured markdown
    elements (movies, series, books, etc.) to files. It:

    1. Reads a template file with field placeholders ({{FieldName:FieldType}})
    2. Generates a dynamic form dialog based on the template fields
    3. Collects user input through the form
    4. Fills the template with the provided values
    5. Either returns the markdown text or inserts it into a specified file

    Supported field types:

    - line: Single-line text input
    - int: Integer number (e.g., season number)
    - float: Floating-point number (e.g., ratings)
    - date: Date picker
    - bool: Checkbox (returns "true" or "false")
    - multiline: Multi-line text area

    Optional default values can be specified: {{FieldName:FieldType:DefaultValue}}
    """

    icon = "📝"
    title = "Add markdown from template"
    bold_title = True

    @ActionBase.handle_exceptions("adding markdown from template")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        # Get available templates from config
        templates = self.config.get("markdown_templates", {})

        if not templates:
            self.add_line("❌ No markdown templates configured in config.json")
            self.show_result()
            return

        # Let user choose a template
        template_names = list(templates.keys())
        selected_template = self.get_choice_from_list(
            "Select Template",
            "Choose a template to use:",
            template_names,
        )

        if not selected_template:
            return

        template_config = templates[selected_template]
        template_file = template_config.get("template_file")

        if not template_file:
            self.add_line(f"❌ Template file not specified for '{selected_template}'")
            self.show_result()
            return

        # Read template file
        template_path = Path(template_file)
        if not template_path.exists():
            self.add_line(f"❌ Template file not found: {template_file}")
            self.show_result()
            return

        with Path.open(template_path, encoding="utf-8") as f:
            template_content = f.read().strip()

        # Parse template to get fields
        fields, _ = TemplateParser.parse_template(template_content)

        if not fields:
            self.add_line(f"❌ No fields found in template: {template_file}")
            self.show_result()
            return

        dialog_links_config = template_config.get("dialog_links", [])
        dialog_links: list[tuple[str, str]] = []

        for item in dialog_links_config:
            if isinstance(item, dict):
                url = item.get("url", "").strip()
                if not url:
                    continue
                label = item.get("label", url).strip() or url
                dialog_links.append((label, url))
            elif isinstance(item, str):
                cleaned = item.strip()
                if cleaned:
                    dialog_links.append((cleaned, cleaned))

        # Show dialog to collect field values
        dialog = TemplateDialog(
            fields=fields,
            title=f"Add {selected_template.capitalize()}",
            links=dialog_links,
        )

        if dialog.exec() != dialog.DialogCode.Accepted:
            self.add_line("❌ Dialog was canceled.")
            self.show_result()
            return

        field_values = dialog.get_field_values()
        if not field_values:
            self.add_line("❌ No field values collected.")
            self.show_result()
            return

        # Fill template with values
        result_markdown = TemplateParser.fill_template(template_content, field_values)

        # Get target file configuration
        target_file = template_config.get("target_file")
        insert_position = template_config.get("insert_position", "end")

        if target_file:
            # Insert into file
            target_path = Path(target_file)

            if not target_path.exists():
                self.add_line(f"❌ Target file not found: {target_file}")
                self.add_line("Generated markdown:")
                self.add_line(result_markdown)
                self.show_result()
                return

            # Read existing file content
            with Path.open(target_path, encoding="utf-8") as f:
                existing_content = f.read()

            # Insert new content based on position
            if insert_position == "end":
                new_content = existing_content.rstrip() + "\n\n" + result_markdown + "\n"
            elif insert_position == "start":
                # Split YAML frontmatter from content
                yaml_md, content_md = h.md.split_yaml_content(existing_content)

                # Find the year heading (# 2025 or ## 2025)
                year_match = re.search(r"^#+ \d{4}", content_md, re.MULTILINE)

                if year_match:
                    # Find the table of contents section
                    toc_match = re.search(r"<details>[\s\S]*?<\/details>", content_md)

                    if toc_match:
                        # Insert new entry right after the TOC
                        toc_end_pos = toc_match.end()
                        updated_content_md = (
                            content_md[:toc_end_pos]
                            + "\n\n"
                            + result_markdown
                            + "\n\n"
                            + content_md[toc_end_pos:].lstrip()
                        )
                    else:
                        # No TOC found, insert after year heading
                        year_pos = year_match.end()
                        updated_content_md = (
                            content_md[:year_pos] + "\n\n" + result_markdown + "\n\n" + content_md[year_pos:].lstrip()
                        )

                    # Combine YAML and updated content
                    new_content = yaml_md + "\n\n" + updated_content_md if yaml_md else updated_content_md
                # No year heading found, just insert after YAML frontmatter
                elif yaml_md:
                    new_content = yaml_md + "\n\n" + result_markdown + "\n\n" + content_md
                else:
                    new_content = result_markdown + "\n\n" + existing_content
            else:
                # Default to end
                new_content = existing_content.rstrip() + "\n\n" + result_markdown + "\n"

            # Write back to file
            with Path.open(target_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            self.add_line(f"✅ Added markdown to {target_file}")
            self.add_line("\nGenerated markdown:")
            self.add_line(result_markdown)
        else:
            # Just return the text
            self.add_line("Generated markdown:")
            self.add_line(result_markdown)

        self.show_result()


class OnBeautifyMdFolder(ActionBase):
    """Apply comprehensive beautification to all Markdown notes.

    This action performs multiple enhancement operations on Markdown files across
    all configured note directories, including:

    - Adding image captions
    - Generating tables of contents
    - Formatting YAML frontmatter
    - Running Prettier for consistent formatting

    It provides a one-click solution for maintaining a high-quality, consistently
    formatted collection of Markdown documents.
    """

    icon = "💎"
    title = "Beautify MD in …"

    def beautify_markdown_common(
        self: ActionBase, folder_path: str, *, is_include_summaries_and_combine: bool = False
    ) -> None:
        """Perform common beautification operations on Markdown files in a folder.

        This method applies a series of enhancement operations to all Markdown files
        in the specified folder, including file renaming (spaces to hyphens), image
        caption generation, table of contents creation, YAML formatting, and Prettier
        formatting. Optionally includes summary generation and file combination operations.

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
        - File renaming converts spaces to hyphens in filenames for better URL compatibility.

        """
        if is_include_summaries_and_combine:
            # Delete *.g.md files
            self.add_line("🔵 Delete *.g.md files")
            self.add_line(h.file.apply_func(folder_path, ".md", h.md.delete_g_md_files_recursively))

        # Rename files with spaces to hyphens
        self.add_line("🔵 Rename files with spaces to hyphens")
        self.add_line(h.file.apply_func(folder_path, ".md", h.file.rename_file_spaces_to_hyphens))

        # Sort sections in Markdown files (using YAML frontmatter if present)
        self.add_line("🔵 Sort sections in Markdown files (YAML-controlled)")
        self.add_line(
            h.file.apply_func(
                folder_path,
                ".md",
                lambda filename: h.md.sort_sections(filename, is_sort_section_from_yaml=True),
            )
        )

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
        commands = "prettier --parser markdown --write **/*.md --end-of-line crlf"
        result = h.dev.run_command(commands, cwd=str(folder_path))
        self.add_line(result)

    @ActionBase.handle_exceptions("beautifying markdown folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("beautifying markdown thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
        if self.folder_path is None:
            return
        self.beautify_markdown_common(str(self.folder_path), is_include_summaries_and_combine=False)

    @ActionBase.handle_exceptions("beautifying markdown thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnBeautifyMdFolderAndRegenerateGMd(ActionBase):
    """Apply comprehensive beautification to all Markdown notes.

    This action performs multiple enhancement operations on Markdown files across
    all configured note directories, including:

    - Adding image captions
    - Generating tables of contents
    - Creating summaries for specified directories
    - Combining related Markdown files
    - Formatting YAML frontmatter
    - Running Prettier for consistent formatting

    It provides a one-click solution for maintaining a high-quality, consistently
    formatted collection of Markdown documents.
    """

    icon = "💎"
    title = "Beautify MD and regenerate .g.md in …"
    bold_title = True

    @ActionBase.handle_exceptions("beautifying markdown folder and regenerating g.md")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("beautifying and regenerating thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
        if self.folder_path is None:
            return
        OnBeautifyMdFolder.beautify_markdown_common(self, str(self.folder_path), is_include_summaries_and_combine=True)

    @ActionBase.handle_exceptions("beautifying and regenerating thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnCheckMdFolder(ActionBase):
    """Action to check all Markdown files in a folder for errors with Harrix rules."""

    icon = "🚧"
    title = "Check in …"

    @ActionBase.handle_exceptions("checking markdown folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        # Get available rules from MarkdownChecker
        checker = h.md_check.MarkdownChecker()
        rules_dict = checker.RULES

        # Convert rules dict to list of rule descriptions for display
        rule_choices = [f"{rule_id}: {description}" for rule_id, description in rules_dict.items()]

        # Show dialog to select rules (all selected by default)
        selected_rules = self.get_checkbox_selection(
            "Select Rules for Markdown Check",
            "Choose which rules to check:",
            rule_choices,
            default_selected=rule_choices,  # All rules selected by default
        )

        if not selected_rules:
            return

        # Extract rule IDs from selected descriptions
        self.selected_rule_ids = set()
        for selected_rule in selected_rules:
            # Extract rule ID (e.g., "H001" from "H001: Description")
            rule_id = selected_rule.split(":")[0].strip()
            self.selected_rule_ids.add(rule_id)

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("markdown folder checking thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        checker = h.md_check.MarkdownChecker()
        if self.folder_path is None:
            return

        # Use selected rules for checking directory
        errors_dict = checker.check_directory(self.folder_path, select=self.selected_rule_ids)

        # Flatten the errors dictionary into a list
        all_errors = []
        for file_path, file_errors in errors_dict.items():
            for error in file_errors:
                all_errors.extend([f"{file_path}: {error}" for error in file_errors])

        if all_errors:
            self.add_line("\n".join(all_errors))
            self.add_line(f"🔢 Count errors = {len(all_errors)}")
        else:
            self.add_line(f"✅ There are no errors in {self.folder_path}.")

    @ActionBase.handle_exceptions("markdown folder checking thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnDecreaseHeadingLevelContent(ActionBase):
    """Decrease the heading level of all headings in Markdown content.

    This action takes Markdown content and decreases the level of all headings
    by removing one '#' character from each heading, making them one level
    shallower in the document hierarchy.
    """

    icon = "👈"
    title = "Heading level: Decrease"

    @ActionBase.handle_exceptions("decreasing heading level")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        content = self.get_text_textarea(
            "Markdown content", "Input Markdown content", "# Title\n\nText\n\n## Subtitle\n\nText"
        )
        if not content:
            return

        new_content = h.md.decrease_heading_level_content(content)
        self.add_line(new_content)
        self.show_result()


class OnDownloadAndReplaceImagesFolder(ActionBase):
    """Download remote images and replace URLs with local references in multiple Markdown files.

    This action processes all Markdown files in a selected folder to find image URLs,
    downloads the images to local directories, and updates the Markdown files to reference
    these local copies instead of the remote URLs, improving document portability and
    reducing external dependencies across an entire collection of documents.
    """

    icon = "📥"
    title = "Download images in …"

    @ActionBase.handle_exceptions("downloading images in folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("downloading images folder thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.download_and_replace_images))

    @ActionBase.handle_exceptions("downloading images folder thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnFixMDWithQuotes(ActionBase):
    """Add author and title information to quote files in a folder.

    This action processes quote files in a folder to add author and book information
    based on the folder structure. Given a file structure like:

    `C:/quotes/Name-Surname/Title-of-book.md`

    The action will:
    1. Extract author name from the parent folder
    2. Extract book title from the filename
    3. Format quotes with proper author attribution

    Example transformation:

    - Before: Plain text quotes separated by `---`
    - After: Block quotes with attribution `-- _Name Surname, Title of book_`
    """

    icon = "❞"
    title = "Fix MD with quotes"

    @ActionBase.handle_exceptions("fixing markdown with quotes")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.show_instructions("""Given a file like `C:/test/Name-Surname/Title-of-book.md` with content:

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
> -- _Name Surname, Title of book_

---

> Line 3.
>
> Line 4.
>
> -- _Name Surname, Modified title of book_

```
""")
        self.folder_path = self.get_existing_directory("Select folder with quotes", self.config["path_quotes"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("fixing markdown with quotes thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        result = h.file.apply_func(self.folder_path, ".md", h.md.generate_author_book)
        self.add_line(result)

    @ActionBase.handle_exceptions("fixing markdown with quotes thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnGenerateShortNoteTocWithLinks(ActionBase):
    """Generate a condensed version of a document with only its table of contents.

    This action creates a shortened version of a selected Markdown file that
    includes only the document's title and table of contents with working links.
    Useful for creating quick reference documents or previews of longer content.
    """

    icon = "📑"
    title = "Generate a short version with only TOC"

    @ActionBase.handle_exceptions("generating short note with TOC")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.filename = self.get_open_filename(
            "Open Markdown file",
            self.config["path_articles"],
            "Markdown (*.md);;All Files (*)",
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("generating short note TOC thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.filename is None:
            return
        self.add_line(h.md.generate_short_note_toc_with_links(self.filename))

    @ActionBase.handle_exceptions("generating short note TOC thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnGetListMoviesBooks(ActionBase):
    """Extract and format a list of movies or books from Markdown content.

    This action takes Markdown content with level-3 headings (`### Title`)
    and converts them into a bulleted list, counting the total number of items.
    Useful for creating web-friendly lists from structured Markdown content.
    """

    icon = "🎬"
    title = "Get a list of movies, books for web"

    @ActionBase.handle_exceptions("extracting movies/books list")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        default_text = """### Song of the Sea: 8.5

- **Original or English title:** Song of the Sea
- **Date watching:** 2019-10-28
- **Kinopoisk:** <https://www.kinopoisk.ru/film/714248/>
- **IMDb:** <https://www.imdb.com/title/tt1865505/>
- **Comments:** A beautiful cartoon that needs to be shown to children.

### Red Turtle: 9

- **Original or English title:** La tortue rouge
- **Date watching:** 2019-10-12
- **Kinopoisk:** <https://www.kinopoisk.ru/film/879827/>
- **IMDb:** <https://www.imdb.com/title/tt3666024/>
- **Comments:** Beautiful meditative cartoon."""

        content = self.get_text_textarea("Markdown content", "Input Markdown content", default_text)
        if not content:
            return

        result = ""
        count = 0
        start_element = "### " if "### " in content else "## "
        for line in content.splitlines():
            if line.startswith(start_element):
                result += f"- {line[4:].strip()}\n"
                count += 1

        result += f"\nCount: {count}"
        self.add_line(result)
        self.show_result()


class OnIncreaseHeadingLevelContent(ActionBase):
    """Increase the heading level of all headings in Markdown content.

    This action takes Markdown content and increases the level of all headings
    by adding an additional '#' character to each heading, making them one level
    deeper in the document hierarchy.
    """

    icon = "👉"
    title = "Heading level: Increase"

    @ActionBase.handle_exceptions("increasing heading level")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        content = self.get_text_textarea(
            "Markdown content", "Input Markdown content", "# Title\n\nText\n\n## Subtitle\n\nText"
        )
        if not content:
            return

        new_content = h.md.increase_heading_level_content(content)
        self.add_line(new_content)
        self.show_result()


class OnNewArticle(ActionBase):
    """Create a new article with predefined template.

    This action prompts the user for an article title, creates a new Markdown file
    in the configured articles directory, and opens it in the configured editor.
    """

    icon = "✍️"
    title = "New article"

    @ActionBase.handle_exceptions("creating new article")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        article_name = self.get_text_input(
            "Article title", "Enter the name of the article (English, without spaces):", "name-of-article"
        )
        if not article_name:
            return

        article_name = article_name.replace(" ", "-")

        text = self.config["beginning_of_article"].replace(
            "[YEAR]",
            datetime.now(tz=datetime.now(tz=datetime.now().astimezone().tzinfo).astimezone().tzinfo).strftime("%Y"),
        )
        text = text.replace("[NAME]", article_name)
        text = text.replace(
            "[DATE]",
            datetime.now(tz=datetime.now(tz=datetime.now().astimezone().tzinfo).astimezone().tzinfo).strftime(
                "%Y-%m-%d"
            ),
        )
        text += f"\n# {article_name.capitalize().replace('-', ' ')}\n\n\n"

        result, filename = h.md.add_note(Path(self.config["path_articles"]), article_name, text, is_with_images=True)
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_articles"]}" "{filename}"')
        self.add_line(result)


class OnNewDiary(ActionBase):
    """Create a new diary entry for the current date.

    This action creates a new diary Markdown file in the configured diary directory
    using the current date, adds the configured template content, and opens it
    in the configured editor.
    """

    icon = "📖"
    title = "New diary note"

    @ActionBase.handle_exceptions("creating new diary entry")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        result, filename = h.md.add_diary_new_dairy_in_year(self.config["path_diary"], self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)


class OnNewDiaryDream(ActionBase):
    """Create a new dream journal entry for the current date.

    This action creates a new dream journal Markdown file in the configured dream directory
    using the current date, adds the configured template content, and opens it
    in the configured editor.
    """

    icon = "💤"
    title = "New dream note"

    @ActionBase.handle_exceptions("creating new dream entry")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        result, filename = h.md.add_diary_new_dream_in_year(self.config["path_dream"], self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)


class OnNewNoteDialog(ActionBase):
    """Create a new general note with a user-specified filename.

    This action prompts the user to save a new Markdown file in the configured notes directory,
    adds template content with the filename as the title, and opens it in the configured editor.
    Supports optional image directory creation.
    """

    icon = "📓"
    title = "New note"

    @ActionBase.handle_exceptions("creating new note")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        filename = self.get_save_filename("Save Note", self.config["path_notes"], "Markdown (*.md);;All Files (*)")
        if not filename:
            return

        self.add_line(f"Folder path: {filename.parent}")
        self.add_line(f"File name without extension: {filename.stem}")

        is_with_images = kwargs.get("is_with_images", False)

        text = self.config["beginning_of_md"] + f"\n# {filename.stem}\n\n\n"

        filename_final = filename.stem.replace("-", "--").replace(" ", "-")

        result, filename = h.md.add_note(filename.parent, filename_final, text, is_with_images=is_with_images)
        h.dev.run_command(f'{self.config["editor-notes"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)


class OnNewNoteDialogWithImages(OnNewNoteDialog):
    """Create a new general note with image support.

    This action extends the OnNewNoteDialog action by automatically creating
    an associated images directory for the new note.
    """

    icon = "📓"
    title = "New note with images"

    @ActionBase.handle_exceptions("creating new note with images")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        super().execute(is_with_images=True)


class OnNewQuotes(ActionBase):
    """Add new quotes with author and book title.

    This action allows you to add a quote with specified author and book title.
    """

    icon = "❞"
    title = "New quotes"

    @ActionBase.handle_exceptions("processing quotes")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.execute_format_with_author_and_book()

    def execute_format_with_author_and_book(self) -> None:
        """Format quotes with specified author and book title via dialog."""
        # Import at the beginning of the method
        from PySide6.QtWidgets import QComboBox
        from harrix_swiss_knife.filtered_combobox import apply_smart_filtering

        # Extract existing authors and books from quotes folder
        quotes_folder = self.config.get("path_quotes", "")
        author_books_dict = self._extract_authors_and_books_from_quotes_folder(quotes_folder)
        authors_list = sorted(author_books_dict.keys())

        # Create template fields for author, book, and quotes
        # Start with empty options for books - will be updated based on author selection
        fields = [
            TemplateField("Author", "combobox", "{{Author:combobox}}", "", options=authors_list),
            TemplateField("Book Title", "combobox", "{{Book Title:combobox}}", "", options=[]),
            TemplateField(
                "Quotes",
                "multiline",
                "{{Quotes:multiline}}",
                (
                    "They can get a big bang out of buying a blanket.\n\n\n"
                    "I just mean that I used to think about old Spencer quite a lot"
                ),
            ),
        ]

        # Show dialog to collect all information
        dialog = TemplateDialog(
            fields=fields,
            title="Enter Book, Author and Quotes",
        )

        # Connect author selection to book list update
        author_widget = dialog.widgets.get("Author")
        book_widget = dialog.widgets.get("Book Title")
        if isinstance(author_widget, QComboBox) and isinstance(book_widget, QComboBox):

            def update_book_list(author_text: str) -> None:
                """Update book list based on selected author."""
                # Store current book value
                current_book = book_widget.currentText()

                # Clear the widget completely
                book_widget.clear()

                # Remove old smart filtering if it exists
                if hasattr(book_widget, '_smart_filter_model'):
                    delattr(book_widget, '_smart_filter_model')
                if hasattr(book_widget, '_smart_filter_proxy'):
                    delattr(book_widget, '_smart_filter_proxy')
                if hasattr(book_widget, '_smart_filter_completer'):
                    delattr(book_widget, '_smart_filter_completer')
                if hasattr(book_widget, '_smart_filter_items'):
                    delattr(book_widget, '_smart_filter_items')

                if author_text and author_text in author_books_dict:
                    books = author_books_dict[author_text]
                    book_widget.addItems(books)
                    # Re-apply smart filtering after adding items
                    apply_smart_filtering(book_widget)

                    # Restore previous value if it's in the list
                    if current_book:
                        index = book_widget.findText(current_book)
                        if index >= 0:
                            book_widget.setCurrentIndex(index)
                        else:
                            book_widget.setCurrentText(current_book)
                else:
                    # No author selected - allow free text entry
                    book_widget.setCurrentText(current_book if current_book else "")

            author_widget.currentTextChanged.connect(update_book_list)

            # Trigger initial update if there's a default author
            if author_widget.currentText():
                update_book_list(author_widget.currentText())

        # Execute dialog
        if dialog.exec() != dialog.DialogCode.Accepted:
            self.add_line("❌ Dialog was canceled.")
            self.show_result()
            return

        field_values = dialog.get_field_values()
        if not field_values:
            self.add_line("❌ No field values collected.")
            self.show_result()
            return

        book_title = field_values.get("Book Title", "")
        author = field_values.get("Author", "")
        quotes_content = field_values.get("Quotes", "")

        if not book_title or not author or not quotes_content:
            self.add_line("❌ Book title, author and quotes are required.")
            self.show_result()
            return

        # Split quotes by double line breaks
        quotes = [q.strip() for q in quotes_content.split("\n\n") if q.strip()]

        # Build the formatted content in the same format as execute_format_quotes_from_text expects
        formatted_content = ""
        for quote in quotes:
            formatted_content += f"{quote}\n\n{book_title}\n{author}\n\n\n"

        # Remove trailing newlines
        formatted_content = formatted_content.rstrip()

        # Apply the same formatting function
        result = h.md.format_quotes_as_markdown_content(formatted_content)

        # Ask if user wants to save to file
        save_to_file = self.get_yes_no_question(
            "Save quotes to file?", "Do you want to save the formatted quotes to a file?"
        )

        if save_to_file:
            # Remove the header from quotes content since it will be added by the save function
            quotes_without_header = result
            if quotes_without_header.startswith(f"# {book_title}"):
                # Find the first empty line after the header
                lines = quotes_without_header.split("\n")
                for i_original, line in enumerate(lines):
                    i = i_original
                    if line.strip() == f"# {book_title}":
                        # Skip the header line and any following empty lines
                        while i + 1 < len(lines) and not lines[i + 1].strip():
                            i += 1
                        quotes_without_header = "\n".join(lines[i + 1 :]).lstrip()
                        break

            success = self._save_quotes_to_file(quotes_without_header, author, book_title)
            if success:
                self.add_line("✅ Quotes saved to file successfully!")
            else:
                self.add_line("❌ Failed to save quotes to file.")
        else:
            self.add_line(result)

        self.show_result()

    def _extract_authors_and_books_from_quotes_folder(self, quotes_folder: str) -> dict[str, list[str]]:
        """Extract authors and their books from markdown quote files.

        Scans all markdown files in the quotes folder and extracts author and book information
        from quote attributions in the format: `> -- _Author, Book Title_`
        Authors starting with `[` are excluded.

        Args:

        - `quotes_folder` (`str`): Path to the folder containing quote markdown files.

        Returns:

        - `dict[str, list[str]]`: Dictionary mapping author names to lists of their book titles.

        """
        author_books: dict[str, set[str]] = {}

        quotes_path = Path(quotes_folder)
        if not quotes_path.exists():
            return {}

        # Pattern to match quote attribution: > -- _Author, Book Title_
        # Matches: > -- _Author Name, Book Title_
        pattern = re.compile(r">\s*--\s*_([^_]+?),\s*([^_]+?)_", re.MULTILINE)

        # Recursively find all markdown files
        for md_file in quotes_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                # Find all matches
                matches = pattern.findall(content)
                for author, book in matches:
                    # Clean up whitespace
                    author_clean = author.strip()
                    book_clean = book.strip()
                    # Skip authors starting with [
                    if author_clean and not author_clean.startswith("["):
                        if author_clean not in author_books:
                            author_books[author_clean] = set()
                        if book_clean:
                            author_books[author_clean].add(book_clean)
            except Exception:
                # Skip files that can't be read
                continue

        # Convert sets to sorted lists
        return {author: sorted(books) for author, books in sorted(author_books.items())}

    def _save_quotes_to_file(self, quotes_content: str, author: str, book_title: str) -> bool:
        """Save quotes to a markdown file.

        Args:

        - `quotes_content` (`str`): Formatted quotes content
        - `author` (`str`): Author name
        - `book_title` (`str`): Book title

        Returns:

        - `bool`: True if file was saved successfully, False otherwise

        """
        # Ask user to select folder
        default_path = self.config.get("path_quotes", "")
        selected_folder = self.get_existing_directory("Select folder to save quotes", default_path)

        if not selected_folder:
            return False

        # Create author folder and file paths
        # Format author name: replace spaces with hyphens
        author_folder_name = "-".join(part.strip() for part in author.split() if part.strip())
        author_folder = selected_folder / author_folder_name
        author_folder.mkdir(exist_ok=True)

        # Format book title: remove quotes and replace spaces with hyphens
        clean_title = book_title.replace("«", "").replace("»", "").replace('"', "").replace("'", "")
        book_filename = "-".join(part.strip() for part in clean_title.split() if part.strip())
        filename = f"{book_filename}.md"
        file_path = author_folder / filename

        # Prepare content
        header = f"# {book_title}"
        separator = "---"

        # Check if file exists
        if file_path.exists():
            # Read existing content
            existing_content = file_path.read_text(encoding="utf-8")

            # Find the header and insert quotes after it, keeping existing content
            lines = existing_content.split("\n")
            new_lines = []
            header_found = False

            for i, line in enumerate(lines):
                new_lines.append(line)
                if line.strip() == header.strip():
                    header_found = True
                    # Add quotes after the header, then separator
                    new_lines.append("")  # Empty line after header
                    new_lines.append(quotes_content)
                    new_lines.append("")
                    new_lines.append(separator)
                    # Add the rest of the existing content
                    new_lines.extend(lines[i + 1 :])
                    break

            # If header not found, add at the end
            if not header_found:
                if not existing_content.rstrip().endswith("---"):
                    new_lines.extend(["", separator, "", quotes_content])
                else:
                    new_lines.extend(["", quotes_content])

            content = "\n".join(new_lines) + "\n"
        else:
            # Create new file with beginning template, header, and quotes
            beginning_template = self.config["beginning_of_md"]
            content = f"{beginning_template}\n{header}\n\n{quotes_content}\n"

        # Save file
        file_path.write_text(content, encoding="utf-8")
        return True


class OnOptimizeImagesFolder(ActionBase):
    """Optimize images in Markdown files with PNG/AVIF size comparison."""

    icon = "🖼️"
    title = "Optimize images in MD in …"

    @ActionBase.handle_exceptions("optimizing images with size comparison")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("optimizing images with size comparison thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", self.optimize_images_in_md_compare_sizes))

    def optimize_images_content_line(
        self,
        markdown_line: str,
        path_md: Path | str,
        image_folder: str = "img",
        *,
        is_convert_png_to_avif: bool = False,
        is_compare_png_avif_sizes: bool = False,
    ) -> str:
        """Process a single line of Markdown to optimize any image reference it contains.

        Args:

        - `markdown_line` (`str`): A single line from the Markdown document.
        - `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
        - `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.
        - `is_convert_png_to_avif` (`bool`): Flag for converting PNG to AVIF. Defaults to `False`.
        - `is_compare_png_avif_sizes` (`bool`): Flag for comparing PNG and AVIF sizes and keeping smaller.
          Defaults to `False`.

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
                    supported_extensions = [".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".png", ".svg", ".avif"]

                    if ext in supported_extensions:
                        # Determine the new extension based on the current one
                        new_ext = ext
                        if ext in [".jpg", ".jpeg", ".webp", ".gif", ".mp4"]:
                            new_ext = ".avif"
                        elif ext == ".png":
                            if is_compare_png_avif_sizes:
                                # Will be determined by the optimization script
                                pass
                            elif is_convert_png_to_avif:
                                new_ext = ".avif"
                            # Otherwise keep .png
                        # For .svg and .avif, keep the original extension

                        # Create temporary directory for optimization
                        with TemporaryDirectory() as temp_folder:
                            temp_folder_path = Path(temp_folder)
                            temp_image_filename = temp_folder_path / image_filename.name
                            shutil.copy(image_filename, temp_image_filename)

                            # Run the optimization command
                            commands = f'npm run optimize imagesFolder="{temp_folder}"'
                            if is_compare_png_avif_sizes and ext == ".png":
                                commands += " convertPngToAvif=compare"
                            elif is_convert_png_to_avif and ext == ".png":
                                commands += " convertPngToAvif=true"

                            h.dev.run_command(commands)

                            # Path to the optimized images directory
                            optimized_images_dir = temp_folder_path / "temp"

                            # For PNG with size comparison, check results file
                            if is_compare_png_avif_sizes and ext == ".png":
                                results_file = optimized_images_dir / "optimization_results.json"
                                if results_file.exists():
                                    with Path.open(results_file) as f:
                                        results = json.load(f)

                                    stem = image_filename.stem
                                    if stem in results:
                                        new_ext = results[stem]

                            # Path to the optimized image
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

    def optimize_images_in_md_compare_sizes(self, filename: Path | str) -> str:
        """Optimize images in a Markdown file with PNG/AVIF size comparison.

        This function reads a Markdown file, processes any local images referenced in it,
        optimizes them, and for PNG images compares optimized PNG vs AVIF sizes to keep the smaller one.

        Args:

        - `filename` (`Path | str`): Path to the Markdown file to process.

        Returns:

        - `str`: A status message indicating whether the file was modified.

        """
        filename = Path(filename)
        with Path.open(filename, encoding="utf-8") as f:
            document = f.read()

        document_new = self.optimize_images_in_md_content(
            document, filename.parent, is_convert_png_to_avif=False, is_compare_png_avif_sizes=True
        )

        if document != document_new:
            with Path.open(filename, "w", encoding="utf-8") as file:
                file.write(document_new)
            return f"✅ File {filename} applied."
        return "File is not changed."

    def optimize_images_in_md_content(
        self,
        markdown_text: str,
        path_md: Path | str,
        image_folder: str = "img",
        *,
        is_convert_png_to_avif: bool = False,
        is_compare_png_avif_sizes: bool = False,
    ) -> str:
        """Optimize images referenced in Markdown content by converting them to more efficient formats.

        This function processes Markdown content to find local image references, optimizes those images,
        and updates the Markdown content to reference the optimized versions. Remote images (URLs)
        are left unchanged.

        Args:

        - `markdown_text` (`str`): The Markdown content to process.
        - `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
        - `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.
        - `is_convert_png_to_avif` (`bool`): Flag for converting PNG to AVIF. Defaults to `False`.
        - `is_compare_png_avif_sizes` (`bool`): Flag for comparing PNG and AVIF sizes and keeping smaller.
          Defaults to `False`.

        Returns:

        - `str`: The updated Markdown content with references to optimized images.

        Notes:

        - Images with extensions .jpg, .jpeg, .webp, .gif, and .mp4 will be converted to .avif
        - PNG files behavior depends on flags:
          - If `is_compare_png_avif_sizes` is True: compares optimized PNG vs AVIF and keeps smaller
          - If `is_convert_png_to_avif` is True: converts PNG to AVIF
          - Otherwise: optimizes PNG and keeps as PNG
        - SVG files keep their original format but may still be optimized
        - The optimization process uses an external npm script
        - Code blocks in the Markdown are preserved without changes

        """
        yaml_md, content_md = h.md.split_yaml_content(markdown_text)

        new_lines = []
        lines = content_md.split("\n")
        for line_content, is_code_block in h.md.identify_code_blocks(lines):
            if is_code_block:
                new_lines.append(line_content)
                continue

            processed_line = self.optimize_images_content_line(
                line_content,
                path_md,
                image_folder,
                is_convert_png_to_avif=is_convert_png_to_avif,
                is_compare_png_avif_sizes=is_compare_png_avif_sizes,
            )
            new_lines.append(processed_line)
        content_md = "\n".join(new_lines)

        return yaml_md + "\n\n" + content_md

    @ActionBase.handle_exceptions("optimizing images with size comparison thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnOptimizeSelectedImages(ActionBase):
    """Optimize specific selected images in their corresponding Markdown file.

    This action allows users to select specific image files and optimizes only those
    images within their corresponding Markdown file. The action:

    1. Opens a file dialog to select multiple image files
    2. Finds the Markdown file one level up from the selected images
    3. Optimizes only the selected images within that Markdown file
    4. Updates the Markdown file with references to the optimized images

    This is useful when you want to optimize specific images without processing
    all images in a folder or when working with images in a specific location.
    """

    icon = "🖼️"
    title = "Optimize selected images in MD"
    bold_title = True

    @ActionBase.handle_exceptions("optimizing selected images")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.selected_images = self.get_open_filenames(
            "Select images to optimize",
            self.config["path_articles"],
            "Image files (*.png *.jpg *.jpeg *.gif *.webp *.mp4 *.svg *.avif);;All Files (*)",
        )
        if not self.selected_images:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def find_markdown_file_one_level_up(self, image_dir: Path) -> Path | None:
        """Find a Markdown file one level up from the given directory.

        Args:

        - `image_dir` (`Path`): Directory containing the images.

        Returns:

        - `Path | None`: Path to the Markdown file if found, None otherwise.

        """
        parent_dir = image_dir.parent
        md_files = list(parent_dir.glob("*.md"))

        if md_files:
            # Return the first .md file found
            return md_files[0]
        return None

    @ActionBase.handle_exceptions("optimizing selected images thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if not self.selected_images:
            return

        # Group images by their parent directory to find corresponding MD files
        images_by_dir = {}
        for image_path in self.selected_images:
            parent_dir = image_path.parent
            if parent_dir not in images_by_dir:
                images_by_dir[parent_dir] = []
            images_by_dir[parent_dir].append(image_path)

        processed_files = []
        for parent_dir, images in images_by_dir.items():
            # Look for Markdown file one level up
            md_file = self.find_markdown_file_one_level_up(parent_dir)
            if md_file:
                self.add_line(f"🔵 Found MD file: {md_file}")
                self.add_line(f"🔵 Processing {len(images)} images in {parent_dir}")

                # Optimize only the selected images in this MD file
                result = self.optimize_selected_images_in_md(md_file, images)
                processed_files.append((md_file, result))
            else:
                self.add_line(f"❌ No Markdown file found one level up from {parent_dir}")

        if processed_files:
            self.add_line(f"✅ Processed {len(processed_files)} Markdown file(s)")
        else:
            self.add_line("❌ No Markdown files were processed")

    def optimize_selected_images_content(
        self,
        markdown_text: str,
        path_md: Path | str,
        selected_image_names: set[str],
        image_folder: str = "img",
    ) -> str:
        """Optimize only selected images referenced in Markdown content.

        Args:

        - `markdown_text` (`str`): The Markdown content to process.
        - `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
        - `selected_image_names` (`set[str]`): Set of image filenames to optimize.
        - `image_folder` (`str`): Folder name where optimized images will be stored. Defaults to `"img"`.

        Returns:

        - `str`: The updated Markdown content with references to optimized images.

        """
        yaml_md, content_md = h.md.split_yaml_content(markdown_text)

        new_lines = []
        lines = content_md.split("\n")
        for line_content, is_code_block in h.md.identify_code_blocks(lines):
            if is_code_block:
                new_lines.append(line_content)
                continue

            processed_line = self.optimize_selected_images_content_line(
                line_content,
                path_md,
                selected_image_names,
                image_folder,
            )
            new_lines.append(processed_line)
        content_md = "\n".join(new_lines)

        return yaml_md + "\n\n" + content_md

    def optimize_selected_images_content_line(
        self,
        markdown_line: str,
        path_md: Path | str,
        selected_image_names: set[str],
        image_folder: str = "img",
    ) -> str:
        """Process a single line of Markdown to optimize only selected image references.

        Args:

        - `markdown_line` (`str`): A single line from the Markdown document.
        - `path_md` (`Path | str`): Path to the Markdown file or its containing directory.
        - `selected_image_names` (`set[str]`): Set of image filenames to optimize.
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

                # Check if the image exists and is in our selected images
                if image_filename.exists() and image_filename.name in selected_image_names:
                    # Get the extension
                    ext = image_filename.suffix.lower()
                    supported_extensions = [".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".png", ".svg", ".avif"]

                    if ext in supported_extensions:
                        # Determine the new extension based on the current one
                        new_ext = ext
                        if ext in [".jpg", ".jpeg", ".webp", ".gif", ".mp4"]:
                            new_ext = ".avif"
                        elif ext == ".png":
                            # For PNG, compare sizes and keep smaller
                            new_ext = ".png"  # Will be determined by optimization

                        # Create temporary directory for optimization
                        with TemporaryDirectory() as temp_folder:
                            temp_folder_path = Path(temp_folder)
                            temp_image_filename = temp_folder_path / image_filename.name
                            shutil.copy(image_filename, temp_image_filename)

                            # Run the optimization command
                            commands = f'npm run optimize imagesFolder="{temp_folder}"'
                            if ext == ".png":
                                commands += " convertPngToAvif=compare"

                            h.dev.run_command(commands)

                            # Path to the optimized images directory
                            optimized_images_dir = temp_folder_path / "temp"

                            # For PNG with size comparison, check results file
                            if ext == ".png":
                                results_file = optimized_images_dir / "optimization_results.json"
                                if results_file.exists():
                                    with Path.open(results_file) as f:
                                        results = json.load(f)

                                    stem = image_filename.stem
                                    if stem in results:
                                        new_ext = results[stem]

                            # Path to the optimized image
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

    def optimize_selected_images_in_md(self, md_file: Path, selected_images: list[Path]) -> str:
        """Optimize only the selected images in a Markdown file.

        Args:

        - `md_file` (`Path`): Path to the Markdown file.
        - `selected_images` (`list[Path]`): List of selected image paths to optimize.

        Returns:

        - `str`: Status message indicating the result of the operation.

        """
        try:
            with Path.open(md_file, encoding="utf-8") as f:
                document = f.read()

            # Get the names of selected images for filtering
            selected_image_names = {img.name for img in selected_images}

            # Process the document, optimizing only selected images
            document_new = self.optimize_selected_images_content(document, md_file.parent, selected_image_names)

            if document != document_new:
                with Path.open(md_file, "w", encoding="utf-8") as file:
                    file.write(document_new)
                return f"✅ File {md_file} updated with optimized images."
        except Exception as e:
            return f"❌ Error processing {md_file}: {e}"
        return f"ℹ️ File {md_file} was not changed (no selected images found)."  # noqa: RUF001

    @ActionBase.handle_exceptions("optimizing selected images thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnSortSections(ActionBase):
    """Organize and enhance a single Markdown file by sorting sections and generating image captions.

    This action processes a user-selected Markdown file, performing two key operations
    to improve its structure and readability:

    1. Section sorting:
       - Identifies sections (headings) within the Markdown file
       - Sorts sections in a logical order based on heading level and content
       - Maintains the hierarchy and structure of nested sections
       - Preserves the content within each section while reordering

    2. Image caption generation:
       - Identifies images within the Markdown file
       - Creates or updates captions for images based on their context or filename
       - Ensures consistent formatting for image references

    Unlike the folder-based version of this action, this operates on a single file selected
    by the user. The user is prompted to select a Markdown file, with the default location
    being the notes directory specified in the configuration.
    """

    icon = "📶"
    title = "Sort sections in one MD"

    @ActionBase.handle_exceptions("sorting sections in markdown file")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.filename = self.get_open_filename(
            "Open Markdown file",
            self.config["path_notes"],
            "Markdown (*.md);;All Files (*)",
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("sorting sections thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.filename is None:
            return
        self.add_line(h.md.sort_sections(self.filename))

    @ActionBase.handle_exceptions("sorting sections thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()
