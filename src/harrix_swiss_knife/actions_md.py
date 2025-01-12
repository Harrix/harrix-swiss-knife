from datetime import datetime
from pathlib import Path

import harrix_pylib as h

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


class on_markdown_add_author_book(action_base.ActionBase):
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


class on_markdown_add_image_captions(action_base.ActionBase):
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


class on_markdown_add_image_captions_folder(action_base.ActionBase):
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


class on_markdown_diary_new(action_base.ActionBase):
    icon: str = "📖"
    title = "New diary note"

    def execute(self, *args, **kwargs):
        output, filename = h.md.add_diary_new_diary(config["path_diary"], config["beginning_of_md"])
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{filename}"')
        self.add_line(output)


class on_markdown_diary_new_dream(action_base.ActionBase):
    icon: str = "💤"
    title = "New dream note"

    def execute(self, *args, **kwargs):
        output, filename = h.md.add_diary_new_dream(config["path_dream"], config["beginning_of_md"])
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{filename}"')
        self.add_line(output)


class on_markdown_diary_new_with_images(action_base.ActionBase):
    icon: str = "📚"
    title = "New diary note with images"

    def execute(self, *args, **kwargs):
        output, filename = h.md.add_diary_new_diary(
            config["path_diary"], config["beginning_of_md"], is_with_images=True
        )
        h.dev.run_powershell_script(f'{config["editor"]} "{config["vscode_workspace_diaries"]}" "{filename}"')
        self.add_line(output)


class on_markdown_get_list_movies_books(action_base.ActionBase):
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


class on_markdown_new_article(action_base.ActionBase):
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


class on_markdown_new_note_dialog(action_base.ActionBase):
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


class on_markdown_new_note_dialog_with_images(action_base.ActionBase):
    icon: str = "📓"
    title = "New note with images"

    def execute(self, *args, **kwargs):
        on_markdown_new_note_dialog.execute(self, is_with_images=True)
