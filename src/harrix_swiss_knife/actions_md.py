from datetime import datetime
from pathlib import Path
import time

import harrix_pylib as h
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication, QMessageBox

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class OnNewDiary(action_base.ActionBase):
    icon = "📖"
    title = "New diary note"

    def execute(self, *args, **kwargs):
        result, filename = h.md.add_diary_new_diary(config["path_diary"], config["beginning_of_md"])
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{filename}"')
        self.add_line(result)


class OnNewDiaryDream(action_base.ActionBase):
    icon = "💤"
    title = "New dream note"

    def execute(self, *args, **kwargs):
        result, filename = h.md.add_diary_new_dream(config["path_dream"], config["beginning_of_md"])
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{filename}"')
        self.add_line(result)


class OnNewDiaryWithImages(action_base.ActionBase):
    icon = "📚"
    title = "New diary note with images"

    def execute(self, *args, **kwargs):
        result, filename = h.md.add_diary_new_diary(
            config["path_diary"], config["beginning_of_md"], is_with_images=True
        )
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{filename}"')
        self.add_line(result)


class OnDownloadAndReplaceImages(action_base.ActionBase):
    icon = "📥"
    title = "Download images in one MD"

    def execute(self, *args, **kwargs):
        self.filename = self.get_open_filename("Open Markdown file", config["path_notes"], "Markdown (*.md);;All Files (*)")
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


class OnIncreaseHeadingLevelContent(action_base.ActionBase): # ⚠️ TODO
    icon = "👉"
    title = "Increase heading level"

    def execute(self, *args, **kwargs):
        content = self.get_text_textarea("Markdown content", "Input Markdown content")
        if not content:
            return

        new_content = h.md.increase_heading_level_content(content)
        self.add_line(new_content)
        clipboard = QApplication.clipboard()
        clipboard.setText(new_content, QClipboard.Clipboard)
        QMessageBox.information(None, "Copy", "Text copied to clipboard!")


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


class OnPettierFolder(action_base.ActionBase): # ⚠️ TODO
    icon = "✨"
    title = "Prettier in …"
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_github"])
        if not folder_path:
            return

        commands = f"cd {folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        result = h.dev.run_powershell_script(commands)
        self.add_line(result)


class OnSortSections(action_base.ActionBase): # ⚠️ TODO
    icon = "📶"
    title = "Sort sections in one MD"

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename("Open Markdown file", config["path_notes"], "Markdown (*.md);;All Files (*)")
        if not filename:
            return

        try:
            self.add_line(h.md.sort_sections(filename))
            self.add_line(h.md.generate_image_captions(filename))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")


class OnSortSectionsFolder(action_base.ActionBase): # ⚠️ TODO
    icon = "📶"
    title = "Sort sections in …"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_notes"])
        if not folder_path:
            return

        try:
            self.add_line(h.file.apply_func(folder_path, ".md", h.md.sort_sections))
            self.add_line(h.file.apply_func(folder_path, ".md", h.md.generate_image_captions))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")

from pathlib import Path
import yaml
import harrix_pylib as h
import re


def identify_code_blocks(lines):
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

def identify_code_blocks_line(markdown_line):
    current_text = ""
    in_code = False
    backtick_count = 0

    i = 0
    while i < len(markdown_line):
        if markdown_line[i] == "`":
            # Counting the number of consecutive backquotes
            count = 1
            while i + 1 < len(markdown_line) and markdown_line[i + 1] == "`":
                count += 1
                i += 1

            if not in_code:
                # Start of code block
                if current_text:
                    yield current_text, False
                    current_text = ""
                backtick_count = count
                current_text = "`" * count
                in_code = True
            elif count == backtick_count:
                # End of code block
                current_text += "`" * count
                yield current_text, True
                current_text = ""
                in_code = False
            else:
                # Backquotes inside the code
                current_text += "`" * count
        else:
            current_text += markdown_line[i]

        i += 1

    if current_text:
        yield current_text, False

def split_yaml_content(markdown_text: str) -> tuple[str, str]:
    if not markdown_text.startswith("---"):
        return "", markdown_text
    parts = markdown_text.split("---", 2)
    if len(parts) < 3:
        return "", markdown_text
    return f"---{parts[1]}---", parts[2].lstrip()

def append_path_to_local_links_images_line(markdown_line: str, adding_path: str) -> str:
    def replace_path_in_links(match):
        link_text = match.group(1)
        file_path = match.group(2).replace("\\", "/")
        if adding_path == "":
            return f"[{link_text}]({file_path})"
        return f"[{link_text}]({adding_path}/{file_path})"

    adding_path = adding_path.replace("\\", "/")
    if adding_path.endswith("/"):
        adding_path = adding_path[:-1]
    return re.sub(r"\[(.*?)\]\(((?!http).*?)\)", replace_path_in_links, markdown_line)

def combine_markdown_files(folder_path):
    folder_path = Path(folder_path)

    # Get all .md files excluding those ending with '.g.md'
    md_files = [f for f in folder_path.glob('**/*.md') if f.is_file() and f.suffix == '.md' and not f.name.endswith('.g.md')]

    data_yaml_headers = []
    contents = []

    for md_file in md_files:
        markdown_text = md_file.read_text(encoding='utf-8')
        yaml_md, content_md = split_yaml_content(markdown_text)

        # Parse YAML and collect headers
        if yaml_md:
            data_yaml = yaml.safe_load(yaml_md.strip("---\n"))
            data_yaml_headers.append(data_yaml)
        else:
            data_yaml = {}

        # Increase heading levels
        content_md = h.md.increase_heading_level_content(content_md)

        # Fix links in no-code lines
        new_lines = []
        lines = content_md.split("\n")
        for line, is_code_block in identify_code_blocks(lines):
            if is_code_block:
                new_lines.append(line)
                continue

            # Check no-code line
            new_parts = []
            for part, is_code in identify_code_blocks_line(line):
                if is_code:
                    new_parts.append(part)
                    continue

                adding_path = '/'.join(md_file.parent.parts[len(folder_path.parts):])
                if adding_path:
                    part_new = append_path_to_local_links_images_line(part, adding_path)
                else:
                    part_new = part
                new_parts.append(part_new)

            line_new = "".join(new_parts)
            new_lines.append(line_new)
        content_md = "\n".join(new_lines)

        # Collect content
        contents.append(content_md.strip())

    # Combine YAML headers
    combined_yaml = {}
    for y in data_yaml_headers:
        combined_yaml.update(y)

    # Prepare the final content
    folder_name = folder_path.name
    output_file = folder_path / f'_{folder_name}.g.md'

    # Dump combined YAML
    yaml_md = yaml.safe_dump(combined_yaml, sort_keys=False)
    final_content = ""
    if combined_yaml:
        final_content += f'---\n{yaml_md}---\n\n'

    final_content += f'# {folder_name}\n\n'
    final_content += '\n\n'.join(contents)

    final_content = h.md.generate_toc_with_links_content(final_content)
    final_content = h.md.generate_image_captions_content(final_content)

    # Write to the output file
    output_file.write_text(final_content, encoding='utf-8')

    return f"File {output_file} is created."


def combine_markdown_files_recursively(folder_path):
    result_lines = []
    folder_path = Path(folder_path)

    for file in filter(
            lambda path: not any((part for part in path.parts if part.startswith("."))),
            Path(folder_path).rglob("*"),
            ):
        if file.is_file() and file.name.endswith(".g.md"):
            file.unlink()

    for folder in filter(
            lambda path: not any((part for part in path.parts if part.startswith("."))),
            Path(folder_path).rglob("*"),
            ):
        if not folder.is_dir():
            continue
        if len(list(folder.rglob("*.md"))) < 2:
            continue
        try:
            result_lines.append(combine_markdown_files(folder))
        except Exception as e:
            result_lines.append(f"❌ Error: {e}")

    return "\n".join(result_lines)


class OnCombineMarkdownFiles(action_base.ActionBase): # ⚠️ TODO
    icon = "🔗"
    title = "Combine MD files in …"
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder with Markdown files",config["path_notes"])
        if not folder_path:
            return

        self.add_line(combine_markdown_files_recursively(folder_path))

