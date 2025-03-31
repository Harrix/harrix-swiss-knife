from datetime import datetime
from pathlib import Path

import harrix_pylib as h

from harrix_swiss_knife import action_base

config = h.dev.load_config("config/config.json")


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

import yaml
from datetime import date


def identify_code_blocks(lines):
    return h.md.identify_code_blocks(lines)

def identify_code_blocks_line(markdown_line):
    return h.md.identify_code_blocks_line(markdown_line)

def split_yaml_content(markdown_text):
    return h.md.split_yaml_content(markdown_text)

def append_path_to_local_links_images_line(markdown_line, adding_path):
    return h.md.append_path_to_local_links_images_line(markdown_line, adding_path)

def combine_markdown_files(folder_path, recursive=False):
    def merge_yaml_values(key, value, combined_dict):
        if key not in combined_dict:
            combined_dict[key] = value
            return

        # If current value and new value are the same, do nothing
        if combined_dict[key] == value:
            return

        # Handling lists
        if isinstance(combined_dict[key], list):
            if isinstance(value, list):
                # Merge two lists, removing duplicates
                for item in value:
                    if item not in combined_dict[key]:
                        combined_dict[key].append(item)
            else:
                # Add new value to the list if it's not already there
                if value not in combined_dict[key]:
                    combined_dict[key].append(value)
        else:
            # Current value is not a list - convert it to a list and add the new value
            current_value = combined_dict[key]
            if isinstance(value, list):
                combined_dict[key] = [current_value]
                for item in value:
                    if item != current_value and item not in combined_dict[key]:
                        combined_dict[key].append(item)
            else:
                if current_value != value:
                    combined_dict[key] = [current_value, value]

    folder_path = Path(folder_path)

    # Delete all files ending with .g.md
    for path in folder_path.glob('*.g.md'):
        if path.is_file():
            path.unlink()

    # Get all .md files based on the recursive flag
    if recursive:
        # For recursive mode, we will structure files by folders
        md_files = []

        # First add files from the current folder
        current_folder_files = [f for f in folder_path.glob('*.md')
                            if f.is_file() and f.suffix == '.md' and not f.name.endswith('.g.md')]
        md_files.extend(current_folder_files)

        # Then process subfolders in alphabetical order
        subfolders = sorted([d for d in folder_path.iterdir() if d.is_dir()])
        for subfolder in subfolders:
            subfolder_files = []
            # Recursively collect files from each subfolder
            for file_path in subfolder.rglob('*.md'):
                if file_path.is_file() and file_path.suffix == '.md' and not file_path.name.endswith('.g.md'):
                    subfolder_files.append(file_path)

            # Sort files in the subfolder
            subfolder_files.sort()
            md_files.extend(subfolder_files)
    else:
        # Non-recursive - only get files in the current folder
        md_files = sorted([f for f in folder_path.glob('*.md')
                        if f.is_file() and f.suffix == '.md' and not f.name.endswith('.g.md')])

    # If there are no markdown files in the folder at all, exit
    if len(md_files) < 1:
        return f"Skipped {folder_path}: no markdown files found."

    data_yaml_headers = []
    contents = []

    for md_file in md_files:
        markdown_text = md_file.read_text(encoding='utf-8')
        yaml_md, content_md = split_yaml_content(markdown_text)

        # Check published flag
        if yaml_md:
            data_yaml = yaml.safe_load(yaml_md.strip("---\n"))
            published = data_yaml.get("published") if data_yaml and "published" in data_yaml else True
            if not published:
                continue

        # Delete old TOC
        content_md = h.md.remove_yaml_content(h.md.remove_toc_content(markdown_text))

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

        contents.append(content_md.strip())

    # Combine YAML headers intelligently
    combined_yaml = {}

    # Special processing for the attribution field
    all_attributions = []

    # Process all YAML headers
    for yaml_header in data_yaml_headers:
        for key, value in yaml_header.items():
            if key == 'attribution':
                # Collect all attributions in a separate list
                if isinstance(value, list):
                    all_attributions.extend(value)
                else:
                    all_attributions.append(value)
            else:
                # For all other fields, use standard merging
                merge_yaml_values(key, value, combined_yaml)

    # Add collected attributions to the final YAML
    if all_attributions:
        combined_yaml['attribution'] = all_attributions


    # Fix final YAML
    if "related-id" in combined_yaml:
        del combined_yaml["related-id"]
    if "date" in combined_yaml:
        del combined_yaml["date"]
    if "lang" in combined_yaml and isinstance(combined_yaml["lang"], list):
            combined_yaml["lang"] = "en" if "en" in combined_yaml["lang"] else combined_yaml["lang"][0]
    combined_yaml["update"] = date.today()

    # Prepare the final content
    folder_name = folder_path.name
    output_file = folder_path / f'_{folder_name}.g.md'

    # Dump combined YAML
    yaml_md = yaml.safe_dump(combined_yaml, allow_unicode=True, sort_keys=False)
    final_content = ""
    if combined_yaml:
        final_content += f'---\n{yaml_md}---\n\n'

    final_content += f'# {folder_name}\n\n'
    final_content += '\n\n'.join(contents)

    final_content = h.md.generate_toc_with_links_content(final_content)
    final_content = h.md.generate_image_captions_content(final_content)

    # Write to the output file
    output_file.write_text(final_content, encoding='utf-8')

    return f"✅ File {output_file} is created."


def combine_markdown_files_recursively(folder_path):
    result_lines = []
    folder_path = Path(folder_path)

    # Удаляем все существующие .g.md файлы
    for file in filter(
            lambda path: not any((part for part in path.parts if part.startswith("."))),
            Path(folder_path).rglob("*.g.md"),
            ):
        if file.is_file():
            file.unlink()

    # Собираем все папки, включая корневую
    all_folders = [folder_path]  # Начинаем с корневой папки

    # Добавляем все подпапки
    for subfolder in filter(
            lambda path: not any((part for part in path.parts if part.startswith("."))),
            Path(folder_path).rglob("*"),
            ):
        if subfolder.is_dir():
            all_folders.append(subfolder)

    # Обрабатываем каждую папку
    for folder in all_folders:
        # Получаем все .md файлы в этой папке (не рекурсивно)
        md_files_in_folder = [f for f in folder.glob("*.md") if f.is_file() and not f.name.endswith('.g.md')]

        # Получаем все .md файлы в этой папке и её подпапках (рекурсивно)
        md_files_recursive = [f for f in folder.rglob("*.md") if f.is_file() and not f.name.endswith('.g.md')]

        # Проверяем, есть ли непосредственно в подпапках markdown файлы
        subfolders = [f for f in folder.iterdir() if f.is_dir()]
        md_files_in_subfolders = []
        for subfolder in subfolders:
            md_files_in_subfolders.extend([f for f in subfolder.rglob("*.md") if f.is_file() and not f.name.endswith('.g.md')])

        # Создаем объединенный файл, если:
        # 1. В папке непосредственно есть как минимум 2 .md файла
        # 2. ИЛИ в папке и её подпапках есть как минимум 2 .md файла (включая случаи, когда все файлы в подпапках)
        if len(md_files_in_folder) >= 2 or (len(md_files_recursive) >= 2 and len(md_files_recursive) > len(md_files_in_folder)):
            try:
                result_lines.append(combine_markdown_files(folder, recursive=True))
            except Exception as e:
                result_lines.append(f"❌ Error processing {folder}: {e}")

    return "\n".join(result_lines)


class OnCombineMarkdownFiles(action_base.ActionBase): # ⚠️ TODO
    icon = "🔗"
    title = "Combine MD files in …"

    def execute(self, *args, **kwargs):
        self.folder_path = self.get_existing_directory("Select a folder with Markdown files",config["path_notes"])
        if not self.folder_path:
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    def in_thread(self):
        self.add_line(combine_markdown_files_recursively(self.folder_path))

    def thread_after(self, result):
        self.show_toast(f"{self.title} completed")
        self.show_result()
