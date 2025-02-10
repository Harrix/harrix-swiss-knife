from datetime import datetime
from pathlib import Path

import harrix_pylib as h
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication, QMessageBox

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class on_diary_new(action_base.ActionBase):
    icon: str = "📖"
    title = "New diary note"

    def execute(self, *args, **kwargs):
        output, filename = h.md.add_diary_new_diary(config["path_diary"], config["beginning_of_md"])
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{filename}"')
        self.add_line(output)


class on_diary_new_dream(action_base.ActionBase):
    icon: str = "💤"
    title = "New dream note"

    def execute(self, *args, **kwargs):
        output, filename = h.md.add_diary_new_dream(config["path_dream"], config["beginning_of_md"])
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{filename}"')
        self.add_line(output)


class on_diary_new_with_images(action_base.ActionBase):
    icon: str = "📚"
    title = "New diary note with images"

    def execute(self, *args, **kwargs):
        output, filename = h.md.add_diary_new_diary(
            config["path_diary"], config["beginning_of_md"], is_with_images=True
        )
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{filename}"')
        self.add_line(output)


class on_download_and_replace_images(action_base.ActionBase):
    icon: str = "📥"
    title: str = "Download images in one MD"

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename("Open Markdown file", config["path_notes"], "Markdown (*.md);;All Files (*)")
        if not filename:
            return

        try:
            self.add_line(h.md.download_and_replace_images(filename))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")


class on_download_and_replace_images_folder(action_base.ActionBase):
    icon: str = "📥"
    title = "Download images in …"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not folder_path:
            return

        try:
            self.add_line(h.file.apply_func(folder_path, ".md", h.md.download_and_replace_images))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")


class on_format_yaml(action_base.ActionBase):
    icon: str = "✨"
    title = "Format YAML"
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not folder_path:
            return

        try:
            self.add_line(h.file.apply_func(folder_path, ".md", h.md.format_yaml))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")


class on_generate_author_book(action_base.ActionBase):
    icon: str = "❞"
    title: str = "Quotes. Add author and title"
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder with quotes", config["path_quotes"])
        if not folder_path:
            return

        try:
            result = h.file.apply_func(folder_path, ".md", h.md.generate_author_book)
            self.add_line(result)
            clipboard = QApplication.clipboard()
            clipboard.setText(result, QClipboard.Clipboard)
            QMessageBox.information(None, "Copy", "Text copied to clipboard!")
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")


class on_generate_image_captions(action_base.ActionBase):
    icon: str = "🌄"
    title: str = "Add image captions in one MD"

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename(
            "Open Markdown file", config["path_articles"], "Markdown (*.md);;All Files (*)"
        )
        if not filename:
            return

        try:
            self.add_line(h.md.generate_image_captions(filename))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")


class on_generate_image_captions_folder(action_base.ActionBase):
    icon: str = "🌄"
    title = "Add image captions in …"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not folder_path:
            return

        try:
            self.add_line(h.file.apply_func(folder_path, ".md", h.md.generate_image_captions))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")


class on_generate_toc(action_base.ActionBase):
    icon: str = "📑"
    title = "Generate TOC in one MD"
    is_show_output = True

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename(
            "Open Markdown file", config["path_articles"], "Markdown (*.md);;All Files (*)"
        )
        if not filename:
            return

        try:
            self.add_line(h.md.generate_toc_with_links(filename))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")


class on_generate_toc_folder(action_base.ActionBase):
    icon: str = "📑"
    title = "Generate TOC in …"
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not folder_path:
            return

        try:
            self.add_line(h.file.apply_func(folder_path, ".md", h.md.generate_toc_with_links))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")


class on_get_list_movies_books(action_base.ActionBase):
    icon: str = "🎬"
    title = "Get a list of movies, books for web"

    def execute(self, *args, **kwargs):
        content = self.get_text_textarea("Markdown content", "Input Markdown content")
        result = ""
        count = 0
        for line in content.splitlines():
            if line.startswith("### "):
                result += f"- {line[4:].strip()}\n"
                count += 1

        result += f"\nCount: {count}"
        self.add_line(result)

        clipboard = QApplication.clipboard()
        clipboard.setText(result, QClipboard.Clipboard)
        QMessageBox.information(None, "Copy", "Text copied to clipboard!")


class on_increase_heading_level_content(action_base.ActionBase):
    icon: str = "👉"
    title = "Increase heading level"

    def execute(self, *args, **kwargs):
        content = self.get_text_textarea("Markdown content", "Input Markdown content")
        new_content = h.md.increase_heading_level_content(content)
        self.add_line(new_content)
        clipboard = QApplication.clipboard()
        clipboard.setText(new_content, QClipboard.Clipboard)
        QMessageBox.information(None, "Copy", "Text copied to clipboard!")


class on_new_article(action_base.ActionBase):
    icon: str = "✍️"
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

        output, filename = h.md.add_note(Path(config["path_articles"]), article_name, text, True)
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_articles"]}" "{filename}"')
        self.add_line(output)


class on_new_note_dialog(action_base.ActionBase):
    icon: str = "📓"
    title = "New note"

    def execute(self, *args, **kwargs):
        filename = self.get_save_filename("Save Note", config["path_notes"], "Markdown (*.md);;All Files (*)")
        if not filename:
            return

        self.add_line(f"Folder path: {filename.parent}")
        self.add_line(f"File name without extension: {filename.stem}")

        is_with_images = kwargs.get("is_with_images", False)

        text = config["beginning_of_md"] + f"\n# {filename.stem}\n\n\n"

        output, filename = h.md.add_note(filename.parent, filename.stem, text, is_with_images)
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_notes"]}" "{filename}"')
        self.add_line(output)


class on_new_note_dialog_with_images(action_base.ActionBase):
    icon: str = "📓"
    title = "New note with images"

    def execute(self, *args, **kwargs):
        on_new_note_dialog.execute(self, is_with_images=True)


class on_prettier_folder(action_base.ActionBase):
    icon: str = "✨"
    title = "Prettier in …"
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_github"])
        if not folder_path:
            return

        commands = f"cd {folder_path}\nprettier --parser markdown --write **/*.md --end-of-line crlf"
        output = h.dev.run_powershell_script(commands)
        self.add_line(output)


class on_sort_sections(action_base.ActionBase):
    icon: str = "📶"
    title: str = "Sort sections in one MD"

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename("Open Markdown file", config["path_notes"], "Markdown (*.md);;All Files (*)")
        if not filename:
            return

        try:
            self.add_line(h.md.sort_sections(filename))
            self.add_line(h.md.generate_image_captions(filename))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")


class on_sort_sections_folder(action_base.ActionBase):
    icon: str = "📶"
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


def append_path_to_local_links_images_line(markdown_line, adding_path):
    adding_path = adding_path.replace('\\', '/')
    if adding_path.endswith('/'):
        adding_path = adding_path[:-1]

    regex_for_images = r"\!\[(.*?)\]\((?!http)(.*?)\.(.*?)\)"

    def replace_path_in_images(match):
        alt_text = match.group(1)
        img_path = match.group(2).replace('\\', '/')
        extension = match.group(3)
        return f"![{alt_text}]({adding_path}/{img_path}.{extension})"

    markdown_line = re.sub(regex_for_images, replace_path_in_images, markdown_line)

    regex_for_links = r"\[(.*?)\]\((?!http)(.*?)\)"

    def replace_path_in_links(match):
        link_text = match.group(1)
        file_path = match.group(2).replace('\\', '/')
        return f"[{link_text}]({adding_path}/{file_path})"

    markdown_line = re.sub(regex_for_links, replace_path_in_links, markdown_line)

    return markdown_line


# m = "Image ![Alt text](img/image.png) text [file.zip](files/file.zip)"
# print(append_path_to_local_links_images_line(m, "folder/subfolder"))

def combine_markdown_files(path):
    """
    Combines all Markdown (.md) files in the specified directory and subdirectories
    into a single Markdown file, excluding files that end with '.g.md'.
    """
    base_path = Path(path)

    # Get all .md files excluding those ending with '.g.md'
    md_files = [f for f in base_path.glob('**/*.md') if f.is_file() and f.suffix == '.md' and not f.name.endswith('.g.md')]

    yaml_headers = []
    contents = []

    for md_file in md_files:
        markdown_text = md_file.read_text(encoding='utf-8')
        parts = markdown_text.split('---', 2)
        if len(parts) < 3:
            yaml_md, content_md = '', markdown_text
        else:
            yaml_md, content_md = f'---{parts[1]}---', parts[2].lstrip()

        # Parse YAML and collect headers
        if yaml_md:
            yaml_content = yaml.safe_load(parts[1])
            yaml_headers.append(yaml_content)
        else:
            yaml_content = {}

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

                adding_path = '/'.join(md_file.parent.parts[len(base_path.parts):])
                part_new = append_path_to_local_links_images_line(part, adding_path)
                if "![" in part:
                    print(part)
                    print(part_new)
                    print("-----")
                new_parts.append(part_new)

            line_new = "".join(new_parts)
            new_lines.append(line_new)
        content_md = "\n".join(new_lines)

        # Collect content
        contents.append(content_md)

    # Combine YAML headers
    combined_yaml = {}
    for y in yaml_headers:
        combined_yaml.update(y)

    # Prepare the final content
    folder_name = base_path.name
    output_file = base_path / f'_{folder_name}.g.md'

    # Dump combined YAML
    yaml_md = yaml.safe_dump(combined_yaml, sort_keys=False)
    final_content = ""
    if combined_yaml:
        final_content += f'---\n{yaml_md}---\n\n'

    final_content += f'# {folder_name}\n\n'
    final_content += '\n\n'.join(contents)

    # Write to the output file
    output_file.write_text(final_content, encoding='utf-8')

    return output_file


class on_combine_markdown_files(action_base.ActionBase):
    icon: str = "📶"
    title = "Combine MD files in …"

    def execute(self, *args, **kwargs):
        # folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_notes"])
        folder_path="D:/Dropbox/Notes/Notes/IT_Dev"
        if not folder_path:
            return

        try:
            output_file = combine_markdown_files(folder_path)
            # h.md.generate_image_captions))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")


# combine_markdown_files("D:/Dropbox/Notes/Notes/IT_Dev")
# print(combine_markdown_files("D:/Dropbox/Notes/Notes/IT_Dev"))

# from pathlib import Path

# path = Path("C:/Notes/")
# path2 = Path("C:/Notes/Python/Pycharm/")

# relative_path_str = '/'.join(path2.parts[len(path.parts):])
# print(relative_path_str)  # Python/Pycharm