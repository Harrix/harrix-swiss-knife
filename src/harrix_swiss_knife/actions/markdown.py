"""Actions for Python development and Markdown file management."""

from datetime import datetime
from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife import markdown_checker
from harrix_swiss_knife.actions import markdown_utils
from harrix_swiss_knife.actions.base import ActionBase


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

    icon = "😎"
    title = "Beautify MD in …"

    @ActionBase.handle_exceptions("beautifying markdown folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select a folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
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
        markdown_utils.beautify_markdown_common(self, str(self.folder_path), is_include_summaries_and_combine=False)

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

    icon = "😎"
    title = "Beautify MD and regenerate .g.md in …"
    bold_title = True

    @ActionBase.handle_exceptions("beautifying markdown folder and regenerating g.md")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select a folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
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
        markdown_utils.beautify_markdown_common(self, str(self.folder_path), is_include_summaries_and_combine=True)

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
            "Select a folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("markdown folder checking thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        checker = markdown_checker.MarkdownChecker()
        if self.folder_path is None:
            return
        errors = h.file.check_func(self.folder_path, ".md", checker)
        if errors:
            self.add_line("\n".join(errors))
            self.add_line(f"🔢 Count errors = {len(errors)}")
        else:
            self.add_line(f"✅ There are no errors in {self.folder_path}.")

    @ActionBase.handle_exceptions("markdown folder checking thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnDownloadAndReplaceImages(ActionBase):
    """Download remote images and replace URLs with local references in a Markdown file.

    This action processes a selected Markdown file to find image URLs, downloads the images
    to a local directory, and updates the Markdown to reference these local copies instead
    of the remote URLs, improving document portability and reducing external dependencies.
    """

    icon = "📥"
    title = "Download images in one MD"

    @ActionBase.handle_exceptions("downloading images in markdown file")
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

    @ActionBase.handle_exceptions("downloading images thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.filename is None:
            return
        self.add_line(h.md.download_and_replace_images(self.filename))

    @ActionBase.handle_exceptions("downloading images thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.filename} completed")
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
            "Select a folder with Markdown files", self.config["path_articles"]
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


class OnGenerateShortNoteTocWithLinks(ActionBase):
    """Generate a condensed version of a document with only its table of contents.

    This action creates a shortened version of a selected Markdown file that
    includes only the document's title and table of contents with working links.
    Useful for creating quick reference documents or previews of longer content.
    """

    icon = "🧏"
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
    title = "Increase heading level"

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
            datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y"),
        )
        text = text.replace("[NAME]", article_name)
        text = text.replace("[DATE]", datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d"))
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


class OnOptimizeImages(ActionBase):
    """Optimize images referenced in a Markdown file.

    This action allows the user to select a Markdown file and optimizes
    all images referenced within it using the optimize_images_in_md function.
    """

    icon = "🖼️"
    title = "Optimize images in one MD"

    @ActionBase.handle_exceptions("optimizing images in markdown file")
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

    @ActionBase.handle_exceptions("optimizing images in markdown thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.filename is None:
            return
        self.add_line(markdown_utils.optimize_images_in_md(self.filename))

    @ActionBase.handle_exceptions("optimizing images in markdown thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnOptimizeImagesFolder(ActionBase):
    """Optimize images referenced in Markdown files within a selected folder.

    This action processes all Markdown files in a selected directory, identifying image
    references and performing various optimizations to improve image quality, reduce file size,
    and enhance overall performance.
    """

    icon = "🖼️"
    title = "Optimize images in …"

    @ActionBase.handle_exceptions("optimizing images in folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("optimizing images folder thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", markdown_utils.optimize_images_in_md))

    @ActionBase.handle_exceptions("optimizing images folder thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnOptimizeImagesFolderCompareSize(ActionBase):
    """Optimize images in Markdown files with PNG/AVIF size comparison."""

    icon = "⚖️"
    title = "Optimize images (compare PNG/AVIF sizes) in …"

    @ActionBase.handle_exceptions("optimizing images with size comparison")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("optimizing images with size comparison thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", markdown_utils.optimize_images_in_md_compare_sizes))

    @ActionBase.handle_exceptions("optimizing images with size comparison thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnOptimizeImagesFolderPngToAvif(ActionBase):
    """Optimize images in Markdown files and convert PNG images to AVIF format too."""

    icon = "🖼️"
    title = "Optimize images (with PNG to AVIF) in …"

    @ActionBase.handle_exceptions("optimizing images with PNG to AVIF conversion")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("optimizing images PNG to AVIF thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", markdown_utils.optimize_images_in_md_png_to_avif))

    @ActionBase.handle_exceptions("optimizing images PNG to AVIF thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnQuotesFormatAsMarkdownContent(ActionBase):
    """Format plain text quotes into properly structured Markdown."""

    icon = "❞"
    title = "Quotes. Format quotes as Markdown content"

    @ActionBase.handle_exceptions("formatting quotes as markdown")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        default_text = """They can get a big bang out of buying a blanket.

The Catcher in the Rye
J.D. Salinger


I just mean that I used to think about old Spencer quite a lot

The Catcher in the Rye
J.D. Salinger"""
        content = self.get_text_textarea("Quotes", "Input quotes", default_text)
        if not content:
            return

        result = h.md.format_quotes_as_markdown_content(content)

        self.add_line(result)
        self.show_result()


class OnQuotesGenerateAuthorAndBook(ActionBase):
    """Process quote files to add author and book information.

    This action traverses a folder of quote Markdown files and processes each file
    to generate or update author and book information based on the content structure.
    Useful for maintaining a consistent format in a collection of literary quotes.
    """

    icon = "❞"
    title = "Quotes. Add author and title"

    @ActionBase.handle_exceptions("generating author and book information")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.show_instructions("""Given a file like `C:/test/Name_Surname/Title_of_book.md` with content:

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
        self.folder_path = self.get_existing_directory("Select a folder with quotes", self.config["path_quotes"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("generating author book thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        result = h.file.apply_func(self.folder_path, ".md", h.md.generate_author_book)
        self.add_line(result)

    @ActionBase.handle_exceptions("generating author book thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
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
