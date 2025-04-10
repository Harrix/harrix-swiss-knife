from datetime import datetime
from pathlib import Path
import re

import harrix_pylib as h

from harrix_swiss_knife import action_base, funcs

config = h.dev.load_config("config/config.json")


class OnCombineMarkdownFiles(action_base.ActionBase):
    icon = "🔗"
    title = "Combine MD files in …"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_notes"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        self.add_line(h.md.combine_markdown_files_recursively(self.folder_path))

        commands = f"cd {self.folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)

    def thread_after(self, result):
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnDownloadAndReplaceImages(action_base.ActionBase):
    icon = "📥"
    title = "Download images in one MD"

    def execute(self, *args, **kwargs):
        self.filename = self.get_open_filename(
            "Open Markdown file", config["path_notes"], "Markdown (*.md);;All Files (*)"
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        try:
            self.add_line(h.md.download_and_replace_images(self.filename))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")

    def thread_after(self, result):
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnDownloadAndReplaceImagesFolder(action_base.ActionBase):
    icon = "📥"
    title = "Download images in …"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.download_and_replace_images))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result):
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnFormatYaml(action_base.ActionBase):
    icon = "✨"
    title = "Format YAML"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.format_yaml))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result):
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnGenerateAuthorBook(action_base.ActionBase):
    icon = "❞"
    title = "Quotes. Add author and title"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select a folder with quotes", config["path_quotes"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        try:
            result = h.file.apply_func(self.folder_path, ".md", h.md.generate_author_book)
            self.add_line(result)
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")

    def thread_after(self, result):
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnGenerateImageCaptions(action_base.ActionBase):
    icon = "🌄"
    title = "Add image captions in one MD"

    def execute(self, *args, **kwargs):
        self.filename = self.get_open_filename(
            "Open Markdown file", config["path_articles"], "Markdown (*.md);;All Files (*)"
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        try:
            self.add_line(h.md.generate_image_captions(self.filename))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")

    def thread_after(self, result):
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnGenerateImageCaptionsFolder(action_base.ActionBase):
    icon = "🌄"
    title = "Add image captions in …"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.generate_image_captions))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result):
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnGenerateToc(action_base.ActionBase):
    icon = "📑"
    title = "Generate TOC in one MD"

    def execute(self, *args, **kwargs):
        self.filename = self.get_open_filename(
            "Open Markdown file", config["path_articles"], "Markdown (*.md);;All Files (*)"
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        try:
            self.add_line(h.md.generate_toc_with_links(self.filename))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")

    def thread_after(self, result):
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnGenerateTocFolder(action_base.ActionBase):
    icon = "📑"
    title = "Generate TOC in …"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.generate_toc_with_links))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result):
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnGetListMoviesBooks(action_base.ActionBase):
    icon = "🎬"
    title = "Get a list of movies, books for web"

    def execute(self, *args, **kwargs):
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
    icon = "👉"
    title = "Increase heading level"

    def execute(self, *args, **kwargs):
        content = self.get_text_textarea("Markdown content", "Input Markdown content")
        if not content:
            return

        new_content = h.md.increase_heading_level_content(content)
        self.add_line(new_content)
        self.show_result()


class OnNewArticle(action_base.ActionBase):
    icon = "✍️"
    title = "New article"

    def execute(self, *args, **kwargs):
        article_name = self.get_text_input("Article title", "Enter the name of the article (English, without spaces):")
        if not article_name:
            return

        article_name = article_name.replace(" ", "-")

        text = config["beginning_of_article"].replace("[YEAR]", datetime.now().strftime("%Y"))
        text = text.replace("[NAME]", article_name)
        text = text.replace("[DATE]", datetime.now().strftime("%Y-%m-%d"))
        text += f"\n# {article_name}\n\n\n"

        result, filename = h.md.add_note(Path(config["path_articles"]), article_name, text, True)
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_articles"]}" "{filename}"')
        self.add_line(result)


class OnNewDiary(action_base.ActionBase):
    icon = "📖"
    title = "New diary note"

    def execute(self, *args, **kwargs):
        result, filename = add_diary_new_dairy_in_year(config["path_diary"], config["beginning_of_md"])
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{filename}"')
        self.add_line(result)


def add_diary_entry_in_year(path_dream: str | Path, beginning_of_md: str, entry_content: str) -> tuple[str, Path]:
    """
    Adds a new diary entry to the yearly markdown file.

    If the yearly file doesn't exist, it creates one with the provided front matter.
    If it exists, it adds a new entry after the year heading and the table of contents.

    Args:
        path_dream (str | Path): The base path where the yearly file is stored.
        beginning_of_md (str): The YAML front matter to include if creating a new file.
        entry_content (str): The content to add after the date and time headers.

    Returns:
        tuple[str, Path]: A message indicating success/failure and the path to the yearly file.
    """
    current_date = datetime.now()
    year = current_date.strftime("%Y")

    path_dream = Path(path_dream)
    year_file = path_dream / f"{year}.md"

    # Prepare the new entry
    new_entry = f"## {current_date.strftime('%Y-%m-%d')}\n\n"
    new_entry += f"### {current_date.strftime('%H:%M')}\n\n"
    new_entry += entry_content

    # Check if the yearly file exists
    if not year_file.exists():
        # Create new yearly file with front matter, year heading, TOC, and new entry
        toc_section = "<details>\n<summary>📖 Contents</summary>\n\n## Contents\n\n</details>\n\n"
        content = f"{beginning_of_md}\n# {year}\n\n{toc_section}{new_entry}"
        year_file.write_text(content, encoding="utf-8")
        return f"✅ File {year_file} created.", year_file
    else:
        # File exists, read its content
        content = year_file.read_text(encoding="utf-8")

        # Find the year heading
        year_match = re.search(r'^# \d{4}', content, re.MULTILINE)
        if not year_match:
            # If no year heading, add it with TOC and the new entry
            toc_section = "<details>\n<summary>📖 Contents</summary>\n\n## Contents\n\n</details>\n\n"
            updated_content = f"{content}\n\n# {year}\n\n{toc_section}{new_entry}"
        else:
            # Find the table of contents section
            toc_match = re.search(r'<details>[\s\S]*?<\/details>', content)

            if toc_match:
                # Insert new entry right after the TOC
                toc_end_pos = toc_match.end()
                updated_content = (
                    content[:toc_end_pos] +
                    "\n\n" + new_entry +
                    content[toc_end_pos:].lstrip()
                )
            else:
                # No TOC found, create one and add new entry after it
                year_pos = year_match.end()
                toc_section = "\n\n<details>\n<summary>📖 Contents</summary>\n\n## Contents\n\n</details>\n\n"
                updated_content = (
                    content[:year_pos] +
                    toc_section +
                    new_entry +
                    content[year_pos:].lstrip()
                )

        # Write the updated content back to the file
        year_file.write_text(updated_content, encoding="utf-8")
        return f"✅ File {year_file} updated.", year_file


def add_diary_new_dream_in_year(path_dream: str | Path, beginning_of_md: str) -> tuple[str, Path]:
    """
    Adds a new dream diary entry to the yearly dream file.

    Args:
        path_dream (str | Path): The base path where the yearly dream file is stored.
        beginning_of_md (str): The YAML front matter to include if creating a new file.

    Returns:
        tuple[str, Path]: A message indicating success/failure and the path to the yearly dream file.
    """
    dream_content = "`` — I don't remember.\n\n" * 16
    return add_diary_entry_in_year(path_dream, beginning_of_md, dream_content)


def add_diary_new_dairy_in_year(path_dream: str | Path, beginning_of_md: str) -> tuple[str, Path]:
    """
    Adds a new diary entry to the yearly diary file.

    Args:
        path_dream (str | Path): The base path where the yearly diary file is stored.
        beginning_of_md (str): The YAML front matter to include if creating a new file.

    Returns:
        tuple[str, Path]: A message indicating success/failure and the path to the yearly diary file.
    """
    diary_content = "Text. \n\n"
    return add_diary_entry_in_year(path_dream, beginning_of_md, diary_content)


class OnNewDiaryDream(action_base.ActionBase):
    icon = "💤"
    title = "New dream note"

    def execute(self, *args, **kwargs):
        result, filename = add_diary_new_dream_in_year(config["path_dream"], config["beginning_of_md"])
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{filename}"')
        self.add_line(result)

class OnNewNoteDialog(action_base.ActionBase):
    icon = "📓"
    title = "New note"

    def execute(self, *args, **kwargs):
        filename = self.get_save_filename("Save Note", config["path_notes"], "Markdown (*.md);;All Files (*)")
        if not filename:
            return

        self.add_line(f"Folder path: {filename.parent}")
        self.add_line(f"File name without extension: {filename.stem}")

        is_with_images = kwargs.get("is_with_images", False)

        text = config["beginning_of_md"] + f"\n# {filename.stem}\n\n\n"

        result, filename = h.md.add_note(filename.parent, filename.stem, text, is_with_images)
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)


class OnNewNoteDialogWithImages(action_base.ActionBase):
    icon = "📓"
    title = "New note with images"

    def execute(self, *args, **kwargs):
        OnNewNoteDialog.execute(self, is_with_images=True)


class OnOptimizeImages(action_base.ActionBase):
    icon = "🖼️"
    title = "Optimize images in one MD"

    def execute(self, *args, **kwargs):
        self.filename = self.get_open_filename(
            "Open Markdown file", config["path_notes"], "Markdown (*.md);;All Files (*)"
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        try:
            self.add_line(funcs.optimize_images_in_md(self.filename))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")

    def thread_after(self, result):
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnOptimizeImagessFolder(action_base.ActionBase):
    icon = "🖼️"
    title = "Optimize images in …"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".md", funcs.optimize_images_in_md))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result):
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnPettierFolder(action_base.ActionBase):
    icon = "✨"
    title = "Prettier in …"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_github"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        commands = f"cd {self.folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)

    def thread_after(self, result):
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnSortSections(action_base.ActionBase):
    icon = "📶"
    title = "Sort sections in one MD"

    def execute(self, *args, **kwargs):
        self.filename = self.get_open_filename(
            "Open Markdown file", config["path_notes"], "Markdown (*.md);;All Files (*)"
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        try:
            self.add_line(h.md.sort_sections(self.filename))
            self.add_line(h.md.generate_image_captions(self.filename))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")

    def thread_after(self, result):
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnSortSectionsFolder(action_base.ActionBase):
    icon = "📶"
    title = "Sort sections in …"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_notes"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.sort_sections))
            self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.generate_image_captions))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result):
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
