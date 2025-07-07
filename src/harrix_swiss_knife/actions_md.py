"""Actions for Python development and Markdown file management."""

from datetime import datetime
from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife import action_base, funcs_md, markdown_checker


class OnBeautifyMdFolder(action_base.ActionBase):
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

    @action_base.ActionBase.handle_exceptions("beautifying markdown folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select a folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("beautifying markdown thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
        if self.folder_path is None:
            return
        funcs_md.beautify_markdown_common(self, str(self.folder_path), is_include_summaries_and_combine=False)

    @action_base.ActionBase.handle_exceptions("beautifying markdown thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnBeautifyMdFolderAndRegenerateGMd(action_base.ActionBase):
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

    @action_base.ActionBase.handle_exceptions("beautifying markdown folder and regenerating g.md")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select a folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("beautifying and regenerating thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        self.add_line(f"🔵 Starting processing for path: {self.folder_path}")
        if self.folder_path is None:
            return
        funcs_md.beautify_markdown_common(self, str(self.folder_path), is_include_summaries_and_combine=True)

    @action_base.ActionBase.handle_exceptions("beautifying and regenerating thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnCheckMd(action_base.ActionBase):
    """Action to check a Markdown file for errors with Harrix rules."""

    icon = "🚧"
    title = "Check one MD"

    @action_base.ActionBase.handle_exceptions("checking markdown file")
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

    @action_base.ActionBase.handle_exceptions("markdown checking thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        checker = markdown_checker.MarkdownChecker()
        if self.filename is None:
            return
        errors = checker(self.filename)
        if errors:
            self.add_line("\n".join(errors))
            self.add_line(f"🔢 Count errors = {len(errors)}")
        else:
            self.add_line(f"✅ There are no errors in {self.filename}.")

    @action_base.ActionBase.handle_exceptions("markdown checking thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnCheckMdFolder(action_base.ActionBase):
    """Action to check all Markdown files in a folder for errors with Harrix rules."""

    icon = "🚧"
    title = "Check in …"

    @action_base.ActionBase.handle_exceptions("checking markdown folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_folder_with_choice_option(
            "Select a folder with Markdown files", self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("markdown folder checking thread")
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

    @action_base.ActionBase.handle_exceptions("markdown folder checking thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnCombineMarkdownFiles(action_base.ActionBase):
    """Combine related Markdown files in a directory structure.

    This action processes a selected folder to find and combine related Markdown files
    based on predefined patterns or references between files. After combining the files,
    it applies Prettier formatting to ensure consistent styling across all documents.
    """

    icon = "🔗"
    title = "Combine MD files in …"

    @action_base.ActionBase.handle_exceptions("combining markdown files")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", self.config["path_notes"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("combining markdown files thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.md.combine_markdown_files_recursively(self.folder_path))

        commands = f"cd {self.folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)

    @action_base.ActionBase.handle_exceptions("combining markdown files thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnDownloadAndReplaceImages(action_base.ActionBase):
    """Download remote images and replace URLs with local references in a Markdown file.

    This action processes a selected Markdown file to find image URLs, downloads the images
    to a local directory, and updates the Markdown to reference these local copies instead
    of the remote URLs, improving document portability and reducing external dependencies.
    """

    icon = "📥"
    title = "Download images in one MD"

    @action_base.ActionBase.handle_exceptions("downloading images in markdown file")
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

    @action_base.ActionBase.handle_exceptions("downloading images thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.filename is None:
            return
        self.add_line(h.md.download_and_replace_images(self.filename))

    @action_base.ActionBase.handle_exceptions("downloading images thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnDownloadAndReplaceImagesFolder(action_base.ActionBase):
    """Download remote images and replace URLs with local references in multiple Markdown files.

    This action processes all Markdown files in a selected folder to find image URLs,
    downloads the images to local directories, and updates the Markdown files to reference
    these local copies instead of the remote URLs, improving document portability and
    reducing external dependencies across an entire collection of documents.
    """

    icon = "📥"
    title = "Download images in …"

    @action_base.ActionBase.handle_exceptions("downloading images in folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("downloading images folder thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.download_and_replace_images))

    @action_base.ActionBase.handle_exceptions("downloading images folder thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnFormatQuotesAsMarkdownContent(action_base.ActionBase):
    """Format plain text quotes into properly structured Markdown."""

    icon = "❞"
    title = "Format quotes as Markdown content"

    @action_base.ActionBase.handle_exceptions("formatting quotes as markdown")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        content = self.get_text_textarea("Quotes", "Input quotes")
        if not content:
            return

        result = h.md.format_quotes_as_markdown_content(content)

        self.add_line(result)
        self.show_result()


class OnFormatYaml(action_base.ActionBase):
    """Format YAML frontmatter in Markdown files within a folder."""

    icon = "✨"
    title = "Format YAML in …"

    @action_base.ActionBase.handle_exceptions("formatting YAML in folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("formatting YAML thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.format_yaml))

    @action_base.ActionBase.handle_exceptions("formatting YAML thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnGenerateAuthorBook(action_base.ActionBase):
    """Process quote files to add author and book information.

    This action traverses a folder of quote Markdown files and processes each file
    to generate or update author and book information based on the content structure.
    Useful for maintaining a consistent format in a collection of literary quotes.
    """

    icon = "❞"
    title = "Quotes. Add author and title"

    @action_base.ActionBase.handle_exceptions("generating author and book information")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory("Select a folder with quotes", self.config["path_quotes"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("generating author book thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        result = h.file.apply_func(self.folder_path, ".md", h.md.generate_author_book)
        self.add_line(result)

    @action_base.ActionBase.handle_exceptions("generating author book thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnGenerateImageCaptions(action_base.ActionBase):
    """Add captions to images in a single Markdown file.

    This action processes a selected Markdown file to add or update captions
    for all images found in the document, enhancing readability and accessibility
    of image content.
    """

    icon = "🌄"
    title = "Add image captions in one MD"

    @action_base.ActionBase.handle_exceptions("generating image captions")
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

    @action_base.ActionBase.handle_exceptions("generating image captions thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.filename is None:
            return
        self.add_line(h.md.generate_image_captions(self.filename))

    @action_base.ActionBase.handle_exceptions("generating image captions thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnGenerateImageCaptionsFolder(action_base.ActionBase):
    """Add captions to images in all Markdown files within a folder.

    This action processes all Markdown files in a selected folder to add or update captions
    for all images found in the documents, enhancing readability and accessibility
    of image content across an entire collection of documents.
    """

    icon = "🌄"
    title = "Add image captions in …"

    @action_base.ActionBase.handle_exceptions("generating image captions in folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("generating image captions folder thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.generate_image_captions))

    @action_base.ActionBase.handle_exceptions("generating image captions folder thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnGenerateShortNoteTocWithLinks(action_base.ActionBase):
    """Generate a condensed version of a document with only its table of contents.

    This action creates a shortened version of a selected Markdown file that
    includes only the document's title and table of contents with working links.
    Useful for creating quick reference documents or previews of longer content.
    """

    icon = "🤏"
    title = "Generate a short version with only TOC"

    @action_base.ActionBase.handle_exceptions("generating short note with TOC")
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

    @action_base.ActionBase.handle_exceptions("generating short note TOC thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.filename is None:
            return
        self.add_line(h.md.generate_short_note_toc_with_links(self.filename))

    @action_base.ActionBase.handle_exceptions("generating short note TOC thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnGenerateToc(action_base.ActionBase):
    """Generate a table of contents for a single Markdown file.

    This action prompts the user to select a Markdown file and generates
    a table of contents with links to all headings in the file.
    """

    icon = "📑"
    title = "Generate TOC in one MD"

    @action_base.ActionBase.handle_exceptions("generating TOC")
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

    @action_base.ActionBase.handle_exceptions("generating TOC thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.filename is None:
            return
        self.add_line(h.md.generate_toc_with_links(self.filename))

    @action_base.ActionBase.handle_exceptions("generating TOC thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnGenerateTocFolder(action_base.ActionBase):
    """Generate tables of contents for all Markdown files in a folder.

    This action prompts the user to select a folder and generates
    tables of contents with links to all headings in every Markdown file
    found in that folder.
    """

    icon = "📑"
    title = "Generate TOC in …"

    @action_base.ActionBase.handle_exceptions("generating TOC in folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("generating TOC folder thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.generate_toc_with_links))

    @action_base.ActionBase.handle_exceptions("generating TOC folder thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnGetListMoviesBooks(action_base.ActionBase):
    """Extract and format a list of movies or books from Markdown content.

    This action takes Markdown content with level-3 headings (`### Title`)
    and converts them into a bulleted list, counting the total number of items.
    Useful for creating web-friendly lists from structured Markdown content.
    """

    icon = "🎬"
    title = "Get a list of movies, books for web"

    @action_base.ActionBase.handle_exceptions("extracting movies/books list")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        content = self.get_text_textarea("Markdown content", "Input Markdown content")
        if not content:
            return

        result = ""
        count = 0
        for line in content.splitlines():
            if line.startswith("### "):
                result += f"- {line[4:].strip()}\n"
                count += 1

        result += f"\nCount: {count}"
        self.add_line(result)
        self.show_result()


class OnIncreaseHeadingLevelContent(action_base.ActionBase):
    """Increase the heading level of all headings in Markdown content.

    This action takes Markdown content and increases the level of all headings
    by adding an additional '#' character to each heading, making them one level
    deeper in the document hierarchy.
    """

    icon = "👉"
    title = "Increase heading level"

    @action_base.ActionBase.handle_exceptions("increasing heading level")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        content = self.get_text_textarea("Markdown content", "Input Markdown content")
        if not content:
            return

        new_content = h.md.increase_heading_level_content(content)
        self.add_line(new_content)
        self.show_result()


class OnNewArticle(action_base.ActionBase):
    """Create a new article with predefined template.

    This action prompts the user for an article title, creates a new Markdown file
    in the configured articles directory, and opens it in the configured editor.
    """

    icon = "✍️"
    title = "New article"

    @action_base.ActionBase.handle_exceptions("creating new article")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        article_name = self.get_text_input("Article title", "Enter the name of the article (English, without spaces):")
        if not article_name:
            return

        article_name = article_name.replace(" ", "-")

        text = self.config["beginning_of_article"].replace(
            "[YEAR]",
            datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y"),
        )
        text = text.replace("[NAME]", article_name)
        text = text.replace("[DATE]", datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d"))
        text += f"\n# {article_name}\n\n\n"

        result, filename = h.md.add_note(Path(self.config["path_articles"]), article_name, text, is_with_images=True)
        h.dev.run_command(f'{self.config["editor"]} "{self.config["vscode_workspace_articles"]}" "{filename}"')
        self.add_line(result)


class OnNewDiary(action_base.ActionBase):
    """Create a new diary entry for the current date.

    This action creates a new diary Markdown file in the configured diary directory
    using the current date, adds the configured template content, and opens it
    in the configured editor.
    """

    icon = "📖"
    title = "New diary note"

    @action_base.ActionBase.handle_exceptions("creating new diary entry")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        result, filename = h.md.add_diary_new_dairy_in_year(self.config["path_diary"], self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)


class OnNewDiaryDream(action_base.ActionBase):
    """Create a new dream journal entry for the current date.

    This action creates a new dream journal Markdown file in the configured dream directory
    using the current date, adds the configured template content, and opens it
    in the configured editor.
    """

    icon = "💤"
    title = "New dream note"

    @action_base.ActionBase.handle_exceptions("creating new dream entry")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        result, filename = h.md.add_diary_new_dream_in_year(self.config["path_dream"], self.config["beginning_of_md"])
        h.dev.run_command(f'{self.config["editor"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)


class OnNewNoteDialog(action_base.ActionBase):
    """Create a new general note with a user-specified filename.

    This action prompts the user to save a new Markdown file in the configured notes directory,
    adds template content with the filename as the title, and opens it in the configured editor.
    Supports optional image directory creation.
    """

    icon = "📓"
    title = "New note"

    @action_base.ActionBase.handle_exceptions("creating new note")
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
        h.dev.run_powershell_script(f'{self.config["editor"]} "{self.config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)


class OnNewNoteDialogWithImages(action_base.ActionBase):
    """Create a new general note with image support.

    This action extends the OnNewNoteDialog action by automatically creating
    an associated images directory for the new note.
    """

    icon = "📓"
    title = "New note with images"

    @action_base.ActionBase.handle_exceptions("creating new note with images")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        super().execute(is_with_images=True)


class OnOptimizeImages(action_base.ActionBase):
    """Optimize images referenced in a Markdown file.

    This action allows the user to select a Markdown file and optimizes
    all images referenced within it using the optimize_images_in_md function.
    """

    icon = "🖼️"
    title = "Optimize images in one MD"

    @action_base.ActionBase.handle_exceptions("optimizing images in markdown file")
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

    @action_base.ActionBase.handle_exceptions("optimizing images in markdown thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.filename is None:
            return
        self.add_line(funcs_md.optimize_images_in_md(self.filename))

    @action_base.ActionBase.handle_exceptions("optimizing images in markdown thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnOptimizeImagesFolder(action_base.ActionBase):
    """Optimize images referenced in Markdown files within a selected folder.

    This action processes all Markdown files in a selected directory, identifying image
    references and performing various optimizations to improve image quality, reduce file size,
    and enhance overall performance.
    """

    icon = "🖼️"
    title = "Optimize images in …"

    @action_base.ActionBase.handle_exceptions("optimizing images in folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("optimizing images folder thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", funcs_md.optimize_images_in_md))

    @action_base.ActionBase.handle_exceptions("optimizing images folder thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnOptimizeImagesFolderPngToAvif(action_base.ActionBase):
    """Optimize images in Markdown files and convert PNG images to AVIF format too."""

    icon = "🖼️"
    title = "Optimize images (with PNG to AVIF) in …"

    @action_base.ActionBase.handle_exceptions("optimizing images with PNG to AVIF conversion")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_articles"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("optimizing images PNG to AVIF thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.folder_path is None:
            return
        self.add_line(h.file.apply_func(self.folder_path, ".md", funcs_md.optimize_images_in_md_png_to_avif))

    @action_base.ActionBase.handle_exceptions("optimizing images PNG to AVIF thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnPettierFolder(action_base.ActionBase):
    """Format Markdown files in a selected folder using Prettier."""

    icon = "✨"
    title = "Prettier in …"

    @action_base.ActionBase.handle_exceptions("running Prettier in folder")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Execute the code. Main method for the action."""
        self.folder_path = self.get_existing_directory(
            "Select a folder with Markdown files", self.config["path_github"]
        )
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @action_base.ActionBase.handle_exceptions("Prettier formatting thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        commands = f"cd {self.folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)

    @action_base.ActionBase.handle_exceptions("Prettier formatting thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnSortSections(action_base.ActionBase):
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

    @action_base.ActionBase.handle_exceptions("sorting sections in markdown file")
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

    @action_base.ActionBase.handle_exceptions("sorting sections thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        if self.filename is None:
            return
        self.add_line(h.md.sort_sections(self.filename))
        self.add_line(h.md.generate_image_captions(self.filename))

    @action_base.ActionBase.handle_exceptions("sorting sections thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()
