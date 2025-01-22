import re
from datetime import datetime
from pathlib import Path

import harrix_pylib as h

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class on_add_author_book(action_base.ActionBase):
    icon: str = "❞"
    title: str = "Quotes. Add author and title"
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder with quotes", config["path_quotes"])
        if not folder_path:
            return

        try:
            self.add_line(h.file.apply_func(folder_path, ".md", h.md.add_author_book))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")


class on_add_image_captions(action_base.ActionBase):
    icon: str = "🌄"
    title: str = "Add image captions in one MD"

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename(
            "Open Markdown file", config["path_articles"], "Markdown (*.md);;All Files (*)"
        )
        if not filename:
            return

        try:
            self.add_line(h.md.add_image_captions(filename))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")


class on_add_image_captions_folder(action_base.ActionBase):
    icon: str = "🌄"
    title = "Add image captions in …"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not folder_path:
            return

        try:
            self.add_line(h.file.apply_func(folder_path, ".md", h.md.add_image_captions))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")


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


class on_generate_toc(action_base.ActionBase):
    icon: str = "📑"
    title = "Generate TOC in …"
    is_show_output = True

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_articles"])
        if not folder_path:
            return

        try:
            self.add_line(h.file.apply_func(folder_path, ".md", generate_toc_with_links))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")


class on_get_list_movies_books(action_base.ActionBase):
    icon: str = "🎬"
    title = "Get a list of movies, books for web"

    def execute(self, *args, **kwargs):
        content = self.get_text_textarea("Markdown content", "Input Markdown content")
        count = 0
        for line in content.splitlines():
            if line.startswith("### "):
                self.add_line(f"- {line[4:].strip()}")
                count += 1

        self.add_line(f"\nCount: {count}")


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
    icon: str = "#"
    title: str = "Sort sections in one MD"

    def execute(self, *args, **kwargs):
        filename = self.get_open_filename("Open Markdown file", config["path_notes"], "Markdown (*.md);;All Files (*)")
        if not filename:
            return

        try:
            self.add_line(h.md.sort_sections(filename))
            self.add_line(h.md.add_image_captions(filename))
        except Exception as e:
            self.add_line(f"❌ Ошибка: {e}")


class on_sort_sections_folder(action_base.ActionBase):
    icon: str = "#"
    title = "Sort sections in …"

    def execute(self, *args, **kwargs):
        folder_path = self.get_existing_directory("Select a folder with Markdown files", config["path_notes"])
        if not folder_path:
            return

        try:
            self.add_line(h.file.apply_func(folder_path, ".md", h.md.sort_sections))
            self.add_line(h.file.apply_func(folder_path, ".md", h.md.add_image_captions))
        except Exception as e:
            self.add_line(f"❌ Error: {e}")


def generate_toc_with_links(filename: Path | str) -> str:
    def generate_id(text, existing_ids):
        # Convert text to lowercase
        text = text.lower()

        # Remove all non-word characters (e.g., punctuation, HTML)
        text = re.sub(r"[^\w\s]", "", text)

        # Replace spaces with hyphens
        text = re.sub(r"\s+", "-", text)

        # Replace two or more hyphens in a row with one
        text = re.sub(r"-+", "-", text)

        # Ensure uniqueness by appending a number if necessary
        original_text = text
        counter = 1
        while text in existing_ids:
            text = f"{original_text}-{counter}"
            counter += 1

        # Add the new unique ID to the set
        existing_ids.add(text)

        return text

    result_lines = []
    filename = Path(filename)

    document = filename.read_text(encoding="utf8")

    parts = document.split("---", 2)
    if len(parts) < 3:
        yaml_md = ""
    else:
        yaml_md = f"---{parts[1]}---"

    # Generate TOC
    existing_ids = set()
    lines = h.md.remove_yaml_and_code(document).splitlines()
    toc_lines = []
    for line in lines:
        if line.startswith("##"):
            # Determine the header level
            level = len(re.match(r"#+", line).group())
            # Extract the header text
            title = line[level:].strip()
            title = title.replace("<!-- top-section -->", "")
            text_link = generate_id(title, existing_ids)
            link = f"#{text_link}"
            title_text = title.strip()
            # Form the table of contents entry
            toc_lines.append(f"{'  ' * (level - 2)}- [{title_text}]({link})")
    toc = "\n".join(toc_lines)
    result_lines.append("TOC:\n\n" + toc)

    # Delete old TOC
    is_stop_searching_toc = False
    new_lines = []
    lines = h.md.remove_yaml(document).splitlines()
    for line, is_code_block in h.md.identify_code_blocks(lines):
        if is_code_block:
            new_lines.append(line)
            continue
        if line.startswith("##"):
            is_stop_searching_toc = True
        if is_stop_searching_toc:
            new_lines.append(line)
        elif not re.match(r"- \[(.*?)\]\(#(.*?)\)$", line.strip()):
            if len(new_lines) == 0 or new_lines[-1].strip() or line:
                new_lines.append(line)
    content_without_yaml = "\n".join(new_lines)

    # Paste TOC
    is_stop_searching_place_toc = False
    is_first_paragraph = False
    new_lines = []
    lines = content_without_yaml.splitlines()
    for line, is_code_block in h.md.identify_code_blocks(lines):
        new_lines.append(line)
        if is_code_block:
            continue
        if line.startswith("##"):
            if not is_stop_searching_place_toc and len(toc_lines) > 1:
                new_lines.insert(len(new_lines) - 1, toc + "\n")
            is_stop_searching_place_toc = True
        if is_stop_searching_place_toc or line.startswith("# ") or line.startswith("![") or not line.strip():
            continue
        if line and not is_first_paragraph and len(toc_lines) > 1:
            new_lines.append("\n" + toc)
            is_first_paragraph = True
            is_stop_searching_place_toc = True
    content_without_yaml = "\n".join(new_lines)
    if content_without_yaml[-1] != "\n":
        content_without_yaml += "\n"

    document_new = yaml_md + "\n\n" + content_without_yaml
    if document != document_new:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(document_new)
        result_lines.append(f"✅ TOC is added or refreshed in {filename}.")
    else:
        result_lines.append("File is not changed.")

    return "\n".join(result_lines)
