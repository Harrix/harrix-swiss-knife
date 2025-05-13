from datetime import datetime
from pathlib import Path
from typing import Any

import harrix_pylib as h

from harrix_swiss_knife import action_base, funcs

config = h.dev.load_config("config/config.json")


class OnBeautifyMdNotesAllInOne(action_base.ActionBase):
    icon = "😎"
    title = "Beautify MD notes (All in one)"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        for path in config["paths_notes"]:
            try:
                # Generate image captions
                self.add_line("🔵 Generate image captions")
                try:
                    self.add_line(h.file.apply_func(path, ".md", h.md.generate_image_captions))
                except Exception as e:  # noqa: BLE001
                    self.add_line(f"❌ Error: {e}")

                # Generate TOC
                self.add_line("🔵 Generate TOC")
                try:
                    self.add_line(h.file.apply_func(path, ".md", h.md.generate_toc_with_links))
                except Exception as e:  # noqa: BLE001
                    self.add_line(f"❌ Error: {e}")

                # Generate summaries
                for path_notes_for_summaries in config["paths_notes_for_summaries"]:
                    if (Path(path_notes_for_summaries).resolve()).is_relative_to(Path(path).resolve()):
                        try:
                            self.add_line(h.md.generate_summaries(path_notes_for_summaries))
                        except Exception as e:  # noqa: BLE001
                            self.add_line(f"❌ Error: {e}")

                # Combine MD files
                self.add_line("🔵 Combine MD files")
                self.add_line(h.md.combine_markdown_files_recursively(path))

                # Format YAML
                self.add_line("🔵 Format YAML")
                try:
                    self.add_line(h.file.apply_func(path, ".md", h.md.format_yaml))
                except Exception as e:  # noqa: BLE001
                    self.add_line(f"❌ Error: {e}")

                # Prettier
                self.add_line("🔵 Prettier")
                commands = f"cd {path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
                result = h.dev.run_powershell_script(commands)
                self.add_line(result)
            except Exception as e:  # noqa: BLE001
                self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnCombineMarkdownFiles(action_base.ActionBase):
    icon = "🔗"
    title = "Combine MD files in …"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_notes"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        self.add_line(h.md.combine_markdown_files_recursively(self.folder_path))

        commands = f"cd {self.folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()


class OnDownloadAndReplaceImages(action_base.ActionBase):
    icon = "📥"
    title = "Download images in one MD"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.filename = self.get_open_filename(
            "Open Markdown file",
            config["path_notes"],
            "Markdown (*.md);;All Files (*)",
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            self.add_line(h.md.download_and_replace_images(self.filename))
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnDownloadAndReplaceImagesFolder(action_base.ActionBase):
    icon = "📥"
    title = "Download images in …"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.download_and_replace_images))
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnFormatQuotesAsMarkdownContent(action_base.ActionBase):
    icon = "❞"
    title = "Format quotes as markdown content"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        content = self.get_text_textarea("Quotes", "Input quotes")
        if not content:
            return

        result = h.md.format_quotes_as_markdown_content(content)

        self.add_line(result)
        self.show_result()


class OnFormatYaml(action_base.ActionBase):
    icon = "✨"
    title = "Format YAML in …"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.format_yaml))
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnGenerateAuthorBook(action_base.ActionBase):
    icon = "❞"
    title = "Quotes. Add author and title"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory("Select a folder with quotes", config["path_quotes"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            result = h.file.apply_func(self.folder_path, ".md", h.md.generate_author_book)
            self.add_line(result)
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnGenerateImageCaptions(action_base.ActionBase):
    icon = "🌄"
    title = "Add image captions in one MD"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.filename = self.get_open_filename(
            "Open Markdown file",
            config["path_articles"],
            "Markdown (*.md);;All Files (*)",
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            self.add_line(h.md.generate_image_captions(self.filename))
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnGenerateImageCaptionsFolder(action_base.ActionBase):
    icon = "🌄"
    title = "Add image captions in …"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.generate_image_captions))
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnGenerateShortNoteTocWithLinks(action_base.ActionBase):
    icon = "🤏"
    title = "Generate a short version with only TOC"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.filename = self.get_open_filename(
            "Open Markdown file",
            config["path_articles"],
            "Markdown (*.md);;All Files (*)",
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            self.add_line(h.md.generate_short_note_toc_with_links(self.filename))
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnGenerateToc(action_base.ActionBase):
    icon = "📑"
    title = "Generate TOC in one MD"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.filename = self.get_open_filename(
            "Open Markdown file",
            config["path_articles"],
            "Markdown (*.md);;All Files (*)",
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            self.add_line(h.md.generate_toc_with_links(self.filename))
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnGenerateTocFolder(action_base.ActionBase):
    icon = "📑"
    title = "Generate TOC in …"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.generate_toc_with_links))
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnGetListMoviesBooks(action_base.ActionBase):
    icon = "🎬"
    title = "Get a list of movies, books for web"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
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

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        content = self.get_text_textarea("Markdown content", "Input Markdown content")
        if not content:
            return

        new_content = h.md.increase_heading_level_content(content)
        self.add_line(new_content)
        self.show_result()


class OnNewArticle(action_base.ActionBase):
    icon = "✍️"
    title = "New article"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        article_name = self.get_text_input("Article title", "Enter the name of the article (English, without spaces):")
        if not article_name:
            return

        article_name = article_name.replace(" ", "-")

        text = config["beginning_of_article"].replace(
            "[YEAR]",
            datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y"),
        )
        text = text.replace("[NAME]", article_name)
        text = text.replace("[DATE]", datetime.now(tz=datetime.now().astimezone().tzinfo).strftime("%Y-%m-%d"))
        text += f"\n# {article_name}\n\n\n"

        result, filename = h.md.add_note(Path(config["path_articles"]), article_name, text, True)
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_articles"]}" "{filename}"')
        self.add_line(result)


class OnNewDiary(action_base.ActionBase):
    icon = "📖"
    title = "New diary note"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        result, filename = h.md.add_diary_new_dairy_in_year(config["path_diary"], config["beginning_of_md"])
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)


class OnNewDiaryDream(action_base.ActionBase):
    icon = "💤"
    title = "New dream note"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        result, filename = h.md.add_diary_new_dream_in_year(config["path_dream"], config["beginning_of_md"])
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)


class OnNewNoteDialog(action_base.ActionBase):
    icon = "📓"
    title = "New note"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        filename = self.get_save_filename("Save Note", config["path_notes"], "Markdown (*.md);;All Files (*)")
        if not filename:
            return

        self.add_line(f"Folder path: {filename.parent}")
        self.add_line(f"File name without extension: {filename.stem}")

        is_with_images = kwargs.get("is_with_images", False)

        text = config["beginning_of_md"] + f"\n# {filename.stem}\n\n\n"

        filename_final = filename.stem.replace("-", "--").replace(" ", "-")

        result, filename = h.md.add_note(filename.parent, filename_final, text, is_with_images=is_with_images)
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(result)


class OnNewNoteDialogWithImages(action_base.ActionBase):
    icon = "📓"
    title = "New note with images"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        OnNewNoteDialog.execute(self, is_with_images=True)


class OnOptimizeImages(action_base.ActionBase):
    icon = "🖼️"
    title = "Optimize images in one MD"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.filename = self.get_open_filename(
            "Open Markdown file",
            config["path_notes"],
            "Markdown (*.md);;All Files (*)",
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            self.add_line(funcs.optimize_images_in_md(self.filename))
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnOptimizeImagesFolder(action_base.ActionBase):
    icon = "🖼️"
    title = "Optimize images in …"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".md", funcs.optimize_images_in_md))
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnOptimizeImagesFolderPngToAvif(action_base.ActionBase):
    icon = "🖼️"
    title = "Optimize images (with PNG to AVIF) in …"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".md", funcs.optimize_images_in_md_png_to_avif))
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnPettierFolder(action_base.ActionBase):
    icon = "✨"
    title = "Prettier in …"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_github"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        commands = f"cd {self.folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()


class OnSortSections(action_base.ActionBase):
    icon = "📶"
    title = "Sort sections in one MD"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.filename = self.get_open_filename(
            "Open Markdown file",
            config["path_notes"],
            "Markdown (*.md);;All Files (*)",
        )
        if not self.filename:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            self.add_line(h.md.sort_sections(self.filename))
            self.add_line(h.md.generate_image_captions(self.filename))
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.filename} completed")
        self.show_result()


class OnSortSectionsFolder(action_base.ActionBase):
    icon = "📶"
    title = "Sort sections in …"

    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_notes"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self) -> None:
        try:
            self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.sort_sections))
            self.add_line(h.file.apply_func(self.folder_path, ".md", h.md.generate_image_captions))
        except Exception as e:  # noqa: BLE001
            self.add_line(f"❌ Error: {e}")

    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} {self.folder_path} completed")
        self.show_result()
